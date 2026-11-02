"""Authentication and session management business logic service."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import (
    AccountLockedException,
    AccountSuspendedException,
    ConflictException,
    DomainException,
    EmailAlreadyExistsException,
    ForbiddenException,
    InvalidCredentialsException,
    InvalidTokenException,
    MobileAlreadyExistsException,
    RateLimitExceededException,
    SessionRevokedException,
    TokenExpiredException,
    TokenReuseDetectedException,
    UnauthorizedException,
)
from src.core.logging import logger
from src.core.security import (
    create_access_token,
    ensure_utc,
    generate_csrf_token,
    generate_otp,
    generate_refresh_token,
    get_password_hash,
    hash_otp,
    hash_token,
    validate_password_strength,
    verify_otp,
    verify_password,
)
from src.models.applications import VolunteerApplication
from src.models.communications import CommunicationJob
from src.models.consent import ConsentRecord
from src.models.users import EmailVerification, PasswordResetToken, User, UserSession
from src.models.volunteers import (
    AlumniProfile,
    CorporateProfile,
    StudentProfile,
    VolunteerProfile,
)
from src.repositories.token_repo import token_repository
from src.repositories.user_repo import user_repository
from src.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserSummaryResponse,
    VerifyEmailResponse,
)

# Permitted account lifecycle status transitions
PERMITTED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "PENDING_VERIFICATION": {"PENDING_APPROVAL"},
    "PENDING_APPROVAL": {"APPROVED", "REJECTED"},
    "APPROVED": {"SUSPENDED", "INACTIVE"},
    "SUSPENDED": {"APPROVED"},
    "REJECTED": set(),
    "INACTIVE": set(),
    # Legacy compatibility:
    "UNVERIFIED": {"PENDING", "PENDING_APPROVAL"},
    "PENDING": {"APPROVED", "REJECTED", "PENDING_APPROVAL"},
}


def enforce_status_transition(current: str, target: str) -> None:
    """Enforce strict account lifecycle state transitions."""
    allowed = PERMITTED_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise DomainException(
            f"Invalid status transition from '{current}' to '{target}'.",
            code="INVALID_STATUS_TRANSITION",
        )


# In-process lock tracker for concurrent token refresh operations
_refresh_locks: dict[str, asyncio.Lock] = {}
_refresh_lock_guard = asyncio.Lock()


class AuthService:
    """Core domain service orchestrating authentication, sessions, and recovery workflows."""

    async def register(
        self,
        db: AsyncSession,
        request: RegisterRequest,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> RegisterResponse:
        """Register a new volunteer with base user, profile, category, and consent records."""
        # 1. Normalize email & validate password strength
        normalized_email = request.email.strip().lower()
        validate_password_strength(request.password)

        # 2. Check email uniqueness
        if await user_repository.check_email_exists(db, normalized_email):
            raise EmailAlreadyExistsException()

        # 3. Check mobile number uniqueness
        if await user_repository.check_mobile_exists(db, request.mobile_number):
            raise MobileAlreadyExistsException()

        # 4. Determine minor safeguarding status
        if request.age < 18:
            parental_consent_status = "PENDING_VERIFICATION"
        else:
            parental_consent_status = "NOT_REQUIRED"

        # 5. Create base User
        pwd_hash = get_password_hash(request.password)
        user = User(
            email=normalized_email,
            password_hash=pwd_hash,
            role="VOLUNTEER",
            status="PENDING_VERIFICATION",
            is_active=True,
        )
        await user_repository.create_user(db, user)

        # 6. Create base VolunteerProfile
        profile = VolunteerProfile(
            user_id=user.id,
            first_name=request.first_name.strip(),
            last_name=request.last_name.strip(),
            mobile_number=request.mobile_number,
            age=request.age,
            gender=request.gender,
            category=request.category,
            parent_guardian_name=request.parent_guardian_name.strip()
            if request.parent_guardian_name
            else None,
            parent_guardian_relationship=request.parent_guardian_relationship.strip()
            if request.parent_guardian_relationship
            else None,
            parent_guardian_contact=request.parent_guardian_contact.strip()
            if request.parent_guardian_contact
            else None,
            parental_consent_claimed=request.parental_consent_claimed,
            parental_consent_evidence_submitted=request.parental_consent_evidence_submitted,
            parental_consent_verified=False,
            parental_consent_submitted=request.parental_consent_submitted,
            parental_consent_document_media_id=request.parental_consent_document_media_id,
            parental_consent_status=parental_consent_status,
        )
        await user_repository.create_volunteer_profile(db, profile)

        # 7. Create category-specific profile
        if request.category == "STUDENT" and request.student_details:
            student = StudentProfile(
                volunteer_profile_id=profile.id,
                college_name=request.student_details.college_name.strip(),
                degree=request.student_details.degree.strip(),
                department=request.student_details.department.strip(),
                batch_year=request.student_details.batch_year,
                current_year=request.student_details.current_year,
                maatram_reg_number=request.student_details.maatram_reg_number.strip(),
            )
            await user_repository.create_student_profile(db, student)
        elif request.category == "ALUMNI" and request.alumni_details:
            alumni = AlumniProfile(
                volunteer_profile_id=profile.id,
                organisation=request.alumni_details.organisation.strip(),
                job_role=request.alumni_details.job_role.strip(),
                years_of_experience=request.alumni_details.years_of_experience,
                location=request.alumni_details.location.strip(),
                skills=request.alumni_details.skills,
                college_name=request.alumni_details.college_name.strip(),
                degree=request.alumni_details.degree.strip(),
                department=request.alumni_details.department.strip(),
                batch_year=request.alumni_details.batch_year,
                graduation_year=request.alumni_details.graduation_year,
            )
            await user_repository.create_alumni_profile(db, alumni)
        elif request.category == "CORPORATE" and request.corporate_details:
            corporate = CorporateProfile(
                volunteer_profile_id=profile.id,
                organisation=request.corporate_details.organisation.strip(),
                designation=request.corporate_details.designation.strip(),
                years_of_experience=request.corporate_details.years_of_experience,
                location=request.corporate_details.location.strip(),
                skills=request.corporate_details.skills,
            )
            await user_repository.create_corporate_profile(db, corporate)

        # 8. Create affirmative ConsentRecord
        consent_data = request.consent
        consent = ConsentRecord(
            volunteer_profile_id=profile.id,
            leaderboard_visible=consent_data.leaderboard_visible if consent_data else False,
            name_visible=consent_data.name_visible if consent_data else False,
            thank_you_emails=consent_data.thank_you_emails if consent_data else False,
            linkedin_content=consent_data.linkedin_content if consent_data else False,
            contact_available=consent_data.contact_available if consent_data else False,
            media_usage=consent_data.media_usage if consent_data else False,
        )
        await user_repository.create_consent_record(db, consent)

        # 8b. Create initial VolunteerApplication record (Phase 5)
        application = VolunteerApplication(
            volunteer_profile_id=profile.id,
            status="PENDING",
            current_stage=6,
        )
        db.add(application)
        await db.flush()

        # 9. Create EmailVerification token & outbox notification
        raw_token = generate_refresh_token()
        verif_hash = hash_token(raw_token)
        verif = EmailVerification(
            user_id=user.id,
            token_hash=verif_hash,
            expires_at=datetime.now(UTC) + timedelta(hours=24),
            is_used=False,
            attempt_count=0,
            max_attempts=5,
        )
        await token_repository.create_email_verification(db, verif)

        try:
            outbox_job = CommunicationJob(
                channel="EMAIL",
                recipient=user.email,
                template_name="VERIFY_EMAIL",
                payload={"token": raw_token, "email": user.email, "first_name": profile.first_name},
                idempotency_key=str(uuid.uuid4()),
            )
            await token_repository.create_communication_job(db, outbox_job)
        except Exception:
            logger.warning("Failed to enqueue email verification outbox job", exc_info=True)

        # 10. Audit log
        await token_repository.create_audit_log(
            db,
            action="USER_REGISTERED",
            resource_type="user",
            resource_id=str(user.id),
            actor_user_id=user.id,
            ip_address=client_ip,
            user_agent=user_agent,
            new_state={"email": user.email, "role": user.role, "category": profile.category},
        )

        return RegisterResponse(
            user_id=user.id,
            email=user.email,
            status=user.status,
            parental_consent_claimed=request.parental_consent_claimed,
            parental_consent_status=parental_consent_status,
            message="Registration submitted. Please verify your email.",
        )

    async def login(
        self,
        db: AsyncSession,
        request: LoginRequest,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[TokenResponse, str, str]:
        """Authenticate user credentials and generate tokens & server-side session."""
        now = datetime.now(UTC)
        normalized_email = request.email.strip().lower()

        # 1. Lookup user
        user = await user_repository.get_by_email(db, normalized_email)
        if not user:
            raise InvalidCredentialsException()

        # 2. Check lockout status
        if user.locked_until and ensure_utc(user.locked_until) > now:
            raise AccountLockedException()
        elif user.locked_until and ensure_utc(user.locked_until) <= now:
            user.locked_until = None
            user.failed_login_attempts = 0

        # 3. Verify password
        if not verify_password(request.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
            await token_repository.create_audit_log(
                db,
                action="LOGIN_FAILED",
                resource_type="user",
                resource_id=str(user.id),
                actor_user_id=user.id,
                ip_address=client_ip,
                user_agent=user_agent,
                reason="Invalid credentials",
            )
            await db.commit()
            raise InvalidCredentialsException()

        # 4. Check account suspension / activation / lifecycle state
        if user.status == "PENDING_VERIFICATION":
            raise ForbiddenException(
                "Email not verified. Please verify your email before logging in."
            )
        if user.status == "PENDING_APPROVAL":
            raise ForbiddenException("Account is pending administrative approval.")
        if user.status == "REJECTED":
            raise ForbiddenException("Volunteer application has been rejected.")
        if user.status == "SUSPENDED":
            raise AccountSuspendedException()
        if user.status == "INACTIVE" or not user.is_active:
            raise ForbiddenException("Account has been deactivated.")
        if user.status not in ("APPROVED",):
            raise ForbiddenException(f"Account with status '{user.status}' cannot log in.")

        # 5. Reset login counters
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now

        # 6. Generate refresh token & session
        raw_refresh_token = generate_refresh_token()
        rt_hash = hash_token(raw_refresh_token)
        session_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=rt_hash,
            device_info=request.device_info,
            ip_address=client_ip,
            client_type=request.client_type,
            is_revoked=False,
            expires_at=session_expires_at,
            created_at=now,
            last_used_at=now,
        )
        await user_repository.create_session(db, session)

        # 7. Generate access & CSRF tokens
        access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            status=user.status,
            session_id=session.id,
        )
        csrf_token = generate_csrf_token(session.id)

        # 8. Audit log
        await token_repository.create_audit_log(
            db,
            action="LOGIN_SUCCESS",
            resource_type="user_session",
            resource_id=str(session.id),
            actor_user_id=user.id,
            ip_address=client_ip,
            user_agent=user_agent,
            new_state={"client_type": request.client_type, "device_info": request.device_info},
        )

        response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=raw_refresh_token,
            csrf_token=csrf_token,
            user=UserSummaryResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                status=user.status,
            ),
        )
        return response, raw_refresh_token, csrf_token

    async def refresh_token(
        self,
        db: AsyncSession,
        presented_token: str | None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[TokenResponse, str, str]:
        """Rotate refresh token, issue new token pair, and detect token theft/reuse."""
        if not presented_token or not presented_token.strip():
            raise InvalidTokenException("Refresh token is required.")

        now = datetime.now(UTC)
        token_hash = hash_token(presented_token.strip())

        # In-process concurrency guard
        async with _refresh_lock_guard:
            if token_hash not in _refresh_locks:
                _refresh_locks[token_hash] = asyncio.Lock()
            token_lock = _refresh_locks[token_hash]

        if token_lock.locked():
            raise ConflictException(
                "Concurrent token refresh in progress. Please retry.",
                code="CONCURRENT_REFRESH_CONFLICT",
            )

        try:
            async with token_lock:
                # 1. Look up session by active refresh token hash with row lock
                try:
                    session = await user_repository.get_session_by_token_hash_for_update(
                        db, token_hash
                    )
                except Exception as exc:
                    if "lock" in str(exc).lower():
                        raise ConflictException(
                            "Concurrent token refresh in progress. Please retry.",
                            code="CONCURRENT_REFRESH_CONFLICT",
                        ) from exc
                    raise

                if session:
                    # Check if session is revoked
                    if session.is_revoked:
                        await token_repository.create_audit_log(
                            db,
                            action="REVOKED_SESSION_ACCESSED",
                            resource_type="user_session",
                            resource_id=str(session.id),
                            actor_user_id=session.user_id,
                            ip_address=client_ip,
                            user_agent=user_agent,
                            reason="Attempt to use refresh token belonging to revoked session",
                        )
                        raise SessionRevokedException()

                    # Check if session expired
                    if ensure_utc(session.expires_at) < now:
                        raise TokenExpiredException("Refresh token has expired.")

                    # Check user account status
                    user = await user_repository.get_by_id(db, session.user_id)
                    if not user or not user.is_active:
                        raise UnauthorizedException("User account is inactive.")
                    if user.status == "SUSPENDED":
                        raise AccountSuspendedException()

                    # 2. Token Rotation
                    new_raw_refresh_token = generate_refresh_token()
                    new_hash = hash_token(new_raw_refresh_token)

                    # Record rotation in audit logs to detect future reuse of old token
                    await token_repository.create_audit_log(
                        db,
                        action="TOKEN_ROTATED",
                        resource_type="user_session",
                        resource_id=str(session.id),
                        actor_user_id=user.id,
                        ip_address=client_ip,
                        user_agent=user_agent,
                        old_state={"token_hash": token_hash},
                        new_state={"token_hash": new_hash},
                    )

                    # Update session
                    session.refresh_token_hash = new_hash
                    session.last_used_at = now
                    session.expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

                    # Generate new access and CSRF tokens
                    access_token = create_access_token(
                        user_id=user.id,
                        role=user.role,
                        status=user.status,
                        session_id=session.id,
                    )
                    csrf_token = generate_csrf_token(session.id)

                    response = TokenResponse(
                        access_token=access_token,
                        token_type="bearer",
                        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        refresh_token=new_raw_refresh_token,
                        csrf_token=csrf_token,
                        user=UserSummaryResponse(
                            id=user.id,
                            email=user.email,
                            role=user.role,
                            status=user.status,
                        ),
                    )
                    return response, new_raw_refresh_token, csrf_token

                # 3. If session not found by token_hash, check for TOKEN REUSE (theft/hijacking)
                compromised_session_id = await token_repository.find_session_by_rotated_token_hash(
                    db, token_hash
                )
                if compromised_session_id:
                    # Revoke entire session lineage immediately
                    await user_repository.revoke_session(db, compromised_session_id)
                    await token_repository.create_audit_log(
                        db,
                        action="TOKEN_REUSE_DETECTED",
                        resource_type="user_session",
                        resource_id=str(compromised_session_id),
                        ip_address=client_ip,
                        user_agent=user_agent,
                        reason="Consumed refresh token presented again; potential token hijacking. Session invalidated.",
                    )
                    await db.commit()
                    raise TokenReuseDetectedException()

                raise InvalidTokenException("Invalid refresh token.")
        finally:
            async with _refresh_lock_guard:
                _refresh_locks.pop(token_hash, None)

    async def logout(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> MessageResponse:
        """Revoke current active session."""
        await user_repository.revoke_session(db, session_id)
        await token_repository.create_audit_log(
            db,
            action="LOGOUT",
            resource_type="user_session",
            resource_id=str(session_id),
            actor_user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
        )
        return MessageResponse(message="Logged out successfully")

    async def logout_all(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> MessageResponse:
        """Revoke all sessions for a user across all devices."""
        await user_repository.revoke_all_sessions(db, user_id)
        await token_repository.create_audit_log(
            db,
            action="LOGOUT_ALL_SESSIONS",
            resource_type="user",
            resource_id=str(user_id),
            actor_user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
        )
        return MessageResponse(message="All sessions revoked successfully")

    async def verify_email(
        self,
        db: AsyncSession,
        token: str,
        email: str | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> VerifyEmailResponse:
        """Confirm volunteer email address using one-time verification token with attempt tracking."""
        now = datetime.now(UTC)
        token_hash = hash_token(token.strip())

        verif: EmailVerification | None = None
        user: User | None = None

        if email:
            normalized_email = email.strip().lower()
            user = await user_repository.get_by_email(db, normalized_email)
            if user:
                verif = await token_repository.get_latest_email_verification_for_user(db, user.id)

        if not verif:
            verif = await token_repository.get_email_verification_by_hash(db, token_hash)
            if verif and not user:
                user = await user_repository.get_by_id(db, verif.user_id)

        if not verif:
            raise DomainException(
                message="Invalid or already used email verification token.",
                code="INVALID_TOKEN",
            )

        # Enforce max 5 attempts
        if verif.attempt_count >= verif.max_attempts:
            verif.is_used = True
            await db.commit()
            raise DomainException(
                message="Maximum verification attempts exceeded.",
                code="MAX_ATTEMPTS_EXCEEDED",
                status_code=429,
            )

        # Check token match if resolved via user/email
        if verif.token_hash != token_hash:
            verif.attempt_count += 1
            await db.commit()
            if verif.attempt_count >= verif.max_attempts:
                verif.is_used = True
                await db.commit()
                raise DomainException(
                    message="Maximum verification attempts exceeded.",
                    code="MAX_ATTEMPTS_EXCEEDED",
                    status_code=429,
                )
            raise DomainException(
                message="Invalid or already used email verification token.",
                code="INVALID_TOKEN",
            )

        if verif.is_used:
            raise DomainException(
                message="Invalid or already used email verification token.",
                code="INVALID_TOKEN",
            )

        if ensure_utc(verif.expires_at) < now:
            raise DomainException(
                message="Email verification token has expired.",
                code="TOKEN_EXPIRED",
                status_code=410,
            )

        verif.is_used = True
        verif.attempt_count += 1

        if user:
            enforce_status_transition(user.status, "PENDING_APPROVAL")
            user.status = "PENDING_APPROVAL"

        await token_repository.create_audit_log(
            db,
            action="EMAIL_VERIFIED",
            resource_type="user",
            resource_id=str(verif.user_id),
            actor_user_id=verif.user_id,
            ip_address=client_ip,
            user_agent=user_agent,
            new_state={"status": "PENDING_APPROVAL"},
        )
        return VerifyEmailResponse(
            status="PENDING_APPROVAL", message="Email verified successfully."
        )

    async def request_password_reset(
        self,
        db: AsyncSession,
        email: str,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> MessageResponse:
        """Generate 6-digit numeric OTP for password reset with anti-enumeration protection."""
        normalized_email = email.strip().lower()
        generic_msg = "If the account exists, a reset code has been sent."

        user = await user_repository.get_by_email(db, normalized_email)
        if not user:
            return MessageResponse(message=generic_msg)

        now = datetime.now(UTC)
        recent_count = await token_repository.count_recent_password_reset_requests(
            db, user.id, since=now - timedelta(hours=24)
        )
        if recent_count >= 3:
            raise RateLimitExceededException(
                "Maximum password reset requests exceeded for this email in 24 hours."
            )

        raw_otp = generate_otp()
        hashed_otp = hash_otp(raw_otp)
        prt = PasswordResetToken(
            user_id=user.id,
            otp_hash=hashed_otp,
            attempt_count=0,
            max_attempts=settings.MAX_OTP_ATTEMPTS,
            expires_at=now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
            is_used=False,
        )
        await token_repository.create_password_reset_token(db, prt)

        try:
            outbox_job = CommunicationJob(
                channel="EMAIL",
                recipient=user.email,
                template_name="PASSWORD_RESET_OTP",
                payload={"email": user.email, "otp": raw_otp},
                idempotency_key=str(uuid.uuid4()),
            )
            await token_repository.create_communication_job(db, outbox_job)
        except Exception:
            logger.warning("Failed to enqueue password reset outbox job", exc_info=True)

        await token_repository.create_audit_log(
            db,
            action="PASSWORD_RESET_REQUESTED",
            resource_type="user",
            resource_id=str(user.id),
            actor_user_id=user.id,
            ip_address=client_ip,
            user_agent=user_agent,
        )
        return MessageResponse(message=generic_msg)

    async def confirm_password_reset(
        self,
        db: AsyncSession,
        email: str,
        otp: str,
        new_password: str,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> MessageResponse:
        """Validate numeric OTP, update password, and revoke all active sessions."""
        validate_password_strength(new_password)
        normalized_email = email.strip().lower()

        user = await user_repository.get_by_email(db, normalized_email)
        if not user:
            raise DomainException("Invalid or expired reset code.", code="INVALID_OTP")

        prt = await token_repository.get_latest_password_reset_token(db, user.id)
        if not prt:
            raise DomainException("Invalid or expired reset code.", code="INVALID_OTP")

        if prt.attempt_count >= prt.max_attempts:
            prt.is_used = True
            raise DomainException(
                "Maximum verification attempts exceeded.", code="MAX_ATTEMPTS_EXCEEDED"
            )

        if not verify_otp(otp, prt.otp_hash):
            prt.attempt_count += 1
            if prt.attempt_count >= prt.max_attempts:
                prt.is_used = True
            raise DomainException("Invalid or expired reset code.", code="INVALID_OTP")

        # OTP verified successfully
        prt.is_used = True
        user.password_hash = get_password_hash(new_password)

        # Invalidate all existing sessions
        await user_repository.revoke_all_sessions(db, user.id)

        await token_repository.create_audit_log(
            db,
            action="PASSWORD_RESET_CONFIRMED",
            resource_type="user",
            resource_id=str(user.id),
            actor_user_id=user.id,
            ip_address=client_ip,
            user_agent=user_agent,
            reason="Password successfully reset via verified OTP",
        )
        return MessageResponse(
            message="Password reset successfully. Please log in with your new credentials."
        )


auth_service = AuthService()
