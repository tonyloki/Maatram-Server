"""Gamification Engine, Decimal Points & Leaderboards domain service."""

import uuid
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.exceptions import DomainException, ForbiddenException, NotFoundException
from src.models.admin import AuditLog
from src.models.attendance import AttendanceRecord
from src.models.communications import CommunicationJob
from src.models.events import Event, EventRegistration
from src.models.gamification import PointTransaction, VolunteerAchievement
from src.models.users import User
from src.models.volunteers import VolunteerProfile
from src.repositories.event_repo import event_repository
from src.repositories.gamification_repo import gamification_repository
from src.schemas.gamification import (
    AchievementDefinitionResponse,
    AttendeeCompletionPreview,
    EventCompletionPreviewResponse,
    EventCompletionResponse,
    GamificationSummaryResponse,
    LeaderboardItemResponse,
    LeaderboardResponse,
    PointAdjustmentRequest,
    PointLedgerResponse,
    PointTransactionResponse,
    VolunteerAchievementsListResponse,
)


class GamificationService:
    """Core domain logic for exact decimal point scoring, append-only ledgers, event finalization, and leaderboards."""

    def _record_audit_log(
        self,
        db: AsyncSession,
        actor_id: uuid.UUID | None,
        action: str,
        resource_type: str,
        resource_id: str,
        old_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
        reason: str | None = None,
    ) -> None:
        """Record an immutable audit log entry."""
        log = AuditLog(
            actor_user_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_state=old_state,
            new_state=new_state,
            reason=reason,
        )
        db.add(log)

    def calculate_hours_credited(self, duration_minutes: int | None) -> Decimal:
        """Calculate credited hours from raw minutes using 2-decimal ROUND_HALF_UP."""
        if duration_minutes is None or duration_minutes <= 0:
            return Decimal("0.00")
        raw_hours = Decimal(duration_minutes) / Decimal(60)
        return raw_hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_scoring(
        self, duration_minutes: int | None, is_qualifying: bool = True
    ) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        """Calculate authoritative points P = (E * 10) + (H * 2).

        Returns:
            (event_points, hour_points, total_points, hours_credited)
        """
        if duration_minutes is None or duration_minutes <= 0:
            return Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00")

        hours_credited = self.calculate_hours_credited(duration_minutes)
        event_points = Decimal("10.00") if is_qualifying else Decimal("0.00")
        hour_points = (hours_credited * Decimal("2.00")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_points = event_points + hour_points
        return event_points, hour_points, total_points, hours_credited

    async def get_completion_preview(
        self, db: AsyncSession, event_id: uuid.UUID, current_user: User
    ) -> EventCompletionPreviewResponse:
        """Generate dry-run completion preview with calculated decimal points and warnings."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can view event completion preview.")

        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        # Query all SELECTED registrations with eager relations
        stmt = (
            select(EventRegistration)
            .where(
                EventRegistration.event_id == event_id,
                EventRegistration.status == "SELECTED",
            )
            .options(
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.consent_record
                ),
                selectinload(EventRegistration.attendance),
            )
        )
        reg_res = await db.execute(stmt)
        registrations = list(reg_res.scalars().all())

        total_selected = len(registrations)
        total_attended = 0
        total_incomplete = 0
        total_absent = 0
        total_hours = Decimal("0.00")
        total_points = Decimal("0.00")
        thank_you_count = 0
        attendee_previews: list[AttendeeCompletionPreview] = []

        for reg in registrations:
            vp = reg.volunteer_profile
            vol_name = f"{vp.first_name} {vp.last_name}" if vp else "Unknown Volunteer"
            category = vp.category if vp else "STUDENT"
            att = reg.attendance
            warnings: list[str] = []

            if not att:
                total_absent += 1
                warnings.append("Volunteer did not check in; will be marked ABSENT with 0 points.")
                attendee_previews.append(
                    AttendeeCompletionPreview(
                        volunteer_profile_id=reg.volunteer_profile_id,
                        volunteer_name=vol_name,
                        category=category,
                        attendance_status="ABSENT",
                        duration_minutes=None,
                        hours_credited=Decimal("0.00"),
                        event_points=Decimal("0.00"),
                        hour_points=Decimal("0.00"),
                        total_points=Decimal("0.00"),
                        is_qualifying=False,
                        warnings=warnings,
                    )
                )
                continue

            if att.status == "IN_PROGRESS":
                total_incomplete += 1
                warnings.append(
                    "Missing check-out; will be marked INCOMPLETE with 0 hours unless checked out or corrected."
                )
                attendee_previews.append(
                    AttendeeCompletionPreview(
                        volunteer_profile_id=reg.volunteer_profile_id,
                        volunteer_name=vol_name,
                        category=category,
                        attendance_status="INCOMPLETE",
                        duration_minutes=None,
                        hours_credited=Decimal("0.00"),
                        event_points=Decimal("0.00"),
                        hour_points=Decimal("0.00"),
                        total_points=Decimal("0.00"),
                        is_qualifying=False,
                        warnings=warnings,
                    )
                )
                continue

            if att.status == "COMPLETED":
                dur = att.duration_minutes or 0
                is_qual = dur >= settings.EVENT_QUALIFICATION_MIN_MINUTES
                if not is_qual:
                    warnings.append(
                        f"Duration {dur} mins is below qualifying threshold ({settings.EVENT_QUALIFICATION_MIN_MINUTES} mins); 0 event attendance points awarded."
                    )
                ev_pts, hr_pts, tot_pts, hrs = self.calculate_scoring(dur, is_qualifying=is_qual)
                total_attended += 1
                total_hours += hrs
                total_points += tot_pts

                # Check thank-you email consent
                if vp and vp.consent_record and vp.consent_record.thank_you_emails:
                    thank_you_count += 1

                attendee_previews.append(
                    AttendeeCompletionPreview(
                        volunteer_profile_id=reg.volunteer_profile_id,
                        volunteer_name=vol_name,
                        category=category,
                        attendance_status="COMPLETED",
                        duration_minutes=dur,
                        hours_credited=hrs,
                        event_points=ev_pts,
                        hour_points=hr_pts,
                        total_points=tot_pts,
                        is_qualifying=is_qual,
                        warnings=warnings,
                    )
                )

        draft_linkedin = (
            f"Proud of our passionate volunteers who contributed {total_hours} service hours "
            f"at '{event.title}'! Together, we empower underprivileged students through education "
            f"and mentorship. Thank you for championing social change with Maatram Foundation. "
            f"#MaatramVolunteering #SocialImpact #EducationForAll"
        )

        return EventCompletionPreviewResponse(
            event_id=event.id,
            event_title=event.title,
            event_status=event.status,
            total_selected=total_selected,
            total_attended=total_attended,
            total_incomplete=total_incomplete,
            total_absent=total_absent,
            total_hours_credited=total_hours,
            total_points_to_award=total_points,
            thank_you_recipients_count=thank_you_count,
            attendees=attendee_previews,
            draft_linkedin_copy=draft_linkedin,
        )

    async def complete_and_award_event(
        self, db: AsyncSession, event_id: uuid.UUID, current_user: User
    ) -> EventCompletionResponse:
        """Atomic event completion finalization with row lock, exactly-once ledger insertion, and outbox jobs."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can finalize event completion.")

        # Pessimistic row-level lock on event record
        stmt = select(Event).where(Event.id == event_id).with_for_update()
        res = await db.execute(stmt)
        event = res.scalar_one_or_none()

        if not event:
            raise NotFoundException("Event not found.")

        # Idempotency / Exactly-Once check: verify no point_transactions already exist
        already_awarded = await gamification_repository.has_awarded_event_points(db, event_id)
        if already_awarded:
            raise DomainException(
                "Gamification points have already been awarded for this event.",
                status_code=400,
                code="POINTS_ALREADY_AWARDED",
            )

        if event.status == "COMPLETED":
            # If status is COMPLETED but no points awarded (e.g. edge case), proceed to award
            pass
        elif event.status in ("ONGOING", "REGISTRATION_CLOSED", "PUBLISHED"):
            event.status = "COMPLETED"
        else:
            raise DomainException(
                f"Cannot complete event in '{event.status}' status.",
                status_code=400,
                code="INVALID_STATE_TRANSITION",
            )

        # Ensure default achievement definitions exist
        await gamification_repository.seed_default_achievements_if_empty(db)

        cycle_year = event.start_time.year

        # Fetch selected registrations
        reg_stmt = (
            select(EventRegistration)
            .where(
                EventRegistration.event_id == event_id,
                EventRegistration.status == "SELECTED",
            )
            .options(
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.consent_record
                ),
                selectinload(EventRegistration.attendance),
            )
        )
        reg_res = await db.execute(reg_stmt)
        registrations = list(reg_res.scalars().all())

        total_awarded = 0
        total_points = Decimal("0.00")
        total_hours = Decimal("0.00")
        outbox_count = 0
        achievements_count = 0

        for reg in registrations:
            vp = reg.volunteer_profile
            att = reg.attendance

            if not att:
                # Mark absent
                absent_rec = AttendanceRecord(
                    event_registration_id=reg.id,
                    check_in_time=event.start_time,
                    check_out_time=event.start_time,
                    duration_minutes=0,
                    status="ABSENT",
                    verified_by_user_id=current_user.id,
                )
                db.add(absent_rec)
                continue

            if att.status == "IN_PROGRESS":
                # Incomplete check-out
                att.status = "INCOMPLETE"
                att.duration_minutes = 0
                continue

            if att.status == "COMPLETED":
                dur = att.duration_minutes or 0
                if dur <= 0:
                    continue

                is_qual = dur >= settings.EVENT_QUALIFICATION_MIN_MINUTES
                ev_pts, hr_pts, tot_pts, hrs = self.calculate_scoring(dur, is_qualifying=is_qual)

                # Exactly-once point ledger entry
                tx = PointTransaction(
                    volunteer_profile_id=reg.volunteer_profile_id,
                    event_id=event.id,
                    event_points=ev_pts,
                    hour_points=hr_pts,
                    total_points=tot_pts,
                    hours_credited=hrs,
                    transaction_type="EVENT_COMPLETION",
                    awarded_by_user_id=current_user.id,
                    cycle_year=cycle_year,
                    reason=f"Event completion award: {event.title}",
                )
                db.add(tx)
                total_awarded += 1
                total_points += tot_pts
                total_hours += hrs

                # Evaluate and award achievements
                earned_now = await self._evaluate_volunteer_achievements(
                    db, reg.volunteer_profile_id
                )
                achievements_count += earned_now

                # Enqueue thank-you email outbox job if consent provided
                if vp and vp.consent_record and vp.consent_record.thank_you_emails and vp.user:
                    idempotency_key = f"thank_you_{event.id}_{vp.id}"
                    job = CommunicationJob(
                        channel="EMAIL",
                        recipient=vp.user.email,
                        template_name="EVENT_THANK_YOU",
                        payload={
                            "event_id": str(event.id),
                            "event_title": event.title,
                            "volunteer_name": f"{vp.first_name} {vp.last_name}",
                            "hours_credited": str(hrs),
                            "points_awarded": str(tot_pts),
                        },
                        idempotency_key=idempotency_key,
                        status="PENDING",
                    )
                    db.add(job)
                    outbox_count += 1

        self._record_audit_log(
            db=db,
            actor_id=current_user.id,
            action="EVENT_COMPLETED_AND_AWARDED",
            resource_type="EVENT",
            resource_id=str(event.id),
            new_state={
                "status": "COMPLETED",
                "volunteers_awarded": total_awarded,
                "total_points": str(total_points),
                "total_hours": str(total_hours),
                "outbox_jobs_created": outbox_count,
            },
        )

        # Single atomic database commit
        await db.commit()

        return EventCompletionResponse(
            event_id=event.id,
            status="COMPLETED",
            completed_at=datetime.now(UTC),
            total_volunteers_awarded=total_awarded,
            total_points_awarded=total_points,
            total_hours_credited=total_hours,
            outbox_jobs_created=outbox_count,
            achievements_awarded_count=achievements_count,
        )

    async def _evaluate_volunteer_achievements(
        self, db: AsyncSession, volunteer_profile_id: uuid.UUID
    ) -> int:
        """Evaluate criteria and award eligible achievements to a volunteer."""
        # Query total lifetime completed events and verified hours
        stmt = select(
            func.count(func.distinct(PointTransaction.event_id)),
            func.coalesce(func.sum(PointTransaction.hours_credited), Decimal("0.00")),
        ).where(
            PointTransaction.volunteer_profile_id == volunteer_profile_id,
            PointTransaction.transaction_type == "EVENT_COMPLETION",
        )
        res = await db.execute(stmt)
        events_count, hours_sum = res.one()
        total_events = events_count or 0
        total_hours = Decimal(str(hours_sum or "0.00"))

        # Fetch existing earned achievements
        existing_stmt = select(VolunteerAchievement.achievement_id).where(
            VolunteerAchievement.volunteer_profile_id == volunteer_profile_id
        )
        existing_res = await db.execute(existing_stmt)
        earned_ids = set(existing_res.scalars().all())

        # Fetch all active definitions
        definitions = await gamification_repository.list_active_achievement_definitions(db)
        awarded_count = 0

        for defn in definitions:
            if defn.id in earned_ids:
                continue

            should_award = False
            if defn.criteria_type == "TOTAL_EVENTS" and total_events >= defn.criteria_threshold:
                should_award = True
            elif defn.criteria_type == "TOTAL_HOURS" and total_hours >= defn.criteria_threshold:
                should_award = True

            if should_award:
                badge = VolunteerAchievement(
                    volunteer_profile_id=volunteer_profile_id,
                    achievement_id=defn.id,
                    awarded_at=datetime.now(UTC),
                )
                db.add(badge)
                awarded_count += 1

        return awarded_count

    async def adjust_points(
        self, db: AsyncSession, data: PointAdjustmentRequest, current_user: User
    ) -> PointTransactionResponse:
        """Execute audited Super Admin point adjustments via compensating rows."""
        if current_user.role != "SUPER_ADMIN":
            raise ForbiddenException("Only SUPER_ADMIN users can apply manual point adjustments.")

        vp_stmt = select(VolunteerProfile).where(VolunteerProfile.id == data.volunteer_profile_id)
        vp_res = await db.execute(vp_stmt)
        if not vp_res.scalar_one_or_none():
            raise NotFoundException("Volunteer profile not found.")

        cycle_year = data.cycle_year or datetime.now(UTC).year
        total_points = (data.event_points + data.hour_points).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        tx = PointTransaction(
            volunteer_profile_id=data.volunteer_profile_id,
            event_id=data.event_id,
            related_transaction_id=data.related_transaction_id,
            event_points=data.event_points,
            hour_points=data.hour_points,
            total_points=total_points,
            hours_credited=data.hours_credited,
            transaction_type="COMPENSATION_REVERSAL" if total_points < 0 else "MANUAL_ADJUSTMENT",
            awarded_by_user_id=current_user.id,
            reason=data.reason,
            cycle_year=cycle_year,
        )
        db.add(tx)

        self._record_audit_log(
            db=db,
            actor_id=current_user.id,
            action="POINT_LEDGER_MANUAL_ADJUSTMENT",
            resource_type="POINT_TRANSACTION",
            resource_id=str(tx.id),
            new_state={
                "volunteer_profile_id": str(data.volunteer_profile_id),
                "total_points": str(total_points),
                "reason": data.reason,
            },
            reason=data.reason,
        )
        await db.commit()
        await db.refresh(tx)

        return PointTransactionResponse(
            id=tx.id,
            volunteer_profile_id=tx.volunteer_profile_id,
            event_id=tx.event_id,
            related_transaction_id=tx.related_transaction_id,
            event_points=tx.event_points,
            hour_points=tx.hour_points,
            total_points=tx.total_points,
            hours_credited=tx.hours_credited,
            transaction_type=tx.transaction_type,
            reason=tx.reason,
            cycle_year=tx.cycle_year,
            created_at=tx.created_at,
        )

    async def get_leaderboard(
        self,
        db: AsyncSession,
        category: str | None,
        cycle_year: int | None,
        page: int = 1,
        page_size: int = 50,
    ) -> LeaderboardResponse:
        """Fetch multi-tier leaderboard rankings with affirmative privacy consent masking."""
        year = cycle_year or datetime.now(UTC).year
        skip = (page - 1) * page_size

        rankings, total = await gamification_repository.get_leaderboard_rankings(
            db=db,
            category=category,
            cycle_year=year,
            skip=skip,
            limit=page_size,
        )

        items: list[LeaderboardItemResponse] = []
        for r in rankings:
            raw_id = r.get("volunteer_profile_id")
            prof_id = uuid.UUID(str(raw_id)) if raw_id is not None else None
            items.append(
                LeaderboardItemResponse(
                    rank=int(str(r["rank"])),
                    volunteer_profile_id=prof_id,
                    volunteer_name=str(r["volunteer_name"]),
                    category=str(r["category"]),
                    total_points=Decimal(str(r["total_points"])),
                    events_attended=int(str(r["events_attended"])),
                    total_hours=Decimal(str(r["total_hours"])),
                    is_anonymous=bool(r["is_anonymous"]),
                )
            )
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return LeaderboardResponse(
            cycle_year=year,
            category=category.upper() if category else "ALL",
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_my_summary(
        self, db: AsyncSession, current_user: User, cycle_year: int | None = None
    ) -> GamificationSummaryResponse:
        """Retrieve authenticated volunteer's gamification overview."""
        vp_stmt = select(VolunteerProfile).where(VolunteerProfile.user_id == current_user.id)
        vp_res = await db.execute(vp_stmt)
        profile = vp_res.scalar_one_or_none()

        if not profile:
            raise NotFoundException("Volunteer profile not found.")

        year = cycle_year or datetime.now(UTC).year
        pts, hrs, evs, badges = await gamification_repository.get_volunteer_summary(
            db=db, volunteer_profile_id=profile.id, cycle_year=year
        )

        # Determine volunteer rank on overall leaderboard
        rank_stmt = (
            select(func.count())
            .select_from(PointTransaction)
            .where(
                PointTransaction.cycle_year == year,
            )
            .group_by(PointTransaction.volunteer_profile_id)
            .having(func.sum(PointTransaction.total_points) > pts)
        )
        rank_res = await db.execute(rank_stmt)
        ahead_count = len(rank_res.all())
        current_rank = ahead_count + 1 if pts > Decimal("0.00") else None

        return GamificationSummaryResponse(
            volunteer_profile_id=profile.id,
            total_points=pts,
            total_hours=hrs,
            completed_events_count=evs,
            badges_earned_count=badges,
            rank=current_rank,
            cycle_year=year,
        )

    async def get_my_ledger(
        self,
        db: AsyncSession,
        current_user: User,
        cycle_year: int | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PointLedgerResponse:
        """Fetch itemized append-only point transactions for the authenticated volunteer."""
        vp_stmt = select(VolunteerProfile).where(VolunteerProfile.user_id == current_user.id)
        vp_res = await db.execute(vp_stmt)
        profile = vp_res.scalar_one_or_none()

        if not profile:
            raise NotFoundException("Volunteer profile not found.")

        skip = (page - 1) * page_size
        items, total, net_points = await gamification_repository.get_volunteer_ledger(
            db=db,
            volunteer_profile_id=profile.id,
            cycle_year=cycle_year,
            skip=skip,
            limit=page_size,
        )

        tx_items = [
            PointTransactionResponse(
                id=tx.id,
                volunteer_profile_id=tx.volunteer_profile_id,
                event_id=tx.event_id,
                related_transaction_id=tx.related_transaction_id,
                event_points=tx.event_points,
                hour_points=tx.hour_points,
                total_points=tx.total_points,
                hours_credited=tx.hours_credited,
                transaction_type=tx.transaction_type,
                reason=tx.reason,
                cycle_year=tx.cycle_year,
                created_at=tx.created_at,
            )
            for tx in items
        ]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return PointLedgerResponse(
            items=tx_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            net_points=net_points,
        )

    async def get_my_achievements(
        self, db: AsyncSession, current_user: User
    ) -> VolunteerAchievementsListResponse:
        """List all available and earned achievements for the authenticated volunteer."""
        vp_stmt = select(VolunteerProfile).where(VolunteerProfile.user_id == current_user.id)
        vp_res = await db.execute(vp_stmt)
        profile = vp_res.scalar_one_or_none()

        if not profile:
            raise NotFoundException("Volunteer profile not found.")

        await gamification_repository.seed_default_achievements_if_empty(db)

        all_defs = await gamification_repository.list_active_achievement_definitions(db)
        earned = await gamification_repository.get_volunteer_achievements(db, profile.id)
        earned_map = {e.achievement_id: e.awarded_at for e in earned}

        items: list[AchievementDefinitionResponse] = []
        for d in all_defs:
            is_earned = d.id in earned_map
            items.append(
                AchievementDefinitionResponse(
                    id=d.id,
                    code=d.code,
                    title=d.title,
                    description=d.description,
                    icon_url=d.icon_url,
                    category=d.category,
                    criteria_type=d.criteria_type,
                    criteria_threshold=d.criteria_threshold,
                    is_active=d.is_active,
                    is_earned=is_earned,
                    awarded_at=earned_map.get(d.id),
                )
            )

        return VolunteerAchievementsListResponse(
            items=items,
            total_earned=len(earned),
            total_available=len(all_defs),
        )


gamification_service = GamificationService()
