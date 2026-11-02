"""Comprehensive test suite for Atomic Event Completion & Gamification Finalization (Phase 9)."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.attendance import AttendanceRecord
from src.models.communications import CommunicationJob
from src.models.consent import ConsentRecord
from src.models.events import Event, EventRegistration
from src.models.gamification import PointTransaction
from src.models.users import User
from src.models.volunteers import VolunteerProfile


async def create_user(
    async_db: AsyncSession,
    role: str = "VOLUNTEER",
    category: str = "STUDENT",
    status: str = "APPROVED",
    email: str | None = None,
    thank_you_emails: bool = True,
) -> tuple[User, VolunteerProfile]:
    """Helper to seed user, volunteer profile, and consent preferences."""
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

    profile = VolunteerProfile(
        user_id=user.id,
        first_name="Participant",
        last_name="Volunteer",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=23,
        gender="FEMALE",
        category=category,
    )
    async_db.add(profile)
    await async_db.flush()

    consent = ConsentRecord(
        volunteer_profile_id=profile.id,
        leaderboard_visible=True,
        name_visible=True,
        thank_you_emails=thank_you_emails,
    )
    async_db.add(consent)
    await async_db.commit()
    await async_db.refresh(user)
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


@pytest.mark.asyncio
async def test_event_completion_preview_generation(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify preview generates accurate attendance breakdowns, calculated points, warnings, and LinkedIn copy."""
    admin_user, _ = await create_user(async_db, role="ADMIN")
    admin_token = await get_auth_token(client, admin_user.email)

    now = datetime.now(UTC)
    event = Event(
        title="Mock Interview Drive",
        description="Interviewing college students.",
        category="MOCK_INTERVIEW",
        mode="ONLINE",
        location="https://meet.google.com/interview-drive",
        start_time=now - timedelta(hours=3),
        end_time=now,
        capacity_required=10,
        registration_deadline=now - timedelta(days=2),
        status="ONGOING",
        created_by_user_id=admin_user.id,
    )
    async_db.add(event)
    await async_db.flush()

    # Vol 1: Attended and Completed (90 mins -> 1.50 hrs -> 13.00 pts)
    _, vol1 = await create_user(async_db, thank_you_emails=True)
    reg1 = EventRegistration(event_id=event.id, volunteer_profile_id=vol1.id, status="SELECTED")
    async_db.add(reg1)
    await async_db.flush()
    att1 = AttendanceRecord(
        event_registration_id=reg1.id,
        check_in_time=now - timedelta(minutes=90),
        check_out_time=now,
        duration_minutes=90,
        status="COMPLETED",
    )
    async_db.add(att1)

    # Vol 2: Incomplete (Checked in, never checked out)
    _, vol2 = await create_user(async_db, thank_you_emails=False)
    reg2 = EventRegistration(event_id=event.id, volunteer_profile_id=vol2.id, status="SELECTED")
    async_db.add(reg2)
    await async_db.flush()
    att2 = AttendanceRecord(
        event_registration_id=reg2.id,
        check_in_time=now - timedelta(minutes=120),
        status="IN_PROGRESS",
    )
    async_db.add(att2)

    # Vol 3: Absent (Selected, never checked in)
    _, vol3 = await create_user(async_db)
    reg3 = EventRegistration(event_id=event.id, volunteer_profile_id=vol3.id, status="SELECTED")
    async_db.add(reg3)

    await async_db.commit()

    # Query completion preview
    res = await client.get(
        f"/api/v1/events/{event.id}/completion-preview",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["total_selected"] == 3
    assert data["total_attended"] == 1
    assert data["total_incomplete"] == 1
    assert data["total_absent"] == 1
    assert data["total_hours_credited"] == "1.50"
    assert data["total_points_to_award"] == "13.00"
    assert data["thank_you_recipients_count"] == 1  # Vol 1 has consent and attended
    assert "Mock Interview Drive" in data["draft_linkedin_copy"]

    # Verify warnings on attendees
    attendees = {a["volunteer_profile_id"]: a for a in data["attendees"]}
    assert len(attendees[str(vol2.id)]["warnings"]) > 0
    assert "Missing check-out" in attendees[str(vol2.id)]["warnings"][0]
    assert "did not check in" in attendees[str(vol3.id)]["warnings"][0]


@pytest.mark.asyncio
async def test_atomic_event_completion_and_point_allocation(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify atomic finalization transitions event, creates ledger entries, and generates outbox jobs."""
    admin_user, _ = await create_user(async_db, role="ADMIN")
    admin_token = await get_auth_token(client, admin_user.email)

    now = datetime.now(UTC)
    event = Event(
        title="Youth Leadership Workshop",
        description="Leadership skills training.",
        category="PANEL_INTERVIEW",
        mode="OFFLINE",
        location="Loyola College, Chennai",
        start_time=now - timedelta(hours=2),
        end_time=now,
        capacity_required=5,
        registration_deadline=now - timedelta(days=1),
        status="ONGOING",
        created_by_user_id=admin_user.id,
    )
    async_db.add(event)
    await async_db.flush()

    # Vol 1: Attended (120 mins = 2.00 hrs -> 14.00 points)
    u1, vol1 = await create_user(async_db, thank_you_emails=True)
    reg1 = EventRegistration(event_id=event.id, volunteer_profile_id=vol1.id, status="SELECTED")
    async_db.add(reg1)
    await async_db.flush()
    att1 = AttendanceRecord(
        event_registration_id=reg1.id,
        check_in_time=now - timedelta(minutes=120),
        check_out_time=now,
        duration_minutes=120,
        status="COMPLETED",
    )
    async_db.add(att1)

    # Vol 2: Incomplete (Never checked out)
    _, vol2 = await create_user(async_db, thank_you_emails=True)
    reg2 = EventRegistration(event_id=event.id, volunteer_profile_id=vol2.id, status="SELECTED")
    async_db.add(reg2)
    await async_db.flush()
    att2 = AttendanceRecord(
        event_registration_id=reg2.id,
        check_in_time=now - timedelta(minutes=60),
        status="IN_PROGRESS",
    )
    async_db.add(att2)

    await async_db.commit()

    # Finalize completion: POST /api/v1/events/{id}/complete-and-award
    res = await client.post(
        f"/api/v1/events/{event.id}/complete-and-award",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["total_volunteers_awarded"] == 1
    assert data["total_points_awarded"] == "14.00"
    assert data["total_hours_credited"] == "2.00"
    assert data["outbox_jobs_created"] == 1

    # Verify PointTransaction in DB
    tx_stmt = select(PointTransaction).where(PointTransaction.event_id == event.id)
    tx_rows = list((await async_db.execute(tx_stmt)).scalars().all())
    assert len(tx_rows) == 1
    tx = tx_rows[0]
    assert tx.volunteer_profile_id == vol1.id
    assert tx.event_points == Decimal("10.00")
    assert tx.hour_points == Decimal("4.00")
    assert tx.total_points == Decimal("14.00")
    assert tx.hours_credited == Decimal("2.00")
    assert tx.transaction_type == "EVENT_COMPLETION"

    # Verify Incomplete attendance was flagged
    await async_db.refresh(att2)
    assert att2.status == "INCOMPLETE"
    assert att2.duration_minutes == 0

    # Verify CommunicationJob created in outbox
    job_stmt = select(CommunicationJob).where(
        CommunicationJob.idempotency_key == f"thank_you_{event.id}_{vol1.id}"
    )
    job = (await async_db.execute(job_stmt)).scalar_one_or_none()
    assert job is not None
    assert job.channel == "EMAIL"
    assert job.recipient == u1.email
    assert job.status == "PENDING"
    assert job.template_name == "EVENT_THANK_YOU"


@pytest.mark.asyncio
async def test_event_completion_idempotency_blocks_duplicate_awards(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify calling event completion a second time returns error and awards zero additional points."""
    admin_user, _ = await create_user(async_db, role="ADMIN")
    admin_token = await get_auth_token(client, admin_user.email)

    now = datetime.now(UTC)
    event = Event(
        title="Scholarship Screening Camp",
        description="Screening applications.",
        category="ADMISSIONS",
        mode="OFFLINE",
        location="Madurai",
        start_time=now - timedelta(hours=2),
        end_time=now,
        capacity_required=5,
        registration_deadline=now - timedelta(days=1),
        status="ONGOING",
        created_by_user_id=admin_user.id,
    )
    async_db.add(event)
    await async_db.flush()

    _, vol = await create_user(async_db)
    reg = EventRegistration(event_id=event.id, volunteer_profile_id=vol.id, status="SELECTED")
    async_db.add(reg)
    await async_db.flush()
    att = AttendanceRecord(
        event_registration_id=reg.id,
        check_in_time=now - timedelta(minutes=60),
        check_out_time=now,
        duration_minutes=60,
        status="COMPLETED",
    )
    async_db.add(att)
    await async_db.commit()

    # 1. First completion succeeds
    res1 = await client.post(
        f"/api/v1/events/{event.id}/complete-and-award",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res1.status_code == 200

    # 2. Second completion call must be rejected
    res2 = await client.post(
        f"/api/v1/events/{event.id}/complete-and-award",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res2.status_code == 400
    assert "POINTS_ALREADY_AWARDED" in res2.text

    # Assert exactly 1 point transaction exists in database
    tx_stmt = select(PointTransaction).where(PointTransaction.event_id == event.id)
    tx_rows = list((await async_db.execute(tx_stmt)).scalars().all())
    assert len(tx_rows) == 1


@pytest.mark.asyncio
async def test_compensating_transaction_on_post_completion_correction(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify attendance correction after event completion generates compensating point transaction."""
    admin_user, _ = await create_user(async_db, role="ADMIN")
    admin_token = await get_auth_token(client, admin_user.email)

    now = datetime.now(UTC)
    event = Event(
        title="Village Education Survey",
        description="Surveying school dropouts.",
        category="SCHOOL_VISIT",
        mode="OFFLINE",
        location="Chengalpattu",
        start_time=now - timedelta(hours=3),
        end_time=now - timedelta(hours=1),
        capacity_required=5,
        registration_deadline=now - timedelta(days=2),
        status="ONGOING",
        created_by_user_id=admin_user.id,
    )
    async_db.add(event)
    await async_db.flush()

    _, vol = await create_user(async_db)
    reg = EventRegistration(event_id=event.id, volunteer_profile_id=vol.id, status="SELECTED")
    async_db.add(reg)
    await async_db.flush()

    in_time = now - timedelta(hours=3)
    out_time = now - timedelta(hours=2)  # 60 minutes = 1.00 hr -> 12.00 pts

    att = AttendanceRecord(
        event_registration_id=reg.id,
        check_in_time=in_time,
        check_out_time=out_time,
        duration_minutes=60,
        status="COMPLETED",
    )
    async_db.add(att)
    await async_db.commit()

    # Complete and award
    res_comp = await client.post(
        f"/api/v1/events/{event.id}/complete-and-award",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_comp.status_code == 200

    # Verify original transaction was 12.00 points
    orig_tx_stmt = select(PointTransaction).where(
        PointTransaction.event_id == event.id,
        PointTransaction.transaction_type == "EVENT_COMPLETION",
    )
    orig_tx = (await async_db.execute(orig_tx_stmt)).scalar_one()
    assert orig_tx.total_points == Decimal("12.00")

    # Now admin corrects attendance: extends by 30 mins (total 90 mins = 1.50 hrs -> 13.00 pts)
    # Delta: +0.50 hrs -> +1.00 point
    corrected_out = out_time + timedelta(minutes=30)
    corr_res = await client.post(
        f"/api/v1/attendance/{att.id}/correct",
        json={
            "new_check_in_time": in_time.isoformat(),
            "new_check_out_time": corrected_out.isoformat(),
            "reason": "Volunteer participated in debrief discussion after event.",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert corr_res.status_code == 200, corr_res.text
    assert corr_res.json()["duration_minutes"] == 90

    # Verify compensating transaction in point ledger
    comp_tx_stmt = select(PointTransaction).where(
        PointTransaction.event_id == event.id,
        PointTransaction.transaction_type == "COMPENSATION_REVERSAL",
    )
    comp_tx = (await async_db.execute(comp_tx_stmt)).scalar_one()
    assert comp_tx.related_transaction_id == orig_tx.id
    assert comp_tx.event_points == Decimal("0.00")  # Already qualified
    assert comp_tx.hour_points == Decimal("1.00")  # +0.50 hrs * 2 = +1.00
    assert comp_tx.total_points == Decimal("1.00")
    assert comp_tx.hours_credited == Decimal("0.50")

    # Total net points for volunteer across both rows = 12.00 + 1.00 = 13.00
    net_stmt = select(func.sum(PointTransaction.total_points)).where(
        PointTransaction.volunteer_profile_id == vol.id
    )
    net_pts = (await async_db.execute(net_stmt)).scalar_one()
    assert net_pts == Decimal("13.00")
