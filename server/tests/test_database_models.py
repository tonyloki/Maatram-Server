"""Comprehensive database models, constraints, decimal precision, and trigger tests."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import pool, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.models import (
    Event,
    PointTransaction,
    StudentProfile,
    User,
    VolunteerProfile,
)

TEST_DB_URL = settings.DIRECT_URL or settings.DATABASE_URL


@pytest_asyncio.fixture
async def db_session():
    """Provide an isolated database session with NullPool to prevent event loop connection leakage."""
    test_engine = create_async_engine(
        TEST_DB_URL,
        poolclass=pool.NullPool,
        connect_args={"statement_cache_size": 0},
    )
    async_session = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_user_creation_and_unique_email(db_session: AsyncSession):
    """Verify user model creation and unique email constraint."""
    user_id = uuid.uuid4()
    unique_email = f"test_{user_id.hex[:8]}@maatram.org"
    user = User(
        id=user_id,
        email=unique_email,
        password_hash="argon2id$v=19$m=65536,t=3,p=4$fakehash",
        role="VOLUNTEER",
        status="APPROVED",
    )
    db_session.add(user)
    await db_session.flush()

    # Query back
    stmt = select(User).where(User.id == user_id)
    retrieved = (await db_session.execute(stmt)).scalar_one()
    assert retrieved.email == unique_email
    assert retrieved.role == "VOLUNTEER"
    assert retrieved.is_active is True

    # Duplicate email violation
    dup_user = User(
        id=uuid.uuid4(),
        email=unique_email,
        password_hash="argon2id$v=19$m=65536,t=3,p=4$fakehash2",
        role="VOLUNTEER",
        status="PENDING",
    )
    db_session.add(dup_user)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_check_constraint_role(db_session: AsyncSession):
    """Verify check constraint on invalid user role."""
    invalid_user = User(
        id=uuid.uuid4(),
        email=f"invalid_role_{uuid.uuid4().hex[:8]}@maatram.org",
        password_hash="fakehash",
        role="INVALID_ROLE",
        status="PENDING",
    )
    db_session.add(invalid_user)
    with pytest.raises(IntegrityError) as exc_info:
        await db_session.flush()
    assert "chk_users_role" in str(exc_info.value).lower() or "check" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_volunteer_profile_polymorphic_hierarchy(db_session: AsyncSession):
    """Verify creation of volunteer profile and polymorphic student profile."""
    user = User(
        id=uuid.uuid4(),
        email=f"student_{uuid.uuid4().hex[:8]}@maatram.org",
        password_hash="fakehash",
        role="VOLUNTEER",
        status="APPROVED",
    )
    db_session.add(user)
    await db_session.flush()

    profile = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        first_name="Logesh",
        last_name="K",
        mobile_number=f"+9198765{uuid.uuid4().int % 100000:05d}",
        age=20,
        gender="MALE",
        category="STUDENT",
        parental_consent_submitted=False,
        parental_consent_status="NOT_REQUIRED",
    )
    db_session.add(profile)
    await db_session.flush()

    student = StudentProfile(
        id=uuid.uuid4(),
        volunteer_profile_id=profile.id,
        college_name="Madras Institute of Technology",
        degree="B.Tech",
        department="Computer Technology",
        batch_year=2024,
        current_year=3,
        maatram_reg_number=f"MTR-{uuid.uuid4().hex[:6].upper()}",
    )
    db_session.add(student)
    await db_session.flush()

    # Query back polymorphic relation
    stmt = select(VolunteerProfile).where(VolunteerProfile.id == profile.id)
    res = (await db_session.execute(stmt)).scalar_one()
    assert res.category == "STUDENT"
    assert res.first_name == "Logesh"


@pytest.mark.asyncio
async def test_event_duration_constraint(db_session: AsyncSession):
    """Verify check constraint on event end_time > start_time."""
    user = User(
        id=uuid.uuid4(),
        email=f"admin_{uuid.uuid4().hex[:8]}@maatram.org",
        password_hash="fakehash",
        role="ADMIN",
        status="APPROVED",
    )
    db_session.add(user)
    await db_session.flush()

    now = datetime.now(UTC)
    invalid_event = Event(
        id=uuid.uuid4(),
        title="Invalid Event",
        description="Testing start/end constraint",
        category="SCHOOL_VISIT",
        mode="OFFLINE",
        location="Chennai",
        start_time=now + timedelta(hours=2),
        end_time=now + timedelta(hours=1),  # Invalid: end before start
        capacity_required=10,
        registration_deadline=now + timedelta(hours=1),
        created_by_user_id=user.id,
    )
    db_session.add(invalid_event)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_gamification_decimal_precision(db_session: AsyncSession):
    """Verify exact NUMERIC(8,2) precision and check constraint total = event + hour points."""
    user = User(
        id=uuid.uuid4(),
        email=f"vol_{uuid.uuid4().hex[:8]}@maatram.org",
        password_hash="fakehash",
        role="VOLUNTEER",
        status="APPROVED",
    )
    db_session.add(user)
    await db_session.flush()

    profile = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        first_name="Decimal",
        last_name="Tester",
        mobile_number=f"+9198765{uuid.uuid4().int % 100000:05d}",
        age=22,
        gender="FEMALE",
        category="ALUMNI",
    )
    db_session.add(profile)
    await db_session.flush()

    # 45 mins = 0.75 hours -> event_points = 10.00, hour_points = 1.50, total = 11.50
    tx = PointTransaction(
        id=uuid.uuid4(),
        volunteer_profile_id=profile.id,
        event_points=Decimal("10.00"),
        hour_points=Decimal("1.50"),
        total_points=Decimal("11.50"),
        hours_credited=Decimal("0.75"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )
    db_session.add(tx)
    await db_session.flush()

    stmt = select(PointTransaction).where(PointTransaction.id == tx.id)
    retrieved = (await db_session.execute(stmt)).scalar_one()
    assert retrieved.event_points == Decimal("10.00")
    assert retrieved.hour_points == Decimal("1.50")
    assert retrieved.total_points == Decimal("11.50")
    assert retrieved.hours_credited == Decimal("0.75")
    assert isinstance(retrieved.total_points, Decimal)


@pytest.mark.asyncio
async def test_point_ledger_immutability_trigger(db_session: AsyncSession):
    """Verify that PostgreSQL trigger trg_prevent_point_ledger_mutation blocks UPDATE and DELETE."""
    user = User(
        id=uuid.uuid4(),
        email=f"immutable_{uuid.uuid4().hex[:8]}@maatram.org",
        password_hash="fakehash",
        role="VOLUNTEER",
        status="APPROVED",
    )
    db_session.add(user)
    await db_session.flush()

    profile = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        first_name="Immutable",
        last_name="Ledger",
        mobile_number=f"+9198765{uuid.uuid4().int % 100000:05d}",
        age=21,
        gender="MALE",
        category="STUDENT",
    )
    db_session.add(profile)
    await db_session.flush()

    tx = PointTransaction(
        id=uuid.uuid4(),
        volunteer_profile_id=profile.id,
        event_points=Decimal("10.00"),
        hour_points=Decimal("2.00"),
        total_points=Decimal("12.00"),
        hours_credited=Decimal("1.00"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )
    db_session.add(tx)
    await db_session.flush()

    # 1. Attempt UPDATE -> Must be rejected by database trigger
    with pytest.raises(DBAPIError) as exc_update:
        await db_session.execute(
            text(f"UPDATE point_transactions SET total_points = 50.00 WHERE id = '{tx.id}';")
        )
    assert "Point transactions ledger is strictly append-only" in str(exc_update.value)

    # 2. Attempt DELETE -> Must be rejected by database trigger
    # In PostgreSQL, after a trigger error the transaction is aborted; rollback cleans it
    await db_session.rollback()

    # In a fresh sub-transaction, insert and test DELETE trigger
    user2 = User(
        id=uuid.uuid4(),
        email=f"del_{uuid.uuid4().hex[:8]}@maatram.org",
        password_hash="fakehash",
        role="VOLUNTEER",
        status="APPROVED",
    )
    db_session.add(user2)
    profile2 = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=user2.id,
        first_name="Delete",
        last_name="Tester",
        mobile_number=f"+9198765{uuid.uuid4().int % 100000:05d}",
        age=23,
        gender="MALE",
        category="STUDENT",
    )
    db_session.add(profile2)
    tx2 = PointTransaction(
        id=uuid.uuid4(),
        volunteer_profile_id=profile2.id,
        event_points=Decimal("10.00"),
        hour_points=Decimal("0.00"),
        total_points=Decimal("10.00"),
        hours_credited=Decimal("0.00"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )
    db_session.add(tx2)
    await db_session.flush()

    with pytest.raises(DBAPIError) as exc_delete:
        await db_session.execute(text(f"DELETE FROM point_transactions WHERE id = '{tx2.id}';"))
    assert "Point transactions ledger is strictly append-only" in str(exc_delete.value)
