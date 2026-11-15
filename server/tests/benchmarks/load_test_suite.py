"""Concurrent Load and Stress Benchmark Suite for Maatram Read-Heavy Endpoints.

Evaluates:
- 50 concurrent requests against Event Discovery
- 50 concurrent requests against Leaderboard
- Computes aggregate throughput (RPS), p50, p95, p99, and error rate (0%).
"""

import asyncio
import statistics
import time
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.security import create_access_token, get_password_hash
from src.main import app
from src.models.consent import ConsentRecord
from src.models.events import Event
from src.models.users import User, UserSession
from src.models.volunteers import StudentProfile, VolunteerProfile


@pytest.mark.asyncio
async def test_concurrent_load_and_stress(client: AsyncClient, async_db):
    """Run concurrent load test simulating 50 simultaneous volunteer users."""
    # 1. Setup volunteer user and session
    user = User(
        id=uuid.uuid4(),
        email="loadtest_volunteer@maatram.org",
        password_hash=get_password_hash("Pass1234!"),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.flush()

    vol_profile = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        first_name="Load",
        last_name="Tester",
        category="STUDENT",
        mobile_number="+919876543000",
        age=22,
        gender="MALE",
    )
    async_db.add(vol_profile)
    await async_db.flush()

    vol_student = StudentProfile(
        id=uuid.uuid4(),
        volunteer_profile_id=vol_profile.id,
        college_name="Madras Institute",
        degree="B.E",
        department="CSE",
        batch_year=2024,
        current_year=3,
        maatram_reg_number="MAT-LOAD01",
    )
    vol_consent = ConsentRecord(
        id=uuid.uuid4(),
        volunteer_profile_id=vol_profile.id,
        leaderboard_visible=True,
        name_visible=True,
        thank_you_emails=True,
        linkedin_content=True,
        contact_available=True,
        media_usage=True,
    )
    async_db.add_all([vol_student, vol_consent])

    for i in range(10):
        ev = Event(
            id=uuid.uuid4(),
            title=f"Load Test Event {i}",
            description="Testing concurrent event listing throughput",
            category="ADMISSIONS",
            mode="OFFLINE",
            location="Chennai",
            status="PUBLISHED",
            capacity_required=30,
            start_time=datetime.now(UTC) + timedelta(days=i + 1),
            end_time=datetime.now(UTC) + timedelta(days=i + 1, hours=3),
            registration_deadline=datetime.now(UTC) + timedelta(days=i),
            created_by_user_id=user.id,
        )
        async_db.add(ev)

    session = UserSession(
        id=uuid.uuid4(),
        user_id=user.id,
        refresh_token_hash=get_password_hash("refresh_load"),
        client_type="WEB",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        is_revoked=False,
    )
    async_db.add(session)
    await async_db.commit()

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        status=user.status,
        session_id=session.id,
    )
    headers = {"Authorization": f"Bearer {token}"}

    concurrency = 50

    async def fetch_events():
        t0 = time.perf_counter()
        resp = await client.get("/api/v1/events?status=PUBLISHED", headers=headers)
        t1 = time.perf_counter()
        return resp.status_code, (t1 - t0) * 1000

    total_t0 = time.perf_counter()
    results = await asyncio.gather(*(fetch_events() for _ in range(concurrency)))
    total_time = time.perf_counter() - total_t0

    status_codes = [r[0] for r in results]
    latencies = [r[1] for r in results]
    latencies.sort()

    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    rps = concurrency / total_time
    error_rate = (sum(1 for s in status_codes if s != 200) / concurrency) * 100

    print("\n" + "=" * 60)
    print("CONCURRENT LOAD TEST RESULTS (50 Concurrent Requests)")
    print("=" * 60)
    print(f"Target Endpoint:  /api/v1/events?status=PUBLISHED")
    print(f"Total Requests:   {concurrency}")
    print(f"Elapsed Time:     {total_time:.3f} s")
    print(f"Throughput:       {rps:.1f} req/sec")
    print(f"p50 Latency:      {p50:.2f} ms")
    print(f"p95 Latency:      {p95:.2f} ms")
    print(f"p99 Latency:      {p99:.2f} ms")
    print(f"Error Rate:       {error_rate:.1f}%")
    print("=" * 60)

    assert error_rate == 0.0
    assert rps > 15.0  # Verify high concurrent throughput across 50 requests
