"""Volunteer Application & Review lifecycle service."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import (
    ConflictException,
    DomainException,
    ForbiddenException,
    NotFoundException,
)
from src.core.logging import logger
from src.models.applications import ApplicationReview, VolunteerApplication
from src.models.communications import CommunicationJob
from src.models.users import User
from src.models.volunteers import VolunteerProfile
from src.repositories.application_repo import application_repository
from src.repositories.token_repo import token_repository
from src.schemas.application import (
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationReviewResponse,
)
from src.schemas.volunteer import VolunteerProfileResponse
from src.services.auth_service import enforce_status_transition


class ApplicationService:
    """Core domain service orchestrating volunteer application reviews, minor safeguards, and approvals."""

    async def get_my_application(self, db: AsyncSession, user_id: uuid.UUID) -> ApplicationResponse:
        """Fetch current volunteer's submitted onboarding application."""
        app = await application_repository.get_by_user_id(db, user_id)
        if not app:
            raise NotFoundException("Volunteer application not found.")
        return ApplicationResponse.model_validate(app)

    async def get_application_by_id(
        self, db: AsyncSession, application_id: uuid.UUID, current_user: User
    ) -> ApplicationDetailResponse:
        """Fetch detailed application record with BOLA/RBAC authorization."""
        app = await application_repository.get_by_id(db, application_id)
        if not app:
            raise NotFoundException("Volunteer application not found.")

        # BOLA Authorization: Admin or owning volunteer
        if (
            current_user.role not in ("ADMIN", "SUPER_ADMIN")
            and app.volunteer_profile.user_id != current_user.id
        ):
            raise ForbiddenException("You do not have permission to view this application.")

        return self._build_detail_response(app)

    async def list_applications(
        self,
        db: AsyncSession,
        current_user: User,
        status: str | None = None,
        category: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ApplicationListResponse:
        """Query applications for administrative review with multi-field search and filters."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Application review requires administrative privileges.")

        items, total = await application_repository.list_applications(
            db=db,
            status=status,
            category=category,
            date_from=date_from,
            date_to=date_to,
            search=search,
            page=page,
            page_size=page_size,
        )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        detail_items = [self._build_detail_response(app) for app in items]

        return ApplicationListResponse(
            items=detail_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def verify_parental_consent(
        self,
        db: AsyncSession,
        application_id: uuid.UUID,
        reviewer_user: User,
        status: str,
        notes: str | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> VolunteerProfile:
        """Administrative review and verification of minor applicant's parental consent."""
        if reviewer_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Consent verification requires administrative privileges.")

        app = await application_repository.get_by_id(db, application_id)
        if not app:
            raise NotFoundException("Volunteer application not found.")

        profile = app.volunteer_profile
        old_status = profile.parental_consent_status

        # Update profile minor safeguarding fields
        profile.parental_consent_verified = status == "VERIFIED"
        profile.parental_consent_status = status
        profile.parental_consent_verified_by_user_id = reviewer_user.id
        profile.parental_consent_verified_at = datetime.now(UTC)
        profile.parental_consent_notes = notes.strip() if notes else None

        # Immutable audit trail
        action = (
            "PARENTAL_CONSENT_VERIFIED" if status == "VERIFIED" else "PARENTAL_CONSENT_REJECTED"
        )
        await token_repository.create_audit_log(
            db,
            action=action,
            resource_type="volunteer_profile",
            resource_id=str(profile.id),
            actor_user_id=reviewer_user.id,
            ip_address=client_ip,
            user_agent=user_agent,
            old_state={"parental_consent_status": old_status},
            new_state={
                "parental_consent_status": status,
                "parental_consent_verified": profile.parental_consent_verified,
                "notes": profile.parental_consent_notes,
            },
        )

        await db.commit()
        return profile

    async def approve_application(
        self,
        db: AsyncSession,
        application_id: uuid.UUID,
        reviewer_user: User,
        notes: str | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> ApplicationResponse:
        """Administrative approval of volunteer application and transition of user account status."""
        if reviewer_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Application approval requires administrative privileges.")

        app = await application_repository.get_by_id(db, application_id)
        if not app:
            raise NotFoundException("Volunteer application not found.")

        if app.status == "APPROVED":
            raise ConflictException("Application has already been approved.")

        profile = app.volunteer_profile
        user = profile.user

        # Minor Safeguarding Invariant: Minor must have verified parental consent
        if profile.age < 18 and not profile.parental_consent_verified:
            raise DomainException(
                "Minor applicant cannot be approved without verified parental consent.",
                code="MINOR_CONSENT_UNVERIFIED",
            )

        # Enforce account lifecycle status transition (e.g. PENDING_APPROVAL -> APPROVED)
        enforce_status_transition(user.status, "APPROVED")

        # Mutate application & user status
        app.status = "APPROVED"
        user.status = "APPROVED"

        # Record review decision
        review = ApplicationReview(
            application_id=app.id,
            reviewer_id=reviewer_user.id,
            action="APPROVED",
            reason=notes.strip() if notes else None,
        )
        await application_repository.create_review(db, review)

        # Audit log
        await token_repository.create_audit_log(
            db,
            action="APPLICATION_APPROVED",
            resource_type="volunteer_application",
            resource_id=str(app.id),
            actor_user_id=reviewer_user.id,
            ip_address=client_ip,
            user_agent=user_agent,
            old_state={"application_status": "PENDING", "user_status": "PENDING_APPROVAL"},
            new_state={"application_status": "APPROVED", "user_status": "APPROVED"},
        )

        # Enqueue welcome email notification
        try:
            outbox_job = CommunicationJob(
                channel="EMAIL",
                recipient=user.email,
                template_name="APPLICATION_APPROVED",
                payload={"first_name": profile.first_name, "email": user.email},
                idempotency_key=str(uuid.uuid4()),
            )
            await token_repository.create_communication_job(db, outbox_job)
        except Exception:
            logger.warning("Failed to enqueue welcome email outbox job", exc_info=True)

        await db.commit()
        return ApplicationResponse.model_validate(app)

    async def reject_application(
        self,
        db: AsyncSession,
        application_id: uuid.UUID,
        reviewer_user: User,
        reason: str,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> ApplicationResponse:
        """Administrative rejection of volunteer application with mandatory reasoning."""
        if reviewer_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Application rejection requires administrative privileges.")

        if not reason or not reason.strip():
            raise DomainException(
                "A non-empty rejection reason is required.",
                code="REJECTION_REASON_REQUIRED",
            )

        app = await application_repository.get_by_id(db, application_id)
        if not app:
            raise NotFoundException("Volunteer application not found.")

        if app.status == "REJECTED":
            raise ConflictException("Application has already been rejected.")

        profile = app.volunteer_profile
        user = profile.user

        # Enforce account lifecycle status transition (e.g. PENDING_APPROVAL -> REJECTED)
        enforce_status_transition(user.status, "REJECTED")

        # Mutate application & user status
        app.status = "REJECTED"
        user.status = "REJECTED"

        # Record review decision
        review = ApplicationReview(
            application_id=app.id,
            reviewer_id=reviewer_user.id,
            action="REJECTED",
            reason=reason.strip(),
        )
        await application_repository.create_review(db, review)

        # Audit log
        await token_repository.create_audit_log(
            db,
            action="APPLICATION_REJECTED",
            resource_type="volunteer_application",
            resource_id=str(app.id),
            actor_user_id=reviewer_user.id,
            ip_address=client_ip,
            user_agent=user_agent,
            old_state={"application_status": "PENDING", "user_status": "PENDING_APPROVAL"},
            new_state={
                "application_status": "REJECTED",
                "user_status": "REJECTED",
                "reason": reason.strip(),
            },
        )

        # Enqueue rejection email notification
        try:
            outbox_job = CommunicationJob(
                channel="EMAIL",
                recipient=user.email,
                template_name="APPLICATION_REJECTED",
                payload={
                    "first_name": profile.first_name,
                    "email": user.email,
                    "reason": reason.strip(),
                },
                idempotency_key=str(uuid.uuid4()),
            )
            await token_repository.create_communication_job(db, outbox_job)
        except Exception:
            logger.warning("Failed to enqueue rejection email outbox job", exc_info=True)

        await db.commit()
        return ApplicationResponse.model_validate(app)

    def _build_detail_response(self, app: VolunteerApplication) -> ApplicationDetailResponse:
        """Helper to construct ApplicationDetailResponse with nested profile and reviews."""
        profile = app.volunteer_profile
        user = profile.user

        reviews = [
            ApplicationReviewResponse(
                id=r.id,
                application_id=r.application_id,
                reviewer_id=r.reviewer_id,
                action=r.action,  # type: ignore[arg-type]
                reason=r.reason,
                created_at=r.created_at,
            )
            for r in app.reviews
        ]

        return ApplicationDetailResponse(
            id=app.id,
            volunteer_profile_id=app.volunteer_profile_id,
            status=app.status,  # type: ignore[arg-type]
            submitted_at=app.submitted_at,
            current_stage=app.current_stage,
            notes=app.notes,
            created_at=app.created_at,
            updated_at=app.updated_at,
            volunteer_profile=VolunteerProfileResponse.model_validate(profile),
            user_email=user.email,
            user_status=user.status,
            reviews=reviews,
        )


application_service = ApplicationService()
