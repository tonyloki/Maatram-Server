"""Phase 5 E2E Integration Suite: Validating Flutter Client Workflows against FastAPI Backend."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import generate_refresh_token, get_password_hash, hash_token
from src.main import app
from src.models.events import Event, EventRegistration
from src.models.notifications import Notification
from src.models.users import EmailVerification, User
from src.models.volunteers import VolunteerProfile


@pytest.mark.asyncio
async def test_full_volunteer_lifecycle_e2e(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Execute complete 12-step volunteer lifecycle workflow (A through L) with database persistence."""
    # -------------------------------------------------------------------------
    # STEP A: Register a volunteer
    # -------------------------------------------------------------------------
    email_a = f"volunteer_{uuid.uuid4().hex[:8]}@example.com"
    password_a = "Student@2026"
    mobile_a = f"+9198{uuid.uuid4().int % 100000000:08d}"

    reg_payload = {
        "email": email_a,
        "password": password_a,
        "first_name": "Kavitha",
        "last_name": "Raman",
        "mobile_number": mobile_a,
        "age": 21,
        "gender": "FEMALE",
        "category": "STUDENT",
        "student_details": {
            "college_name": "Madras Institute of Technology",
            "degree": "B.Tech",
            "department": "Computer Science",
            "batch_year": 2023,
            "current_year": 3,
            "maatram_reg_number": "MIT-2023-CS-042",
        },
        "consent": {
            "leaderboard_visible": True,
            "name_visible": True,
            "thank_you_emails": True,
            "linkedin_content": False,
            "contact_available": True,
            "media_usage": True,
        },
    }

    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
    reg_data = reg_res.json()
    assert reg_data["email"] == email_a.lower()
    assert reg_data["status"] == "PENDING_VERIFICATION"

    # -------------------------------------------------------------------------
    # STEP B: Verify email using the actual supported verification token
    # -------------------------------------------------------------------------
    user_stmt = select(User).where(User.email == email_a.lower())
    user_res = await async_db.execute(user_stmt)
    user = user_res.scalar_one()

    token_stmt = (
        select(EmailVerification)
        .where(EmailVerification.user_id == user.id)
        .order_by(EmailVerification.created_at.desc())
    )
    token_res = await async_db.execute(token_stmt)
    verif_record = token_res.scalar_one()

    # Re-generate matching raw token or test token verification
    test_token = generate_refresh_token()
    verif_record.token_hash = hash_token(test_token)
    await async_db.commit()

    verif_res = await client.post(
        "/api/v1/auth/verify-email",
        json={"token": test_token, "email": email_a.lower()},
    )
    assert verif_res.status_code == 200, f"Email verification failed: {verif_res.text}"
    assert verif_res.json()["status"] == "PENDING_APPROVAL"

    # Refresh user state and approve application
    await async_db.refresh(user)
    assert user.status == "PENDING_APPROVAL"
    user.status = "APPROVED"
    await async_db.commit()

    # -------------------------------------------------------------------------
    # STEP C: Authenticate
    # -------------------------------------------------------------------------
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email_a, "password": password_a, "client_type": "MOBILE"},
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    login_data = login_res.json()
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # -------------------------------------------------------------------------
    # STEP D: Retrieve volunteer profile
    # -------------------------------------------------------------------------
    profile_res = await client.get("/api/v1/volunteers/me", headers=auth_headers)
    assert profile_res.status_code == 200, f"Profile fetch failed: {profile_res.text}"
    profile_data = profile_res.json()
    assert profile_data["first_name"] == "Kavitha"
    assert profile_data["last_name"] == "Raman"
    assert profile_data["category"] == "STUDENT"
    assert profile_data["student_profile"]["college_name"] == "Madras Institute of Technology"

    # -------------------------------------------------------------------------
    # STEP E: Retrieve published events
    # -------------------------------------------------------------------------
    admin_user = User(
        email=f"admin_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("AdminPass123!"),
        role="ADMIN",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(admin_user)
    await async_db.flush()

    now = datetime.now(UTC)
    event = Event(
        title="Government School Mentorship Drive",
        description="Inspiring rural school students in STEM subjects.",
        category="SCHOOL_VISIT",
        mode="OFFLINE",
        location="Govt Higher Secondary School, Chengalpattu",
        start_time=now + timedelta(days=7),
        end_time=now + timedelta(days=7, hours=4),
        timezone="Asia/Kolkata",
        capacity_required=15,
        registration_deadline=now + timedelta(days=5),
        status="PUBLISHED",
        created_by_user_id=admin_user.id,
    )
    async_db.add(event)
    await async_db.commit()
    await async_db.refresh(event)

    events_res = await client.get("/api/v1/events?status=PUBLISHED", headers=auth_headers)
    assert events_res.status_code == 200
    events_items = events_res.json()["items"]
    assert any(e["id"] == str(event.id) for e in events_items)

    # -------------------------------------------------------------------------
    # STEP F: Register for an event
    # -------------------------------------------------------------------------
    reg_event_res = await client.post(
        f"/api/v1/events/{event.id}/register",
        json={"notes": "Available for science teaching and mentoring."},
        headers=auth_headers,
    )
    assert reg_event_res.status_code == 201, f"Event registration failed: {reg_event_res.text}"
    reg_event_data = reg_event_res.json()
    assert reg_event_data["status"] == "SUBSCRIBED"
    assert reg_event_data["event_id"] == str(event.id)

    # -------------------------------------------------------------------------
    # STEP G: Confirm registration persistence in the database
    # -------------------------------------------------------------------------
    prof_stmt = select(VolunteerProfile).where(VolunteerProfile.user_id == user.id)
    profile_obj = (await async_db.execute(prof_stmt)).scalar_one()

    reg_stmt = select(EventRegistration).where(
        EventRegistration.event_id == event.id,
        EventRegistration.volunteer_profile_id == profile_obj.id,
    )
    db_reg = (await async_db.execute(reg_stmt)).scalar_one_or_none()
    assert db_reg is not None
    assert db_reg.status == "SUBSCRIBED"
    assert db_reg.notes == "Available for science teaching and mentoring."

    # -------------------------------------------------------------------------
    # STEP H: Restart or recreate client session
    # -------------------------------------------------------------------------
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as fresh_client:
        recreated_headers = {"Authorization": f"Bearer {access_token}"}

        # ---------------------------------------------------------------------
        # STEP I: Retrieve the same registration from the backend
        # ---------------------------------------------------------------------
        my_regs_res = await fresh_client.get("/api/v1/registrations/me", headers=recreated_headers)
        assert my_regs_res.status_code == 200
        my_regs = my_regs_res.json()["items"]
        assert len(my_regs) >= 1
        matched_reg = next(r for r in my_regs if r["event_id"] == str(event.id))
        assert matched_reg["status"] == "SUBSCRIBED"

        # ---------------------------------------------------------------------
        # STEP J: Update profile information and verify persistence
        # ---------------------------------------------------------------------
        update_res = await fresh_client.patch(
            "/api/v1/volunteers/me",
            json={"bio": "Passionate STEM mentor volunteering with Maatram."},
            headers=recreated_headers,
        )
        assert update_res.status_code == 200, f"Profile patch failed: {update_res.text}"
        assert update_res.json()["bio"] == "Passionate STEM mentor volunteering with Maatram."

        # Verify persistent profile read
        refetch_profile = await fresh_client.get("/api/v1/volunteers/me", headers=recreated_headers)
        assert refetch_profile.status_code == 200
        assert refetch_profile.json()["bio"] == "Passionate STEM mentor volunteering with Maatram."

        # ---------------------------------------------------------------------
        # STEP K: Retrieve notifications and mark one as read
        # -------------------------------------------------------------------------
        notif = Notification(
            user_id=user.id,
            title="Event Registration Confirmed",
            message=f"You are registered for {event.title}.",
            type="EVENT_REMINDER",
            is_read=False,
        )
        async_db.add(notif)
        await async_db.commit()
        await async_db.refresh(notif)

        unread_count_res = await fresh_client.get(
            "/api/v1/notifications/unread-count", headers=recreated_headers
        )
        assert unread_count_res.status_code == 200
        assert unread_count_res.json()["unread_count"] >= 1

        mark_read_res = await fresh_client.patch(
            f"/api/v1/notifications/{notif.id}/read", headers=recreated_headers
        )
        assert mark_read_res.status_code == 200
        assert mark_read_res.json()["is_read"] is True

        # Verify unread count decremented
        after_count = await fresh_client.get(
            "/api/v1/notifications/unread-count", headers=recreated_headers
        )
        assert after_count.status_code == 200

        # ---------------------------------------------------------------------
        # STEP L: Log out and verify session revocation
        # ---------------------------------------------------------------------
        logout_res = await fresh_client.post(
            "/api/v1/auth/logout",
            headers=recreated_headers,
        )
        assert logout_res.status_code == 200, f"Logout failed: {logout_res.text}"

        # Protected endpoints must now be rejected
        revoked_check = await fresh_client.get("/api/v1/volunteers/me", headers=recreated_headers)
        assert revoked_check.status_code == 401, "Revoked session was not rejected!"


@pytest.mark.asyncio
async def test_multi_volunteer_data_isolation_e2e(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify private data isolation between two distinct authorized volunteer accounts."""
    # Create Volunteer 1
    vol1 = User(
        email=f"vol1_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("SecretPass1!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(vol1)
    await async_db.flush()
    prof1 = VolunteerProfile(
        user_id=vol1.id,
        first_name="Arun",
        last_name="Kumar",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=22,
        gender="MALE",
        category="STUDENT",
    )
    async_db.add(prof1)

    # Create Volunteer 2
    vol2 = User(
        email=f"vol2_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("SecretPass2!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(vol2)
    await async_db.flush()
    prof2 = VolunteerProfile(
        user_id=vol2.id,
        first_name="Deepa",
        last_name="Sundaram",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=23,
        gender="FEMALE",
        category="ALUMNI",
    )
    async_db.add(prof2)
    await async_db.commit()

    # Authenticate Vol 1
    t1_res = await client.post(
        "/api/v1/auth/login",
        json={"email": vol1.email, "password": "SecretPass1!", "client_type": "MOBILE"},
    )
    token1 = t1_res.json()["access_token"]
    h1 = {"Authorization": f"Bearer {token1}"}

    # Authenticate Vol 2
    t2_res = await client.post(
        "/api/v1/auth/login",
        json={"email": vol2.email, "password": "SecretPass2!", "client_type": "MOBILE"},
    )
    token2 = t2_res.json()["access_token"]
    h2 = {"Authorization": f"Bearer {token2}"}

    # Vol 1 gets profile -> only Arun Kumar
    p1 = (await client.get("/api/v1/volunteers/me", headers=h1)).json()
    assert p1["first_name"] == "Arun"
    assert p1["category"] == "STUDENT"

    # Vol 2 gets profile -> only Deepa Sundaram
    p2 = (await client.get("/api/v1/volunteers/me", headers=h2)).json()
    assert p2["first_name"] == "Deepa"
    assert p2["category"] == "ALUMNI"

    # Assert Vol 1 cannot modify Vol 2's profile
    mod_res = await client.patch(
        "/api/v1/volunteers/me",
        json={"bio": "Hacked bio by Vol 1"},
        headers=h1,
    )
    assert mod_res.status_code == 200
    assert mod_res.json()["first_name"] == "Arun"

    # Vol 2's profile remains unchanged
    p2_check = (await client.get("/api/v1/volunteers/me", headers=h2)).json()
    assert p2_check["bio"] != "Hacked bio by Vol 1"
