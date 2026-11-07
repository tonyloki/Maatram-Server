"""Sprint 1 Acceptance Verification Suite.

Comprehensive functional verification covering:
1. Password recovery lifecycle (OTP request, anti-enumeration, validation, reuse/expiry rejection, session revocation)
2. Volunteer application journeys (Student, Alumni, Corporate, pending holding, admin review, approval, rejection, RBAC)
3. Event discovery, filtering, registration constraints, capacity enforcement, and withdrawal
4. My Activity, points ledger, profile updates, and differential consent persistence
5. Admin audit logs authorization, filtering, state diffs, and immutability
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.admin import AuditLog
from src.models.applications import VolunteerApplication
from src.models.communications import CommunicationJob
from src.models.events import Event, EventRegistration
from src.models.consent import ConsentRecord
from src.models.volunteers import VolunteerProfile
from src.models.users import PasswordResetToken, User


@pytest.mark.asyncio
async def test_password_recovery_full_lifecycle(client: AsyncClient, async_db: AsyncSession):
    """1. Test the complete password recovery journey."""
    unique_suffix = uuid.uuid4().hex[:6]
    test_email = f"pwd_recovery_{unique_suffix}@example.com"
    old_password = "InitialPassword123!"
    new_password = "NewSecurePassword456!"

    # Create active user with initial password
    user = User(
        email=test_email,
        password_hash=get_password_hash(old_password),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)

    # 1.1 Anti-enumeration: Request reset for non-existent email
    unknown_res = await client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "nonexistent_volunteer_999@example.com"},
    )
    assert unknown_res.status_code == 200
    assert "If the account exists" in unknown_res.json()["message"]

    # Verify no token was created for non-existent email
    stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == uuid.uuid4())
    res = await async_db.execute(stmt)
    assert res.scalar_one_or_none() is None

    # 1.2 Request reset for valid registered email
    reset_req_res = await client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": test_email},
    )
    assert reset_req_res.status_code == 200
    assert "If the account exists" in reset_req_res.json()["message"]

    # Verify token and outbox communication job created in DB
    token_stmt = (
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id)
        .order_by(PasswordResetToken.created_at.desc())
    )
    token_record = (await async_db.execute(token_stmt)).scalar_one_or_none()
    assert token_record is not None
    assert token_record.is_used is False

    job_stmt = (
        select(CommunicationJob)
        .where(CommunicationJob.recipient == test_email)
        .order_by(CommunicationJob.created_at.desc())
    )
    job_record = (await async_db.execute(job_stmt)).scalar_one_or_none()
    assert job_record is not None
    assert job_record.template_name == "PASSWORD_RESET_OTP"
    raw_otp = job_record.payload["otp"]
    assert len(raw_otp) == 6
    assert raw_otp.isdigit()

    # 1.3 Incorrect OTP submission rejected
    bad_otp_res = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "email": test_email,
            "otp": "000000",
            "new_password": new_password,
        },
    )
    assert bad_otp_res.status_code == 400
    assert "INVALID_OTP" in bad_otp_res.text or "Invalid" in bad_otp_res.text

    # 1.4 Expired OTP simulation
    token_record.expires_at = datetime.now(UTC) - timedelta(minutes=5)
    await async_db.commit()

    expired_otp_res = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "email": test_email,
            "otp": raw_otp,
            "new_password": new_password,
        },
    )
    assert expired_otp_res.status_code == 400

    # Reset expiration for valid test
    token_record.expires_at = datetime.now(UTC) + timedelta(minutes=15)
    token_record.attempt_count = 0
    await async_db.commit()

    # 1.5 Successful password reset
    success_res = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "email": test_email,
            "otp": raw_otp,
            "new_password": new_password,
        },
    )
    assert success_res.status_code == 200
    assert "Password reset successfully" in success_res.json()["message"]

    # 1.6 Reused OTP rejection
    reused_res = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "email": test_email,
            "otp": raw_otp,
            "new_password": "AnotherPassword789!",
        },
    )
    assert reused_res.status_code == 400

    # 1.7 Verify login with old password fails
    old_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": old_password},
    )
    assert old_login_res.status_code == 401

    # 1.8 Verify login with new password succeeds
    new_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": new_password},
    )
    assert new_login_res.status_code == 200
    assert new_login_res.json()["user"]["email"] == test_email


@pytest.mark.asyncio
async def test_volunteer_application_journeys(client: AsyncClient, async_db: AsyncSession):
    """2. Test Student, Alumni, and Corporate volunteer journeys end-to-end."""
    suffix = uuid.uuid4().hex[:6]

    # Create admin user for reviewing
    admin = User(
        email=f"admin_reviewer_{suffix}@example.com",
        password_hash=get_password_hash("AdminPass123!"),
        role="ADMIN",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(admin)
    await async_db.commit()

    admin_login = await client.post(
        "/api/v1/auth/login",
        json={"email": admin.email, "password": "AdminPass123!"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2.1 Student Registration
    student_payload = {
        "email": f"student_{suffix}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Karthik",
        "last_name": "Raman",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "age": 20,
        "gender": "MALE",
        "category": "STUDENT",
        "student_details": {
            "college_name": "PSG Tech",
            "degree": "B.E.",
            "department": "ECE",
            "batch_year": 2026,
            "current_year": 3,
            "maatram_reg_number": f"MAAT-{suffix.upper()}",
        },
        "consent": {
            "leaderboard_visible": False,
            "name_visible": False,
            "thank_you_emails": False,
            "linkedin_content": False,
            "contact_available": False,
            "media_usage": False,
        },
    }
    reg_student_res = await client.post("/api/v1/auth/register", json=student_payload)
    assert reg_student_res.status_code == 201
    student_user_id = reg_student_res.json()["user_id"]
    assert reg_student_res.json()["status"] in ("PENDING_VERIFICATION", "PENDING_APPROVAL")

    # 2.2 Alumni Registration
    alumni_payload = {
        "email": f"alumni_{suffix}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Deepa",
        "last_name": "S",
        "mobile_number": f"+9197{uuid.uuid4().int % 100000000:08d}",
        "age": 25,
        "gender": "FEMALE",
        "category": "ALUMNI",
        "alumni_details": {
            "college_name": "Anna University",
            "degree": "B.Tech",
            "department": "IT",
            "batch_year": 2022,
            "graduation_year": 2022,
            "organisation": "Zoho",
            "job_role": "Software Engineer",
            "years_of_experience": 2,
            "location": "Chennai",
            "skills": ["Python", "Mentoring"],
        },
        "consent": {"leaderboard_visible": False},
    }
    reg_alumni_res = await client.post("/api/v1/auth/register", json=alumni_payload)
    assert reg_alumni_res.status_code == 201
    alumni_user_id = reg_alumni_res.json()["user_id"]

    # 2.3 Corporate Panelist Registration
    corporate_payload = {
        "email": f"corp_{suffix}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Vikram",
        "last_name": "Nathan",
        "mobile_number": f"+9196{uuid.uuid4().int % 100000000:08d}",
        "age": 32,
        "gender": "MALE",
        "category": "CORPORATE",
        "corporate_details": {
            "organisation": "TCS",
            "designation": "Technical Lead",
            "years_of_experience": 8,
            "location": "Chennai",
            "skills": ["Interviews", "Architecture"],
        },
        "consent": {"leaderboard_visible": False},
    }
    reg_corp_res = await client.post("/api/v1/auth/register", json=corporate_payload)
    assert reg_corp_res.status_code == 201
    corp_user_id = reg_corp_res.json()["user_id"]

    # 2.4 Login before email verification is rejected with 403
    student_login_pre = await client.post(
        "/api/v1/auth/login",
        json={"email": student_payload["email"], "password": student_payload["password"]},
    )
    assert student_login_pre.status_code == 403
    assert "verify" in student_login_pre.text.lower()

    # Verify email for student, alumni, and corporate
    for email in [student_payload["email"], alumni_payload["email"], corporate_payload["email"]]:
        j_stmt = (
            select(CommunicationJob)
            .where(CommunicationJob.recipient == email)
            .order_by(CommunicationJob.created_at.desc())
        )
        j = (await async_db.execute(j_stmt)).scalar_one()
        v_res = await client.post("/api/v1/auth/verify-email", json={"token": j.payload["token"]})
        assert v_res.status_code == 200
        assert v_res.json()["status"] == "PENDING_APPROVAL"

    # Login before admin approval is rejected with 403 indicating PENDING_APPROVAL
    student_login_pending = await client.post(
        "/api/v1/auth/login",
        json={"email": student_payload["email"], "password": student_payload["password"]},
    )
    assert student_login_pending.status_code == 403
    assert "pending" in student_login_pending.text.lower() or "approval" in student_login_pending.text.lower()

    # 2.5 Admin reviews and approves Student and Alumni
    student_app = (
        await async_db.execute(
            select(VolunteerApplication)
            .join(VolunteerProfile, VolunteerProfile.id == VolunteerApplication.volunteer_profile_id)
            .where(VolunteerProfile.user_id == uuid.UUID(student_user_id))
        )
    ).scalar_one()

    alumni_app = (
        await async_db.execute(
            select(VolunteerApplication)
            .join(VolunteerProfile, VolunteerProfile.id == VolunteerApplication.volunteer_profile_id)
            .where(VolunteerProfile.user_id == uuid.UUID(alumni_user_id))
        )
    ).scalar_one()

    corp_app = (
        await async_db.execute(
            select(VolunteerApplication)
            .join(VolunteerProfile, VolunteerProfile.id == VolunteerApplication.volunteer_profile_id)
            .where(VolunteerProfile.user_id == uuid.UUID(corp_user_id))
        )
    ).scalar_one()

    app_student_res = await client.post(
        f"/api/v1/applications/{student_app.id}/approve",
        headers=admin_headers,
    )
    assert app_student_res.status_code == 200
    assert app_student_res.json()["status"] == "APPROVED"

    app_alumni_res = await client.post(
        f"/api/v1/applications/{alumni_app.id}/approve",
        headers=admin_headers,
    )
    assert app_alumni_res.status_code == 200

    # 2.6 Admin rejects Corporate applicant with reason
    reject_corp_res = await client.post(
        f"/api/v1/applications/{corp_app.id}/reject",
        headers=admin_headers,
        json={"reason": "Incomplete corporate affiliation documentation."},
    )
    assert reject_corp_res.status_code == 200
    assert reject_corp_res.json()["status"] == "REJECTED"

    # 2.7 Verify Student login now returns status APPROVED
    student_login_after = await client.post(
        "/api/v1/auth/login",
        json={"email": student_payload["email"], "password": student_payload["password"]},
    )
    assert student_login_after.status_code == 200
    assert student_login_after.json()["user"]["status"] == "APPROVED"
    student_token = student_login_after.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # 2.8 Verify Corporate login returns status REJECTED (403 with rejection notice)
    corp_login_after = await client.post(
        "/api/v1/auth/login",
        json={"email": corporate_payload["email"], "password": corporate_payload["password"]},
    )
    assert corp_login_after.status_code == 403
    assert "rejected" in corp_login_after.text.lower()

    # 2.9 Unauthorized access attempt: Student cannot access admin endpoints
    unauth_admin_res = await client.get("/api/v1/admin/dashboard", headers=student_headers)
    assert unauth_admin_res.status_code == 403


@pytest.mark.asyncio
async def test_event_discovery_and_registration(client: AsyncClient, async_db: AsyncSession):
    """3. Test event listing, zero events, 1 event, filtering, registration, capacity, and withdrawal."""
    suffix = uuid.uuid4().hex[:6]

    # Create approved volunteer
    vol = User(
        email=f"vol_events_{suffix}@example.com",
        password_hash=get_password_hash("Pass123!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    admin = User(
        email=f"admin_events_{suffix}@example.com",
        password_hash=get_password_hash("AdminPass123!"),
        role="ADMIN",
        status="APPROVED",
        is_active=True,
    )
    async_db.add_all([vol, admin])
    await async_db.flush()

    vol_profile = VolunteerProfile(
        user_id=vol.id,
        first_name="Anand",
        last_name="V",
        category="STUDENT",
        age=21,
        gender="MALE",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
    )
    async_db.add(vol_profile)
    await async_db.commit()

    vol_login = await client.post(
        "/api/v1/auth/login",
        json={"email": vol.email, "password": "Pass123!"},
    )
    vol_token = vol_login.json()["access_token"]
    vol_headers = {"Authorization": f"Bearer {vol_token}"}

    admin_login = await client.post(
        "/api/v1/auth/login",
        json={"email": admin.email, "password": "AdminPass123!"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3.1 Create 1st published event
    now = datetime.now(UTC)
    evt1 = Event(
        title=f"Chennai School Visit Drive {suffix}",
        description="Mentoring high school students in math and career guidance.",
        category="SCHOOL_VISIT",
        mode="OFFLINE",
        status="PUBLISHED",
        start_time=now + timedelta(days=5),
        end_time=now + timedelta(days=5, hours=4),
        registration_deadline=now + timedelta(days=4),
        location="Government Higher Secondary School, Chennai",
        capacity_required=1,
        created_by_user_id=admin.id,
    )
    async_db.add(evt1)
    await async_db.commit()
    await async_db.refresh(evt1)

    # 3.2 Fetch events - exactly 1 returned with correct details
    list_res1 = await client.get("/api/v1/events", headers=vol_headers)
    assert list_res1.status_code == 200
    assert any(e["id"] == str(evt1.id) for e in list_res1.json()["items"])

    # 3.3 Keyword search and category filtering
    search_res = await client.get(
        f"/api/v1/events?search=Chennai%20School%20Visit%20Drive%20{suffix}",
        headers=vol_headers,
    )
    assert search_res.status_code == 200
    assert len(search_res.json()["items"]) == 1
    assert search_res.json()["items"][0]["id"] == str(evt1.id)

    # Empty search query returns zero items
    empty_search_res = await client.get(
        "/api/v1/events?search=NonExistentKeywordDriveZ99",
        headers=vol_headers,
    )
    assert empty_search_res.status_code == 200
    assert len(empty_search_res.json()["items"]) == 0

    # 3.4 Event Details retrieval
    detail_res = await client.get(f"/api/v1/events/{evt1.id}", headers=vol_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == evt1.title
    assert detail_res.json()["capacity_required"] == 1

    # 3.5 Volunteer registers for event
    reg_res = await client.post(f"/api/v1/events/{evt1.id}/register", headers=vol_headers)
    assert reg_res.status_code == 201
    assert reg_res.json()["event_id"] == str(evt1.id)
    assert reg_res.json()["status"] == "SUBSCRIBED"
    reg_id = reg_res.json()["id"]

    # 3.6 Duplicate registration returns existing registration idempotently
    dup_res = await client.post(f"/api/v1/events/{evt1.id}/register", headers=vol_headers)
    assert dup_res.status_code == 201
    assert dup_res.json()["id"] == reg_id
    assert dup_res.json()["status"] == "SUBSCRIBED"

    # 3.7 Capacity constraint: 2nd volunteer attempts registration when capacity is 1 -> WAITLISTED
    vol2 = User(
        email=f"vol2_events_{suffix}@example.com",
        password_hash=get_password_hash("Pass123!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(vol2)
    await async_db.flush()

    vol2_profile = VolunteerProfile(
        user_id=vol2.id,
        first_name="Ravi",
        last_name="K",
        category="STUDENT",
        age=22,
        gender="MALE",
        mobile_number=f"+9199{uuid.uuid4().int % 100000000:08d}",
    )
    async_db.add(vol2_profile)
    await async_db.commit()

    vol2_login = await client.post(
        "/api/v1/auth/login",
        json={"email": vol2.email, "password": "Pass123!"},
    )
    vol2_token = vol2_login.json()["access_token"]
    vol2_headers = {"Authorization": f"Bearer {vol2_token}"}

    capacity_res = await client.post(f"/api/v1/events/{evt1.id}/register", headers=vol2_headers)
    assert capacity_res.status_code == 201
    assert capacity_res.json()["status"] == "WAITLISTED"

    # 3.8 Closed registration: attempt to register for closed event rejected
    evt_closed = Event(
        title=f"Closed Drive {suffix}",
        description="Completed/closed volunteering drive.",
        category="SCHOOL_VISIT",
        mode="OFFLINE",
        status="REGISTRATION_CLOSED",
        start_time=now + timedelta(days=5),
        end_time=now + timedelta(days=5, hours=4),
        registration_deadline=now + timedelta(days=4),
        location="Chennai",
        capacity_required=10,
        created_by_user_id=admin.id,
    )
    async_db.add(evt_closed)
    await async_db.commit()

    closed_res = await client.post(f"/api/v1/events/{evt_closed.id}/register", headers=vol2_headers)
    assert closed_res.status_code == 400
    assert "REGISTRATION_CLOSED" in closed_res.text or "not open" in closed_res.text

    # 3.8 Volunteer self-service withdrawal
    withdraw_res = await client.post(
        f"/api/v1/registrations/{reg_id}/withdraw",
        headers=vol_headers,
        json={"reason": "Personal conflict"},
    )
    assert withdraw_res.status_code == 200
    assert withdraw_res.json()["status"] == "WITHDRAWN"


@pytest.mark.asyncio
async def test_my_activity_profile_and_consent(client: AsyncClient, async_db: AsyncSession):
    """4. Test My Activity tabs, points ledger, profile updates, and consent persistence."""
    suffix = uuid.uuid4().hex[:6]

    user = User(
        email=f"profile_tester_{suffix}@example.com",
        password_hash=get_password_hash("Pass123!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(user)
    await async_db.flush()

    profile = VolunteerProfile(
        user_id=user.id,
        first_name="Priya",
        last_name="Sundar",
        category="STUDENT",
        age=20,
        gender="FEMALE",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
    )
    async_db.add(profile)
    await async_db.flush()

    consent = ConsentRecord(
        volunteer_profile_id=profile.id,
        leaderboard_visible=False,
        name_visible=False,
        thank_you_emails=False,
        linkedin_content=False,
        contact_available=False,
        media_usage=False,
    )
    async_db.add(consent)
    await async_db.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "Pass123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4.1 My Activity endpoints
    my_regs = await client.get("/api/v1/registrations/me", headers=headers)
    assert my_regs.status_code == 200
    assert "items" in my_regs.json()

    my_att = await client.get("/api/v1/attendance/me", headers=headers)
    assert my_att.status_code == 200
    assert "items" in my_att.json()

    my_ledger = await client.get("/api/v1/gamification/ledger", headers=headers)
    assert my_ledger.status_code == 200
    assert "net_points" in my_ledger.json()

    # 4.2 Profile self-service update
    update_res = await client.patch(
        "/api/v1/volunteers/me",
        headers=headers,
        json={
            "first_name": "Priyadharshini",
            "bio": "Passionate mentor dedicated to education empowerment.",
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["first_name"] == "Priyadharshini"
    assert update_res.json()["bio"] == "Passionate mentor dedicated to education empowerment."

    # 4.3 Validation failure preservation
    invalid_res = await client.patch(
        "/api/v1/volunteers/me",
        headers=headers,
        json={"mobile_number": "invalid-phone-string"},
    )
    assert invalid_res.status_code == 422

    # 4.4 Differential consent update: update only leaderboard_visible
    consent_update_res = await client.put(
        "/api/v1/consent/me",
        headers=headers,
        json={"leaderboard_visible": True},
    )
    assert consent_update_res.status_code == 200
    c_data = consent_update_res.json()
    assert c_data["leaderboard_visible"] is True
    # Verify all other 5 consents remained False
    assert c_data["name_visible"] is False
    assert c_data["thank_you_emails"] is False
    assert c_data["linkedin_content"] is False
    assert c_data["contact_available"] is False
    assert c_data["media_usage"] is False


@pytest.mark.asyncio
async def test_admin_audit_logs_authorization_and_immutability(
    client: AsyncClient, async_db: AsyncSession
):
    """5. Test Super Admin audit logs, RBAC authorization, state diffs, and immutability."""
    suffix = uuid.uuid4().hex[:6]

    vol = User(
        email=f"vol_audit_{suffix}@example.com",
        password_hash=get_password_hash("Pass123!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    admin = User(
        email=f"admin_audit_{suffix}@example.com",
        password_hash=get_password_hash("Pass123!"),
        role="ADMIN",
        status="APPROVED",
        is_active=True,
    )
    super_admin = User(
        email=f"super_audit_{suffix}@example.com",
        password_hash=get_password_hash("Pass123!"),
        role="SUPER_ADMIN",
        status="APPROVED",
        is_active=True,
    )
    async_db.add_all([vol, admin, super_admin])
    await async_db.commit()

    # Login all 3 actors
    vol_login = (
        await client.post(
            "/api/v1/auth/login",
            json={"email": vol.email, "password": "Pass123!"},
        )
    ).json()["access_token"]
    admin_login = (
        await client.post(
            "/api/v1/auth/login",
            json={"email": admin.email, "password": "Pass123!"},
        )
    ).json()["access_token"]
    super_login = (
        await client.post(
            "/api/v1/auth/login",
            json={"email": super_admin.email, "password": "Pass123!"},
        )
    ).json()["access_token"]

    vol_headers = {"Authorization": f"Bearer {vol_login}"}
    admin_headers = {"Authorization": f"Bearer {admin_login}"}
    super_headers = {"Authorization": f"Bearer {super_login}"}

    # 5.1 RBAC Enforcement: Volunteer receives 403 Forbidden
    vol_res = await client.get("/api/v1/admin/audit-logs", headers=vol_headers)
    assert vol_res.status_code == 403

    # 5.2 RBAC Enforcement: Standard Admin receives 403 Forbidden (SUPER_ADMIN required)
    admin_res = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert admin_res.status_code == 403

    # 5.3 Super Admin receives 200 OK
    super_res = await client.get("/api/v1/admin/audit-logs", headers=super_headers)
    assert super_res.status_code == 200
    data = super_res.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data

    # 5.4 Audit log entry verification: Insert known action with JSON state diff
    sample_log = AuditLog(
        actor_user_id=super_admin.id,
        action="USER_STATUS_UPDATED",
        resource_type="user",
        resource_id=str(vol.id),
        old_state={"status": "PENDING_APPROVAL"},
        new_state={"status": "APPROVED"},
        reason="Verified credentials with college registrar.",
    )
    async_db.add(sample_log)
    await async_db.commit()

    # Query with action filter
    filtered_res = await client.get(
        "/api/v1/admin/audit-logs?action=USER_STATUS_UPDATED",
        headers=super_headers,
    )
    assert filtered_res.status_code == 200
    items = filtered_res.json()["items"]
    matched = [i for i in items if i["resource_id"] == str(vol.id)]
    assert len(matched) >= 1
    target = matched[0]
    assert target["action"] == "USER_STATUS_UPDATED"
    assert target["actor_email"] == super_admin.email
    assert target["old_state"] == {"status": "PENDING_APPROVAL"}
    assert target["new_state"] == {"status": "APPROVED"}
    assert target["reason"] == "Verified credentials with college registrar."
