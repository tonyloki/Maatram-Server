"""End-to-End minor safeguarding and parental consent lifecycle test."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.applications import VolunteerApplication
from src.models.communications import CommunicationJob
from src.models.users import User
from src.models.volunteers import VolunteerProfile


@pytest.mark.asyncio
async def test_minor_safeguarding_consent_lifecycle_e2e(client: AsyncClient, async_db: AsyncSession):
    """Scenario B: Minor volunteer (< 18) onboarding and parental consent verification lifecycle.
    
    Workflow steps:
    1. Register minor volunteer (age 16) with required parent/guardian details.
    2. Complete email verification via token from outbox.
    3. Admin attempts to approve the application without verifying parental consent -> MUST FAIL with MINOR_CONSENT_UNVERIFIED.
    4. Admin performs documentary verification of parental consent via PATCH /api/v1/applications/{id}/verify-parental-consent.
    5. Admin re-attempts approval -> MUST SUCCEED with HTTP 200, transitioning user status to APPROVED.
    """
    # 1. Setup Admin user and authenticate
    admin_password = "AdminSecurePassword123!"
    admin_email = f"admin_guard_{uuid.uuid4().hex[:6]}@maatram.org"
    admin_user = User(
        email=admin_email,
        password_hash=get_password_hash(admin_password),
        role="ADMIN",
        status="APPROVED",
    )
    async_db.add(admin_user)
    await async_db.commit()

    admin_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_email, "password": admin_password, "client_type": "WEB"},
    )
    assert admin_login_res.status_code == 200
    admin_token = admin_login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Register Minor Volunteer (Age 16)
    minor_email = f"minor_vol_{uuid.uuid4().hex[:6]}@example.com"
    minor_password = "MinorSecurePass123!"
    reg_payload = {
        "email": minor_email,
        "password": minor_password,
        "first_name": "Meera",
        "last_name": "Sundaram",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "gender": "FEMALE",
        "age": 16,
        "category": "STUDENT",
        "parent_guardian_name": "Sundaram R",
        "parent_guardian_relationship": "FATHER",
        "parent_guardian_contact": "+919876543219",
        "parental_consent_claimed": True,
        "student_details": {
            "college_name": "Anna University",
            "degree": "B.E Computer Science",
            "department": "CSE",
            "batch_year": 2027,
            "current_year": 1,
            "maatram_reg_number": "MAAT-2027-010",
        },
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"

    # 3. Verify Email
    job_stmt = (
        select(CommunicationJob)
        .where(CommunicationJob.recipient == minor_email)
        .order_by(CommunicationJob.created_at.desc())
    )
    job = (await async_db.execute(job_stmt)).scalars().first()
    assert job is not None
    raw_token = job.payload["token"]

    verif_res = await client.post(
        "/api/v1/auth/verify-email",
        json={"email": minor_email, "token": raw_token},
    )
    assert verif_res.status_code == 200

    # 4. Resolve Application ID
    app_stmt = (
        select(VolunteerApplication)
        .join(VolunteerProfile, VolunteerApplication.volunteer_profile_id == VolunteerProfile.id)
        .join(User, VolunteerProfile.user_id == User.id)
        .where(User.email == minor_email)
    )
    app_obj = (await async_db.execute(app_stmt)).scalars().first()
    assert app_obj is not None
    app_id = str(app_obj.id)

    # 5. Invariant Check: Admin approval WITHOUT parental consent MUST FAIL with MINOR_CONSENT_UNVERIFIED
    failed_approve_res = await client.post(
        f"/api/v1/applications/{app_id}/approve",
        json={"notes": "Premature approval attempt"},
        headers=admin_headers,
    )
    assert failed_approve_res.status_code == 400
    err_body = failed_approve_res.json()
    err_code = err_body.get("error_code") or err_body.get("error", {}).get("code")
    assert err_code == "MINOR_CONSENT_UNVERIFIED", f"Expected MINOR_CONSENT_UNVERIFIED, got {err_code}"

    # 6. Admin verifies parental consent
    verify_consent_res = await client.patch(
        f"/api/v1/applications/{app_id}/verify-parental-consent",
        json={"status": "VERIFIED", "notes": "Parent confirmed identity and consent via telephone interview."},
        headers=admin_headers,
    )
    assert verify_consent_res.status_code == 200, f"Consent verification failed: {verify_consent_res.text}"
    profile_data = verify_consent_res.json()
    assert profile_data["parental_consent_verified"] is True
    assert profile_data["parental_consent_status"] == "VERIFIED"

    # 7. Admin re-attempts approval -> MUST SUCCEED
    success_approve_res = await client.post(
        f"/api/v1/applications/{app_id}/approve",
        json={"notes": "Approved with verified parental consent"},
        headers=admin_headers,
    )
    assert success_approve_res.status_code == 200, f"Approval after consent failed: {success_approve_res.text}"
    app_data = success_approve_res.json()
    assert app_data["status"] == "APPROVED"

    # 8. Confirm user account status is now APPROVED
    user_stmt = select(User).where(User.email == minor_email)
    refreshed_user = (await async_db.execute(user_stmt)).scalars().first()
    assert refreshed_user is not None
    assert refreshed_user.status == "APPROVED"
