"""End-to-End concurrency test for event capacity invariants and race condition resilience."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import TestingSessionLocal
from src.core.database import get_db
from src.core.security import create_access_token, get_password_hash
from src.main import app
from src.models.events import Event, EventRegistration
from src.models.users import User
from src.models.volunteers import VolunteerProfile


@pytest.mark.asyncio
async def test_concurrent_registration_capacity_invariants(client: AsyncClient, async_db: AsyncSession):
    """Scenario C: 20 concurrent volunteer registrations on an event with capacity=5.
    
    Verifies that:
    1. Pessimistic row locking on the Event model serializes registration transactions safely.
    2. Exactly 5 registrations receive 'SUBSCRIBED' status.
    3. Exactly 15 registrations receive 'WAITLISTED' status.
    4. Duplicate concurrent or sequential registration by the same volunteer is idempotent (returns existing status without duplicating rows).
    5. No deadlock exceptions occur.
    """
    now = datetime.now(UTC)

    # 1. Setup Admin user
    admin = User(
        email=f"admin_conc_{uuid.uuid4().hex[:6]}@maatram.org",
        password_hash=get_password_hash("Password123!"),
        role="ADMIN",
        status="APPROVED",
    )
    async_db.add(admin)
    await async_db.flush()

    # 2. Setup Event with capacity_required = 5
    event_obj = Event(
        title="Concurrent Admissions Screening",
        description="High demand volunteer event",
        category="ADMISSIONS",
        mode="OFFLINE",
        location="Loyola College Campus, Chennai",
        start_time=now + timedelta(hours=2),
        end_time=now + timedelta(hours=6),
        registration_deadline=now + timedelta(hours=1),
        capacity_required=5,
        status="PUBLISHED",
        created_by_user_id=admin.id,
    )
    async_db.add(event_obj)
    await async_db.flush()
    event_id = event_obj.id

    # 3. Seed 20 APPROVED volunteers with profiles and active tokens
    volunteer_tokens: list[str] = []
    total_volunteers = 20

    for i in range(total_volunteers):
        u_email = f"conc_vol_{i}_{uuid.uuid4().hex[:4]}@example.com"
        u_pass = "Password123!"
        u = User(
            email=u_email,
            password_hash=get_password_hash(u_pass),
            role="VOLUNTEER",
            status="APPROVED",
        )
        async_db.add(u)
        await async_db.flush()

        vp = VolunteerProfile(
            user_id=u.id,
            first_name=f"Vol{i}",
            last_name="Concurrent",
            mobile_number=f"+9198{i:08d}",
            gender="MALE",
            age=21,
            category="STUDENT",
        )
        async_db.add(vp)
        await async_db.flush()
        await async_db.commit()

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": u_email, "password": u_pass, "client_type": "WEB"},
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        volunteer_tokens.append(login_res.json()["access_token"])

    # 4. Fire 20 concurrent registration HTTP requests
    transport = ASGITransport(app=app)

    async def register_single(token: str) -> dict:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            res = await ac.post(
                f"/api/v1/events/{event_id}/register",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert res.status_code == 201, f"Registration failed with status {res.status_code}: {res.text}"
            return res.json()

    # Execute all 20 simultaneously
    responses = await asyncio.gather(*[register_single(tok) for tok in volunteer_tokens])

    # 5. Verify Capacity Invariants
    statuses = [r["status"] for r in responses]
    subscribed_count = statuses.count("SUBSCRIBED")
    waitlisted_count = statuses.count("WAITLISTED")

    assert subscribed_count == 5, f"Expected exactly 5 SUBSCRIBED, got {subscribed_count}"
    assert waitlisted_count == 15, f"Expected exactly 15 WAITLISTED, got {waitlisted_count}"

    # Verify directly in database
    db_stmt = select(EventRegistration).where(EventRegistration.event_id == event_id)
    db_records = (await async_db.execute(db_stmt)).scalars().all()
    assert len(db_records) == 20

    db_subscribed = sum(1 for r in db_records if r.status == "SUBSCRIBED")
    db_waitlisted = sum(1 for r in db_records if r.status == "WAITLISTED")
    assert db_subscribed == 5
    assert db_waitlisted == 15

    # 6. Verify Idempotent Duplicate Registration
    # Volunteer 0 (who is SUBSCRIBED) registers again
    dup_token_0 = volunteer_tokens[0]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        dup_res = await ac.post(
            f"/api/v1/events/{event_id}/register",
            headers={"Authorization": f"Bearer {dup_token_0}"},
        )
        assert dup_res.status_code == 201 or dup_res.status_code == 200
        dup_data = dup_res.json()
        assert dup_data["status"] == responses[0]["status"]

    # Verify no extra record was created in database
    db_records_after = (await async_db.execute(db_stmt)).scalars().all()
    assert len(db_records_after) == 20
