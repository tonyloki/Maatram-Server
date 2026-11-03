"""Event Management domain service."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import (
    DomainException,
    ForbiddenException,
    NotFoundException,
)
from src.models.admin import AuditLog
from src.models.events import Event, EventRegistration, RegistrationHistory
from src.models.users import User
from src.repositories.event_repo import event_repository
from src.schemas.event import (
    EventCreateRequest,
    EventDuplicateRequest,
    EventListItem,
    EventListResponse,
    EventResponse,
    EventUpdateRequest,
)

# Canonical State Transition Matrix per BUSINESS_RULES.md & PHASE_06_EVENTS.md
VALID_EVENT_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"PUBLISHED"},
    "PUBLISHED": {"REGISTRATION_CLOSED", "ONGOING", "CANCELLED"},
    "REGISTRATION_CLOSED": {"ONGOING", "CANCELLED"},
    "ONGOING": {"COMPLETED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}


class EventService:
    """Core domain service orchestrating event lifecycle, state machine, and visibility rules."""

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
        """Helper to append an immutable audit log entry."""
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

    def _build_event_response(self, event: Event, counts: dict[str, int]) -> EventResponse:
        """Map ORM Event model and computed registration counts to EventResponse DTO."""
        registered = counts.get("registered", 0)
        selected = counts.get("selected", 0)
        waitlisted = counts.get("waitlisted", 0)
        available = max(0, event.capacity_required - registered)

        # For online events, online_meeting_url defaults to location
        online_url = event.location if event.mode == "ONLINE" else None

        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            category=event.category,
            mode=event.mode,
            location=event.location,
            online_meeting_url=online_url,
            start_time=event.start_time,
            end_time=event.end_time,
            timezone=event.timezone,
            capacity_required=event.capacity_required,
            volunteer_capacity=event.capacity_required,
            registration_deadline=event.registration_deadline,
            status=event.status,
            cover_media_id=event.cover_media_id,
            created_by_user_id=event.created_by_user_id,
            created_at=event.created_at,
            updated_at=event.updated_at,
            registered_count=registered,
            selected_count=selected,
            waitlisted_count=waitlisted,
            available_spots=available,
        )

    async def create_event(
        self, db: AsyncSession, data: EventCreateRequest, current_user: User
    ) -> EventResponse:
        """Create a new event in DRAFT state."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can create events.")

        event_dict: dict[str, Any] = {
            "title": data.title,
            "description": data.description,
            "category": data.category.value,
            "mode": data.mode.value,
            "location": data.location or data.online_meeting_url or "",
            "start_time": data.start_time,
            "end_time": data.end_time,
            "timezone": data.timezone,
            "capacity_required": data.capacity_required,
            "registration_deadline": data.registration_deadline,
            "status": "DRAFT",
            "cover_media_id": data.cover_media_id,
        }

        event = await event_repository.create(db, event_dict, current_user.id)

        self._record_audit_log(
            db=db,
            actor_id=current_user.id,
            action="EVENT_CREATED",
            resource_type="EVENT",
            resource_id=str(event.id),
            new_state={"status": event.status, "title": event.title},
        )
        await db.commit()
        await db.refresh(event)

        counts = {"registered": 0, "selected": 0, "waitlisted": 0}
        return self._build_event_response(event, counts)

    async def get_event(
        self, db: AsyncSession, event_id: uuid.UUID, current_user: User
    ) -> EventResponse:
        """Retrieve detailed event by ID with RBAC/visibility filtering."""
        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        # Non-admins cannot see DRAFT events
        if event.status == "DRAFT" and current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise NotFoundException("Event not found.")

        counts = await event_repository.get_registration_counts(db, event.id)
        return self._build_event_response(event, counts)

    async def list_events(
        self,
        db: AsyncSession,
        current_user: User,
        status: str | None = None,
        category: str | None = None,
        mode: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> EventListResponse:
        """List events with role-governed visibility and multi-field filters."""
        is_admin = current_user.role in ("ADMIN", "SUPER_ADMIN")
        skip = (page - 1) * page_size

        events, total = await event_repository.list_events(
            db=db,
            status=status,
            category=category,
            mode=mode,
            from_date=from_date,
            to_date=to_date,
            search=search,
            skip=skip,
            limit=page_size,
            include_drafts=is_admin,
            published_only=not is_admin,
        )

        event_ids = [ev.id for ev in events]
        batch_counts = await event_repository.get_batch_registration_counts(db, event_ids)

        items: list[EventListItem] = []
        for ev in events:
            counts = batch_counts.get(ev.id, {"registered": 0, "selected": 0, "waitlisted": 0})
            registered = counts.get("registered", 0)
            selected = counts.get("selected", 0)
            available = max(0, ev.capacity_required - registered)
            online_url = ev.location if ev.mode == "ONLINE" else None

            items.append(
                EventListItem(
                    id=ev.id,
                    title=ev.title,
                    category=ev.category,
                    mode=ev.mode,
                    location=ev.location,
                    online_meeting_url=online_url,
                    start_time=ev.start_time,
                    end_time=ev.end_time,
                    timezone=ev.timezone,
                    capacity_required=ev.capacity_required,
                    volunteer_capacity=ev.capacity_required,
                    registration_deadline=ev.registration_deadline,
                    status=ev.status,
                    registered_count=registered,
                    selected_count=selected,
                    available_spots=available,
                )
            )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return EventListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def update_event(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        data: EventUpdateRequest,
        current_user: User,
    ) -> EventResponse:
        """Update mutable fields on an existing event."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can update events.")

        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        if event.status in ("COMPLETED", "CANCELLED"):
            raise DomainException(
                f"Cannot update event in '{event.status}' status.",
                status_code=400,
                code="EVENT_IMMUTABLE",
            )

        update_dict: dict[str, Any] = {}
        if data.title is not None:
            update_dict["title"] = data.title
        if data.description is not None:
            update_dict["description"] = data.description
        if data.category is not None:
            update_dict["category"] = data.category.value
        if data.mode is not None:
            update_dict["mode"] = data.mode.value
        if data.timezone is not None:
            update_dict["timezone"] = data.timezone
        if data.cover_media_id is not None:
            update_dict["cover_media_id"] = data.cover_media_id

        # Location / Online URL
        if data.location is not None:
            update_dict["location"] = data.location
        elif data.online_meeting_url is not None:
            update_dict["location"] = data.online_meeting_url

        # Dates & Times
        if data.start_time is not None and isinstance(data.start_time, datetime):
            update_dict["start_time"] = data.start_time
        if data.end_time is not None and isinstance(data.end_time, datetime):
            update_dict["end_time"] = data.end_time
        if data.registration_deadline is not None:
            update_dict["registration_deadline"] = data.registration_deadline

        # Capacity check against current selected volunteers
        new_cap = data.capacity_required or data.volunteer_capacity
        if new_cap is not None:
            selected_count = await event_repository.count_selected(db, event.id)
            if new_cap < selected_count:
                raise DomainException(
                    f"Cannot reduce capacity to {new_cap}; {selected_count} volunteers are already SELECTED.",
                    status_code=400,
                    code="CAPACITY_CONFLICT",
                )
            update_dict["capacity_required"] = new_cap

        old_state = {"title": event.title, "capacity": event.capacity_required}
        updated_event = await event_repository.update(db, event, update_dict)

        self._record_audit_log(
            db=db,
            actor_id=current_user.id,
            action="EVENT_UPDATED",
            resource_type="EVENT",
            resource_id=str(updated_event.id),
            old_state=old_state,
            new_state=update_dict,
        )
        await db.commit()
        await db.refresh(updated_event)

        counts = await event_repository.get_registration_counts(db, updated_event.id)
        return self._build_event_response(updated_event, counts)

    async def transition_status(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        new_status: str,
        current_user: User,
        reason: str | None = None,
    ) -> EventResponse:
        """Enforce strict lifecycle state machine transition."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can transition event statuses.")

        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        current_status = event.status
        allowed_targets = VALID_EVENT_TRANSITIONS.get(current_status, set())

        if new_status not in allowed_targets:
            raise DomainException(
                f"Invalid state transition from '{current_status}' to '{new_status}'.",
                status_code=400,
                code="INVALID_STATE_TRANSITION",
            )

        # Enforce cancellation reason requirement
        if new_status == "CANCELLED":
            if not reason or not reason.strip():
                raise DomainException(
                    "Cancellation reason is required when cancelling an event.",
                    status_code=400,
                    code="CANCELLATION_REASON_REQUIRED",
                )

        old_state = {"status": current_status}
        updated_event = await event_repository.update_status(
            db=db, event=event, new_status=new_status, actor_id=current_user.id, reason=reason
        )

        # If event is cancelled, decline active registrations and write registration history
        if new_status == "CANCELLED":
            stmt = (
                select(EventRegistration)
                .where(EventRegistration.event_id == event.id)
                .where(EventRegistration.status.in_(["SUBSCRIBED", "WAITLISTED", "SELECTED"]))
            )
            reg_res = await db.execute(stmt)
            active_regs = reg_res.scalars().all()
            for reg in active_regs:
                old_reg_status = reg.status
                reg.status = "DECLINED"
                hist = RegistrationHistory(
                    registration_id=reg.id,
                    old_status=old_reg_status,
                    new_status="DECLINED",
                    changed_by_user_id=current_user.id,
                    reason=f"Event cancelled by admin: {reason}",
                )
                db.add(hist)

        self._record_audit_log(
            db=db,
            actor_id=current_user.id,
            action=f"EVENT_TRANSITION_{new_status}",
            resource_type="EVENT",
            resource_id=str(updated_event.id),
            old_state=old_state,
            new_state={"status": new_status},
            reason=reason,
        )
        await db.commit()
        await db.refresh(updated_event)

        counts = await event_repository.get_registration_counts(db, updated_event.id)
        return self._build_event_response(updated_event, counts)

    async def publish_event(
        self, db: AsyncSession, event_id: uuid.UUID, current_user: User
    ) -> EventResponse:
        """Publish a DRAFT event to volunteers."""
        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        # Validate event is currently DRAFT
        if event.status != "DRAFT":
            raise DomainException(
                f"Cannot publish event in status '{event.status}'. Must be DRAFT.",
                status_code=400,
                code="INVALID_STATE_TRANSITION",
            )

        # Validate required fields
        if not event.title or len(event.title) < 3:
            raise DomainException("Event title is invalid.", status_code=400, code="INVALID_EVENT")
        if not event.location:
            raise DomainException(
                "Event location is required.", status_code=400, code="INVALID_EVENT"
            )
        if event.capacity_required < 1:
            raise DomainException(
                "Event capacity must be >= 1.", status_code=400, code="INVALID_EVENT"
            )

        return await self.transition_status(
            db=db, event_id=event_id, new_status="PUBLISHED", current_user=current_user
        )

    async def close_registration(
        self, db: AsyncSession, event_id: uuid.UUID, current_user: User
    ) -> EventResponse:
        """Close volunteer registrations for a PUBLISHED event."""
        return await self.transition_status(
            db=db, event_id=event_id, new_status="REGISTRATION_CLOSED", current_user=current_user
        )

    async def cancel_event(
        self, db: AsyncSession, event_id: uuid.UUID, reason: str, current_user: User
    ) -> EventResponse:
        """Cancel an event with mandatory explanation reason."""
        return await self.transition_status(
            db=db,
            event_id=event_id,
            new_status="CANCELLED",
            current_user=current_user,
            reason=reason,
        )

    async def complete_event(
        self, db: AsyncSession, event_id: uuid.UUID, current_user: User
    ) -> EventResponse:
        """Transition event from ONGOING to COMPLETED."""
        return await self.transition_status(
            db=db, event_id=event_id, new_status="COMPLETED", current_user=current_user
        )

    async def duplicate_event(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        data: EventDuplicateRequest,
        current_user: User,
    ) -> EventResponse:
        """Clone an existing event into a new DRAFT event with adjusted dates."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can duplicate events.")

        source = await event_repository.get_by_id(db, event_id)
        if not source:
            raise NotFoundException("Source event not found.")

        cloned_dict: dict[str, Any] = {
            "title": f"Copy of {source.title}",
            "description": source.description,
            "category": source.category,
            "mode": source.mode,
            "location": source.location,
            "start_time": data.new_start_time,
            "end_time": data.new_end_time,
            "timezone": source.timezone,
            "capacity_required": source.capacity_required,
            "registration_deadline": data.new_registration_deadline,
            "status": "DRAFT",
            "cover_media_id": source.cover_media_id,
        }

        cloned = await event_repository.create(db, cloned_dict, current_user.id)

        self._record_audit_log(
            db=db,
            actor_id=current_user.id,
            action="EVENT_DUPLICATED",
            resource_type="EVENT",
            resource_id=str(cloned.id),
            new_state={"source_event_id": str(source.id)},
        )
        await db.commit()
        await db.refresh(cloned)

        counts = {"registered": 0, "selected": 0, "waitlisted": 0}
        return self._build_event_response(cloned, counts)


event_service = EventService()
