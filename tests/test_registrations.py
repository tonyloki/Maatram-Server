"""Comprehensive unit and integration test suite for Event Registrations & Volunteer Selection (Phase 7)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.events import Event, RegistrationHistory
from src.models.users import User
from src.models.volunteers import VolunteerProfile


async def create_user(
    async_db: AsyncSession,
    role: str = "VOLUNTEER",
    status: str = "APPROVED",
    email: str | None = None,
) -> User:
    """Helper to seed user and associated volunteer profile."""
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

    if role == "VOLUNTEER":
        profile = VolunteerProfile(
            user_id=user.id,
            first_name="Volunteer",
            last_name="Test",
            mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
            age=24,
            gender="MALE",
            category="CORPORATE",
        )
        async_db.add(profile)

    await async_db.commit()
    await async_db.refresh(user)
    return user


async def get_auth_token(client: AsyncClient, email: str, password: str = "Password123!") -> str:
    """Helper to authenticate and obtain JWT access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]  # type: ignore[no-any-return]


async def seed_published_event(
    async_db: AsyncSession,
    admin_user: User,
    capacity: int = 10,
    deadline_offset_days: int = 5,
    start_offset_days: int = 10,
) -> Event:
    """Helper to seed an event in PUBLISHED status."""
    now = datetime.now(UTC)
    start_dt = now + timedelta(days=start_offset_days)
    end_dt = start_dt + timedelta(hours=4)
    deadline_dt = now + timedelta(days=deadline_offset_days)

    event = Event(
        title="Scholarship Interview Panel",
        description="Interviewing shortlisted candidates.",
        category="PANEL_INTERVIEW",
        mode="OFFLINE",
        location="IIT Madras Research Park, Chennai",
        start_time=start_dt,
        end_time=end_dt,
        timezone="Asia/Kolkata",
        capacity_required=capacity,
        registration_deadline=deadline_dt,
        status="PUBLISHED",
        created_by_user_id=admin_user.id,
    )
    async_db.add(event)
    await async_db.commit()
    await async_db.refresh(event)
    return event


