"""Gamification persistence repository abstraction."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.consent import ConsentRecord
from src.models.gamification import AchievementDefinition, PointTransaction, VolunteerAchievement
from src.models.volunteers import VolunteerProfile


class GamificationRepository:
    """Database persistence abstraction for point transactions, achievements, and leaderboard rankings."""

    async def create_transaction(
        self,
        db: AsyncSession,
        volunteer_profile_id: uuid.UUID,
        event_points: Decimal,
        hour_points: Decimal,
        hours_credited: Decimal,
        transaction_type: str,
        cycle_year: int,
        event_id: uuid.UUID | None = None,
        related_transaction_id: uuid.UUID | None = None,
        awarded_by_user_id: uuid.UUID | None = None,
        reason: str | None = None,
    ) -> PointTransaction:
        """Create and persist a new immutable point transaction."""
        total_points = event_points + hour_points
        tx = PointTransaction(
            volunteer_profile_id=volunteer_profile_id,
            event_id=event_id,
            related_transaction_id=related_transaction_id,
            event_points=event_points,
            hour_points=hour_points,
            total_points=total_points,
            hours_credited=hours_credited,
            transaction_type=transaction_type,
            awarded_by_user_id=awarded_by_user_id,
            reason=reason,
            cycle_year=cycle_year,
        )
        db.add(tx)
        await db.flush()
        await db.refresh(tx)
        return tx

    async def get_transaction_by_id(
        self, db: AsyncSession, tx_id: uuid.UUID
    ) -> PointTransaction | None:
        """Fetch transaction by primary key."""
        stmt = select(PointTransaction).where(PointTransaction.id == tx_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def has_awarded_event_points(self, db: AsyncSession, event_id: uuid.UUID) -> bool:
        """Check whether completion points have already been awarded for this event."""
        stmt = (
            select(func.count())
            .select_from(PointTransaction)
            .where(
                PointTransaction.event_id == event_id,
                PointTransaction.transaction_type == "EVENT_COMPLETION",
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one() > 0

    async def get_volunteer_ledger(
        self,
        db: AsyncSession,
        volunteer_profile_id: uuid.UUID,
        cycle_year: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[PointTransaction], int, Decimal]:
        """Fetch paginated ledger entries for a volunteer with net balance."""
        base_query = select(PointTransaction).where(
            PointTransaction.volunteer_profile_id == volunteer_profile_id
        )
        if cycle_year is not None:
            base_query = base_query.where(PointTransaction.cycle_year == cycle_year)

        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        sum_stmt = select(
            func.coalesce(func.sum(PointTransaction.total_points), Decimal("0.00"))
        ).where(PointTransaction.volunteer_profile_id == volunteer_profile_id)
        if cycle_year is not None:
            sum_stmt = sum_stmt.where(PointTransaction.cycle_year == cycle_year)
        sum_res = await db.execute(sum_stmt)
        net_points = Decimal(str(sum_res.scalar_one() or "0.00"))

        stmt = base_query.order_by(PointTransaction.created_at.desc()).offset(skip).limit(limit)
        items_res = await db.execute(stmt)
        items = list(items_res.scalars().all())

        return items, total, net_points

    async def get_volunteer_summary(
        self,
        db: AsyncSession,
        volunteer_profile_id: uuid.UUID,
        cycle_year: int,
    ) -> tuple[Decimal, Decimal, int, int]:
        """Aggregate total points, credited hours, completed events, and badge counts."""
        # Total points and total hours for cycle year
        pt_stmt = select(
            func.coalesce(func.sum(PointTransaction.total_points), Decimal("0.00")),
            func.coalesce(func.sum(PointTransaction.hours_credited), Decimal("0.00")),
        ).where(
            PointTransaction.volunteer_profile_id == volunteer_profile_id,
            PointTransaction.cycle_year == cycle_year,
        )
        pt_res = await db.execute(pt_stmt)
        pts_row = pt_res.one()
        total_pts = Decimal(str(pts_row[0] or "0.00"))
        total_hrs = Decimal(str(pts_row[1] or "0.00"))

        # Distinct completed events attended
        events_stmt = select(func.count(func.distinct(PointTransaction.event_id))).where(
            PointTransaction.volunteer_profile_id == volunteer_profile_id,
            PointTransaction.transaction_type == "EVENT_COMPLETION",
            PointTransaction.event_id.isnot(None),
            PointTransaction.cycle_year == cycle_year,
        )
        events_res = await db.execute(events_stmt)
        completed_events = events_res.scalar_one()

        # Earned badges count (lifetime)
        badge_stmt = (
            select(func.count())
            .select_from(VolunteerAchievement)
            .where(VolunteerAchievement.volunteer_profile_id == volunteer_profile_id)
        )
        badge_res = await db.execute(badge_stmt)
        badge_count = badge_res.scalar_one()

        return total_pts, total_hrs, completed_events, badge_count

    async def get_leaderboard_rankings(
        self,
        db: AsyncSession,
        category: str | None,
        cycle_year: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, object]], int]:
        """Fetch multi-tier leaderboard rankings respecting affirmative privacy consent."""
        # Join PointTransaction with VolunteerProfile and ConsentRecord
        # Consent filter: leaderboard_visible must be TRUE
        query = (
            select(
                VolunteerProfile.id.label("profile_id"),
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                VolunteerProfile.category,
                func.coalesce(ConsentRecord.leaderboard_visible, False).label(
                    "leaderboard_visible"
                ),
                func.coalesce(ConsentRecord.name_visible, False).label("name_visible"),
                func.coalesce(func.sum(PointTransaction.total_points), Decimal("0.00")).label(
                    "total_points"
                ),
                func.coalesce(func.sum(PointTransaction.hours_credited), Decimal("0.00")).label(
                    "total_hours"
                ),
                func.count(func.distinct(PointTransaction.event_id)).label("events_attended"),
                func.min(PointTransaction.created_at).label("first_awarded_at"),
            )
            .join(VolunteerProfile, PointTransaction.volunteer_profile_id == VolunteerProfile.id)
            .outerjoin(ConsentRecord, VolunteerProfile.id == ConsentRecord.volunteer_profile_id)
            .where(
                PointTransaction.cycle_year == cycle_year,
                func.coalesce(ConsentRecord.leaderboard_visible, False).is_(True),
            )
            .group_by(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                VolunteerProfile.category,
                ConsentRecord.leaderboard_visible,
                ConsentRecord.name_visible,
            )
            .having(func.sum(PointTransaction.total_points) > Decimal("0.00"))
        )

        if category and category.upper() not in ("ALL", "OVERALL"):
            query = query.where(VolunteerProfile.category == category.upper())

        # Count total qualifying ranked volunteers
        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        # Order by total points descending, then tie-breaker
        ranked_query = (
            query.order_by(
                desc("total_points"),
                "first_awarded_at",
                VolunteerProfile.id,
            )
            .offset(skip)
            .limit(limit)
        )
        rows_res = await db.execute(ranked_query)
        rows = rows_res.all()

        results: list[dict[str, object]] = []
        for idx, r in enumerate(rows):
            rank = skip + idx + 1
            is_anon = not bool(r.name_visible)
            name = "Anonymous Volunteer" if is_anon else f"{r.first_name} {r.last_name}"
            prof_id = None if is_anon else r.profile_id

            results.append(
                {
                    "rank": rank,
                    "volunteer_profile_id": prof_id,
                    "volunteer_name": name,
                    "category": r.category,
                    "total_points": Decimal(str(r.total_points)),
                    "total_hours": Decimal(str(r.total_hours)),
                    "events_attended": r.events_attended,
                    "is_anonymous": is_anon,
                }
            )

        return results, total

    async def list_active_achievement_definitions(
        self, db: AsyncSession
    ) -> list[AchievementDefinition]:
        """Fetch all active achievement criteria."""
        stmt = select(AchievementDefinition).where(AchievementDefinition.is_active.is_(True))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_volunteer_achievements(
        self, db: AsyncSession, volunteer_profile_id: uuid.UUID
    ) -> list[VolunteerAchievement]:
        """Fetch all badges earned by a volunteer."""
        stmt = (
            select(VolunteerAchievement)
            .where(VolunteerAchievement.volunteer_profile_id == volunteer_profile_id)
            .options(selectinload(VolunteerAchievement.definition))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def award_achievement(
        self, db: AsyncSession, volunteer_profile_id: uuid.UUID, achievement_id: uuid.UUID
    ) -> VolunteerAchievement:
        """Persist newly earned volunteer badge."""
        badge = VolunteerAchievement(
            volunteer_profile_id=volunteer_profile_id,
            achievement_id=achievement_id,
            awarded_at=datetime.now(UTC),
        )
        db.add(badge)
        await db.flush()
        await db.refresh(badge)
        return badge

    async def seed_default_achievements_if_empty(self, db: AsyncSession) -> None:
        """Seed standard achievement badges if catalog is empty."""
        stmt = select(func.count()).select_from(AchievementDefinition)
        res = await db.execute(stmt)
        if res.scalar_one() > 0:
            return

        defaults = [
            AchievementDefinition(
                code="FIRST_STEP",
                title="First Step",
                description="Attended and completed your first volunteering event.",
                icon_url="https://assets.maatram.org/badges/first_step.svg",
                category="MILESTONE",
                criteria_type="TOTAL_EVENTS",
                criteria_threshold=Decimal("1.00"),
                is_active=True,
            ),
            AchievementDefinition(
                code="DEDICATED_VOLUNTEER",
                title="Dedicated Volunteer",
                description="Completed 10 hours of verified volunteering service.",
                icon_url="https://assets.maatram.org/badges/dedicated.svg",
                category="HOURS",
                criteria_type="TOTAL_HOURS",
                criteria_threshold=Decimal("10.00"),
                is_active=True,
            ),
            AchievementDefinition(
                code="PILLAR_OF_MAATRAM",
                title="Pillar of Maatram",
                description="Attended and completed 10 volunteering events.",
                icon_url="https://assets.maatram.org/badges/pillar.svg",
                category="EVENTS",
                criteria_type="TOTAL_EVENTS",
                criteria_threshold=Decimal("10.00"),
                is_active=True,
            ),
            AchievementDefinition(
                code="CENTURION",
                title="Centurion",
                description="Achieved 100 hours of selfless volunteering contribution.",
                icon_url="https://assets.maatram.org/badges/centurion.svg",
                category="HOURS",
                criteria_type="TOTAL_HOURS",
                criteria_threshold=Decimal("100.00"),
                is_active=True,
            ),
        ]
        for d in defaults:
            chk = select(AchievementDefinition).where(AchievementDefinition.code == d.code)
            existing = (await db.execute(chk)).scalar_one_or_none()
            if not existing:
                db.add(d)
        await db.flush()


gamification_repository = GamificationRepository()
