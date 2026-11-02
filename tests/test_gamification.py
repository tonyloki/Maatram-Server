"""Comprehensive test suite for Gamification Engine, Decimal Points & Leaderboards (Phase 9)."""

import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.consent import ConsentRecord
from src.models.gamification import PointTransaction
from src.models.users import User
from src.models.volunteers import VolunteerProfile
from src.services.gamification_service import gamification_service


async def create_user(
    async_db: AsyncSession,
    role: str = "VOLUNTEER",
    category: str = "STUDENT",
    status: str = "APPROVED",
    first_name: str = "Test",
    last_name: str = "Volunteer",
    email: str | None = None,
    leaderboard_visible: bool = True,
    name_visible: bool = True,
) -> tuple[User, VolunteerProfile]:
    """Helper to seed user, volunteer profile, and affirmative consent preferences."""
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

    profile = VolunteerProfile(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=22,
        gender="MALE",
        category=category,
    )
    async_db.add(profile)
    await async_db.flush()

    consent = ConsentRecord(
        volunteer_profile_id=profile.id,
        leaderboard_visible=leaderboard_visible,
        name_visible=name_visible,
        thank_you_emails=True,
    )
    async_db.add(consent)
    await async_db.commit()
    await async_db.refresh(user)
    await async_db.refresh(profile)
    return user, profile


