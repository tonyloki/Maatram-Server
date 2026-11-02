"""Event Registration persistence repository abstraction."""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.events import Event, EventRegistration, RegistrationHistory
from src.models.volunteers import VolunteerProfile


class RegistrationRepository:
    """Database persistence abstraction for event registrations and state transition history."""

    async def create(
        self,
        db: AsyncSession,
        volunteer_profile_id: uuid.UUID,
        event_id: uuid.UUID,
        status: str = "SUBSCRIBED",
        notes: str | None = None,
    ) -> EventRegistration:
        """Create and persist a new event registration."""
        registration = EventRegistration(
            volunteer_profile_id=volunteer_profile_id,
            event_id=event_id,
            status=status,
            notes=notes,
        )
        db.add(registration)
        await db.flush()
        await db.refresh(registration)
        return registration

    async def get_by_id(
        self, db: AsyncSession, registration_id: uuid.UUID
    ) -> EventRegistration | None:
        """Fetch registration by ID with related event, volunteer, and history eager loaded."""
        stmt = (
            select(EventRegistration)
            .where(EventRegistration.id == registration_id)
            .options(
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(EventRegistration.event),
                selectinload(EventRegistration.history_entries),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_lock(
        self, db: AsyncSession, registration_id: uuid.UUID
    ) -> EventRegistration | None:
        """Fetch registration by ID with exclusive row-level lock (FOR UPDATE)."""
        stmt = (
            select(EventRegistration)
            .where(EventRegistration.id == registration_id)
            .with_for_update()
            .options(
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(EventRegistration.event),
                selectinload(EventRegistration.history_entries),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_volunteer_and_event(
        self, db: AsyncSession, volunteer_profile_id: uuid.UUID, event_id: uuid.UUID
    ) -> EventRegistration | None:
        """Fetch existing registration for a specific volunteer and event pair."""
        stmt = (
            select(EventRegistration)
            .where(
                EventRegistration.volunteer_profile_id == volunteer_profile_id,
                EventRegistration.event_id == event_id,
            )
            .options(
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(EventRegistration.event),
                selectinload(EventRegistration.history_entries),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_event(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        status_filter: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[EventRegistration], int]:
        """List registrations for an event with optional status filter."""
        stmt = select(EventRegistration).where(EventRegistration.event_id == event_id)
        if status_filter:
            stmt = stmt.where(EventRegistration.status == status_filter)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = (
            stmt.order_by(EventRegistration.created_at.asc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(EventRegistration.event),
                selectinload(EventRegistration.history_entries),
            )
        )
        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def list_by_volunteer(
        self,
        db: AsyncSession,
        volunteer_profile_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[EventRegistration], int]:
        """List all event registrations for a specific volunteer profile."""
        stmt = select(EventRegistration).where(
            EventRegistration.volunteer_profile_id == volunteer_profile_id
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = (
            stmt.order_by(EventRegistration.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(EventRegistration.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(EventRegistration.event),
                selectinload(EventRegistration.history_entries),
            )
        )
        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def count_selected_for_event(self, db: AsyncSession, event_id: uuid.UUID) -> int:
        """Count registrations with SELECTED status for an event."""
        stmt = (
            select(func.count(EventRegistration.id))
            .where(EventRegistration.event_id == event_id)
            .where(EventRegistration.status == "SELECTED")
        )
        res = await db.execute(stmt)
        return res.scalar() or 0

    async def count_subscribed_for_event(self, db: AsyncSession, event_id: uuid.UUID) -> int:
        """Count registrations with SUBSCRIBED status for an event."""
        stmt = (
            select(func.count(EventRegistration.id))
            .where(EventRegistration.event_id == event_id)
            .where(EventRegistration.status == "SUBSCRIBED")
        )
        res = await db.execute(stmt)
        return res.scalar() or 0

    async def count_waitlisted_for_event(self, db: AsyncSession, event_id: uuid.UUID) -> int:
        """Count registrations with WAITLISTED status for an event."""
        stmt = (
            select(func.count(EventRegistration.id))
            .where(EventRegistration.event_id == event_id)
            .where(EventRegistration.status == "WAITLISTED")
        )
        res = await db.execute(stmt)
        return res.scalar() or 0

    async def update_status(
        self,
        db: AsyncSession,
        registration: EventRegistration,
        new_status: str,
        actor_id: uuid.UUID,
        reason: str | None = None,
        selected_at: datetime | None = None,
        withdrawn_at: datetime | None = None,
    ) -> EventRegistration:
        """Mutate registration status and record timestamps."""
        old_status = registration.status
        registration.status = new_status
        if selected_at is not None:
            registration.selected_at = selected_at
        if withdrawn_at is not None:
            registration.withdrawn_at = withdrawn_at

        await self.append_history(
            db=db,
            registration_id=registration.id,
            old_status=old_status,
            new_status=new_status,
            actor_id=actor_id,
            reason=reason,
        )
        await db.flush()
        await db.refresh(registration)
        return registration

    async def append_history(
        self,
        db: AsyncSession,
        registration_id: uuid.UUID,
        old_status: str,
        new_status: str,
        actor_id: uuid.UUID,
        reason: str | None = None,
    ) -> RegistrationHistory:
        """Append an immutable audit entry to registration_history."""
        history = RegistrationHistory(
            registration_id=registration_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_user_id=actor_id,
            reason=reason,
        )
        db.add(history)
        await db.flush()
        return history

    async def get_overlapping_registrations(
        self,
        db: AsyncSession,
        volunteer_profile_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_event_id: uuid.UUID | None = None,
    ) -> list[EventRegistration]:
        """Find active registrations (SUBSCRIBED/SELECTED) for events overlapping with the window."""
        stmt = (
            select(EventRegistration)
            .join(Event, EventRegistration.event_id == Event.id)
            .where(EventRegistration.volunteer_profile_id == volunteer_profile_id)
            .where(EventRegistration.status.in_(["SUBSCRIBED", "SELECTED"]))
            .where(Event.status.notin_(["CANCELLED", "COMPLETED"]))
            .where(Event.start_time < end_time)
            .where(Event.end_time > start_time)
        )
        if exclude_event_id:
            stmt = stmt.where(Event.id != exclude_event_id)

        result = await db.execute(stmt)
        return list(result.scalars().all())


registration_repository = RegistrationRepository()
