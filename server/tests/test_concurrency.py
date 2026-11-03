"""Concurrency and pessimistic locking tests against live Supabase PostgreSQL.

Validates that high-concurrency event registration and admin selection requests
strictly respect volunteer capacity constraints and maintain data integrity
using PostgreSQL row-level locks (SELECT ... FOR UPDATE).
"""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete, pool, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.core.exceptions import DomainException
from src.models import (
    AuditLog,
    Event,
    EventRegistration,
    RegistrationHistory,
    User,
    VolunteerProfile,
)
from src.services.registration_service import registration_service

# Concurrency tests must connect directly to PostgreSQL with NullPool
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
    # In async fixture cleanup we can't await directly in sync fixture,
    # engine cleanup handled per test


@pytest.fixture
def session_factory(live_engine):
    """Provide sessionmaker bound to NullPool engine."""
    return async_sessionmaker(
        bind=live_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


class EntityTracker:
    """Track created entity IDs for reliable teardown."""

    def __init__(self) -> None:
        self.user_ids: list[uuid.UUID] = []
        self.profile_ids: list[uuid.UUID] = []
        self.event_ids: list[uuid.UUID] = []
        self.registration_ids: list[uuid.UUID] = []

    async def cleanup(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Teardown created records in reverse FK dependency order."""
        async with session_factory() as session:
            try:
                # 1. Delete registration history
                if self.registration_ids:
                    await session.execute(
                        delete(RegistrationHistory).where(
                            RegistrationHistory.registration_id.in_(self.registration_ids)
                        )
                    )
                # 2. Delete event registrations
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
                # 3. Delete audit logs referencing test users or events
                if self.user_ids or self.event_ids:
                    await session.execute(
                        delete(AuditLog).where(
                            AuditLog.actor_user_id.in_(self.user_ids)
                            | AuditLog.target_entity_id.in_(self.event_ids + self.user_ids)
                        )
                    )
                # 4. Delete events
                if self.event_ids:
                    await session.execute(delete(Event).where(Event.id.in_(self.event_ids)))
                # 5. Delete volunteer profiles
                if self.profile_ids:
                    await session.execute(
                        delete(VolunteerProfile).where(VolunteerProfile.id.in_(self.profile_ids))
                    )
                # 6. Delete users
                if self.user_ids:
                    await session.execute(delete(User).where(User.id.in_(self.user_ids)))
                await session.commit()
            except Exception:
                await session.rollback()


async def create_live_admin(
    session_factory: async_sessionmaker[AsyncSession], tracker: EntityTracker
) -> User:
    """Helper to seed an admin user in live PostgreSQL."""
    async with session_factory() as session:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"concurrency_admin_{user_id.hex[:8]}@maatram.org",
            password_hash="argon2id$v=19$m=65536,t=3,p=4$fakehash",
            role="ADMIN",
            status="APPROVED",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        tracker.user_ids.append(user_id)
        return user


async def create_live_volunteer(
    session_factory: async_sessionmaker[AsyncSession],
    tracker: EntityTracker,
    status: str = "APPROVED",
) -> tuple[User, VolunteerProfile]:
    """Helper to seed a volunteer user and profile in live PostgreSQL."""
    async with session_factory() as session:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"concurrency_vol_{user_id.hex[:8]}@maatram.org",
            password_hash="argon2id$v=19$m=65536,t=3,p=4$fakehash",
            role="VOLUNTEER",
            status=status,
            is_active=True,
        )
        session.add(user)
        await session.flush()

        profile_id = uuid.uuid4()
        profile = VolunteerProfile(
            id=profile_id,
            user_id=user_id,
            first_name="Test",
            last_name="Volunteer",
            mobile_number=f"+9198{user_id.int % 100000000:08d}",
            age=25,
            gender="MALE",
            category="STUDENT",
            parental_consent_submitted=False,
            parental_consent_status="NOT_REQUIRED",
        )
        session.add(profile)
        await session.commit()

        tracker.user_ids.append(user_id)
        tracker.profile_ids.append(profile_id)
        return user, profile


async def create_live_published_event(
    session_factory: async_sessionmaker[AsyncSession],
    tracker: EntityTracker,
    admin: User,
    capacity: int = 2,
) -> Event:
    """Helper to seed a published event in live PostgreSQL."""
    async with session_factory() as session:
        event_id = uuid.uuid4()
        now = datetime.now(UTC)
        event = Event(
            id=event_id,
            title=f"Concurrency Event {event_id.hex[:6]}",
            description="Testing concurrent registrations with PostgreSQL row locks.",
            category="SCHOOL_VISIT",
            mode="OFFLINE",
            location="Chennai School Hall",
            start_time=now + timedelta(days=5),
            end_time=now + timedelta(days=5, hours=4),
            timezone="Asia/Kolkata",
            capacity_required=capacity,
            registration_deadline=now + timedelta(days=3),
            status="PUBLISHED",
            created_by_user_id=admin.id,
        )
        session.add(event)
        await session.commit()
        tracker.event_ids.append(event_id)
        return event


@pytest.mark.asyncio
async def test_concurrent_registrations_do_not_exceed_capacity(session_factory) -> None:
    """Verify that concurrent registrations for an event never exceed capacity.

    With capacity=2 and 6 concurrent registrations:
    - Exactly 2 must receive status SUBSCRIBED
    - Exactly 4 must receive status WAITLISTED
    - Total registrations must equal 6
    """
    tracker = EntityTracker()
    try:
        admin = await create_live_admin(session_factory, tracker)
        event = await create_live_published_event(session_factory, tracker, admin, capacity=2)

        # Seed 6 approved volunteers
        volunteers: list[User] = []
        for _ in range(6):
            user, _ = await create_live_volunteer(session_factory, tracker)
            volunteers.append(user)

        # Worker to register a volunteer in its own session
        async def register_worker(vol_user: User) -> None:
            async with session_factory() as session:
                reg_resp = await registration_service.register_volunteer(
                    session, event.id, vol_user.id, notes="concurrency-worker"
                )
                await session.commit()
                tracker.registration_ids.append(reg_resp.id)

        # Fire all 6 registrations simultaneously
        await asyncio.gather(*[register_worker(u) for u in volunteers])

        # Verify state in database
        async with session_factory() as session:
            stmt = select(EventRegistration).where(EventRegistration.event_id == event.id)
            res = await session.execute(stmt)
            regs = list(res.scalars().all())

            assert len(regs) == 6
            subscribed = [r for r in regs if r.status == "SUBSCRIBED"]
            waitlisted = [r for r in regs if r.status == "WAITLISTED"]

            # Capacity was 2, so exactly 2 SUBSCRIBED and 4 WAITLISTED
            assert len(subscribed) == 2, f"Expected 2 SUBSCRIBED, got {len(subscribed)}"
            assert len(waitlisted) == 4, f"Expected 4 WAITLISTED, got {len(waitlisted)}"
    finally:
        await tracker.cleanup(session_factory)


@pytest.mark.asyncio
async def test_concurrent_duplicate_registration_only_creates_one_record(session_factory) -> None:
    """Verify that multiple concurrent registration attempts by the same volunteer produce exactly 1 record."""
    tracker = EntityTracker()
    try:
        admin = await create_live_admin(session_factory, tracker)
        event = await create_live_published_event(session_factory, tracker, admin, capacity=5)
        user, _ = await create_live_volunteer(session_factory, tracker)

        # Worker attempting duplicate registration
        async def duplicate_worker() -> uuid.UUID | None:
            async with session_factory() as session:
                try:
                    reg_resp = await registration_service.register_volunteer(
                        session, event.id, user.id, notes="duplicate-check"
                    )
                    await session.commit()
                    return reg_resp.id
                except Exception:
                    await session.rollback()
                    return None

        # Fire 5 concurrent requests for the exact same volunteer
        results = await asyncio.gather(
            *[duplicate_worker() for _ in range(5)], return_exceptions=True
        )

        for r in results:
            if isinstance(r, uuid.UUID):
                tracker.registration_ids.append(r)

        # Verify database only contains exactly 1 registration row for this user & event
        async with session_factory() as session:
            stmt = select(EventRegistration).where(EventRegistration.event_id == event.id)
            res = await session.execute(stmt)
            regs = list(res.scalars().all())

            assert len(regs) == 1, f"Expected exactly 1 registration row, got {len(regs)}"
    finally:
        await tracker.cleanup(session_factory)


@pytest.mark.asyncio
async def test_concurrent_selection_cannot_exceed_capacity(session_factory) -> None:
    """Verify that concurrent admin selection calls cannot select more volunteers than event capacity."""
    tracker = EntityTracker()
    try:
        admin = await create_live_admin(session_factory, tracker)
        event = await create_live_published_event(session_factory, tracker, admin, capacity=2)

        # Seed 4 registered volunteers (2 SUBSCRIBED, 2 WAITLISTED)
        reg_ids: list[uuid.UUID] = []
        for _ in range(4):
            user, _ = await create_live_volunteer(session_factory, tracker)
            async with session_factory() as session:
                r = await registration_service.register_volunteer(session, event.id, user.id)
                await session.commit()
                reg_ids.append(r.id)
                tracker.registration_ids.append(r.id)

        # Two concurrent admin requests attempt to select 2 volunteers each:
        # Group A tries to select [reg_ids[0], reg_ids[1]]
        # Group B tries to select [reg_ids[2], reg_ids[3]]
        async def selection_worker(ids_to_select: list[uuid.UUID]) -> str:
            async with session_factory() as session:
                try:
                    await registration_service.select_volunteers(
                        session, event.id, ids_to_select, admin.id
                    )
                    await session.commit()
                    return "SUCCESS"
                except DomainException as de:
                    await session.rollback()
                    return f"DOMAIN_ERR:{de.code}"
                except Exception as ex:
                    await session.rollback()
                    return f"ERR:{type(ex).__name__}"

        results = await asyncio.gather(
            selection_worker([reg_ids[0], reg_ids[1]]),
            selection_worker([reg_ids[2], reg_ids[3]]),
        )

        # One should succeed, the other should be rejected due to capacity limit
        assert "SUCCESS" in results, f"At least one selection must succeed: {results}"
        assert any("CAPACITY_EXCEEDED" in str(r) for r in results), (
            f"Excess selection must be rejected with CAPACITY_EXCEEDED: {results}"
        )

        # Verify in database: selected count must be strictly <= capacity (2)
        async with session_factory() as session:
            stmt = select(EventRegistration).where(
                EventRegistration.event_id == event.id,
                EventRegistration.status == "SELECTED",
            )
            res = await session.execute(stmt)
            selected = list(res.scalars().all())
            assert len(selected) == 2, f"Expected exactly 2 SELECTED, found {len(selected)}"
    finally:
        await tracker.cleanup(session_factory)


@pytest.mark.asyncio
async def test_capacity_boundary_exactly_at_limit(session_factory) -> None:
    """Verify capacity boundary conditions: filling, overflow rejection, withdrawal, and waitlist promotion."""
    tracker = EntityTracker()
    try:
        admin = await create_live_admin(session_factory, tracker)
        event = await create_live_published_event(session_factory, tracker, admin, capacity=1)

        vol1, _ = await create_live_volunteer(session_factory, tracker)
        vol2, _ = await create_live_volunteer(session_factory, tracker)

        # 1. Register vol1 -> fits into capacity 1 -> SUBSCRIBED
        async with session_factory() as session:
            r1 = await registration_service.register_volunteer(session, event.id, vol1.id)
            await session.commit()
            tracker.registration_ids.append(r1.id)
            assert r1.status == "SUBSCRIBED"

        # 2. Register vol2 -> capacity 1 is full -> WAITLISTED
        async with session_factory() as session:
            r2 = await registration_service.register_volunteer(session, event.id, vol2.id)
            await session.commit()
            tracker.registration_ids.append(r2.id)
            assert r2.status == "WAITLISTED"

        # 3. Select vol1 -> SELECTED (capacity 1/1 selected)
        async with session_factory() as session:
            sel_res = await registration_service.select_volunteers(
                session, event.id, [r1.id], admin.id
            )
            await session.commit()
            assert sel_res.selected_count == 1
            assert len(sel_res.registrations) == 1

        # 4. Attempt to promote vol2 from waitlist while capacity is full -> rejected
        async with session_factory() as session:
            with pytest.raises(DomainException) as exc_info:
                await registration_service.promote_from_waitlist(session, event.id, r2.id, admin.id)
            assert exc_info.value.code == "CAPACITY_EXCEEDED"

        # 5. Volunteer 1 withdraws -> frees up slot
        async with session_factory() as session:
            withdrawn = await registration_service.withdraw_registration(
                session, r1.id, vol1, reason="Test withdrawal"
            )
            await session.commit()
            assert withdrawn.status == "WITHDRAWN"

        # 6. Now slot is free -> promote vol2 from waitlist -> succeeds!
        async with session_factory() as session:
            promoted = await registration_service.promote_from_waitlist(
                session, event.id, r2.id, admin.id
            )
            await session.commit()
            assert promoted.status == "SELECTED"

        # 7. Final database state check
        async with session_factory() as session:
            stmt = select(EventRegistration).where(EventRegistration.event_id == event.id)
            res = await session.execute(stmt)
            regs = {r.id: r.status for r in res.scalars().all()}
            assert regs[r1.id] == "WITHDRAWN"
            assert regs[r2.id] == "SELECTED"
    finally:
        await tracker.cleanup(session_factory)
