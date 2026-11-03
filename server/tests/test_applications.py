"""Integration test suite for Volunteer Onboarding Applications, Approvals & Minor Safeguards (Phase 5)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.admin import AuditLog
from src.models.applications import ApplicationReview, VolunteerApplication
from src.models.communications import CommunicationJob
from src.models.users import User
from src.models.volunteers import VolunteerProfile


async def create_admin_user(async_db: AsyncSession, email: str | None = None) -> User:
    """Helper to seed an active Admin user."""
    admin_email = email or f"admin_{uuid.uuid4().hex[:6]}@maatram.org"
    user = User(
        email=admin_email,
        password_hash=get_password_hash("AdminPass123!"),
        role="ADMIN",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user


async def get_token(client: AsyncClient, email: str, password: str = "AdminPass123!") -> str:
    """Helper to get JWT access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_registration_creates_pending_application(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify registration creates base application with PENDING status in the same transaction."""
    email = f"app_vol_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "SecurePassword123!",
        "first_name": "Vignesh",
        "last_name": "S",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "age": 22,
        "gender": "MALE",
        "category": "CORPORATE",
        "corporate_details": {
            "organisation": "Cognizant",
            "designation": "Associate",
            "years_of_experience": 2.0,
            "location": "Coimbatore",
            "skills": ["Java", "SQL"],
        },
    }
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201

    # Check VolunteerApplication exists in DB
    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    profile = (
        await async_db.execute(select(VolunteerProfile).where(VolunteerProfile.user_id == user.id))
    ).scalar_one()

    app = (
        await async_db.execute(
            select(VolunteerApplication).where(
                VolunteerApplication.volunteer_profile_id == profile.id
            )
        )
    ).scalar_one_or_none()

    assert app is not None
    assert app.status == "PENDING"
    assert app.current_stage == 6


@pytest.mark.asyncio
async def test_get_my_application(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify volunteer can fetch their own application via /api/v1/applications/me."""
    email = f"app_me_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Pooja",
            "last_name": "M",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 21,
            "gender": "FEMALE",
            "category": "STUDENT",
            "student_details": {
                "college_name": "CIT",
                "degree": "B.E.",
                "department": "Mechanical",
                "batch_year": 2025,
                "current_year": 4,
                "maatram_reg_number": f"MAAT-{uuid.uuid4().hex[:6].upper()}",
            },
        },
    )

    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    token = await get_token(client, email, "SecurePassword123!")

    res = await client.get("/api/v1/applications/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PENDING"
    assert data["current_stage"] == 6


@pytest.mark.asyncio
async def test_get_application_by_id_bola(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify BOLA: volunteer can view their own application, other volunteer is blocked, admin succeeds."""
    email1 = f"app_u1_{uuid.uuid4().hex[:6]}@example.com"
    email2 = f"app_u2_{uuid.uuid4().hex[:6]}@example.com"

    for em in (email1, email2):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": em,
                "password": "SecurePassword123!",
                "first_name": "Test",
                "last_name": "User",
                "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
                "age": 22,
                "gender": "OTHER",
                "category": "CORPORATE",
                "corporate_details": {
                    "organisation": "TCS",
                    "designation": "Analyst",
                    "years_of_experience": 1.0,
                    "location": "Chennai",
                    "skills": [],
                },
            },
        )
        u = (await async_db.execute(select(User).where(User.email == em))).scalar_one()
        u.status = "APPROVED"
        await async_db.commit()

    token1 = await get_token(client, email1, "SecurePassword123!")
    token2 = await get_token(client, email2, "SecurePassword123!")

    u1 = (await async_db.execute(select(User).where(User.email == email1))).scalar_one()
    p1 = (
        await async_db.execute(select(VolunteerProfile).where(VolunteerProfile.user_id == u1.id))
    ).scalar_one()
    app1 = (
        await async_db.execute(
            select(VolunteerApplication).where(VolunteerApplication.volunteer_profile_id == p1.id)
        )
    ).scalar_one()

    # User 1 views own app -> 200 OK
    res1 = await client.get(
        f"/api/v1/applications/{app1.id}", headers={"Authorization": f"Bearer {token1}"}
    )
    assert res1.status_code == 200
    assert res1.json()["id"] == str(app1.id)

    # User 2 attempts to view User 1's app -> 403 Forbidden
    res2 = await client.get(
        f"/api/v1/applications/{app1.id}", headers={"Authorization": f"Bearer {token2}"}
    )
    assert res2.status_code == 403

    # Admin views User 1's app -> 200 OK
    admin = await create_admin_user(async_db)
    admin_token = await get_token(client, admin.email)
    res_admin = await client.get(
        f"/api/v1/applications/{app1.id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["user_email"] == email1


@pytest.mark.asyncio
async def test_minor_safeguarding_approval_blocked_without_verified_consent(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify minor applicant (< 18) CANNOT be approved if parental consent is not admin-verified."""
    minor_email = f"minor_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": minor_email,
            "password": "SecurePassword123!",
            "first_name": "Young",
            "last_name": "Volunteer",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 16,
            "gender": "FEMALE",
            "category": "STUDENT",
            "parent_guardian_name": "Mrs. Volunteer",
            "parent_guardian_relationship": "Mother",
            "parent_guardian_contact": "+919876543210",
            "parental_consent_claimed": True,
            "student_details": {
                "college_name": "School / Jr College",
                "degree": "12th Standard",
                "department": "Science",
                "batch_year": 2026,
                "current_year": 1,
                "maatram_reg_number": f"MAAT-{uuid.uuid4().hex[:6].upper()}",
            },
        },
    )

    user = (await async_db.execute(select(User).where(User.email == minor_email))).scalar_one()
    # Simulate email verification step: status transitions to PENDING_APPROVAL
    user.status = "PENDING_APPROVAL"
    await async_db.commit()

    prof = (
        await async_db.execute(select(VolunteerProfile).where(VolunteerProfile.user_id == user.id))
    ).scalar_one()
    app = (
        await async_db.execute(
            select(VolunteerApplication).where(VolunteerApplication.volunteer_profile_id == prof.id)
        )
    ).scalar_one()

    admin = await create_admin_user(async_db)
    admin_token = await get_token(client, admin.email)

    # Attempt approval without verifying consent -> 400 Bad Request
    res_approve = await client.post(
        f"/api/v1/applications/{app.id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_approve.status_code == 400
    assert "parental consent" in res_approve.json()["message"].lower()


@pytest.mark.asyncio
async def test_minor_safeguarding_parental_consent_verification_and_approval(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify end-to-end minor onboarding: verify parental consent first, then approval succeeds."""
    minor_email = f"minor_flow_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": minor_email,
            "password": "SecurePassword123!",
            "first_name": "Rahul",
            "last_name": "Minor",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 17,
            "gender": "MALE",
            "category": "STUDENT",
            "parent_guardian_name": "Mr. Minor",
            "parent_guardian_relationship": "Father",
            "parent_guardian_contact": "+919876543211",
            "parental_consent_claimed": True,
            "student_details": {
                "college_name": "HSC School",
                "degree": "12th Standard",
                "department": "Commerce",
                "batch_year": 2026,
                "current_year": 1,
                "maatram_reg_number": f"MAAT-{uuid.uuid4().hex[:6].upper()}",
            },
        },
    )

    user = (await async_db.execute(select(User).where(User.email == minor_email))).scalar_one()
    user.status = "PENDING_APPROVAL"
    await async_db.commit()

    prof = (
        await async_db.execute(select(VolunteerProfile).where(VolunteerProfile.user_id == user.id))
    ).scalar_one()
    app = (
        await async_db.execute(
            select(VolunteerApplication).where(VolunteerApplication.volunteer_profile_id == prof.id)
        )
    ).scalar_one()

    admin = await create_admin_user(async_db)
    admin_token = await get_token(client, admin.email)

    # 1. Admin verifies parental consent
    res_consent = await client.post(
        f"/api/v1/applications/{app.id}/verify-parental-consent",
        json={"status": "VERIFIED", "notes": "Parent phone verification confirmed verbally."},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_consent.status_code == 200
    c_data = res_consent.json()
    assert c_data["parental_consent_verified"] is True
    assert c_data["parental_consent_status"] == "VERIFIED"

    # Verify audit log for consent verification
    audit = (
        await async_db.execute(
            select(AuditLog).where(
                AuditLog.action == "PARENTAL_CONSENT_VERIFIED",
                AuditLog.resource_id == str(prof.id),
            )
        )
    ).scalar_one_or_none()
    assert audit is not None

    # 2. Admin approves application
    res_approve = await client.post(
        f"/api/v1/applications/{app.id}/approve",
        json={"notes": "All documents in order."},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_approve.status_code == 200
    app_data = res_approve.json()
    assert app_data["status"] == "APPROVED"

    # Verify DB state
    await async_db.refresh(user)
    assert user.status == "APPROVED"

    # Verify ApplicationReview recorded
    review = (
        await async_db.execute(
            select(ApplicationReview).where(ApplicationReview.application_id == app.id)
        )
    ).scalar_one()
    assert review.action == "APPROVED"
    assert review.reviewer_id == admin.id

    # Verify welcome email notification enqueued
    job = (
        await async_db.execute(
            select(CommunicationJob).where(
                CommunicationJob.recipient == user.email,
                CommunicationJob.template_name == "APPLICATION_APPROVED",
            )
        )
    ).scalar_one_or_none()
    assert job is not None

    # 3. Duplicate approval attempt -> 409 Conflict
    res_dup = await client.post(
        f"/api/v1/applications/{app.id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_dup.status_code == 409


@pytest.mark.asyncio
async def test_admin_rejection_workflow(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify application rejection requires mandatory reasoning and updates account lifecycle."""
    email = f"reject_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Incomplete",
            "last_name": "Applicant",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 24,
            "gender": "MALE",
            "category": "CORPORATE",
            "corporate_details": {
                "organisation": "Unregistered Ltd",
                "designation": "Staff",
                "years_of_experience": 1.0,
                "location": "Trichy",
                "skills": [],
            },
        },
    )

    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    user.status = "PENDING_APPROVAL"
    await async_db.commit()

    prof = (
        await async_db.execute(select(VolunteerProfile).where(VolunteerProfile.user_id == user.id))
    ).scalar_one()
    app = (
        await async_db.execute(
            select(VolunteerApplication).where(VolunteerApplication.volunteer_profile_id == prof.id)
        )
    ).scalar_one()

    admin = await create_admin_user(async_db)
    admin_token = await get_token(client, admin.email)

    # 1. Missing or empty reason -> 422 Unprocessable Entity
    res_empty_reason = await client.post(
        f"/api/v1/applications/{app.id}/reject",
        json={"reason": "  "},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_empty_reason.status_code == 422

    # 2. Valid rejection
    res_reject = await client.post(
        f"/api/v1/applications/{app.id}/reject",
        json={"reason": "Applicant provided unverified corporate organization credentials."},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_reject.status_code == 200
    assert res_reject.json()["status"] == "REJECTED"

    # Verify user state is REJECTED
    await async_db.refresh(user)
    assert user.status == "REJECTED"

    # Verify ApplicationReview recorded
    review = (
        await async_db.execute(
            select(ApplicationReview).where(ApplicationReview.application_id == app.id)
        )
    ).scalar_one()
    assert review.action == "REJECTED"
    assert "unverified corporate" in (review.reason or "")

    # Verify rejection email notification enqueued
    job = (
        await async_db.execute(
            select(CommunicationJob).where(
                CommunicationJob.recipient == user.email,
                CommunicationJob.template_name == "APPLICATION_REJECTED",
            )
        )
    ).scalar_one_or_none()
    assert job is not None

    # 3. Duplicate rejection -> 409 Conflict
    res_dup = await client.post(
        f"/api/v1/applications/{app.id}/reject",
        json={"reason": "Second rejection attempt."},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_dup.status_code == 409
