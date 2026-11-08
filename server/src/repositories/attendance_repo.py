"""Attendance Tracking & Hours Management persistence repository."""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.attendance import AttendanceCorrection, AttendanceRecord
from src.models.events import EventRegistration
from src.models.volunteers import VolunteerProfile


class AttendanceRepository:
    """Database persistence abstraction for volunteer attendance logs and administrative corrections."""

    async def create_record(
        self,
        db: AsyncSession,
        event_registration_id: uuid.UUID,
        check_in_time: datetime,
        verified_by_user_id: uuid.UUID | None = None,
        status: str = "IN_PROGRESS",
    ) -> AttendanceRecord:
        """Create and persist a new attendance record."""
        record = AttendanceRecord(
            event_registration_id=event_registration_id,
            check_in_time=check_in_time,
            verified_by_user_id=verified_by_user_id,
            status=status,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    async def get_by_id(self, db: AsyncSession, record_id: uuid.UUID) -> AttendanceRecord | None:
        """Fetch attendance record by ID with eager loading."""
        stmt = (
            select(AttendanceRecord)
            .where(AttendanceRecord.id == record_id)
            .options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_lock(
        self, db: AsyncSession, record_id: uuid.UUID
    ) -> AttendanceRecord | None:
        """Fetch attendance record with exclusive row-level lock (FOR UPDATE)."""
        stmt = (
            select(AttendanceRecord)
            .where(AttendanceRecord.id == record_id)
            .with_for_update()
            .options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_registration_id(
        self, db: AsyncSession, registration_id: uuid.UUID
    ) -> AttendanceRecord | None:
        """Fetch attendance record for a specific registration."""
        stmt = (
            select(AttendanceRecord)
            .where(AttendanceRecord.event_registration_id == registration_id)
            .options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_registration_id_with_lock(
        self, db: AsyncSession, registration_id: uuid.UUID
    ) -> AttendanceRecord | None:
        """Fetch attendance record for a registration with exclusive row lock."""
        stmt = (
            select(AttendanceRecord)
            .where(AttendanceRecord.event_registration_id == registration_id)
            .with_for_update()
            .options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_event_and_volunteer(
        self, db: AsyncSession, event_id: uuid.UUID, volunteer_profile_id: uuid.UUID
    ) -> AttendanceRecord | None:
        """Fetch attendance record for a volunteer at a specific event."""
        stmt = (
            select(AttendanceRecord)
            .join(EventRegistration, AttendanceRecord.event_registration_id == EventRegistration.id)
            .where(
                EventRegistration.event_id == event_id,
                EventRegistration.volunteer_profile_id == volunteer_profile_id,
            )
            .options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_registrations_batch_with_lock(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        volunteer_profile_ids: list[uuid.UUID],
    ) -> list[EventRegistration]:
        """Fetch registrations for multiple volunteers at an event with deterministic sort and row locks."""
        if not volunteer_profile_ids:
            return []
        sorted_ids = sorted(volunteer_profile_ids, key=lambda x: str(x))
        stmt = (
            select(EventRegistration)
            .where(
                EventRegistration.event_id == event_id,
                EventRegistration.volunteer_profile_id.in_(sorted_ids),
            )
            .order_by(EventRegistration.volunteer_profile_id)
            .with_for_update()
            .options(
                selectinload(EventRegistration.volunteer_profile).selectinload(VolunteerProfile.user),
                selectinload(EventRegistration.event),
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_records_batch_by_registrations_with_lock(
        self,
        db: AsyncSession,
        registration_ids: list[uuid.UUID],
    ) -> list[AttendanceRecord]:
        """Fetch attendance records for multiple registrations with row locks."""
        if not registration_ids:
            return []
        sorted_ids = sorted(registration_ids, key=lambda x: str(x))
        stmt = (
            select(AttendanceRecord)
            .where(AttendanceRecord.event_registration_id.in_(sorted_ids))
            .order_by(AttendanceRecord.event_registration_id)
            .with_for_update()
            .options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_records_batch_by_event_and_volunteers_with_lock(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        volunteer_profile_ids: list[uuid.UUID],
    ) -> list[AttendanceRecord]:
        """Fetch attendance records for multiple volunteers at an event with row locks."""
        if not volunteer_profile_ids:
            return []
        sorted_ids = sorted(volunteer_profile_ids, key=lambda x: str(x))
        stmt = (
            select(AttendanceRecord)
            .join(EventRegistration, AttendanceRecord.event_registration_id == EventRegistration.id)
            .where(
                EventRegistration.event_id == event_id,
                EventRegistration.volunteer_profile_id.in_(sorted_ids),
            )
            .order_by(EventRegistration.volunteer_profile_id)
            .with_for_update()
            .options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_event(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AttendanceRecord], int]:
        """List attendance records for an event with pagination and optional status filter."""
        base_query = (
            select(AttendanceRecord)
            .join(EventRegistration, AttendanceRecord.event_registration_id == EventRegistration.id)
            .where(EventRegistration.event_id == event_id)
        )
        if status:
            base_query = base_query.where(AttendanceRecord.status == status)

        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = (
            base_query.options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
            .order_by(AttendanceRecord.check_in_time.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    async def list_by_volunteer(
        self,
        db: AsyncSession,
        volunteer_profile_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AttendanceRecord], int]:
        """List attendance records for a volunteer across all events."""
        base_query = (
            select(AttendanceRecord)
            .join(EventRegistration, AttendanceRecord.event_registration_id == EventRegistration.id)
            .where(EventRegistration.volunteer_profile_id == volunteer_profile_id)
        )

        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = (
            base_query.options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
                selectinload(AttendanceRecord.corrections),
            )
            .order_by(AttendanceRecord.check_in_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    async def list_in_progress_for_event(
        self, db: AsyncSession, event_id: uuid.UUID
    ) -> list[AttendanceRecord]:
        """List all active in-progress attendance records for an event."""
        stmt = (
            select(AttendanceRecord)
            .join(EventRegistration, AttendanceRecord.event_registration_id == EventRegistration.id)
            .where(
                EventRegistration.event_id == event_id,
                AttendanceRecord.status == "IN_PROGRESS",
            )
            .options(
                selectinload(AttendanceRecord.registration)
                .selectinload(EventRegistration.volunteer_profile)
                .selectinload(VolunteerProfile.user),
                selectinload(AttendanceRecord.registration).selectinload(EventRegistration.event),
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_correction(
        self,
        db: AsyncSession,
        attendance_record_id: uuid.UUID,
        admin_id: uuid.UUID,
        old_check_in_time: datetime,
        new_check_in_time: datetime,
        old_check_out_time: datetime | None,
        new_check_out_time: datetime,
        old_duration_minutes: int | None,
        new_duration_minutes: int,
        reason: str,
        super_admin_approved_by: uuid.UUID | None = None,
    ) -> AttendanceCorrection:
        """Create and persist an auditable attendance correction."""
        correction = AttendanceCorrection(
            attendance_record_id=attendance_record_id,
            admin_id=admin_id,
            old_check_in_time=old_check_in_time,
            new_check_in_time=new_check_in_time,
            old_check_out_time=old_check_out_time,
            new_check_out_time=new_check_out_time,
            old_duration_minutes=old_duration_minutes,
            new_duration_minutes=new_duration_minutes,
            reason=reason,
            super_admin_approved_by=super_admin_approved_by,
        )
        db.add(correction)
        await db.flush()
        await db.refresh(correction)
        return correction


attendance_repository = AttendanceRepository()
