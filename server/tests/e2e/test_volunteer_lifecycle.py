"""End-to-End full lifecycle integration test for adult volunteer onboarding, event participation, and gamification."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

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
async def test_full_adult_volunteer_lifecycle_e2e(client: AsyncClient, async_db: AsyncSession):
    """Scenario A: Full adult volunteer lifecycle from registration to gamification leaderboard.
    
    Workflow steps:
    1. Register adult volunteer account via API.
    2. Extract one-time email verification token from outbox and verify email.
    3. Admin logs in and approves the volunteer onboarding application.
    4. Admin creates and publishes an admissions event.
    5. Volunteer logs in and registers for the event (status: SUBSCRIBED).
    6. Admin selects the volunteer for the event (status: SELECTED).
    7. Admin logs volunteer check-in.
    8. Admin logs volunteer check-out 3 hours later (180 minutes, 3.00 credited hours).
    9. Admin completes event and triggers authoritative gamification point awarding.
    10. Verify points calculation: P = (1 * 10) + (3.00 * 2) = 16.00 points.
    11. Verify volunteer points balance, immutable point transaction ledger, and rank 1 on leaderboard.
    """
    now = datetime.now(UTC)

    # 1. Setup Admin User
    admin_password = "AdminSecurePassword123!"
    admin_email = f"admin_e2e_{uuid.uuid4().hex[:6]}@maatram.org"
    admin_user = User(
        email=admin_email,
        password_hash=get_password_hash(admin_password),
        role="ADMIN",
        status="APPROVED",
    )
    async_db.add(admin_user)
    await async_db.commit()

    # Log in Admin
    admin_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_email, "password": admin_password, "client_type": "WEB"},
    )
    assert admin_login_res.status_code == 200, f"Admin login failed: {admin_login_res.text}"
    admin_token = admin_login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Register Adult Volunteer (Age 24)
    vol_email = f"adult_vol_{uuid.uuid4().hex[:6]}@example.com"
    vol_password = "VolSecurePassword123!"
    reg_payload = {
        "email": vol_email,
        "password": vol_password,
        "first_name": "Karthik",
        "last_name": "Raman",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "gender": "MALE",
        "age": 24,
        "category": "STUDENT",
        "student_details": {
            "college_name": "Loyola College",
            "degree": "B.Sc Computer Science",
            "department": "Computer Science",
            "batch_year": 2026,
            "current_year": 3,
            "maatram_reg_number": "MAAT-2026-001",
        },
        "consent": {
            "leaderboard_visible": True,
            "name_visible": True,
        },
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, f"Volunteer registration failed: {reg_res.text}"

    # 3. Verify Email ownership via verification token from outbox
    job_stmt = (
        select(CommunicationJob)
        .where(CommunicationJob.recipient == vol_email)
        .order_by(CommunicationJob.created_at.desc())
    )
    job = (await async_db.execute(job_stmt)).scalars().first()
    assert job is not None, "Email verification outbox job not found"
    raw_token = job.payload["token"]

    verif_res = await client.post(
        "/api/v1/auth/verify-email",
        json={"email": vol_email, "token": raw_token},
    )
    assert verif_res.status_code == 200, f"Email verification failed: {verif_res.text}"

    # 4. Resolve Onboarding Application ID and Admin Approves Application
    app_stmt = (
        select(VolunteerApplication)
        .join(VolunteerProfile, VolunteerApplication.volunteer_profile_id == VolunteerProfile.id)
        .join(User, VolunteerProfile.user_id == User.id)
        .where(User.email == vol_email)
    )
    app_obj = (await async_db.execute(app_stmt)).scalars().first()
    assert app_obj is not None, "Volunteer onboarding application not found"

    approve_res = await client.post(
        f"/api/v1/applications/{app_obj.id}/approve",
        json={"notes": "Adult volunteer verified and approved"},
        headers=admin_headers,
    )
    assert approve_res.status_code == 200, f"Application approval failed: {approve_res.text}"

    # 5. Admin creates and publishes Admissions Event
    event_payload = {
        "title": "Admissions Screening Panel 2026",
        "description": "Student candidate admissions interview panel",
        "category": "ADMISSIONS",
        "mode": "OFFLINE",
        "location": "Loyola College Campus, Chennai",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=5)).isoformat(),
        "registration_deadline": (now + timedelta(minutes=45)).isoformat(),
        "capacity_required": 10,
    }
    create_event_res = await client.post(
        "/api/v1/events",
        json=event_payload,
        headers=admin_headers,
    )
    assert create_event_res.status_code == 201, f"Event creation failed: {create_event_res.text}"
    event_id = create_event_res.json()["id"]

    pub_res = await client.post(
        f"/api/v1/events/{event_id}/publish",
        headers=admin_headers,
    )
    assert pub_res.status_code == 200, f"Event publish failed: {pub_res.text}"

    # 6. Volunteer logs in and registers for event
    vol_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": vol_email, "password": vol_password, "client_type": "WEB"},
    )
    assert vol_login_res.status_code == 200, f"Volunteer login failed: {vol_login_res.text}"
    vol_token = vol_login_res.json()["access_token"]
    vol_headers = {"Authorization": f"Bearer {vol_token}"}

    vol_reg_res = await client.post(
        f"/api/v1/events/{event_id}/register",
        headers=vol_headers,
    )
    assert vol_reg_res.status_code == 201, f"Event registration failed: {vol_reg_res.text}"
    reg_data = vol_reg_res.json()
    assert reg_data["status"] == "SUBSCRIBED"
    registration_id = reg_data["id"]

    # 7. Admin selects volunteer
    select_res = await client.post(
        f"/api/v1/events/{event_id}/select",
        json={"registration_ids": [registration_id]},
        headers=admin_headers,
    )
    assert select_res.status_code == 200, f"Volunteer selection failed: {select_res.text}"

    # 8. Admin checks in volunteer
    vol_prof_stmt = (
        select(VolunteerProfile)
        .join(User, VolunteerProfile.user_id == User.id)
        .where(User.email == vol_email)
    )
    vol_profile = (await async_db.execute(vol_prof_stmt)).scalars().first()
    assert vol_profile is not None
    vol_profile_id = str(vol_profile.id)

    check_in_time = now - timedelta(hours=3)
    cin_res = await client.post(
        f"/api/v1/events/{event_id}/attendance/check-in",
        json={
            "volunteer_profile_ids": [vol_profile_id],
            "check_in_time": check_in_time.isoformat(),
        },
        headers=admin_headers,
    )
    assert cin_res.status_code == 200, f"Check-in failed: {cin_res.text}"
    cin_records = cin_res.json()
    assert len(cin_records) == 1
    assert cin_records[0]["status"] == "IN_PROGRESS"

    # 9. Admin checks out volunteer 3 hours later (180 minutes duration = 3.00 credited hours)
    check_out_time = now
    cout_res = await client.post(
        f"/api/v1/events/{event_id}/attendance/check-out",
        json={
            "volunteer_profile_ids": [vol_profile_id],
            "check_out_time": check_out_time.isoformat(),
        },
        headers=admin_headers,
    )
    assert cout_res.status_code == 200, f"Check-out failed: {cout_res.text}"
    cout_records = cout_res.json()
    assert len(cout_records) == 1
    assert cout_records[0]["status"] == "COMPLETED"
    assert cout_records[0]["duration_minutes"] == 180
    assert Decimal(str(cout_records[0]["hours_credited"])) == Decimal("3.00")

    # 10. Admin completes event and triggers gamification point awarding
    award_res = await client.post(
        f"/api/v1/gamification/events/{event_id}/complete-and-award",
        headers=admin_headers,
    )
    assert award_res.status_code == 200, f"Event completion failed: {award_res.text}"
    award_data = award_res.json()
    assert award_data["status"] == "COMPLETED"
    assert award_data["total_volunteers_awarded"] == 1
    assert Decimal(str(award_data["total_points_awarded"])) == Decimal("16.00")
    assert Decimal(str(award_data["total_hours_credited"])) == Decimal("3.00")

    # 11. Verify gamification balance, ledger transaction, and leaderboard
    # Formula: P = (1 * 10) + (3.00 * 2) = 16.00 points
    expected_points = Decimal("16.00")

    summary_res = await client.get(
        "/api/v1/gamification/summary",
        headers=vol_headers,
    )
    assert summary_res.status_code == 200, f"Summary failed: {summary_res.text}"
    summary = summary_res.json()
    assert Decimal(str(summary["total_points"])) == expected_points
    assert summary["completed_events_count"] == 1
    assert Decimal(str(summary["total_hours"])) == Decimal("3.00")

    ledger_res = await client.get(
        "/api/v1/gamification/ledger",
        headers=vol_headers,
    )
    assert ledger_res.status_code == 200, f"Ledger failed: {ledger_res.text}"
    ledger_items = ledger_res.json()["items"]
    assert len(ledger_items) >= 1
    assert any(
        Decimal(str(item["total_points"])) == expected_points and item["event_id"] == str(event_id)
        for item in ledger_items
    )

    lb_res = await client.get("/api/v1/gamification/leaderboard", headers=vol_headers)
    assert lb_res.status_code == 200, f"Leaderboard failed: {lb_res.text}"
    lb_items = lb_res.json()["items"]
    assert len(lb_items) >= 1
    assert lb_items[0]["rank"] == 1
    assert Decimal(str(lb_items[0]["total_points"])) == expected_points