@pytest.mark.asyncio
async def test_approved_volunteer_can_register_for_published_event(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify approved volunteer can register for an open published event (SUBSCRIBED)."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin, capacity=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    token = await get_auth_token(client, volunteer.email)

    res = await client.post(
        f"/api/v1/events/{event.id}/register",
        json={"notes": "Available full day."},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "SUBSCRIBED"
    assert data["event_id"] == str(event.id)
    assert data["notes"] == "Available full day."


@pytest.mark.asyncio
async def test_unapproved_volunteer_cannot_register(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify volunteer with status PENDING_APPROVAL is rejected."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin)

    vol = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    token = await get_auth_token(client, vol.email)

    # Simulate volunteer not yet approved or revoked to PENDING_APPROVAL
    vol.status = "PENDING_APPROVAL"
    await async_db.commit()

    res = await client.post(
        f"/api/v1/events/{event.id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VOLUNTEER_NOT_APPROVED"


@pytest.mark.asyncio
async def test_registration_after_deadline_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify registration attempt after registration_deadline has passed is rejected."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    # Event with registration deadline in the past
    event = await seed_published_event(
        async_db, admin, deadline_offset_days=-1, start_offset_days=2
    )

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    token = await get_auth_token(client, volunteer.email)

    res = await client.post(
        f"/api/v1/events/{event.id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "DEADLINE_EXPIRED"


@pytest.mark.asyncio
async def test_registration_for_draft_event_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify registration for a DRAFT event is rejected."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    now = datetime.now(UTC)
    draft_event = Event(
        title="Draft Event",
        description="Not ready yet.",
        category="BGV",
        mode="OFFLINE",
        location="Madurai",
        start_time=now + timedelta(days=10),
        end_time=now + timedelta(days=10, hours=3),
        timezone="Asia/Kolkata",
        capacity_required=10,
        registration_deadline=now + timedelta(days=5),
        status="DRAFT",
        created_by_user_id=admin.id,
    )
    async_db.add(draft_event)
    await async_db.commit()

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    token = await get_auth_token(client, volunteer.email)

    res = await client.post(
        f"/api/v1/events/{draft_event.id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "EVENT_NOT_PUBLISHED"


@pytest.mark.asyncio
async def test_registration_for_cancelled_event_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify registration for a CANCELLED event is rejected."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    now = datetime.now(UTC)
    cancelled_event = Event(
        title="Cancelled Event",
        description="Cancelled due to rain.",
        category="BGV",
        mode="OFFLINE",
        location="Madurai",
        start_time=now + timedelta(days=10),
        end_time=now + timedelta(days=10, hours=3),
        timezone="Asia/Kolkata",
        capacity_required=10,
        registration_deadline=now + timedelta(days=5),
        status="CANCELLED",
        created_by_user_id=admin.id,
    )
    async_db.add(cancelled_event)
    await async_db.commit()

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    token = await get_auth_token(client, volunteer.email)

    res = await client.post(
        f"/api/v1/events/{cancelled_event.id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "REGISTRATION_CLOSED"


@pytest.mark.asyncio
async def test_duplicate_registration_is_idempotent(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify repeated registration returns existing record idempotently without error."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin, capacity=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    token = await get_auth_token(client, volunteer.email)

    # First registration
    res1 = await client.post(
        f"/api/v1/events/{event.id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 201
    reg1_id = res1.json()["id"]

    # Second registration
    res2 = await client.post(
        f"/api/v1/events/{event.id}/register",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 201
    assert res2.json()["id"] == reg1_id


@pytest.mark.asyncio
async def test_admin_can_select_volunteers(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify admin can transition subscribed volunteers to SELECTED."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)
    event = await seed_published_event(async_db, admin, capacity=5)

    v1 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    v2 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")

    t1 = await get_auth_token(client, v1.email)
    t2 = await get_auth_token(client, v2.email)

    r1 = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t1}"}
    )
    r2 = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t2}"}
    )

    reg1_id = r1.json()["id"]
    reg2_id = r2.json()["id"]

    # Admin batch selection
    sel_res = await client.post(
        f"/api/v1/events/{event.id}/select",
        json={"registration_ids": [reg1_id, reg2_id]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert sel_res.status_code == 200
    data = sel_res.json()
    assert data["selected_count"] == 2
    assert all(r["status"] == "SELECTED" for r in data["registrations"])
    assert all(r["selected_at"] is not None for r in data["registrations"])


@pytest.mark.asyncio
async def test_admin_can_mark_not_selected(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify admin can mark a subscribed volunteer NOT_SELECTED."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)
    event = await seed_published_event(async_db, admin, capacity=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    reg_res = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {vol_token}"}
    )
    reg_id = reg_res.json()["id"]

    not_sel_res = await client.post(
        f"/api/v1/events/{event.id}/registrations/{reg_id}/not-selected",
        json={"reason": "Profile did not match panel requirement."},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert not_sel_res.status_code == 200
    assert not_sel_res.json()["status"] == "NOT_SELECTED"


@pytest.mark.asyncio
async def test_volunteer_cannot_select_themselves(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify volunteers cannot select themselves (403 Forbidden)."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin, capacity=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    reg_res = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {vol_token}"}
    )
    reg_id = reg_res.json()["id"]

    sel_res = await client.post(
        f"/api/v1/events/{event.id}/registrations/{reg_id}/select",
        headers={"Authorization": f"Bearer {vol_token}"},
    )
    assert sel_res.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_promote_from_waitlist(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify admin can manually promote a WAITLISTED volunteer to SELECTED."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)
    # Event with capacity 1
    event = await seed_published_event(async_db, admin, capacity=1)

    v1 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    v2 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")

    t1 = await get_auth_token(client, v1.email)
    t2 = await get_auth_token(client, v2.email)

    r1 = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t1}"}
    )
    r2 = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t2}"}
    )

    assert r1.json()["status"] == "SUBSCRIBED"
    assert r2.json()["status"] == "WAITLISTED"
    reg2_id = r2.json()["id"]

    # First volunteer withdraws, opening capacity
    await client.post(
        f"/api/v1/events/{event.id}/withdraw", headers={"Authorization": f"Bearer {t1}"}
    )

    # Admin promotes v2
    promote_res = await client.post(
        f"/api/v1/events/{event.id}/waitlist/{reg2_id}/promote",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert promote_res.status_code == 200
    assert promote_res.json()["status"] == "SELECTED"


@pytest.mark.asyncio
async def test_volunteer_can_withdraw_registration(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify volunteer can withdraw own registration prior to withdrawal deadline."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin, capacity=5, start_offset_days=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    token = await get_auth_token(client, volunteer.email)

    reg_res = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {token}"}
    )
    reg_id = reg_res.json()["id"]

    withdraw_res = await client.post(
        f"/api/v1/registrations/{reg_id}/withdraw",
        json={"reason": "Emergency travel."},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert withdraw_res.status_code == 200
    assert withdraw_res.json()["status"] == "WITHDRAWN"
    assert withdraw_res.json()["withdrawn_at"] is not None


@pytest.mark.asyncio
async def test_admin_decline_registration(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify admin can decline an event registration."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)
    event = await seed_published_event(async_db, admin, capacity=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    reg_res = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {vol_token}"}
    )
    reg_id = reg_res.json()["id"]

    dec_res = await client.post(
        f"/api/v1/registrations/{reg_id}/decline",
        json={"reason": "Candidate unable to reach venue on time."},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["status"] == "DECLINED"


@pytest.mark.asyncio
async def test_registration_history_preserved_on_status_change(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify registration_history records every status change."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)
    event = await seed_published_event(async_db, admin, capacity=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    reg_res = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {vol_token}"}
    )
    reg_id = reg_res.json()["id"]

    # Admin selects
    await client.post(
        f"/api/v1/events/{event.id}/select",
        json={"registration_ids": [reg_id]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Inspect history table directly
    stmt = (
        select(RegistrationHistory)
        .where(RegistrationHistory.registration_id == uuid.UUID(reg_id))
        .order_by(RegistrationHistory.created_at.asc())
    )
    hist_res = await async_db.execute(stmt)
    entries = hist_res.scalars().all()

    assert len(entries) >= 2
    assert entries[0].new_status == "SUBSCRIBED"
    assert entries[1].old_status == "SUBSCRIBED"
    assert entries[1].new_status == "SELECTED"


@pytest.mark.asyncio
async def test_registration_history_preserved_on_withdrawal(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify registration_history records withdrawal action."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin, capacity=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    reg_res = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {vol_token}"}
    )
    reg_id = reg_res.json()["id"]

    await client.post(
        f"/api/v1/registrations/{reg_id}/withdraw",
        json={"reason": "Schedule clash."},
        headers={"Authorization": f"Bearer {vol_token}"},
    )

    stmt = (
        select(RegistrationHistory)
        .where(RegistrationHistory.registration_id == uuid.UUID(reg_id))
        .where(RegistrationHistory.new_status == "WITHDRAWN")
    )
    hist_res = await async_db.execute(stmt)
    withdrawn_entry = hist_res.scalar_one_or_none()

    assert withdrawn_entry is not None
    assert withdrawn_entry.old_status == "SUBSCRIBED"
    assert withdrawn_entry.reason == "Schedule clash."


@pytest.mark.asyncio
async def test_beyond_capacity_registration_goes_to_waitlist(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify registrations beyond capacity are automatically placed in WAITLISTED status."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin, capacity=2)

    v1 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    v2 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    v3 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")

    t1 = await get_auth_token(client, v1.email)
    t2 = await get_auth_token(client, v2.email)
    t3 = await get_auth_token(client, v3.email)

    r1 = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t1}"}
    )
    r2 = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t2}"}
    )
    r3 = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t3}"}
    )

    assert r1.json()["status"] == "SUBSCRIBED"
    assert r2.json()["status"] == "SUBSCRIBED"
    assert r3.json()["status"] == "WAITLISTED"


@pytest.mark.asyncio
async def test_admin_view_event_registrations(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify admin can list all registrations for an event."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)
    event = await seed_published_event(async_db, admin, capacity=5)

    v1 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    t1 = await get_auth_token(client, v1.email)
    await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t1}"}
    )

    list_res = await client.get(
        f"/api/v1/events/{event.id}/registrations",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] == 1
    assert data["items"][0]["volunteer"]["first_name"] == "Volunteer"


@pytest.mark.asyncio
async def test_volunteer_view_own_registrations(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify volunteer can view their own registration history via /registrations/me and /volunteers/me/registrations."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin, capacity=5)

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    token = await get_auth_token(client, volunteer.email)

    await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {token}"}
    )

    # Test /registrations/me
    res_reg_me = await client.get(
        "/api/v1/registrations/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_reg_me.status_code == 200
    assert res_reg_me.json()["total"] == 1

    # Test /volunteers/me/registrations
    res_vol_me = await client.get(
        "/api/v1/volunteers/me/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_vol_me.status_code == 200
    assert res_vol_me.json()["total"] == 1


@pytest.mark.asyncio
async def test_unauthorized_access_to_other_volunteer_registration_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify BOLA authorization prevents volunteer A from viewing volunteer B's registration."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    event = await seed_published_event(async_db, admin, capacity=5)

    v1 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    v2 = await create_user(async_db, role="VOLUNTEER", status="APPROVED")

    t1 = await get_auth_token(client, v1.email)
    t2 = await get_auth_token(client, v2.email)

    reg_res = await client.post(
        f"/api/v1/events/{event.id}/register", headers={"Authorization": f"Bearer {t1}"}
    )
    reg_id = reg_res.json()["id"]

    # v2 tries to inspect v1's registration
    sneak_res = await client.get(
        f"/api/v1/registrations/{reg_id}",
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert sneak_res.status_code == 403
