"""Concurrency and pessimistic locking tests for Attendance & Gamification (Phase 8 & 9).

Validates that high-concurrency check-in/out and atomic event completion
requests strictly maintain data integrity and prevent race conditions
using PostgreSQL row-level locks and transaction serialization.
"""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import delete, pool, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.core.exceptions import DomainException
from src.models.admin import AuditLog
from src.models.attendance import AttendanceRecord
from src.models.communications import CommunicationJob
from src.models.consent import ConsentRecord
from src.models.events import Event, EventRegistration, RegistrationHistory
from src.models.gamification import PointTransaction, VolunteerAchievement
from src.models.users import User
from src.models.volunteers import VolunteerProfile
from src.services.attendance_service import attendance_service
from src.services.gamification_service import gamification_service

LIVE_DB_URL = settings.DIRECT_URL or settings.DATABASE_URL


@pytest.fixture(scope="module")
def live_engine():
    """Create dedicated NullPool async engine for live PostgreSQL concurrency tests."""
    engine = create_async_engine(
        LIVE_DB_URL,
        poolclass=pool.NullPool,
        connect_args={"statement_cache_size": 0},
    )
    yield engine


@pytest.fixture
def session_factory(live_engine):
    """Provide sessionmaker bound to NullPool engine."""
    return async_sessionmaker(
        bind=live_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


class Group5EntityTracker:
    """Track created entity IDs for reliable teardown in reverse FK order."""

    def __init__(self) -> None:
        self.user_ids: list[uuid.UUID] = []
        self.profile_ids: list[uuid.UUID] = []
        self.event_ids: list[uuid.UUID] = []
        self.registration_ids: list[uuid.UUID] = []
        self.attendance_ids: list[uuid.UUID] = []
        self.point_tx_ids: list[uuid.UUID] = []
        self.comm_job_ids: list[uuid.UUID] = []

    async def cleanup(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Teardown created records cleanly."""
        async with session_factory() as session:
            try:
                # 1. Delete CommunicationJobs
                if self.comm_job_ids:
                    await session.execute(
                        delete(CommunicationJob).where(CommunicationJob.id.in_(self.comm_job_ids))
                    )
                # 2. Delete PointTransactions (using replica role to bypass immutable trigger)
                if self.point_tx_ids or self.event_ids:
                    await session.execute(text("SET session_replication_role = 'replica';"))
                    if self.point_tx_ids:
                        await session.execute(
                            delete(PointTransaction).where(
                                PointTransaction.id.in_(self.point_tx_ids)
                            )
                        )
                    if self.event_ids:
                        await session.execute(
                            delete(PointTransaction).where(
                                PointTransaction.event_id.in_(self.event_ids)
                            )
                        )
                    await session.execute(text("SET session_replication_role = 'origin';"))

                # 3. Delete VolunteerAchievements
                if self.profile_ids:
                    await session.execute(
                        delete(VolunteerAchievement).where(
                            VolunteerAchievement.volunteer_profile_id.in_(self.profile_ids)
                        )
                    )

                # 4. Delete AttendanceRecords
                if self.attendance_ids:
                    await session.execute(
                        delete(AttendanceRecord).where(AttendanceRecord.id.in_(self.attendance_ids))
                    )
                elif self.registration_ids:
                    await session.execute(
                        delete(AttendanceRecord).where(
                            AttendanceRecord.event_registration_id.in_(self.registration_ids)
                        )
                    )

                # 5. Delete RegistrationHistory
                if self.registration_ids:
                    await session.execute(
                        delete(RegistrationHistory).where(
                            RegistrationHistory.registration_id.in_(self.registration_ids)
                        )
                    )

                # 6. Delete EventRegistrations
                if self.registration_ids:
                    await session.execute(
                        delete(EventRegistration).where(
                            EventRegistration.id.in_(self.registration_ids)
                        )
                    )
                elif self.event_ids:
                    await session.execute(
                        delete(EventRegistration).where(
                            EventRegistration.event_id.in_(self.event_ids)
                        )
                    )

                # 7. Delete AuditLogs
                if self.user_ids or self.event_ids:
                    await session.execute(
                        delete(AuditLog).where(
                            AuditLog.actor_user_id.in_(self.user_ids)
                            | AuditLog.resource_id.in_(
                                [str(i) for i in self.event_ids + self.user_ids]
                            )
                        )
                    )

                # 8. Delete ConsentRecords
                if self.profile_ids:
                    await session.execute(
                        delete(ConsentRecord).where(
                            ConsentRecord.volunteer_profile_id.in_(self.profile_ids)
                        )
                    )

                # 9. Delete Events
                if self.event_ids:
                    await session.execute(delete(Event).where(Event.id.in_(self.event_ids)))

                # 10. Delete VolunteerProfiles
                if self.profile_ids:
                    await session.execute(
                        delete(VolunteerProfile).where(VolunteerProfile.id.in_(self.profile_ids))
                    )

                # 11. Delete Users
                if self.user_ids:
                    await session.execute(delete(User).where(User.id.in_(self.user_ids)))

                await session.commit()
            except Exception:
                await session.rollback()


async def seed_live_admin(
    session_factory: async_sessionmaker[AsyncSession], tracker: Group5EntityTracker
) -> User:
    """Helper to seed an admin user in live PostgreSQL."""
    async with session_factory() as session:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"concurrency_g5_admin_{user_id.hex[:8]}@maatram.org",
            password_hash="argon2id$v=19$m=65536,t=3,p=4$fakehash",
            role="ADMIN",
            status="APPROVED",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        tracker.user_ids.append(user_id)
        return user


async def seed_live_volunteer(
    session_factory: async_sessionmaker[AsyncSession],
    tracker: Group5EntityTracker,
) -> tuple[User, VolunteerProfile]:
    """Helper to seed a volunteer in live PostgreSQL."""
    async with session_factory() as session:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"concurrency_g5_vol_{user_id.hex[:8]}@maatram.org",
            password_hash="argon2id$v=19$m=65536,t=3,p=4$fakehash",
            role="VOLUNTEER",
            status="APPROVED",
            is_active=True,
        )
        session.add(user)
        await session.flush()

        profile_id = uuid.uuid4()
        profile = VolunteerProfile(
            id=profile_id,
            user_id=user_id,
            first_name="Live",
            last_name="ConcurrentVol",
            mobile_number=f"+9198{user_id.int % 100000000:08d}",
            age=25,
            gender="FEMALE",
            category="STUDENT",
        )
        session.add(profile)

        consent = ConsentRecord(
            volunteer_profile_id=profile_id,
            leaderboard_visible=True,
            name_visible=True,
            thank_you_emails=True,
        )
        session.add(consent)
        await session.commit()

        tracker.user_ids.append(user_id)
        tracker.profile_ids.append(profile_id)
        return user, profile


async def seed_live_ongoing_event(
    session_factory: async_sessionmaker[AsyncSession],
    tracker: Group5EntityTracker,
    admin: User,
) -> Event:
    """Helper to seed an ongoing event in live PostgreSQL."""
    async with session_factory() as session:
        event_id = uuid.uuid4()
        now = datetime.now(UTC)
        event = Event(
            id=event_id,
            title=f"Live Concurrency Event {event_id.hex[:6]}",
            description="Testing concurrent check-in and completion.",
            category="SCHOOL_VISIT",
            mode="ONLINE",
            location="https://meet.google.com/concurrency-test",
            start_time=now - timedelta(hours=2),
            end_time=now + timedelta(hours=2),
            timezone="Asia/Kolkata",
            capacity_required=5,
            registration_deadline=now - timedelta(hours=3),
            status="ONGOING",
            created_by_user_id=admin.id,
        )
        session.add(event)
        await session.commit()
        tracker.event_ids.append(event_id)
        return event


# ---------------------------------------------------------------------------
# 1. Concurrent Check-In Test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_check_in_only_one_record_created(session_factory) -> None:
    """Verify that multiple concurrent check-in requests for the same volunteer produce exactly 1 record."""
    tracker = Group5EntityTracker()
    try:
        admin = await seed_live_admin(session_factory, tracker)
        user, profile = await seed_live_volunteer(session_factory, tracker)
        event = await seed_live_ongoing_event(session_factory, tracker, admin)

        # Register and select volunteer
        async with session_factory() as session:
            reg = EventRegistration(
                id=uuid.uuid4(),
                event_id=event.id,
                volunteer_profile_id=profile.id,
                status="SELECTED",
            )
            session.add(reg)
            await session.commit()
            tracker.registration_ids.append(reg.id)

        # 5 workers attempt check-in simultaneously
        async def check_in_worker() -> str:
            async with session_factory() as session:
                try:
                    recs = await attendance_service.check_in_volunteers(
                        db=session,
                        event_id=event.id,
                        volunteer_profile_ids=[profile.id],
                        check_in_time=datetime.now(UTC),
                        current_user=admin,
                    )
                    return f"SUCCESS:{recs[0].id}"
                except DomainException as de:
                    return f"DOMAIN_ERR:{de.code}"
                except Exception as ex:
                    return f"ERR:{type(ex).__name__}"

        results = await asyncio.gather(*[check_in_worker() for _ in range(5)])

        successes = [r for r in results if r.startswith("SUCCESS:")]
        errors = [r for r in results if not r.startswith("SUCCESS:")]

        assert len(successes) == 1, f"Expected exactly 1 successful check-in, got {successes}"
        assert len(errors) == 4, f"Expected 4 rejected check-ins, got {errors}"
        assert any("DUPLICATE_CHECKIN" in str(e) for e in errors)

        # Verify database contains exactly 1 attendance row
        async with session_factory() as session:
            stmt = select(AttendanceRecord).where(AttendanceRecord.event_registration_id == reg.id)
            res = await session.execute(stmt)
            records = list(res.scalars().all())
            assert len(records) == 1
            tracker.attendance_ids.append(records[0].id)
            assert records[0].status == "IN_PROGRESS"

    finally:
        await tracker.cleanup(session_factory)


# ---------------------------------------------------------------------------
# 2. Concurrent Event Completion & Exactly-Once Point Allocation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_event_completion_serializes_and_prevents_duplicate_awards(
    session_factory,
) -> None:
    """Verify PostgreSQL row-level lock serializes concurrent event completion and awards points exactly once."""
    tracker = Group5EntityTracker()
    try:
        admin = await seed_live_admin(session_factory, tracker)
        user, profile = await seed_live_volunteer(session_factory, tracker)
        event = await seed_live_ongoing_event(session_factory, tracker, admin)

        now = datetime.now(UTC)
        async with session_factory() as session:
            reg = EventRegistration(
                id=uuid.uuid4(),
                event_id=event.id,
                volunteer_profile_id=profile.id,
                status="SELECTED",
            )
            session.add(reg)
            await session.flush()
            tracker.registration_ids.append(reg.id)

            att = AttendanceRecord(
                id=uuid.uuid4(),
                event_registration_id=reg.id,
                check_in_time=now - timedelta(minutes=90),
                check_out_time=now,
                duration_minutes=90,
                status="COMPLETED",
            )
            session.add(att)
            await session.commit()
            tracker.attendance_ids.append(att.id)

        # Two concurrent admin requests attempt to complete and award the event simultaneously
        async def completion_worker() -> str:
            async with session_factory() as session:
                try:
                    resp = await gamification_service.complete_and_award_event(
                        db=session,
                        event_id=event.id,
                        current_user=admin,
                    )
                    return f"SUCCESS:{resp.total_points_awarded}"
                except DomainException as de:
                    return f"DOMAIN_ERR:{de.code}"
                except Exception as ex:
                    return f"ERR:{type(ex).__name__}"

        results = await asyncio.gather(completion_worker(), completion_worker())

        success_results = [r for r in results if r.startswith("SUCCESS:")]
        rejected_results = [r for r in results if not r.startswith("SUCCESS:")]

        # Exactly 1 must succeed, the other must be rejected
        assert len(success_results) == 1, f"Expected exactly 1 successful completion: {results}"
        assert len(rejected_results) == 1, f"Expected 1 rejected completion: {results}"
        assert "POINTS_ALREADY_AWARDED" in str(rejected_results[0])

        # Verify database state in live PostgreSQL
        async with session_factory() as session:
            # 1. Event is COMPLETED
            ev_stmt = select(Event).where(Event.id == event.id)
            ev = (await session.execute(ev_stmt)).scalar_one()
            assert ev.status == "COMPLETED"

            # 2. Exactly 1 PointTransaction exists for this event
            tx_stmt = select(PointTransaction).where(PointTransaction.event_id == event.id)
            tx_rows = list((await session.execute(tx_stmt)).scalars().all())
            assert len(tx_rows) == 1
            tracker.point_tx_ids.append(tx_rows[0].id)

            # 3. Assert exact mathematical points: 90 mins = 1.50 hrs -> 10.00 + 3.00 = 13.00
            assert tx_rows[0].total_points == Decimal("13.00")
            assert tx_rows[0].hours_credited == Decimal("1.50")

    finally:
        await tracker.cleanup(session_factory)
