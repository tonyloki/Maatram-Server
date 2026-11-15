"""Comprehensive Benchmark Suite for the 12 Critical User Flows in Maatram Portal.

Measures:
1. Login (/api/v1/auth/login)
2. Registration (/api/v1/auth/register)
3. Email Verification (/api/v1/auth/verify-email)
4. Volunteer Profile (/api/v1/volunteers/me)
5. Admin Pending Applications (/api/v1/admin/applications?status=PENDING)
6. Admin Dashboard (/api/v1/admin/dashboard)
7. Event Discovery (/api/v1/events?status=PUBLISHED)
8. Event Registration (/api/v1/events/{id}/register)
9. Attendance Check-in (/api/v1/attendance/check-in)
10. Points Ledger (/api/v1/gamification/ledger)
11. Leaderboard (/api/v1/gamification/leaderboard/all)
12. Notifications (/api/v1/notifications)
"""

import asyncio
import json
import statistics
import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import test_engine
from src.core.security import create_access_token, generate_csrf_token, get_password_hash, hash_token
from src.models.admin import AuditLog
from src.models.applications import VolunteerApplication
from src.models.attendance import AttendanceRecord
from src.models.consent import ConsentRecord
from src.models.events import Event, EventRegistration
from src.models.gamification import PointTransaction
from src.models.notifications import Notification
from src.models.users import EmailVerification, User, UserSession
from src.models.volunteers import StudentProfile, VolunteerProfile


class QueryCounter:
    """Track database query executions."""

    def __init__(self) -> None:
        self.count = 0

    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