async def get_auth_token(client: AsyncClient, email: str, password: str = "Password123!") -> str:
    """Helper to authenticate and obtain JWT access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# 1. Decimal Scoring Formula Verification
# ---------------------------------------------------------------------------


def test_scoring_formula_exact_decimal_arithmetic() -> None:
    """Verify P = (E * 10) + (H * 2) across repeating fractions and boundary conditions."""
    # 45 minutes = 0.75 hours -> 1.50 hour points + 10.00 event points = 11.50
    ev, hr, tot, hrs = gamification_service.calculate_scoring(45, is_qualifying=True)
    assert hrs == Decimal("0.75")
    assert hr == Decimal("1.50")
    assert ev == Decimal("10.00")
    assert tot == Decimal("11.50")
    assert all(isinstance(x, Decimal) for x in (ev, hr, tot, hrs))

    # 90 minutes = 1.50 hours -> 3.00 hour points + 10.00 event points = 13.00
    ev, hr, tot, hrs = gamification_service.calculate_scoring(90, is_qualifying=True)
    assert hrs == Decimal("1.50")
    assert hr == Decimal("3.00")
    assert tot == Decimal("13.00")

    # 20 minutes repeating fraction (20/60 = 0.333... -> 0.33) -> 0.66 hour points
    # Non-qualifying (< 60 minutes) -> E = 0 -> total = 0.66
    ev, hr, tot, hrs = gamification_service.calculate_scoring(20, is_qualifying=False)
    assert hrs == Decimal("0.33")
    assert hr == Decimal("0.66")
    assert ev == Decimal("0.00")
    assert tot == Decimal("0.66")

    # Zero minutes
    ev, hr, tot, hrs = gamification_service.calculate_scoring(0, is_qualifying=False)
    assert tot == Decimal("0.00")
    assert hrs == Decimal("0.00")


# ---------------------------------------------------------------------------
# 2. Point Ledger & Balance Queries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_volunteer_point_ledger_and_summary_endpoints(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify ledger queries return itemized entries with exact decimal precision and net sum."""
    user, profile = await create_user(async_db, role="VOLUNTEER")
    token = await get_auth_token(client, user.email)

    # Seed point transactions
    tx1 = PointTransaction(
        volunteer_profile_id=profile.id,
        event_id=uuid.uuid4(),
        event_points=Decimal("10.00"),
        hour_points=Decimal("4.00"),
        total_points=Decimal("14.00"),
        hours_credited=Decimal("2.00"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )
    tx2 = PointTransaction(
        volunteer_profile_id=profile.id,
        event_points=Decimal("0.00"),
        hour_points=Decimal("1.50"),
        total_points=Decimal("1.50"),
        hours_credited=Decimal("0.75"),
        transaction_type="MANUAL_ADJUSTMENT",
        cycle_year=2026,
    )
    async_db.add_all([tx1, tx2])
    await async_db.commit()

    # Query /gamification/ledger
    ledger_res = await client.get(
        "/api/v1/gamification/ledger",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ledger_res.status_code == 200, ledger_res.text
    ledger_data = ledger_res.json()
    assert ledger_data["total"] == 2
    assert ledger_data["net_points"] == "15.50"
    assert len(ledger_data["items"]) == 2

    # Query /gamification/summary
    sum_res = await client.get(
        "/api/v1/gamification/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sum_res.status_code == 200, sum_res.text
    sum_data = sum_res.json()
    assert sum_data["total_points"] == "15.50"
    assert sum_data["total_hours"] == "2.75"
    assert sum_data["completed_events_count"] == 1


# ---------------------------------------------------------------------------
# 3. Super Admin Manual & Compensating Point Adjustments
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_super_admin_point_adjustment_workflow(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify Super Admin can apply compensating adjustments and ordinary Admin is blocked."""
    admin_user, _ = await create_user(async_db, role="ADMIN")
    admin_token = await get_auth_token(client, admin_user.email)

    super_user, _ = await create_user(async_db, role="SUPER_ADMIN")
    super_token = await get_auth_token(client, super_user.email)

    vol_user, vol_profile = await create_user(async_db, role="VOLUNTEER")

    # Standard Admin blocked
    res_admin = await client.post(
        "/api/v1/gamification/adjust",
        json={
            "volunteer_profile_id": str(vol_profile.id),
            "event_points": "0.00",
            "hour_points": "5.00",
            "hours_credited": "2.50",
            "reason": "Special project contribution bonus verified.",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 403

    # Super Admin succeeds
    res_super = await client.post(
        "/api/v1/gamification/adjust",
        json={
            "volunteer_profile_id": str(vol_profile.id),
            "event_points": "0.00",
            "hour_points": "5.00",
            "hours_credited": "2.50",
            "reason": "Special project contribution bonus verified by director.",
        },
        headers={"Authorization": f"Bearer {super_token}"},
    )
    assert res_super.status_code == 200, res_super.text
    data = res_super.json()
    assert data["total_points"] == "5.00"
    assert data["transaction_type"] == "MANUAL_ADJUSTMENT"


# ---------------------------------------------------------------------------
# 4. Multi-Tier Leaderboards & Privacy Governance
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_leaderboard_rankings_and_privacy_consent_masking(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify multi-tier leaderboards respect affirmative consent (masked name vs completely excluded)."""
    # 1. Volunteer A: Opted in fully (Student, 25 points)
    _, vol_a = await create_user(
        async_db,
        first_name="Priya",
        last_name="Rajan",
        category="STUDENT",
        leaderboard_visible=True,
        name_visible=True,
    )
    tx_a = PointTransaction(
        volunteer_profile_id=vol_a.id,
        event_points=Decimal("10.00"),
        hour_points=Decimal("15.00"),
        total_points=Decimal("25.00"),
        hours_credited=Decimal("7.50"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )

    # 2. Volunteer B: Opted in with anonymous masking (Student, 20 points)
    _, vol_b = await create_user(
        async_db,
        first_name="Karthik",
        last_name="S",
        category="STUDENT",
        leaderboard_visible=True,
        name_visible=False,
    )
    tx_b = PointTransaction(
        volunteer_profile_id=vol_b.id,
        event_points=Decimal("10.00"),
        hour_points=Decimal("10.00"),
        total_points=Decimal("20.00"),
        hours_credited=Decimal("5.00"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )

    # 3. Volunteer C: Opted out completely (Student, 30 points) -> MUST NOT APPEAR
    _, vol_c = await create_user(
        async_db,
        first_name="Secret",
        last_name="Hero",
        category="STUDENT",
        leaderboard_visible=False,
        name_visible=False,
    )
    tx_c = PointTransaction(
        volunteer_profile_id=vol_c.id,
        event_points=Decimal("10.00"),
        hour_points=Decimal("20.00"),
        total_points=Decimal("30.00"),
        hours_credited=Decimal("10.00"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )

    # 4. Volunteer D: Alumni (Alumni, 15 points)
    _, vol_d = await create_user(
        async_db,
        first_name="Anand",
        last_name="Kumar",
        category="ALUMNI",
        leaderboard_visible=True,
        name_visible=True,
    )
    tx_d = PointTransaction(
        volunteer_profile_id=vol_d.id,
        event_points=Decimal("10.00"),
        hour_points=Decimal("5.00"),
        total_points=Decimal("15.00"),
        hours_credited=Decimal("2.50"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )

    async_db.add_all([tx_a, tx_b, tx_c, tx_d])
    await async_db.commit()

    # Query overall leaderboard
    viewer_user, _ = await create_user(async_db)
    token = await get_auth_token(client, viewer_user.email)

    res = await client.get(
        "/api/v1/gamification/leaderboard/overall?cycle_year=2026",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    items = data["items"]

    # Exactly 3 visible volunteers (Vol C is excluded!)
    assert len(items) == 3
    # Rank 1: Priya Rajan (25.00 pts)
    assert items[0]["rank"] == 1
    assert items[0]["volunteer_name"] == "Priya Rajan"
    assert items[0]["total_points"] == "25.00"
    assert items[0]["is_anonymous"] is False

    # Rank 2: Anonymous Volunteer (20.00 pts)
    assert items[1]["rank"] == 2
    assert items[1]["volunteer_name"] == "Anonymous Volunteer"
    assert items[1]["total_points"] == "20.00"
    assert items[1]["is_anonymous"] is True
    assert items[1]["volunteer_profile_id"] is None

    # Rank 3: Anand Kumar (15.00 pts, Alumni)
    assert items[2]["rank"] == 3
    assert items[2]["volunteer_name"] == "Anand Kumar"
    assert items[2]["category"] == "ALUMNI"

    # Query Student Tier leaderboard
    student_res = await client.get(
        "/api/v1/gamification/leaderboard/student?cycle_year=2026",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert student_res.status_code == 200
    student_items = student_res.json()["items"]
    assert len(student_items) == 2
    assert student_items[0]["volunteer_name"] == "Priya Rajan"
    assert student_items[1]["volunteer_name"] == "Anonymous Volunteer"


# ---------------------------------------------------------------------------
# 5. Achievements Catalog & Automatic Evaluation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_achievements_evaluation_and_duplicate_prevention(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify achievements are awarded when criteria met and duplicate awarding is prevented."""
    user, profile = await create_user(async_db, role="VOLUNTEER")
    token = await get_auth_token(client, user.email)

    # Seed default achievements
    await gamification_service.get_my_achievements(async_db, user)

    # Seed point transaction with 1 event and 12 hours
    event_id = uuid.uuid4()
    tx = PointTransaction(
        volunteer_profile_id=profile.id,
        event_id=event_id,
        event_points=Decimal("10.00"),
        hour_points=Decimal("24.00"),
        total_points=Decimal("34.00"),
        hours_credited=Decimal("12.00"),
        transaction_type="EVENT_COMPLETION",
        cycle_year=2026,
    )
    async_db.add(tx)
    await async_db.commit()

    # Trigger evaluation
    count1 = await gamification_service._evaluate_volunteer_achievements(async_db, profile.id)
    await async_db.commit()
    # Should award FIRST_STEP (1 event) and DEDICATED_VOLUNTEER (10 hours)
    assert count1 == 2

    # Second evaluation must award 0 (prevent duplicates)
    count2 = await gamification_service._evaluate_volunteer_achievements(async_db, profile.id)
    assert count2 == 0

    # Query endpoint
    res = await client.get(
        "/api/v1/gamification/achievements/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["total_earned"] == 2
    assert data["total_available"] >= 4
    earned_codes = [a["code"] for a in data["items"] if a["is_earned"]]
    assert "FIRST_STEP" in earned_codes
    assert "DEDICATED_VOLUNTEER" in earned_codes
