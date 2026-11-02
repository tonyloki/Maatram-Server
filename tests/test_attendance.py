"""Comprehensive test suite for Attendance Tracking & Hours Management (Phase 8)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.attendance import AttendanceCorrection
from src.models.events import Event, EventRegistration
from src.models.users import User
from src.models.volunteers import VolunteerProfile


async def create_user(
    async_db: AsyncSession,
    role: str = "VOLUNTEER",
    status: str = "APPROVED",
    email: str | None = None,
) -> tuple[User, VolunteerProfile | None]:
    """Helper to seed user and optional volunteer profile."""
    user_email = email or f"{role.lower()}_{uuid.uuid4().hex[:6]}@example.com"
    user = User(
        email=user_email,
        password_hash=get_password_hash("Password123!"),
        role=role,
        status=status,
        is_active=True,
    )
    async_db.add(user)
    await async_db.flush()

    profile: VolunteerProfile | None = None
    if role == "VOLUNTEER":
        profile = VolunteerProfile(
            user_id=user.id,
            first_name="Test",
            last_name="Volunteer",
            mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
            age=24,
            gender="FEMALE",
            category="STUDENT",
        )
        async_db.add(profile)

    await async_db.commit()
    await async_db.refresh(user)
    if profile:
        await async_db.refresh(profile)
    return user, profile


async def get_auth_token(client: AsyncClient, email: str, password: str = "Password123!") -> str:
    """Helper to authenticate and obtain JWT access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]  # type: ignore[no-any-return]


async def seed_event_with_selected_volunteer(
    async_db: AsyncSession,
    event_status: str = "ONGOING",
) -> tuple[Event, User, VolunteerProfile, EventRegistration, User]:
    """Helper to seed an active event and selected volunteer registration."""
    admin, _ = await create_user(async_db, role="ADMIN", status="APPROVED")
    vol_user, vol_profile = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    assert vol_profile is not None

    now = datetime.now(UTC)
    start_dt = now - timedelta(hours=2)
    end_dt = now + timedelta(hours=3)

    event = Event(
        title="School Career Guidance Camp",
        description="Providing guidance to high school students.",
        category="SCHOOL_VISIT",
        mode="OFFLINE",
        location="Government Higher Secondary School, Tiruvallur",
        start_time=start_dt,
        end_time=end_dt,
        timezone="Asia/Kolkata",
        capacity_required=5,
        registration_deadline=start_dt - timedelta(days=1),
        status=event_status,
        created_by_user_id=admin.id,
    )
    async_db.add(event)
    await async_db.flush()

    registration = EventRegistration(
        event_id=event.id,
        volunteer_profile_id=vol_profile.id,
        status="SELECTED",
        selected_at=now - timedelta(days=2),
    )
    async_db.add(registration)
    await async_db.commit()
    await async_db.refresh(event)
    await async_db.refresh(registration)

    return event, vol_user, vol_profile, registration, admin


