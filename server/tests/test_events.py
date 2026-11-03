"""Comprehensive unit and integration test suite for Event Management Lifecycle (Phase 6)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.users import User
from src.models.volunteers import VolunteerProfile


async def create_user(
    async_db: AsyncSession,
    role: str = "VOLUNTEER",
    status: str = "APPROVED",
    email: str | None = None,
) -> User:
    """Helper to seed user record with specific role and status."""
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
            first_name="Test",
            last_name="Volunteer",
            mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
            age=25,
            gender="FEMALE",
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


def build_event_payload(
    category: str = "PANEL_INTERVIEW",
    mode: str = "OFFLINE",
    location: str | None = "Loyola College Campus, Chennai",
    online_meeting_url: str | None = None,
    capacity: int = 15,
    start_delta_days: int = 10,
    duration_hours: int = 4,
    deadline_delta_days: int = 5,
) -> dict[str, object]:
    """Helper to generate valid event creation payload."""
    now = datetime.now(UTC)
    start_dt = now + timedelta(days=start_delta_days)
    end_dt = start_dt + timedelta(hours=duration_hours)
    deadline_dt = now + timedelta(days=deadline_delta_days)

    payload: dict[str, object] = {
        "title": "Annual Admissions Interview",
        "description": "Comprehensive scholarship panel evaluations.",
        "category": category,
        "mode": mode,
        "location": location,
        "online_meeting_url": online_meeting_url,
        "volunteer_capacity": capacity,
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "registration_deadline": deadline_dt.isoformat(),
        "timezone": "Asia/Kolkata",
    }
    return payload


@pytest.mark.asyncio
async def test_admin_can_create_event(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify administrator can create an event in DRAFT status."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    token = await get_auth_token(client, admin.email)

    payload = build_event_payload()
    res = await client.post(
        "/api/v1/events",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "DRAFT"
    assert data["title"] == payload["title"]
    assert data["capacity_required"] == 15
    assert data["volunteer_capacity"] == 15


@pytest.mark.asyncio
async def test_event_creation_requires_location_for_offline(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify OFFLINE event creation fails if location is missing or empty."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    token = await get_auth_token(client, admin.email)

    payload = build_event_payload(mode="OFFLINE", location="")
    res = await client.post(
        "/api/v1/events",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_event_creation_requires_meeting_url_for_online(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify ONLINE event creation fails if both location and meeting URL are empty."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    token = await get_auth_token(client, admin.email)

    payload = build_event_payload(mode="ONLINE", location=None, online_meeting_url=None)
    res = await client.post(
        "/api/v1/events",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_event_creation_invalid_category_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify invalid category string is rejected with validation error."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    token = await get_auth_token(client, admin.email)

    payload = build_event_payload(category="NON_EXISTENT_CATEGORY")
    res = await client.post(
        "/api/v1/events",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_event_time_validation_end_before_start_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify end_time prior to start_time is rejected."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    token = await get_auth_token(client, admin.email)

    now = datetime.now(UTC)
    payload = build_event_payload()
    payload["start_time"] = (now + timedelta(days=5)).isoformat()
    payload["end_time"] = (now + timedelta(days=4)).isoformat()

    res = await client.post(
        "/api/v1/events",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_event_registration_deadline_must_be_before_event_date(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify registration deadline after start_time is rejected."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    token = await get_auth_token(client, admin.email)

    now = datetime.now(UTC)
    payload = build_event_payload()
    payload["start_time"] = (now + timedelta(days=5)).isoformat()
    payload["end_time"] = (now + timedelta(days=5, hours=4)).isoformat()
    payload["registration_deadline"] = (now + timedelta(days=6)).isoformat()

    res = await client.post(
        "/api/v1/events",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_draft_event_not_visible_to_volunteers(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify non-admin volunteers receive 404 when querying a DRAFT event."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    event_id = res.json()["id"]

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    vol_res = await client.get(
        f"/api/v1/events/{event_id}",
        headers={"Authorization": f"Bearer {vol_token}"},
    )
    assert vol_res.status_code == 404


@pytest.mark.asyncio
async def test_publish_event_transitions_status(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify admin can publish a DRAFT event transitioning status to PUBLISHED."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    event_id = res.json()["id"]

    pub_res = await client.post(
        f"/api/v1/events/{event_id}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "PUBLISHED"


@pytest.mark.asyncio
async def test_publish_event_validates_required_fields(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify publish checks invariants and state machine rules."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    event_id = res.json()["id"]

    # Publish once
    pub_res = await client.post(
        f"/api/v1/events/{event_id}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert pub_res.status_code == 200

    # Attempting to re-publish an already PUBLISHED event raises invalid state transition
    repub_res = await client.post(
        f"/api/v1/events/{event_id}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert repub_res.status_code == 400
    assert repub_res.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


@pytest.mark.asyncio
async def test_cancel_event_requires_reason(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify cancelling an event requires a non-empty reason."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    event_id = res.json()["id"]

    # Publish first
    await client.post(
        f"/api/v1/events/{event_id}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Cancel without reason
    cancel_res = await client.post(
        f"/api/v1/events/{event_id}/cancel",
        json={"reason": ""},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert cancel_res.status_code == 400
    assert cancel_res.json()["error"]["code"] == "CANCELLATION_REASON_REQUIRED"

    # Cancel with valid reason
    cancel_ok = await client.post(
        f"/api/v1/events/{event_id}/cancel",
        json={"reason": "Inclement weather and venue waterlogging."},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert cancel_ok.status_code == 200
    assert cancel_ok.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_invalid_state_transition_rejected(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify invalid state machine transitions raise 400 with code INVALID_STATE_TRANSITION."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    event_id = res.json()["id"]

    # DRAFT -> COMPLETED is forbidden
    comp_res = await client.post(
        f"/api/v1/events/{event_id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert comp_res.status_code == 400
    assert comp_res.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


@pytest.mark.asyncio
async def test_volunteer_can_discover_published_events(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify volunteers only see PUBLISHED events in public discovery."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    # Create 1 DRAFT, 1 PUBLISHED
    draft_res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    pub_res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    pub_id = pub_res.json()["id"]
    await client.post(
        f"/api/v1/events/{pub_id}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    list_res = await client.get(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {vol_token}"},
    )
    assert list_res.status_code == 200
    items = list_res.json()["items"]
    # Only the published event should appear
    assert all(item["status"] == "PUBLISHED" for item in items)
    item_ids = [item["id"] for item in items]
    assert pub_id in item_ids
    assert draft_res.json()["id"] not in item_ids


@pytest.mark.asyncio
async def test_admin_can_list_all_statuses(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify administrator can retrieve events across all lifecycle statuses."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    draft_id = res.json()["id"]

    admin_list = await client.get(
        "/api/v1/events?status=DRAFT",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_list.status_code == 200
    items = admin_list.json()["items"]
    item_ids = [item["id"] for item in items]
    assert draft_id in item_ids


@pytest.mark.asyncio
async def test_event_filtering_by_category(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify events can be filtered by specific categories."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    res1 = await client.post(
        "/api/v1/events",
        json=build_event_payload(category="SCHOOL_VISIT"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        f"/api/v1/events/{res1.json()['id']}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    res2 = await client.post(
        "/api/v1/events",
        json=build_event_payload(category="MOCK_INTERVIEW"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        f"/api/v1/events/{res2.json()['id']}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    list_res = await client.get(
        "/api/v1/events?category=SCHOOL_VISIT",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_res.status_code == 200
    items = list_res.json()["items"]
    assert all(item["category"] == "SCHOOL_VISIT" for item in items)


@pytest.mark.asyncio
async def test_event_filtering_by_mode(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify events can be filtered by ONLINE or OFFLINE mode."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    res_off = await client.post(
        "/api/v1/events",
        json=build_event_payload(mode="OFFLINE", location="Auditorium"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        f"/api/v1/events/{res_off.json()['id']}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    res_on = await client.post(
        "/api/v1/events",
        json=build_event_payload(
            mode="ONLINE", online_meeting_url="https://meet.google.com/abc-xyz"
        ),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        f"/api/v1/events/{res_on.json()['id']}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    online_list = await client.get(
        "/api/v1/events?mode=ONLINE",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert online_list.status_code == 200
    items = online_list.json()["items"]
    assert all(item["mode"] == "ONLINE" for item in items)


@pytest.mark.asyncio
async def test_event_capacity_must_be_positive(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify event capacity < 1 is rejected."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    token = await get_auth_token(client, admin.email)

    payload = build_event_payload(capacity=0)
    res = await client.post(
        "/api/v1/events",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_volunteer_cannot_create_event(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify volunteers cannot create events (403 Forbidden)."""
    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {vol_token}"},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_completed_event_rejects_new_registrations(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify COMPLETED event rejects attempts to register volunteers."""
    admin = await create_user(async_db, role="ADMIN", status="APPROVED")
    admin_token = await get_auth_token(client, admin.email)

    # Create, publish, transition to ONGOING then COMPLETED
    res = await client.post(
        "/api/v1/events",
        json=build_event_payload(),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    event_id = res.json()["id"]

    await client.post(
        f"/api/v1/events/{event_id}/publish",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Transition PUBLISHED -> ONGOING
    from src.services.event_service import event_service

    await event_service.transition_status(
        db=async_db, event_id=uuid.UUID(event_id), new_status="ONGOING", current_user=admin
    )
    # Transition ONGOING -> COMPLETED
    await client.post(
        f"/api/v1/events/{event_id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Volunteer tries to register
    volunteer = await create_user(async_db, role="VOLUNTEER", status="APPROVED")
    vol_token = await get_auth_token(client, volunteer.email)

    reg_res = await client.post(
        f"/api/v1/events/{event_id}/register",
        headers={"Authorization": f"Bearer {vol_token}"},
    )
    assert reg_res.status_code == 400
    assert reg_res.json()["error"]["code"] == "REGISTRATION_CLOSED"
