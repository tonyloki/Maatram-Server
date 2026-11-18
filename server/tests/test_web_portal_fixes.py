"""Targeted test suite verifying web portal fixes and role-based access control."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.integrations.email_templates import render_email_template
from src.models.applications import VolunteerApplication
from src.models.communications import CommunicationJob
from src.models.users import User
from src.models.volunteers import VolunteerProfile, StudentProfile, AlumniProfile
from src.repositories.report_repo import report_repository
from src.repositories.application_repo import application_repository
from src.repositories.volunteer_repo import volunteer_repository


@pytest.mark.asyncio
async def test_volunteer_registration_email_template_content():
    """Verify registration email template produces the exact required notification copy."""
    payload = {"first_name": "Priya", "email": "priya@example.com"}
    subject, html, text = render_email_template("VOLUNTEER_REGISTRATION", payload)

    expected_copy = (
        "We have received your registration. Our team will review your application and approve it within 2 days. Your current application status is Pending."
    )
    assert "Registration" in subject or "Maatram" in subject
    assert expected_copy in text
    assert expected_copy in html


@pytest.mark.asyncio
async def test_admin_dashboard_metrics_counts_pending_volunteers(async_db: AsyncSession):
    """Verify admin dashboard metrics include PENDING/PENDING_APPROVAL/PENDING_VERIFICATION applications."""
    # Create test volunteer with pending status
    user = User(
        email=f"pending_vol_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="PENDING_APPROVAL",
        is_active=True,
    )
    async_db.add(user)
    await async_db.flush()

    profile = VolunteerProfile(
        user_id=user.id,
        first_name="Pending",
        last_name="Applicant",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=21,
        gender="FEMALE",
        category="STUDENT",
    )
    async_db.add(profile)
    await async_db.flush()

    app = VolunteerApplication(
        volunteer_profile_id=profile.id,
        status="PENDING",
        current_stage=6,
    )
    async_db.add(app)
    await async_db.commit()

    # Query metrics
    metrics = await report_repository.get_admin_dashboard_metrics(async_db)
    assert metrics["applications"]["pending"] >= 1
    assert metrics["volunteers"]["total_volunteers"] >= 1


@pytest.mark.asyncio
async def test_application_repo_filters_pending_consistently(async_db: AsyncSession):
    """Verify application repository list_applications filters pending applications accurately."""
    user = User(
        email=f"app_filter_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="PENDING_VERIFICATION",
        is_active=True,
    )
    async_db.add(user)
    await async_db.flush()

    profile = VolunteerProfile(
        user_id=user.id,
        first_name="Filter",
        last_name="Test",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=22,
        gender="MALE",
        category="STUDENT",
    )
    async_db.add(profile)
    await async_db.flush()

    app = VolunteerApplication(
        volunteer_profile_id=profile.id,
        status="PENDING",
        current_stage=6,
    )
    async_db.add(app)
    await async_db.commit()

    items, total = await application_repository.list_applications(async_db, status="PENDING")
    assert total >= 1
    matching = [i for i in items if i.id == app.id]
    assert len(matching) == 1
    assert matching[0].volunteer_profile.first_name == "Filter"


@pytest.mark.asyncio
async def test_cross_role_backend_security_enforcement(client: AsyncClient, async_db: AsyncSession):
    """Verify backend rejects volunteer accessing admin endpoints and accessing other volunteer profiles."""
    # 1. Seed regular volunteer
    v_user = User(
        email=f"vol_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(v_user)
    await async_db.flush()
    v_prof = VolunteerProfile(
        user_id=v_user.id,
        first_name="Vol",
        last_name="User",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=23,
        gender="FEMALE",
        category="STUDENT",
    )
    async_db.add(v_prof)

    # 2. Seed other volunteer
    other_user = User(
        email=f"other_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(other_user)
    await async_db.flush()
    other_prof = VolunteerProfile(
        user_id=other_user.id,
        first_name="Other",
        last_name="Person",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=24,
        gender="MALE",
        category="ALUMNI",
    )
    async_db.add(other_prof)

    # 3. Seed admin
    admin_user = User(
        email=f"admin_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="ADMIN",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(admin_user)
    await async_db.commit()

    # Login as volunteer
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": v_user.email, "password": "Password123!"},
    )
    v_token = login_res.json()["access_token"]
    v_headers = {"Authorization": f"Bearer {v_token}"}

    # Volunteer cannot access admin dashboard
    admin_dash_res = await client.get("/api/v1/admin/dashboard", headers=v_headers)
    assert admin_dash_res.status_code == 403

    # Volunteer cannot access admin applications list
    admin_apps_res = await client.get("/api/v1/applications", headers=v_headers)
    assert admin_apps_res.status_code == 403

    # Volunteer cannot access other volunteer's profile
    other_prof_res = await client.get(f"/api/v1/volunteers/{other_prof.id}", headers=v_headers)
    assert other_prof_res.status_code == 403

    # Volunteer CAN access their own profile
    own_prof_res = await client.get(f"/api/v1/volunteers/{v_prof.id}", headers=v_headers)
    assert own_prof_res.status_code == 200

    # Login as admin
    admin_login = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "Password123!"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin CAN view any volunteer's profile (read-only admin view)
    admin_view_res = await client.get(f"/api/v1/volunteers/{other_prof.id}", headers=admin_headers)
    assert admin_view_res.status_code == 200
    assert admin_view_res.json()["first_name"] == "Other"


@pytest.mark.asyncio
async def test_volunteer_cannot_invoke_admin_decision_or_audit_endpoints(client: AsyncClient, async_db: AsyncSession):
    """Verify volunteers receive HTTP 403 on application review and audit endpoints."""
    # Seed volunteer
    v_user = User(
        email=f"v_actor_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(v_user)
    await async_db.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": v_user.email, "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    fake_id = uuid.uuid4()
    # Approve attempt -> 403
    res_approve = await client.post(f"/api/v1/applications/{fake_id}/approve", json={"notes": "hack"}, headers=headers)
    assert res_approve.status_code == 403

    # Reject attempt -> 403
    res_reject = await client.post(f"/api/v1/applications/{fake_id}/reject", json={"reason": "hack"}, headers=headers)
    assert res_reject.status_code == 403

    # Audit logs -> 403
    res_audit = await client.get("/api/v1/admin/audit-logs", headers=headers)
    assert res_audit.status_code == 403

    # Admin reports -> 403
    res_report = await client.get("/api/v1/admin/reports/student-contributions", headers=headers)
    assert res_report.status_code == 403

    # Outbox jobs -> 403
    res_outbox = await client.get("/api/v1/admin/outbox/jobs", headers=headers)
    assert res_outbox.status_code == 403


@pytest.mark.asyncio
async def test_pending_and_rejected_volunteers_blocked_from_event_registration(client: AsyncClient, async_db: AsyncSession):
    """Verify pending and rejected volunteers cannot register for events."""
    from datetime import datetime, timezone, timedelta
    from src.models.events import Event

    # 0. Seed admin creator
    admin_creator = User(
        email=f"admin_creator_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="ADMIN",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(admin_creator)
    await async_db.flush()

    # 1. Create a published event
    now = datetime.now(timezone.utc)
    event = Event(
        title="School Outreach Drive",
        description="Community outreach initiative to government high school students.",
        category="SCHOOL_VISIT",
        mode="OFFLINE",
        status="PUBLISHED",
        location="Govt School, Chennai",
        start_time=now + timedelta(days=2),
        end_time=now + timedelta(days=2, hours=4),
        registration_deadline=now + timedelta(days=1),
        timezone="Asia/Kolkata",
        capacity_required=10,
        created_by_user_id=admin_creator.id,
    )
    async_db.add(event)
    await async_db.flush()

    # 2. Seed PENDING volunteer
    p_user = User(
        email=f"pending_reg_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="PENDING_APPROVAL",
        is_active=True,
    )
    async_db.add(p_user)
    await async_db.flush()
    p_prof = VolunteerProfile(
        user_id=p_user.id,
        first_name="Pending",
        last_name="Vol",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=20,
        gender="FEMALE",
        category="STUDENT",
    )
    async_db.add(p_prof)

    # 3. Seed REJECTED volunteer
    r_user = User(
        email=f"rejected_reg_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="REJECTED",
        is_active=True,
    )
    async_db.add(r_user)
    await async_db.flush()
    r_prof = VolunteerProfile(
        user_id=r_user.id,
        first_name="Rejected",
        last_name="Vol",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=22,
        gender="MALE",
        category="STUDENT",
    )
    async_db.add(r_prof)
    await async_db.commit()

    # 4. Verify login succeeds for pending and rejected volunteers to access Application Status Page
    p_login = await client.post(
        "/api/v1/auth/login",
        json={"email": p_user.email, "password": "Password123!"},
    )
    assert p_login.status_code == 200
    assert p_login.json()["user"]["status"] == "PENDING_APPROVAL"

    r_login = await client.post(
        "/api/v1/auth/login",
        json={"email": r_user.email, "password": "Password123!"},
    )
    assert r_login.status_code == 200
    assert r_login.json()["user"]["status"] == "REJECTED"

    # 5. Verify direct service invariant throws VOLUNTEER_NOT_APPROVED even when authenticated
    from src.core.exceptions import DomainException
    from src.services.registration_service import registration_service

    with pytest.raises(DomainException) as exc_info:
        await registration_service.register_volunteer(
            db=async_db,
            event_id=event.id,
            requesting_user_id=p_user.id,
        )
    assert exc_info.value.code == "VOLUNTEER_NOT_APPROVED"

    with pytest.raises(DomainException) as exc_info_r:
        await registration_service.register_volunteer(
            db=async_db,
            event_id=event.id,
            requesting_user_id=r_user.id,
        )
    assert exc_info_r.value.code == "VOLUNTEER_NOT_APPROVED"

    with pytest.raises(DomainException) as exc_info_r:
        await registration_service.register_volunteer(
            db=async_db,
            event_id=event.id,
            requesting_user_id=r_user.id,
        )
    assert exc_info_r.value.code == "VOLUNTEER_NOT_APPROVED"