@pytest.mark.asyncio
async def test_admin_can_check_in_selected_volunteer(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify admin can log check-in for a SELECTED volunteer on an active event."""
    event, _, vol_profile, reg, admin = await seed_event_with_selected_volunteer(async_db)
    token = await get_auth_token(client, admin.email)

    in_time = datetime.now(UTC) - timedelta(hours=1)
    res = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={
            "volunteer_profile_id": str(vol_profile.id),
            "check_in_time": in_time.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 1
    record = data[0]
    assert record["status"] == "IN_PROGRESS"
    assert record["event_registration_id"] == str(reg.id)
    assert record["volunteer_profile_id"] == str(vol_profile.id)


@pytest.mark.asyncio
async def test_unselected_volunteer_check_in_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify check-in is rejected if volunteer is not SELECTED."""
    event, _, _, reg, admin = await seed_event_with_selected_volunteer(async_db)
    token = await get_auth_token(client, admin.email)

    # Change registration status to SUBSCRIBED
    reg.status = "SUBSCRIBED"
    await async_db.commit()

    _, other_vol = await create_user(async_db, role="VOLUNTEER")
    assert other_vol is not None

    res = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={"volunteer_profile_id": str(other_vol.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "REGISTRATION_NOT_SELECTED" in res.text


@pytest.mark.asyncio
async def test_check_in_on_inactive_event_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify check-in on DRAFT or CANCELLED event is rejected."""
    event, _, vol_profile, _, admin = await seed_event_with_selected_volunteer(
        async_db, event_status="CANCELLED"
    )
    token = await get_auth_token(client, admin.email)

    res = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={"volunteer_profile_id": str(vol_profile.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "EVENT_NOT_ACTIVE" in res.text


@pytest.mark.asyncio
async def test_duplicate_check_in_rejected(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify duplicate check-in raises DUPLICATE_CHECKIN error."""
    event, _, vol_profile, _, admin = await seed_event_with_selected_volunteer(async_db)
    token = await get_auth_token(client, admin.email)

    # First check-in
    res1 = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={"volunteer_profile_id": str(vol_profile.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 200

    # Duplicate check-in attempt
    res2 = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={"volunteer_profile_id": str(vol_profile.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 400
    assert "DUPLICATE_CHECKIN" in res2.text


@pytest.mark.asyncio
async def test_check_out_calculates_duration_and_hours(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify check-out updates status to COMPLETED and computes duration in exact minutes and Decimal hours."""
    event, _, vol_profile, _, admin = await seed_event_with_selected_volunteer(async_db)
    token = await get_auth_token(client, admin.email)

    now = datetime.now(UTC)
    in_time = now - timedelta(minutes=90)
    out_time = now

    # Check in
    await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={
            "volunteer_profile_id": str(vol_profile.id),
            "check_in_time": in_time.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # Check out 90 minutes later (1.50 hours)
    res = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-out",
        json={
            "volunteer_profile_id": str(vol_profile.id),
            "check_out_time": out_time.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 1
    record = data[0]
    assert record["status"] == "COMPLETED"
    assert record["duration_minutes"] == 90
    assert record["hours_credited"] == "1.50"


@pytest.mark.asyncio
async def test_checkout_before_checkin_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify check-out time preceding check-in is rejected."""
    event, _, vol_profile, _, admin = await seed_event_with_selected_volunteer(async_db)
    token = await get_auth_token(client, admin.email)

    now = datetime.now(UTC)
    await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={
            "volunteer_profile_id": str(vol_profile.id),
            "check_in_time": now.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # Attempt check-out 10 minutes BEFORE check-in
    res = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-out",
        json={
            "volunteer_profile_id": str(vol_profile.id),
            "check_out_time": (now - timedelta(minutes=10)).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "INVALID_CHECKOUT_TIME" in res.text


@pytest.mark.asyncio
async def test_checkout_without_checkin_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify check-out without prior check-in is rejected."""
    event, _, vol_profile, _, admin = await seed_event_with_selected_volunteer(async_db)
    token = await get_auth_token(client, admin.email)

    res = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-out",
        json={"volunteer_profile_id": str(vol_profile.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "NO_ACTIVE_CHECKIN" in res.text


@pytest.mark.asyncio
async def test_attendance_correction_under_threshold_by_admin(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify admin can correct attendance within 2-hour threshold and records audit log."""
    event, _, vol_profile, _, admin = await seed_event_with_selected_volunteer(async_db)
    admin_token = await get_auth_token(client, admin.email)

    now = datetime.now(UTC)
    in_time = now - timedelta(hours=2)
    out_time = now - timedelta(hours=1)

    # Check-in and check-out
    await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={"volunteer_profile_id": str(vol_profile.id), "check_in_time": in_time.isoformat()},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    res_out = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-out",
        json={"volunteer_profile_id": str(vol_profile.id), "check_out_time": out_time.isoformat()},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    record_id = res_out.json()[0]["id"]

    # Admin correction: extend by 60 minutes (1 hour diff <= 2 hour threshold)
    corrected_out = out_time + timedelta(minutes=60)
    corr_res = await client.post(
        f"/api/v1/attendance/{record_id}/correct",
        json={
            "new_check_in_time": in_time.isoformat(),
            "new_check_out_time": corrected_out.isoformat(),
            "reason": "Scanner hardware malfunction at departure gate.",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert corr_res.status_code == 200, corr_res.text
    data = corr_res.json()
    assert data["duration_minutes"] == 120
    assert data["hours_credited"] == "2.00"
    assert data["corrections_count"] == 1

    # Verify correction record in database
    stmt = select(AttendanceCorrection).where(
        AttendanceCorrection.attendance_record_id == uuid.UUID(record_id)
    )
    corr = (await async_db.execute(stmt)).scalar_one()
    assert corr.new_duration_minutes == 120
    assert "Scanner hardware" in corr.reason


@pytest.mark.asyncio
async def test_attendance_correction_over_threshold_requires_super_admin(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify corrections exceeding 2 hours fail for standard Admin and succeed for Super Admin."""
    event, _, vol_profile, _, admin = await seed_event_with_selected_volunteer(async_db)
    admin_token = await get_auth_token(client, admin.email)

    super_admin, _ = await create_user(async_db, role="SUPER_ADMIN", status="APPROVED")
    super_admin_token = await get_auth_token(client, super_admin.email)

    now = datetime.now(UTC)
    in_time = now - timedelta(hours=1)
    out_time = now

    await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={"volunteer_profile_id": str(vol_profile.id), "check_in_time": in_time.isoformat()},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    res_out = await client.post(
        f"/api/v1/events/{event.id}/attendance/check-out",
        json={"volunteer_profile_id": str(vol_profile.id), "check_out_time": out_time.isoformat()},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    record_id = res_out.json()[0]["id"]

    # Try 3-hour extension (180 mins diff > 120 threshold) as ADMIN -> Forbidden
    huge_out = out_time + timedelta(hours=3)
    res_admin = await client.post(
        f"/api/v1/attendance/{record_id}/correct",
        json={
            "new_check_in_time": in_time.isoformat(),
            "new_check_out_time": huge_out.isoformat(),
            "reason": "Major system failure during all afternoon activities.",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 403
    assert "SUPER_ADMIN" in res_admin.text

    # Same request by SUPER_ADMIN -> Succeeds!
    res_super = await client.post(
        f"/api/v1/attendance/{record_id}/correct",
        json={
            "new_check_in_time": in_time.isoformat(),
            "new_check_out_time": huge_out.isoformat(),
            "reason": "Major system failure during all afternoon activities verified.",
        },
        headers={"Authorization": f"Bearer {super_admin_token}"},
    )
    assert res_super.status_code == 200, res_super.text
    assert res_super.json()["duration_minutes"] == 240


@pytest.mark.asyncio
async def test_bulk_attendance_processing(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify bulk check-in and bulk check-out across multiple volunteers."""
    admin, _ = await create_user(async_db, role="ADMIN", status="APPROVED")
    token = await get_auth_token(client, admin.email)

    now = datetime.now(UTC)
    event = Event(
        title="College Mentorship Meet",
        description="Mentoring college scholars.",
        category="MOCK_INTERVIEW",
        mode="ONLINE",
        location="https://meet.google.com/test-meet",
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=2),
        capacity_required=10,
        registration_deadline=now - timedelta(days=1),
        status="ONGOING",
        created_by_user_id=admin.id,
    )
    async_db.add(event)
    await async_db.flush()

    vol_ids: list[uuid.UUID] = []
    for _ in range(3):
        _, prof = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
        assert prof is not None
        reg = EventRegistration(
            event_id=event.id,
            volunteer_profile_id=prof.id,
            status="SELECTED",
        )
        async_db.add(reg)
        vol_ids.append(prof.id)
    await async_db.commit()

    # Bulk Check-in
    bulk_in_res = await client.post(
        f"/api/v1/events/{event.id}/attendance/bulk",
        json={
            "action": "CHECK_IN",
            "volunteer_profile_ids": [str(i) for i in vol_ids],
            "timestamp": (now - timedelta(minutes=45)).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bulk_in_res.status_code == 200, bulk_in_res.text
    in_data = bulk_in_res.json()
    assert in_data["successful_count"] == 3
    assert in_data["failed_count"] == 0

    # Bulk Check-out
    bulk_out_res = await client.post(
        f"/api/v1/events/{event.id}/attendance/bulk",
        json={
            "action": "CHECK_OUT",
            "volunteer_profile_ids": [str(i) for i in vol_ids],
            "timestamp": now.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bulk_out_res.status_code == 200, bulk_out_res.text
    out_data = bulk_out_res.json()
    assert out_data["successful_count"] == 3
    assert out_data["failed_count"] == 0


@pytest.mark.asyncio
async def test_volunteer_can_view_own_attendance_history(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify volunteer can view their personal attendance records via /attendance/me."""
    event, vol_user, vol_profile, _, admin = await seed_event_with_selected_volunteer(async_db)
    admin_token = await get_auth_token(client, admin.email)
    vol_token = await get_auth_token(client, vol_user.email)

    now = datetime.now(UTC)
    await client.post(
        f"/api/v1/events/{event.id}/attendance/check-in",
        json={
            "volunteer_profile_id": str(vol_profile.id),
            "check_in_time": (now - timedelta(hours=1)).isoformat(),
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Volunteer fetches own attendance
    res = await client.get(
        "/api/v1/attendance/me",
        headers={"Authorization": f"Bearer {vol_token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "IN_PROGRESS"
    assert data["items"][0]["volunteer_profile_id"] == str(vol_profile.id)
