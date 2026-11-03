"""Event persistence repository abstraction."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.events import Event, EventRegistration


class EventRepository:
    """Database persistence abstraction for events and volunteering opportunities."""

    async def create(
        self, db: AsyncSession, data: dict[str, Any], created_by_user_id: uuid.UUID
    ) -> Event:
        """Create and persist a new event record."""
        event = Event(
            title=data["title"],
            description=data["description"],
            category=data["category"],
            mode=data["mode"],
            location=data["location"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            timezone=data.get("timezone", "Asia/Kolkata"),
            capacity_required=data["capacity_required"],
            registration_deadline=data["registration_deadline"],
            status=data.get("status", "DRAFT"),
            cover_media_id=data.get("cover_media_id"),
            created_by_user_id=created_by_user_id,
        )
        db.add(event)
        await db.flush()
        await db.refresh(event)
        return event

    async def get_by_id(self, db: AsyncSession, event_id: uuid.UUID) -> Event | None:
        """Fetch event by ID."""
        stmt = (
            select(Event)
            .where(Event.id == event_id)
            .options(
                selectinload(Event.created_by),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_update(self, db: AsyncSession, event_id: uuid.UUID) -> Event | None:
        """Fetch event by ID with pessimistic row-level exclusive lock (FOR UPDATE)."""
        stmt = (
            select(Event)
            .where(Event.id == event_id)
            .with_for_update()
            .options(
                selectinload(Event.created_by),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_events(
        self,
        db: AsyncSession,
        status: str | None = None,
        category: str | None = None,
        mode: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
        include_drafts: bool = False,
        published_only: bool = False,
    ) -> tuple[list[Event], int]:
        """List events with multi-field filtering and pagination."""
        stmt = select(Event)

        # Status visibility rules
        if published_only:
            stmt = stmt.where(Event.status == "PUBLISHED")
        elif not include_drafts:
            stmt = stmt.where(Event.status != "DRAFT")
            if status:
                stmt = stmt.where(Event.status == status)
        elif status:
            stmt = stmt.where(Event.status == status)

        if category:
            stmt = stmt.where(Event.category == category)
        if mode:
            stmt = stmt.where(Event.mode == mode)
        if from_date:
            stmt = stmt.where(Event.start_time >= from_date)
        if to_date:
            stmt = stmt.where(Event.start_time <= to_date)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Event.title.ilike(pattern),
                    Event.description.ilike(pattern),
                    Event.location.ilike(pattern),
                )
            )

        # Count total matching
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        # Paginate results ordered by start_time
        stmt = stmt.order_by(Event.start_time.asc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def update(self, db: AsyncSession, event: Event, data: dict[str, Any]) -> Event:
        """Update mutable fields on an event record."""
        for key, val in data.items():
            if hasattr(event, key) and val is not None:
                setattr(event, key, val)
        await db.flush()
        await db.refresh(event)
        return event

    async def update_status(
        self,
        db: AsyncSession,
        event: Event,
        new_status: str,
        actor_id: uuid.UUID,
        reason: str | None = None,
    ) -> Event:
        """Mutate event status state machine."""
        event.status = new_status
        await db.flush()
        await db.refresh(event)
        return event

    async def count_registered(self, db: AsyncSession, event_id: uuid.UUID) -> int:
        """Count registrations with SUBSCRIBED or SELECTED status."""
        stmt = (
            select(func.count(EventRegistration.id))
            .where(EventRegistration.event_id == event_id)
            .where(EventRegistration.status.in_(["SUBSCRIBED", "SELECTED"]))
        )
        res = await db.execute(stmt)
        return res.scalar() or 0

    async def count_selected(self, db: AsyncSession, event_id: uuid.UUID) -> int:
        """Count registrations with SELECTED status."""
        stmt = (
            select(func.count(EventRegistration.id))
            .where(EventRegistration.event_id == event_id)
            .where(EventRegistration.status == "SELECTED")
        )
        res = await db.execute(stmt)
        return res.scalar() or 0

    async def count_waitlisted(self, db: AsyncSession, event_id: uuid.UUID) -> int:
        """Count registrations with WAITLISTED status."""
        stmt = (
            select(func.count(EventRegistration.id))
            .where(EventRegistration.event_id == event_id)
            .where(EventRegistration.status == "WAITLISTED")
        )
        res = await db.execute(stmt)
        return res.scalar() or 0

    async def get_registration_counts(
        self, db: AsyncSession, event_id: uuid.UUID
    ) -> dict[str, int]:
        """Compute aggregated registration status tallies in a single query."""
        stmt = (
            select(EventRegistration.status, func.count(EventRegistration.id))
            .where(EventRegistration.event_id == event_id)
            .group_by(EventRegistration.status)
        )
        res = await db.execute(stmt)
        counts: dict[str, int] = {str(row[0]): int(row[1]) for row in res.all()}

        selected = counts.get("SELECTED", 0)
        subscribed = counts.get("SUBSCRIBED", 0)
        waitlisted = counts.get("WAITLISTED", 0)
        registered = selected + subscribed

        return {
            "registered": registered,
            "selected": selected,
            "waitlisted": waitlisted,
        }


event_repository = EventRepository()