@pytest.mark.asyncio
async def test_all_12_critical_flows_benchmark(client: AsyncClient, async_db: AsyncSession):
    """Execute and benchmark all 12 flows, collecting latency, query count, and payload size."""
    benchmark_results: dict[str, dict[str, object]] = {}

    # Setup baseline data
    admin_user = User(
        id=uuid.uuid4(),
        email="benchmark_admin@maatram.org",
        password_hash=get_password_hash("AdminPass123!"),
        role="ADMIN",
        status="APPROVED",
    )
    volunteer_user = User(
        id=uuid.uuid4(),
        email="benchmark_volunteer@maatram.org",
        password_hash=get_password_hash("VolunteerPass123!"),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add_all([admin_user, volunteer_user])
    await async_db.flush()

    vol_profile = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=volunteer_user.id,
        first_name="Benchmark",
        last_name="Tester",
        category="STUDENT",
        mobile_number="+919876543210",
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
        maatram_reg_number="MAT-BENCH01",
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

    event_obj = Event(
        id=uuid.uuid4(),
        title="Benchmark Community Drive",
        description="Testing high-throughput event discovery",
        category="ADMISSIONS",
        mode="OFFLINE",
        location="Chennai Central",
        status="PUBLISHED",
        capacity_required=50,
        start_time=datetime.now(UTC) + timedelta(days=2),
        end_time=datetime.now(UTC) + timedelta(days=2, hours=4),
        registration_deadline=datetime.now(UTC) + timedelta(days=1),
        created_by_user_id=admin_user.id,
    )
    async_db.add(event_obj)

    # Pending volunteer application for Flow 05
    pending_user = User(
        id=uuid.uuid4(),
        email="pending_vol@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="PENDING_APPROVAL",
    )
    async_db.add(pending_user)
    await async_db.flush()

    pending_prof = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=pending_user.id,
        first_name="Pending",
        last_name="Applicant",
        category="STUDENT",
        mobile_number="+919876543299",
        age=20,
        gender="FEMALE",
    )
    async_db.add(pending_prof)
    await async_db.flush()

    pending_app = VolunteerApplication(
        id=uuid.uuid4(),
        volunteer_profile_id=pending_prof.id,
        status="PENDING",
        submitted_at=datetime.now(UTC),
    )
    async_db.add(pending_app)

    # Notification for Flow 12
    notif = Notification(
        id=uuid.uuid4(),
        user_id=volunteer_user.id,
        title="Welcome to Maatram",
        message="Thank you for joining as a volunteer!",
        type="SYSTEM",
        is_read=False,
    )
    async_db.add(notif)
    await async_db.commit()

    # Sessions for authentication
    admin_session = UserSession(
        id=uuid.uuid4(),
        user_id=admin_user.id,
        refresh_token_hash=get_password_hash("refresh_token_admin"),
        client_type="WEB",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        is_revoked=False,
    )
    vol_session = UserSession(
        id=uuid.uuid4(),
        user_id=volunteer_user.id,
        refresh_token_hash=get_password_hash("refresh_token_vol"),
        client_type="WEB",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        is_revoked=False,
    )
    async_db.add_all([admin_session, vol_session])
    await async_db.commit()

    admin_token = create_access_token(
        user_id=admin_user.id,
        role=admin_user.role,
        status=admin_user.status,
        session_id=admin_session.id,
    )
    vol_token = create_access_token(
        user_id=volunteer_user.id,
        role=volunteer_user.role,
        status=volunteer_user.status,
        session_id=vol_session.id,
    )

    admin_csrf = generate_csrf_token(admin_session.id)
    vol_csrf = generate_csrf_token(vol_session.id)

    admin_headers = {"Authorization": f"Bearer {admin_token}", "X-CSRF-Token": admin_csrf}
    vol_headers = {"Authorization": f"Bearer {vol_token}", "X-CSRF-Token": vol_csrf}

    async def run_flow_benchmark(name: str, fn, runs: int = 5) -> dict[str, object]:
        latencies: list[float] = []
        payload_sizes: list[int] = []
        query_counts: list[int] = []

        for _ in range(runs):
            counter = QueryCounter()
            event.listen(test_engine.sync_engine, "before_cursor_execute", counter)
            t0 = time.perf_counter()
            resp = await fn()
            t1 = time.perf_counter()
            event.remove(test_engine.sync_engine, "before_cursor_execute", counter)

            assert resp.status_code in (200, 201), (
                f"{name} failed with {resp.status_code}: {resp.text}"
            )
            latencies.append((t1 - t0) * 1000)
            payload_sizes.append(len(resp.content))
            query_counts.append(counter.count)

        latencies.sort()
        p50 = statistics.median(latencies)
        p95 = latencies[int(len(latencies) * 0.95)]
        avg_queries = statistics.mean(query_counts)
        avg_payload = statistics.mean(payload_sizes)

        res = {
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "avg_queries": round(avg_queries, 1),
            "avg_payload_bytes": int(avg_payload),
            "status": "PASS",
        }
        benchmark_results[name] = res
        return res

    # 1. Login
    await run_flow_benchmark(
        "Flow 01: Login",
        lambda: client.post(
            "/api/v1/auth/login",
            json={"email": "benchmark_volunteer@maatram.org", "password": "VolunteerPass123!"},
        ),
        runs=3,
    )

    # 2. Registration
    await run_flow_benchmark(
        "Flow 02: Registration",
        lambda: client.post(
            "/api/v1/auth/register",
            json={
                "email": f"bench_{uuid.uuid4().hex[:6]}@example.com",
                "password": "StrongPassword123!",
                "first_name": "Test",
                "last_name": "Applicant",
                "category": "STUDENT",
                "mobile_number": f"+919{uuid.uuid4().int % 1000000000:09d}",
                "age": 21,
                "gender": "MALE",
                "student_details": {
                    "college_name": "Engineering College",
                    "degree": "B.Tech",
                    "department": "CSE",
                    "batch_year": 2024,
                    "current_year": 3,
                    "maatram_reg_number": f"MAT-{uuid.uuid4().hex[:6].upper()}",
                },
                "consent": {
                    "leaderboard_visible": True,
                    "name_visible": True,
                    "thank_you_emails": True,
                    "linkedin_content": True,
                    "contact_available": True,
                    "media_usage": True,
                },
            },
        ),
        runs=2,
    )

    # 3. Email Verification
    verify_user = User(
        id=uuid.uuid4(),
        email=f"verify_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="PENDING_VERIFICATION",
    )
    raw_token = f"raw_token_{uuid.uuid4().hex}"
    token_rec = EmailVerification(
        id=uuid.uuid4(),
        user_id=verify_user.id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )
    async_db.add_all([verify_user, token_rec])
    await async_db.commit()

    await run_flow_benchmark(
        "Flow 03: Email Verification",
        lambda: client.post(
            "/api/v1/auth/verify-email",
            json={"token": raw_token},
        ),
        runs=1,
    )

    # 4. Volunteer Profile
    await run_flow_benchmark(
        "Flow 04: Volunteer Profile",
        lambda: client.get("/api/v1/volunteers/me", headers=vol_headers),
    )

    # 5. Admin Pending Applications
    await run_flow_benchmark(
        "Flow 05: Admin Pending Applications",
        lambda: client.get("/api/v1/applications?status=PENDING", headers=admin_headers),
    )

    # 6. Admin Dashboard
    await run_flow_benchmark(
        "Flow 06: Admin Dashboard",
        lambda: client.get("/api/v1/admin/dashboard", headers=admin_headers),
    )

    # 7. Event Discovery
    await run_flow_benchmark(
        "Flow 07: Event Discovery",
        lambda: client.get("/api/v1/events?status=PUBLISHED", headers=vol_headers),
    )

    # 8. Event Registration
    await run_flow_benchmark(
        "Flow 08: Event Registration",
        lambda: client.post(
            f"/api/v1/events/{event_obj.id}/register",
            headers=vol_headers,
            json={"notes": "Excited to support the initiative"},
        ),
        runs=1,
    )

    # 9. Attendance Check-in
    reg_stmt = select(EventRegistration).where(EventRegistration.event_id == event_obj.id)
    reg_res = await async_db.execute(reg_stmt)
    reg = reg_res.scalar_one()
    reg.status = "SELECTED"
    await async_db.commit()

    await run_flow_benchmark(
        "Flow 09: Attendance Check-in",
        lambda: client.post(
            f"/api/v1/events/{event_obj.id}/attendance/check-in",
            headers=admin_headers,
            json={"volunteer_profile_id": str(vol_profile.id)},
        ),
        runs=1,
    )

    # 10. Points Ledger
    pt = PointTransaction(
        id=uuid.uuid4(),
        volunteer_profile_id=vol_profile.id,
        event_id=event_obj.id,
        event_points=Decimal("50.00"),
        hour_points=Decimal("20.00"),
        total_points=Decimal("70.00"),
        hours_credited=Decimal("4.00"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=datetime.now(UTC).year,
    )
    async_db.add(pt)
    await async_db.commit()

    await run_flow_benchmark(
        "Flow 10: Points Ledger",
        lambda: client.get("/api/v1/gamification/ledger", headers=vol_headers),
    )

    # 11. Leaderboard
    await run_flow_benchmark(
        "Flow 11: Leaderboard",
        lambda: client.get("/api/v1/gamification/leaderboard/overall", headers=vol_headers),
    )

    # 12. Notifications
    await run_flow_benchmark(
        "Flow 12: Notifications",
        lambda: client.get("/api/v1/notifications", headers=vol_headers),
    )

    print("\n" + "=" * 80)
    print(f"{'FLOW NAME':35} | {'P50 (ms)':9} | {'P95 (ms)':9} | {'QUERIES':7} | {'PAYLOAD':9}")
    print("-" * 80)
    for name, res in benchmark_results.items():
        print(
            f"{name:35} | {res['p50_ms']:9.2f} | {res['p95_ms']:9.2f} | "
            f"{res['avg_queries']:7.1f} | {res['avg_payload_bytes']:7d} B"
        )
    print("=" * 80)
