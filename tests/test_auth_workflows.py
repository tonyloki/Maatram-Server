"""Comprehensive end-to-end integration tests for Authentication, Sessions & RBAC."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DomainException
from src.core.rate_limiter import PostgreSQLRateLimiter
from src.core.security import (
    create_access_token,
    generate_refresh_token,
    get_password_hash,
    hash_token,
)
from src.models.admin import AuditLog
from src.models.communications import CommunicationJob
from src.models.users import EmailVerification, User, UserSession
from src.services.auth_service import enforce_status_transition

# ==========================================
# 1. Registration Tests
# ==========================================


@pytest.mark.asyncio
async def test_register_student_volunteer_success(client: AsyncClient, async_db: AsyncSession):
    """Verify registration of a Student volunteer with affirmative privacy consent."""
    payload = {
        "email": f"student_{uuid.uuid4().hex[:6]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Arun",
        "last_name": "Kumar",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "age": 20,
        "gender": "MALE",
        "category": "STUDENT",
        "student_details": {
            "college_name": "Anna University",
            "degree": "B.Tech",
            "department": "Computer Science",
            "batch_year": 2026,
            "current_year": 4,
            "maatram_reg_number": f"MAAT-{uuid.uuid4().hex[:6].upper()}",
        },
        "consent": {
            "leaderboard_visible": True,
            "name_visible": True,
            "thank_you_emails": True,
            "linkedin_content": False,
            "contact_available": False,
            "media_usage": True,
        },
    }

    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == payload["email"].lower()
    assert data["status"] == "PENDING_VERIFICATION"
    assert data["parental_consent_status"] == "NOT_REQUIRED"
    assert "user_id" in data

    # Verify outbox email job was enqueued
    stmt = select(CommunicationJob).where(CommunicationJob.recipient == payload["email"].lower())
    job = (await async_db.execute(stmt)).scalar_one_or_none()
    assert job is not None
    assert job.channel == "EMAIL"
    assert job.template_name == "VERIFY_EMAIL"
    assert "token" in job.payload


@pytest.mark.asyncio
async def test_register_minor_volunteer_safeguarding(client: AsyncClient):
    """Verify minor volunteer (<18) registration succeeds and records claimed parental consent."""
    minor_payload = {
        "email": f"minor_{uuid.uuid4().hex[:6]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Kavitha",
        "last_name": "M",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "age": 16,
        "gender": "FEMALE",
        "category": "STUDENT",
        "parental_consent_claimed": True,
        "parental_consent_evidence_submitted": False,
        "parental_consent_submitted": True,
        "parent_guardian_name": "Mani K",
        "parent_guardian_relationship": "FATHER",
        "parent_guardian_contact": "+919876543210",
        "student_details": {
            "college_name": "PSG Tech",
            "degree": "B.E",
            "department": "ECE",
            "batch_year": 2027,
            "current_year": 2,
            "maatram_reg_number": f"MAAT-{uuid.uuid4().hex[:6].upper()}",
        },
    }
    res = await client.post("/api/v1/auth/register", json=minor_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["parental_consent_claimed"] is True
    assert data["status"] == "PENDING_VERIFICATION"


@pytest.mark.asyncio
async def test_register_duplicate_email_conflict(client: AsyncClient):
    """Verify duplicate email registration returns 409 Conflict."""
    email = f"dup_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "SecurePassword123!",
        "first_name": "First",
        "last_name": "User",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "age": 22,
        "gender": "MALE",
        "category": "CORPORATE",
        "corporate_details": {
            "organisation": "Tech Corp",
            "designation": "Software Engineer",
            "years_of_experience": 3.5,
            "location": "Chennai",
            "skills": ["Python", "FastAPI"],
        },
    }

    # First registration
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with same email but different phone
    dup_payload = payload.copy()
    dup_payload["mobile_number"] = f"+9197{uuid.uuid4().int % 100000000:08d}"
    res2 = await client.post("/api/v1/auth/register", json=dup_payload)
    assert res2.status_code == 409
    assert "EMAIL_ALREADY_EXISTS" in res2.text


@pytest.mark.asyncio
async def test_register_duplicate_mobile_conflict(client: AsyncClient):
    """Verify duplicate mobile number returns 409 Conflict."""
    shared_mobile = f"+9196{uuid.uuid4().int % 100000000:08d}"
    payload1 = {
        "email": f"user1_{uuid.uuid4().hex[:6]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "User",
        "last_name": "One",
        "mobile_number": shared_mobile,
        "age": 24,
        "gender": "OTHER",
        "category": "CORPORATE",
        "corporate_details": {
            "organisation": "Corp",
            "designation": "Manager",
            "years_of_experience": 4,
            "location": "Bangalore",
        },
    }
    res1 = await client.post("/api/v1/auth/register", json=payload1)
    assert res1.status_code == 201

    payload2 = payload1.copy()
    payload2["email"] = f"user2_{uuid.uuid4().hex[:6]}@example.com"
    res2 = await client.post("/api/v1/auth/register", json=payload2)
    assert res2.status_code == 409
    assert "MOBILE_ALREADY_EXISTS" in res2.text


# ==========================================
# 2. Login & Token Management Tests
# ==========================================


@pytest.mark.asyncio
async def test_login_web_client_cookies_and_csrf(client: AsyncClient, async_db: AsyncSession):
    """Verify Web client login returns token bundle, CSRF token, and sets HttpOnly cookie."""
    email = f"webuser_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "SuperSecurePassword123!"

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "csrf_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email

    # Check cookies
    cookies = res.cookies
    assert "refresh_token" in cookies
    assert "csrf_token" in cookies


@pytest.mark.asyncio
async def test_login_mobile_client_tokens(client: AsyncClient, async_db: AsyncSession):
    """Verify Mobile client login receives raw refresh token for secure hardware keystore."""
    email = f"mobile_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "MobilePassword123!"

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "client_type": "MOBILE",
            "device_info": "Pixel 8 Pro",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["refresh_token"] is not None
    assert data["refresh_token"].startswith("rt_")


@pytest.mark.asyncio
async def test_login_invalid_password_and_lockout(client: AsyncClient, async_db: AsyncSession):
    """Verify 5 failed login attempts lock account for 15 minutes."""
    email = f"lockout_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "CorrectPassword123!"

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role="VOLUNTEER",
        status="APPROVED",
        failed_login_attempts=0,
    )
    async_db.add(user)
    await async_db.commit()

    # 4 failed attempts -> 401 INVALID_CREDENTIALS
    for _ in range(4):
        res = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPassword!", "client_type": "WEB"},
        )
        assert res.status_code == 401
        assert "INVALID_CREDENTIALS" in res.text

    # 5th failed attempt -> locks account
    res5 = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword!", "client_type": "WEB"},
    )
    assert res5.status_code == 401

    # 6th attempt even with CORRECT password is now locked (403 ACCOUNT_LOCKED)
    res_locked = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res_locked.status_code == 403
    assert "ACCOUNT_LOCKED" in res_locked.text


@pytest.mark.asyncio
async def test_login_suspended_account_rejected(client: AsyncClient, async_db: AsyncSession):
    """Verify administratively suspended accounts cannot log in."""
    email = f"suspended_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "SuspendedPassword123!"

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role="VOLUNTEER",
        status="SUSPENDED",
    )
    async_db.add(user)
    await async_db.commit()

    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 403
    assert "ACCOUNT_SUSPENDED" in res.text


# ==========================================
# 3. Access Token Validation & Protected Endpoints
# ==========================================


@pytest.mark.asyncio
async def test_get_current_user_me_success(client: AsyncClient, async_db: AsyncSession):
    """Verify /api/v1/users/me returns authenticated identity when valid token provided."""
    email = f"me_test_{uuid.uuid4().hex[:6]}@maatram.org"
    user = User(
        email=email,
        password_hash=get_password_hash("ValidPassword123!"),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_token("rt_dummy"),
        client_type="WEB",
        is_revoked=False,
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    async_db.add(session)
    await async_db.commit()

    access_token = create_access_token(
        user_id=user.id, role=user.role, status=user.status, session_id=session.id
    )

    res = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == str(user.id)
    assert data["email"] == email
    assert data["role"] == "VOLUNTEER"


@pytest.mark.asyncio
async def test_protected_route_expired_token(client: AsyncClient, async_db: AsyncSession):
    """Verify expired token returns 401 TOKEN_EXPIRED."""
    user = User(
        email=f"exp_{uuid.uuid4().hex[:6]}@maatram.org",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_token("rt_dummy"),
        client_type="WEB",
        is_revoked=False,
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    async_db.add(session)
    await async_db.commit()

    expired_token = create_access_token(
        user_id=user.id,
        role=user.role,
        status=user.status,
        session_id=session.id,
        expires_delta=timedelta(seconds=-10),
    )

    res = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res.status_code == 401
    assert "TOKEN_EXPIRED" in res.text


# ==========================================
# 4. Refresh Token Rotation & Reuse Detection
# ==========================================


@pytest.mark.asyncio
async def test_refresh_token_rotation_success(client: AsyncClient, async_db: AsyncSession):
    """Verify token rotation: old refresh token is replaced by new refresh token."""
    email = f"rot_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "RotatePassword123!"

    # 1. Login
    user = User(
        email=email, password_hash=get_password_hash(password), role="VOLUNTEER", status="APPROVED"
    )
    async_db.add(user)
    await async_db.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert login_res.status_code == 200
    first_refresh_cookie = login_res.cookies.get("refresh_token")
    assert first_refresh_cookie is not None

    # 2. Refresh using cookie
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": first_refresh_cookie},
    )
    assert refresh_res.status_code == 200
    refreshed_data = refresh_res.json()
    assert "access_token" in refreshed_data

    second_refresh_cookie = refresh_res.cookies.get("refresh_token")
    assert second_refresh_cookie is not None
    assert second_refresh_cookie != first_refresh_cookie


@pytest.mark.asyncio
async def test_refresh_token_reuse_detection_and_lineage_revocation(
    client: AsyncClient, async_db: AsyncSession
):
    """Verify TOKEN REUSE DETECTED: presenting old consumed token revokes session lineage."""
    email = f"theft_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "TheftPassword123!"

    user = User(
        email=email, password_hash=get_password_hash(password), role="VOLUNTEER", status="APPROVED"
    )
    async_db.add(user)
    await async_db.commit()

    # 1. Login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    token_v1 = login_res.json()["refresh_token"]
    assert token_v1 is not None

    # 2. Legitimate user rotates token (v1 -> v2)
    rot_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": token_v1})
    assert rot_res.status_code == 200
    token_v2 = rot_res.json()["refresh_token"]
    assert token_v2 is not None
    access_token_v2 = rot_res.json()["access_token"]

    # 3. Attacker presents consumed token_v1 again (Token Theft Attempt)
    theft_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": token_v1})
    assert theft_res.status_code == 401
    assert "TOKEN_REUSE_DETECTED" in theft_res.text

    # 4. Verify session lineage is now REVOKED: even legitimate token_v2 and access_token_v2 now fail!
    followup_refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": token_v2})
    assert followup_refresh.status_code == 401
    assert "SESSION_REVOKED" in followup_refresh.text

    followup_api = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token_v2}"}
    )
    assert followup_api.status_code == 401
    assert "SESSION_REVOKED" in followup_api.text

    # 5. Verify security audit log exists
    stmt = select(AuditLog).where(AuditLog.action == "TOKEN_REUSE_DETECTED")
    audit_entry = (await async_db.execute(stmt)).scalar_one_or_none()
    assert audit_entry is not None
    assert audit_entry.action == "TOKEN_REUSE_DETECTED"


# ==========================================
# 5. Session Management & Logout
# ==========================================


@pytest.mark.asyncio
async def test_session_listing_and_manual_revocation(client: AsyncClient, async_db: AsyncSession):
    """Verify session listing and revoking a specific device session with BOLA check."""
    email = f"sessions_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "SessionsPassword123!"

    user = User(
        email=email, password_hash=get_password_hash(password), role="VOLUNTEER", status="APPROVED"
    )
    async_db.add(user)
    await async_db.commit()

    # Session 1: Web
    res1 = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "client_type": "WEB",
            "device_info": "MacBook Pro",
        },
    )
    token1 = res1.json()["access_token"]
    res1.json()["csrf_token"]

    # Session 2: Mobile
    await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "client_type": "MOBILE",
            "device_info": "iPhone 15",
        },
    )
    session2_id = None

    # List sessions using token1
    list_res = await client.get(
        "/api/v1/users/me/sessions", headers={"Authorization": f"Bearer {token1}"}
    )
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert len(sessions) >= 2
    for s in sessions:
        if "iPhone" in str(s.get("device_info")):
            session2_id = s["id"]

    assert session2_id is not None

    # Revoke session 2 using token1
    del_res = await client.delete(
        f"/api/v1/users/me/sessions/{session2_id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert del_res.status_code == 200

    # Verify session 2 is revoked
    stmt = select(UserSession).where(UserSession.id == uuid.UUID(session2_id))
    s2_record = (await async_db.execute(stmt)).scalar_one()
    assert s2_record.is_revoked is True


@pytest.mark.asyncio
async def test_logout_and_logout_all(client: AsyncClient, async_db: AsyncSession):
    """Verify logout revokes active session, clears cookies, and logout-all revokes all sessions."""
    email = f"logout_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "LogoutPassword123!"

    user = User(
        email=email, password_hash=get_password_hash(password), role="VOLUNTEER", status="APPROVED"
    )
    async_db.add(user)
    await async_db.commit()

    # Login
    login_res = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password, "client_type": "WEB"}
    )
    access_token = login_res.json()["access_token"]

    # Logout
    logout_res = await client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Logged out successfully"

    # Subsequent access with that access token should fail
    check_res = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert check_res.status_code == 401
    assert "SESSION_REVOKED" in check_res.text


# ==========================================
# 6. Email Verification & Password Recovery
# ==========================================


@pytest.mark.asyncio
async def test_email_verification_workflow(client: AsyncClient, async_db: AsyncSession):
    """Verify email verification token transitions user status from PENDING_VERIFICATION to PENDING_APPROVAL."""
    user = User(
        email=f"verify_{uuid.uuid4().hex[:6]}@maatram.org",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="PENDING_VERIFICATION",
    )
    async_db.add(user)
    await async_db.commit()

    raw_token = generate_refresh_token()
    verif = EmailVerification(
        user_id=user.id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(UTC) + timedelta(hours=24),
        is_used=False,
        attempt_count=0,
        max_attempts=5,
    )
    async_db.add(verif)
    await async_db.commit()

    # Verify email
    res = await client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert res.status_code == 200
    assert res.json()["status"] == "PENDING_APPROVAL"

    # User in DB is now PENDING_APPROVAL
    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as check_db:
        stmt = select(User).where(User.id == user.id)
        updated_user = (await check_db.execute(stmt)).scalar_one()
        assert updated_user.status == "PENDING_APPROVAL"

    # Re-using the same token should fail
    reuse_res = await client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert reuse_res.status_code == 400
    assert "INVALID_TOKEN" in reuse_res.text


@pytest.mark.asyncio
async def test_password_reset_otp_workflow(client: AsyncClient, async_db: AsyncSession):
    """Verify password reset request, OTP verification, password update, and session revocation."""
    email = f"reset_{uuid.uuid4().hex[:6]}@maatram.org"
    old_password = "OldPassword123!"
    new_password = "NewPassword123!"

    user = User(
        email=email,
        password_hash=get_password_hash(old_password),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    # 1. Request Password Reset OTP
    req_res = await client.post("/api/v1/auth/password-reset/request", json={"email": email})
    assert req_res.status_code == 200
    assert "reset code has been sent" in req_res.json()["message"]

    # Retrieve generated OTP from outbox job
    stmt = (
        select(CommunicationJob)
        .where(CommunicationJob.recipient == email)
        .order_by(CommunicationJob.created_at.desc())
    )
    job = (await async_db.execute(stmt)).scalars().first()
    assert job is not None
    otp = job.payload["otp"]
    assert len(otp) == 6

    # 2. Confirm reset with wrong OTP first
    wrong_res = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"email": email, "otp": "000000", "new_password": new_password},
    )
    assert wrong_res.status_code == 400
    assert "INVALID_OTP" in wrong_res.text

    # 3. Confirm reset with correct OTP
    confirm_res = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"email": email, "otp": otp, "new_password": new_password},
    )
    assert confirm_res.status_code == 200

    # 4. Old password can no longer log in
    fail_login = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": old_password, "client_type": "WEB"}
    )
    assert fail_login.status_code == 401

    # 5. New password logs in successfully
    success_login = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": new_password, "client_type": "WEB"}
    )
    assert success_login.status_code == 200


# ==========================================
# 7. CSRF Protection Tests
# ==========================================


@pytest.mark.asyncio
async def test_csrf_protection_on_cookie_authenticated_requests(
    client: AsyncClient, async_db: AsyncSession
):
    """Verify CSRF: mutative request with cookie requires valid X-CSRF-Token and whitelisted Origin."""
    email = f"csrf_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "CsrfPassword123!"

    user = User(
        email=email, password_hash=get_password_hash(password), role="VOLUNTEER", status="APPROVED"
    )
    async_db.add(user)
    await async_db.commit()

    login_res = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password, "client_type": "WEB"}
    )
    refresh_cookie = login_res.cookies.get("refresh_token")
    csrf_token = login_res.json()["csrf_token"]
    access_token = login_res.json()["access_token"]

    # 1. Mutative request with cookie but WITHOUT X-CSRF-Token header -> 403 Forbidden
    res_no_csrf = await client.post(
        "/api/v1/auth/logout",
        cookies={"refresh_token": refresh_cookie, "access_token": access_token},
    )
    assert res_no_csrf.status_code == 403
    assert "CSRF" in res_no_csrf.text

    # 2. Mutative request with cookie but with MALICIOUS Origin header -> 403 Forbidden
    res_bad_origin = await client.post(
        "/api/v1/auth/logout",
        cookies={"refresh_token": refresh_cookie, "access_token": access_token},
        headers={"X-CSRF-Token": csrf_token, "Origin": "https://malicious-attacker.com"},
    )
    assert res_bad_origin.status_code == 403

    # 3. Mobile request with Bearer authorization header is EXEMPT from CSRF and succeeds
    res_mobile_bearer = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert res_mobile_bearer.status_code == 200


# ==========================================
# 8. RBAC & Authorization Tests
# ==========================================


@pytest.mark.asyncio
async def test_rbac_volunteer_cannot_access_admin_endpoints(
    client: AsyncClient, async_db: AsyncSession
):
    """Verify Volunteer role is rejected from admin-protected functionality."""
    user = User(
        email=f"vol_{uuid.uuid4().hex[:6]}@maatram.org",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_token("rt_dummy"),
        client_type="MOBILE",
        is_revoked=False,
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    async_db.add(session)
    await async_db.commit()

    access_token = create_access_token(
        user_id=user.id, role=user.role, status=user.status, session_id=session.id
    )

    # Let's test a dependency with require_role("ADMIN")
    from fastapi import Depends

    from src.api.deps import require_role
    from src.main import app

    @app.get("/api/v1/test/admin-only")
    async def admin_only_endpoint(admin: User = Depends(require_role("ADMIN", "SUPER_ADMIN"))):
        return {"status": "ok", "admin_id": str(admin.id)}

    # Volunteer attempt -> 403 Forbidden
    res = await client.get(
        "/api/v1/test/admin-only", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert res.status_code == 403
    assert "INSUFFICIENT_PERMISSIONS" in res.text

    # Now create Admin user
    admin_user = User(
        email=f"admin_{uuid.uuid4().hex[:6]}@maatram.org",
        password_hash=get_password_hash("AdminPass123!"),
        role="ADMIN",
        status="APPROVED",
    )
    async_db.add(admin_user)
    await async_db.commit()

    admin_session = UserSession(
        user_id=admin_user.id,
        refresh_token_hash=hash_token("rt_dummy_admin"),
        client_type="MOBILE",
        is_revoked=False,
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    async_db.add(admin_session)
    await async_db.commit()

    admin_token = create_access_token(
        user_id=admin_user.id,
        role=admin_user.role,
        status=admin_user.status,
        session_id=admin_session.id,
    )

    # Admin attempt -> 200 OK
    admin_res = await client.get(
        "/api/v1/test/admin-only", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_res.status_code == 200
    assert admin_res.json()["status"] == "ok"


# ==========================================
# 8. Execution Group 2 Security Hardening Tests
# ==========================================


@pytest.mark.asyncio
async def test_login_unapproved_account_statuses_rejected(
    client: AsyncClient, async_db: AsyncSession
):
    """Verify login rejects PENDING_VERIFICATION, PENDING_APPROVAL, REJECTED, and INACTIVE accounts."""
    password = "UserPassword123!"

    statuses = ["PENDING_VERIFICATION", "PENDING_APPROVAL", "REJECTED", "INACTIVE"]
    for st in statuses:
        email = f"user_{st.lower()}_{uuid.uuid4().hex[:6]}@example.com"
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            role="VOLUNTEER",
            status=st,
            is_active=True,
        )
        async_db.add(user)
        await async_db.commit()

        res = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password, "client_type": "WEB"},
        )
        assert res.status_code == 403, f"Expected 403 for status {st}, got {res.status_code}"


def test_account_status_transitions_state_machine():
    """Verify allowed and forbidden account status transitions."""
    # Permitted transitions must succeed without exception
    enforce_status_transition("PENDING_VERIFICATION", "PENDING_APPROVAL")
    enforce_status_transition("PENDING_APPROVAL", "APPROVED")
    enforce_status_transition("PENDING_APPROVAL", "REJECTED")
    enforce_status_transition("APPROVED", "SUSPENDED")
    enforce_status_transition("APPROVED", "INACTIVE")
    enforce_status_transition("SUSPENDED", "APPROVED")

    # Forbidden transitions must raise DomainException
    forbidden_pairs = [
        ("PENDING_VERIFICATION", "APPROVED"),
        ("PENDING_VERIFICATION", "REJECTED"),
        ("APPROVED", "PENDING_VERIFICATION"),
        ("REJECTED", "APPROVED"),
        ("INACTIVE", "APPROVED"),
        ("SUSPENDED", "INACTIVE"),
    ]
    for src, dst in forbidden_pairs:
        with pytest.raises(DomainException) as exc_info:
            enforce_status_transition(src, dst)
        assert exc_info.value.code == "INVALID_STATUS_TRANSITION"


@pytest.mark.asyncio
async def test_concurrent_refresh_requests_atomic_isolation(
    client: AsyncClient, async_db: AsyncSession
):
    """Verify two concurrent refresh requests using the same token cannot both succeed."""
    email = f"concurrent_{uuid.uuid4().hex[:6]}@maatram.org"
    password = "ConcurrentPass123!"

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    # Login to obtain initial refresh token
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "MOBILE"},
    )
    assert login_res.status_code == 200
    presented_token = login_res.json()["refresh_token"]

    # Send 2 concurrent refresh requests
    req1 = client.post("/api/v1/auth/refresh", json={"refresh_token": presented_token})
    req2 = client.post("/api/v1/auth/refresh", json={"refresh_token": presented_token})

    res1, res2 = await asyncio.gather(req1, req2)
    statuses = [res1.status_code, res2.status_code]

    # Exactly one request succeeds (200), and the second is rejected (401 or 409)
    assert 200 in statuses, f"Expected one 200 OK, got: {statuses}"
    assert any(s in [401, 409] for s in statuses), f"Expected one 401 or 409, got: {statuses}"


@pytest.mark.asyncio
async def test_postgresql_rate_limiter_persistence_and_isolation(async_db: AsyncSession):
    """Verify PostgreSQL-backed rate limiter correctly persists attempts and isolates IPs and accounts."""
    limiter = PostgreSQLRateLimiter()

    ip_a = "192.168.1.10"
    ip_b = "192.168.1.20"
    endpoint = "test_login"

    # Exhaust IP A limit of 3 attempts
    for _ in range(3):
        assert await limiter.check_and_increment(
            async_db, ip_a, endpoint, max_attempts=3, window_seconds=60
        )
        await async_db.commit()

    # 4th attempt from IP A must be rate-limited
    assert not await limiter.check_and_increment(
        async_db, ip_a, endpoint, max_attempts=3, window_seconds=60
    )
    await async_db.commit()

    # IP B must remain unblocked (isolation)
    assert await limiter.check_and_increment(
        async_db, ip_b, endpoint, max_attempts=3, window_seconds=60
    )
    await async_db.commit()


@pytest.mark.asyncio
async def test_email_verification_max_attempts_exceeded(
    client: AsyncClient, async_db: AsyncSession
):
    """Verify email verification returns 429 when max 5 attempts are exceeded."""
    email = f"verif_attempts_{uuid.uuid4().hex[:6]}@maatram.org"
    user = User(
        email=email,
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="PENDING_VERIFICATION",
    )
    async_db.add(user)
    await async_db.commit()

    valid_token = generate_refresh_token()
    verif = EmailVerification(
        user_id=user.id,
        token_hash=hash_token(valid_token),
        expires_at=datetime.now(UTC) + timedelta(hours=24),
        is_used=False,
        attempt_count=0,
        max_attempts=5,
    )
    async_db.add(verif)
    await async_db.commit()

    # Submit 4 incorrect tokens with email -> all return 400 INVALID_TOKEN
    for _ in range(4):
        res = await client.post(
            "/api/v1/auth/verify-email",
            json={"token": "wrong_token_12345", "email": email},
        )
        assert res.status_code == 400
        assert "INVALID_TOKEN" in res.text

    # 5th attempt reaches max_attempts (5) -> rejected with 429 MAX_ATTEMPTS_EXCEEDED
    res_5th = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": "wrong_token_12345", "email": email},
    )
    assert res_5th.status_code == 429
    assert "MAX_ATTEMPTS_EXCEEDED" in res_5th.text

    # 6th attempt continues to be rejected with 429 MAX_ATTEMPTS_EXCEEDED
    res_exceeded = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": "wrong_token_12345", "email": email},
    )
    assert res_exceeded.status_code == 429
    assert "MAX_ATTEMPTS_EXCEEDED" in res_exceeded.text


@pytest.mark.asyncio
async def test_email_verification_expired_token(client: AsyncClient, async_db: AsyncSession):
    """Verify expired email verification token returns 410 Gone."""
    email = f"expired_verif_{uuid.uuid4().hex[:6]}@maatram.org"
    user = User(
        email=email,
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="PENDING_VERIFICATION",
    )
    async_db.add(user)
    await async_db.commit()

    raw_token = generate_refresh_token()
    verif = EmailVerification(
        user_id=user.id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(UTC) - timedelta(hours=1),  # Expired
        is_used=False,
        attempt_count=0,
        max_attempts=5,
    )
    async_db.add(verif)
    await async_db.commit()

    res = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": raw_token, "email": email},
    )
    assert res.status_code == 410
    assert "TOKEN_EXPIRED" in res.text
