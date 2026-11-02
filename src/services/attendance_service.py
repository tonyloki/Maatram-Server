"""Attendance Tracking & Hours Management domain service."""

import uuid
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import DomainException, ForbiddenException, NotFoundException
from src.core.security import ensure_utc
from src.models.admin import AuditLog
from src.models.attendance import AttendanceRecord
from src.models.events import EventRegistration
from src.models.gamification import PointTransaction
from src.models.users import User
from src.models.volunteers import VolunteerProfile
from src.repositories.attendance_repo import attendance_repository
from src.repositories.event_repo import event_repository
from src.schemas.attendance import (
    AttendanceCorrectionRequest,
    AttendanceListResponse,
    AttendanceRecordResponse,
    BulkAttendanceRequest,
    BulkAttendanceResponse,
    BulkAttendanceResultItem,
)


class AttendanceService:
    """Core business logic for volunteer check-in, check-out, duration calculation, and corrections."""

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
        """Append an immutable entry to the central audit log."""
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

    def _calculate_hours_credited(self, duration_minutes: int | None) -> Decimal:
        """Calculate credited hours with exact 2-decimal half-up rounding."""
        if duration_minutes is None or duration_minutes <= 0:
            return Decimal("0.00")
        raw_hours = Decimal(duration_minutes) / Decimal(60)
        return raw_hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _build_record_response(self, record: AttendanceRecord) -> AttendanceRecordResponse:
        """Convert ORM AttendanceRecord to response DTO."""
        hours = self._calculate_hours_credited(record.duration_minutes)
        vol_name = None
        vol_email = None
        event_title = None

        if record.registration:
            if record.registration.volunteer_profile:
                vp = record.registration.volunteer_profile
                vol_name = f"{vp.first_name} {vp.last_name}"
                if vp.user:
                    vol_email = vp.user.email
            if record.registration.event:
                event_title = record.registration.event.title

        return AttendanceRecordResponse(
            id=record.id,
            event_registration_id=record.event_registration_id,
            event_id=record.registration.event_id if record.registration else uuid.uuid4(),
            volunteer_profile_id=(
                record.registration.volunteer_profile_id if record.registration else uuid.uuid4()
            ),
            volunteer_name=vol_name,
            volunteer_email=vol_email,
            event_title=event_title,
            check_in_time=record.check_in_time,
            check_out_time=record.check_out_time,
            duration_minutes=record.duration_minutes,
            hours_credited=hours,
            status=record.status,
            verified_by_user_id=record.verified_by_user_id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            corrections_count=len(record.corrections) if record.corrections else 0,
        )

    async def check_in_volunteers(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        volunteer_profile_ids: list[uuid.UUID],
        check_in_time: datetime | None,
        current_user: User,
    ) -> list[AttendanceRecordResponse]:
        """Check in one or more volunteers for an ongoing/published event."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can log volunteer check-ins.")

        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        # Event must be ONGOING or PUBLISHED
        if event.status not in ("ONGOING", "PUBLISHED"):
            raise DomainException(
                f"Cannot check in volunteers for event in '{event.status}' status. Event must be active.",
                status_code=400,
                code="EVENT_NOT_ACTIVE",
            )

        in_time = ensure_utc(check_in_time) if check_in_time else datetime.now(UTC)
        responses: list[AttendanceRecordResponse] = []

        for vol_id in volunteer_profile_ids:
            # Verify active SELECTED registration exists under row lock
            stmt = (
                select(EventRegistration)
                .where(
                    EventRegistration.event_id == event_id,
                    EventRegistration.volunteer_profile_id == vol_id,
                )
                .with_for_update()
            )
            res = await db.execute(stmt)
            registration = res.scalar_one_or_none()

            if not registration or registration.status != "SELECTED":
                raise DomainException(
                    f"Volunteer {vol_id} is not SELECTED for this event.",
                    status_code=400,
                    code="REGISTRATION_NOT_SELECTED",
                )

            # Check existing attendance record
            existing = await attendance_repository.get_by_registration_id_with_lock(
                db, registration.id
            )
            if existing and existing.status in ("IN_PROGRESS", "COMPLETED"):
                raise DomainException(
                    f"Volunteer {vol_id} is already checked in or attendance is completed.",
                    status_code=400,
                    code="DUPLICATE_CHECKIN",
                )

            if existing:
                # Re-activate an incomplete or absent record
                existing.check_in_time = in_time
                existing.check_out_time = None
                existing.duration_minutes = None
                existing.status = "IN_PROGRESS"
                existing.verified_by_user_id = current_user.id
                record = existing
            else:
                record = await attendance_repository.create_record(
                    db=db,
                    event_registration_id=registration.id,
                    check_in_time=in_time,
                    verified_by_user_id=current_user.id,
                    status="IN_PROGRESS",
                )

            self._record_audit_log(
                db=db,
                actor_id=current_user.id,
                action="ATTENDANCE_CHECK_IN",
                resource_type="ATTENDANCE_RECORD",
                resource_id=str(record.id),
                new_state={
                    "event_id": str(event_id),
                    "volunteer_profile_id": str(vol_id),
                    "check_in_time": in_time.isoformat(),
                    "status": "IN_PROGRESS",
                },
            )

            # Eager load relationships for response
            reloaded = await attendance_repository.get_by_id(db, record.id)
            if reloaded:
                responses.append(self._build_record_response(reloaded))

        await db.commit()
        return responses

    async def check_out_volunteers(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        volunteer_profile_ids: list[uuid.UUID],
        check_out_time: datetime | None,
        current_user: User,
    ) -> list[AttendanceRecordResponse]:
        """Check out one or more volunteers and calculate duration in minutes."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can log volunteer check-outs.")

        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        out_time = ensure_utc(check_out_time) if check_out_time else datetime.now(UTC)
        responses: list[AttendanceRecordResponse] = []

        for vol_id in volunteer_profile_ids:
            record = await attendance_repository.get_by_event_and_volunteer(db, event_id, vol_id)
            if not record:
                raise DomainException(
                    f"No attendance record found for volunteer {vol_id}.",
                    status_code=400,
                    code="NO_ACTIVE_CHECKIN",
                )

            if record.status == "COMPLETED":
                raise DomainException(
                    f"Volunteer {vol_id} is already checked out.",
                    status_code=400,
                    code="ALREADY_CHECKED_OUT",
                )

            if record.status != "IN_PROGRESS":
                raise DomainException(
                    f"Volunteer {vol_id} has invalid status '{record.status}' for checkout.",
                    status_code=400,
                    code="NO_ACTIVE_CHECKIN",
                )

            check_in_utc = ensure_utc(record.check_in_time)
            if out_time < check_in_utc:
                raise DomainException(
                    "Check-out time cannot precede check-in time.",
                    status_code=400,
                    code="INVALID_CHECKOUT_TIME",
                )

            duration_minutes = int((out_time - check_in_utc).total_seconds() // 60)
            if duration_minutes < 0:
                duration_minutes = 0

            record.check_out_time = out_time
            record.duration_minutes = duration_minutes
            record.status = "COMPLETED"

            self._record_audit_log(
                db=db,
                actor_id=current_user.id,
                action="ATTENDANCE_CHECK_OUT",
                resource_type="ATTENDANCE_RECORD",
                resource_id=str(record.id),
                new_state={
                    "event_id": str(event_id),
                    "volunteer_profile_id": str(vol_id),
                    "check_out_time": out_time.isoformat(),
                    "duration_minutes": duration_minutes,
                    "status": "COMPLETED",
                },
            )

            reloaded = await attendance_repository.get_by_id(db, record.id)
            if reloaded:
                responses.append(self._build_record_response(reloaded))

        await db.commit()
        return responses

    async def correct_attendance(
        self,
        db: AsyncSession,
        record_id: uuid.UUID,
        data: AttendanceCorrectionRequest,
        current_user: User,
    ) -> AttendanceRecordResponse:
        """Apply an auditable administrative attendance correction with compensating transactions if needed."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can correct attendance records.")

        record = await attendance_repository.get_by_id_with_lock(db, record_id)
        if not record:
            raise NotFoundException("Attendance record not found.")

        new_in = ensure_utc(data.new_check_in_time)
        new_out = ensure_utc(data.new_check_out_time)

        if new_out < new_in:
            raise DomainException(
                "Corrected check-out time cannot precede check-in time.",
                status_code=400,
                code="INVALID_CHECKOUT_TIME",
            )

        new_duration = int((new_out - new_in).total_seconds() // 60)
        old_duration = record.duration_minutes

        # Check 2-hour threshold
        diff_minutes = abs(new_duration - (old_duration or 0))
        super_admin_approved_by: uuid.UUID | None = None

        if diff_minutes > settings.CORRECTION_SUPER_ADMIN_THRESHOLD_MINUTES:
            if current_user.role != "SUPER_ADMIN":
                raise ForbiddenException(
                    "Corrections adjusting duration by more than 2 hours require SUPER_ADMIN authorization.",
                    code="SUPER_ADMIN_REQUIRED",
                )
            super_admin_approved_by = current_user.id

        # Record correction log
        corr_entry = await attendance_repository.create_correction(
            db=db,
            attendance_record_id=record.id,
            admin_id=current_user.id,
            old_check_in_time=record.check_in_time,
            new_check_in_time=new_in,
            old_check_out_time=record.check_out_time,
            new_check_out_time=new_out,
            old_duration_minutes=old_duration,
            new_duration_minutes=new_duration,
            reason=data.reason,
            super_admin_approved_by=super_admin_approved_by,
        )
        if record.corrections is not None:
            record.corrections.append(corr_entry)
        else:
            record.corrections = [corr_entry]

        old_state = {
            "check_in_time": record.check_in_time.isoformat() if record.check_in_time else None,
            "check_out_time": record.check_out_time.isoformat() if record.check_out_time else None,
            "duration_minutes": record.duration_minutes,
            "status": record.status,
        }

        # Update primary record
        record.check_in_time = new_in
        record.check_out_time = new_out
        record.duration_minutes = new_duration
        record.status = "COMPLETED"

        self._record_audit_log(
            db=db,
            actor_id=current_user.id,
            action="ATTENDANCE_CORRECTED",
            resource_type="ATTENDANCE_RECORD",
            resource_id=str(record.id),
            old_state=old_state,
            new_state={
                "check_in_time": new_in.isoformat(),
                "check_out_time": new_out.isoformat(),
                "duration_minutes": new_duration,
                "status": "COMPLETED",
            },
            reason=data.reason,
        )

        # Check if gamification points were already awarded for this event
        event_id = record.registration.event_id
        vol_profile_id = record.registration.volunteer_profile_id

        stmt = select(PointTransaction).where(
            PointTransaction.event_id == event_id,
            PointTransaction.volunteer_profile_id == vol_profile_id,
            PointTransaction.transaction_type == "EVENT_COMPLETION",
        )
        tx_res = await db.execute(stmt)
        original_tx = tx_res.scalar_one_or_none()

        if original_tx:
            # Event was already completed and points awarded. Generate compensating transaction!
            old_hours = self._calculate_hours_credited(old_duration)
            new_hours = self._calculate_hours_credited(new_duration)

            old_qualifying = (old_duration or 0) >= settings.EVENT_QUALIFICATION_MIN_MINUTES
            new_qualifying = new_duration >= settings.EVENT_QUALIFICATION_MIN_MINUTES

            old_event_points = Decimal("10.00") if old_qualifying else Decimal("0.00")
            new_event_points = Decimal("10.00") if new_qualifying else Decimal("0.00")

            old_hour_points = (old_hours * Decimal("2.00")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            new_hour_points = (new_hours * Decimal("2.00")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            diff_event_points = new_event_points - old_event_points
            diff_hour_points = new_hour_points - old_hour_points
            diff_total_points = diff_event_points + diff_hour_points
            diff_hours = (new_hours - old_hours).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if diff_total_points != Decimal("0.00") or diff_hours != Decimal("0.00"):
                compensating_tx = PointTransaction(
                    volunteer_profile_id=vol_profile_id,
                    event_id=event_id,
                    related_transaction_id=original_tx.id,
                    event_points=diff_event_points,
                    hour_points=diff_hour_points,
                    total_points=diff_total_points,
                    hours_credited=diff_hours,
                    transaction_type="COMPENSATION_REVERSAL",
                    awarded_by_user_id=current_user.id,
                    reason=f"Compensating adjustment for attendance correction: {data.reason}",
                    cycle_year=original_tx.cycle_year,
                )
                db.add(compensating_tx)

                self._record_audit_log(
                    db=db,
                    actor_id=current_user.id,
                    action="POINT_LEDGER_COMPENSATING_ADJUSTMENT",
                    resource_type="POINT_TRANSACTION",
                    resource_id=str(compensating_tx.id),
                    new_state={
                        "related_transaction_id": str(original_tx.id),
                        "diff_total_points": str(diff_total_points),
                        "diff_hours": str(diff_hours),
                    },
                    reason=data.reason,
                )

        await db.commit()
        reloaded = await attendance_repository.get_by_id(db, record.id)
        if not reloaded:
            raise NotFoundException("Attendance record not found after update.")
        return self._build_record_response(reloaded)

    async def bulk_attendance(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        data: BulkAttendanceRequest,
        current_user: User,
    ) -> BulkAttendanceResponse:
        """Process bulk check-in or check-out atomically."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can execute bulk attendance.")

        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        results: list[BulkAttendanceResultItem] = []
        successful = 0
        failed = 0

        timestamp = ensure_utc(data.timestamp) if data.timestamp else datetime.now(UTC)

        for vol_id in data.volunteer_profile_ids:
            try:
                # Use a savepoint per item so individual errors can be reported
                async with db.begin_nested():
                    if data.action == "CHECK_IN":
                        stmt = select(EventRegistration).where(
                            EventRegistration.event_id == event_id,
                            EventRegistration.volunteer_profile_id == vol_id,
                        )
                        res = await db.execute(stmt)
                        reg = res.scalar_one_or_none()
                        if not reg or reg.status != "SELECTED":
                            raise DomainException(
                                "Volunteer is not SELECTED for this event.",
                                status_code=400,
                                code="REGISTRATION_NOT_SELECTED",
                            )

                        existing = await attendance_repository.get_by_registration_id(db, reg.id)
                        if existing and existing.status in ("IN_PROGRESS", "COMPLETED"):
                            raise DomainException(
                                "Volunteer is already checked in or completed.",
                                status_code=400,
                                code="DUPLICATE_CHECKIN",
                            )

                        if existing:
                            existing.check_in_time = timestamp
                            existing.status = "IN_PROGRESS"
                            existing.verified_by_user_id = current_user.id
                            rec = existing
                        else:
                            rec = await attendance_repository.create_record(
                                db=db,
                                event_registration_id=reg.id,
                                check_in_time=timestamp,
                                verified_by_user_id=current_user.id,
                                status="IN_PROGRESS",
                            )

                        results.append(
                            BulkAttendanceResultItem(
                                volunteer_profile_id=vol_id,
                                success=True,
                                status="IN_PROGRESS",
                                attendance_record_id=rec.id,
                            )
                        )
                        successful += 1

                    elif data.action == "CHECK_OUT":
                        checkout_rec = await attendance_repository.get_by_event_and_volunteer(
                            db, event_id, vol_id
                        )
                        if not checkout_rec or checkout_rec.status != "IN_PROGRESS":
                            raise DomainException(
                                "No active check-in found for volunteer.",
                                status_code=400,
                                code="NO_ACTIVE_CHECKIN",
                            )

                        rec_in_utc = ensure_utc(checkout_rec.check_in_time)
                        if timestamp < rec_in_utc:
                            raise DomainException(
                                "Check-out time cannot precede check-in time.",
                                status_code=400,
                                code="INVALID_CHECKOUT_TIME",
                            )

                        dur = int((timestamp - rec_in_utc).total_seconds() // 60)
                        checkout_rec.check_out_time = timestamp
                        checkout_rec.duration_minutes = max(0, dur)
                        checkout_rec.status = "COMPLETED"

                        results.append(
                            BulkAttendanceResultItem(
                                volunteer_profile_id=vol_id,
                                success=True,
                                status="COMPLETED",
                                attendance_record_id=checkout_rec.id,
                            )
                        )
                        successful += 1

            except Exception as ex:
                err_msg = str(getattr(ex, "message", str(ex)))
                results.append(
                    BulkAttendanceResultItem(
                        volunteer_profile_id=vol_id,
                        success=False,
                        error=err_msg,
                    )
                )
                failed += 1

        self._record_audit_log(
            db=db,
            actor_id=current_user.id,
            action=f"BULK_ATTENDANCE_{data.action}",
            resource_type="EVENT",
            resource_id=str(event_id),
            new_state={
                "action": data.action,
                "total_requested": len(data.volunteer_profile_ids),
                "successful_count": successful,
                "failed_count": failed,
            },
        )
        await db.commit()

        return BulkAttendanceResponse(
            action=data.action,
            total_requested=len(data.volunteer_profile_ids),
            successful_count=successful,
            failed_count=failed,
            results=results,
        )

    async def list_event_attendance(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        status: str | None,
        page: int,
        page_size: int,
        current_user: User,
    ) -> AttendanceListResponse:
        """List attendance records for an event with pagination."""
        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        # Non-admins can only see attendance if they are participating
        skip = (page - 1) * page_size
        records, total = await attendance_repository.list_by_event(
            db=db,
            event_id=event_id,
            status=status,
            skip=skip,
            limit=page_size,
        )

        items = [self._build_record_response(r) for r in records]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return AttendanceListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def list_volunteer_attendance(
        self,
        db: AsyncSession,
        current_user: User,
        page: int = 1,
        page_size: int = 50,
    ) -> AttendanceListResponse:
        """List personal attendance records for the authenticated volunteer."""
        vp_stmt = select(VolunteerProfile).where(VolunteerProfile.user_id == current_user.id)
        vp_res = await db.execute(vp_stmt)
        profile = vp_res.scalar_one_or_none()

        if not profile:
            raise NotFoundException("Volunteer profile not found.")

        skip = (page - 1) * page_size
        records, total = await attendance_repository.list_by_volunteer(
            db=db,
            volunteer_profile_id=profile.id,
            skip=skip,
            limit=page_size,
        )

        items = [self._build_record_response(r) for r in records]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return AttendanceListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


attendance_service = AttendanceService()
