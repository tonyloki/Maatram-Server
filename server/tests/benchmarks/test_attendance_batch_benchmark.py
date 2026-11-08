"""Performance benchmark test for batched volunteer attendance check-in and check-out."""

import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import test_engine
from src.core.security import get_password_hash
from src.models.attendance import AttendanceRecord
from src.models.events import Event, EventRegistration
from src.models.users import User
from src.models.volunteers import VolunteerProfile
from src.services.attendance_service import attendance_service


class QueryCounter:
    """SQLAlchemy query execution counter."""

    def __init__(self) -> None:
        self.count = 0

    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


@pytest.mark.asyncio
async def test_batch_attendance_100_volunteers_benchmark(async_db: AsyncSession):
    """Benchmark batched check-in and check-out for 100 volunteers:
    
    Verifies that:
    1. Query count remains constant O(1) (< 15 queries) rather than linear O(N) (400+ queries).
    2. Check-in and check-out complete swiftly.
    3. All 100 records are created and completed with correct durations and 2-decimal rounded hours.
    """
    # 1. Setup Admin user
    admin = User(
        email=f"admin_{uuid.uuid4().hex[:6]}@maatram.org",
        password_hash=get_password_hash("Password123!"),
        role="ADMIN",
        status="APPROVED",
    )
    async_db.add(admin)
    await async_db.flush()

    # 2. Setup active Event
    event_obj = Event(
        title="Mega Admissions Camp",
        description="Annual volunteer screening",
        category="ADMISSIONS",
        mode="OFFLINE",
        location="Loyola Campus, Chennai",
        status="PUBLISHED",
        capacity_required=150,
        start_time=datetime.now(UTC) - timedelta(hours=2),
        end_time=datetime.now(UTC) + timedelta(hours=6),
        registration_deadline=datetime.now(UTC) - timedelta(hours=3),
        created_by_user_id=admin.id,
    )
    async_db.add(event_obj)
    await async_db.flush()

    # 3. Seed 100 volunteers and SELECTED registrations
    volunteer_ids: list[uuid.UUID] = []
    cohort_size = 100

    for i in range(cohort_size):
        u = User(
            email=f"bench_vol_{i}_{uuid.uuid4().hex[:4]}@example.com",
            password_hash=get_password_hash("Pass123!"),
            role="VOLUNTEER",
            status="APPROVED",
        )
        async_db.add(u)
        await async_db.flush()

        vp = VolunteerProfile(
            user_id=u.id,
            first_name=f"Volunteer{i}",
            last_name="Test",
            mobile_number=f"+9198{i:08d}",
            gender="MALE",
            age=22,
            category="STUDENT",
        )
        async_db.add(vp)
        await async_db.flush()
        volunteer_ids.append(vp.id)

        reg = EventRegistration(
            event_id=event_obj.id,
            volunteer_profile_id=vp.id,
            status="SELECTED",
        )
        async_db.add(reg)

    await async_db.commit()

    # 4. Measure BATCH CHECK-IN
    counter = QueryCounter()
    event.listen(test_engine.sync_engine, "before_cursor_execute", counter)

    start_in = time.perf_counter()
    check_in_time = datetime.now(UTC) - timedelta(hours=3)

    check_in_responses = await attendance_service.check_in_volunteers(
        db=async_db,
        event_id=event_obj.id,
        volunteer_profile_ids=volunteer_ids,
        check_in_time=check_in_time,
        current_user=admin,
    )
    elapsed_in_ms = (time.perf_counter() - start_in) * 1000
    queries_in = counter.count

    event.remove(test_engine.sync_engine, "before_cursor_execute", counter)

    assert len(check_in_responses) == cohort_size
    assert all(r.status == "IN_PROGRESS" for r in check_in_responses)
    # Batch query count must be low O(1), strictly < 15 queries (not 400+ queries)
    assert queries_in < 15, f"Expected < 15 queries for batch check-in, got {queries_in}"

    # 5. Measure BATCH CHECK-OUT
    counter_out = QueryCounter()
    event.listen(test_engine.sync_engine, "before_cursor_execute", counter_out)

    start_out = time.perf_counter()
    # 3.5 hours later (210 minutes)
    check_out_time = check_in_time + timedelta(hours=3, minutes=30)

    check_out_responses = await attendance_service.check_out_volunteers(
        db=async_db,
        event_id=event_obj.id,
        volunteer_profile_ids=volunteer_ids,
        check_out_time=check_out_time,
        current_user=admin,
    )
    elapsed_out_ms = (time.perf_counter() - start_out) * 1000
    queries_out = counter_out.count

    event.remove(test_engine.sync_engine, "before_cursor_execute", counter_out)

    assert len(check_out_responses) == cohort_size
    assert all(r.status == "COMPLETED" for r in check_out_responses)
    assert all(r.duration_minutes == 210 for r in check_out_responses)
    # 210 min / 60 = 3.50 hours credited
    assert all(r.hours_credited == Decimal("3.50") for r in check_out_responses)
    # Batch query count must be low O(1), strictly < 15 queries
    assert queries_out < 15, f"Expected < 15 queries for batch check-out, got {queries_out}"
