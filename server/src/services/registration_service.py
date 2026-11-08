"""Event Registration & Volunteer Selection domain service."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import (
    ConflictException,
    DomainException,
    ForbiddenException,
    NotFoundException,
)
from src.models.admin import AuditLog
from src.models.events import EventRegistration
from src.models.users import User
from src.repositories.event_repo import event_repository
from src.repositories.registration_repo import registration_repository
from src.repositories.volunteer_repo import volunteer_repository
from src.schemas.registration import (
    BatchSelectionResponse,
    EventSummary,
    RegistrationHistoryItem,
    RegistrationListResponse,
    RegistrationResponse,
    VolunteerSummary,
)


def _ensure_aware_utc(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware and converted to UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class RegistrationService:
    """Core domain service orchestrating volunteer event registrations, capacity locks, and selections."""

    def __init__(self) -> None:
        self._event_locks: dict[uuid.UUID, asyncio.Lock] = {}

    def _get_event_lock(self, event_id: uuid.UUID) -> asyncio.Lock:
        if event_id not in self._event_locks:
            self._event_locks[event_id] = asyncio.Lock()
        return self._event_locks[event_id]

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

    def _build_response(self, reg: EventRegistration) -> RegistrationResponse:
        """Map ORM EventRegistration to RegistrationResponse DTO."""
        volunteer_summary: VolunteerSummary | None = None
        if reg.volunteer_profile:
            vp = reg.volunteer_profile
            user_email = vp.user.email if vp.user else None
            volunteer_summary = VolunteerSummary(
                id=vp.id,
                user_id=vp.user_id,
                first_name=vp.first_name,
                last_name=vp.last_name,
                mobile_number=vp.mobile_number,
                category=vp.category,
                email=user_email,
            )

        event_summary: EventSummary | None = None
        if reg.event:
            ev = reg.event
            event_summary = EventSummary(
                id=ev.id,
                title=ev.title,
                category=ev.category,
                mode=ev.mode,
                location=ev.location,
                start_time=ev.start_time,
                end_time=ev.end_time,
                status=ev.status,
            )

        history_items: list[RegistrationHistoryItem] = []
        if reg.history_entries:
            for h in sorted(reg.history_entries, key=lambda x: x.created_at):
                history_items.append(
                    RegistrationHistoryItem(
                        id=h.id,
                        registration_id=h.registration_id,
                        old_status=h.old_status,
                        new_status=h.new_status,
                        changed_by_user_id=h.changed_by_user_id,
                        reason=h.reason,
                        created_at=h.created_at,
                    )
                )

        return RegistrationResponse(
            id=reg.id,
            event_id=reg.event_id,
            volunteer_profile_id=reg.volunteer_profile_id,
            status=reg.status,
            selected_at=reg.selected_at,
            withdrawn_at=reg.withdrawn_at,
            notes=reg.notes,
            created_at=reg.created_at,
            updated_at=reg.updated_at,
            volunteer=volunteer_summary,
            event=event_summary,
            history_entries=history_items,
        )

    async def register_volunteer(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        notes: str | None = None,
    ) -> RegistrationResponse:
        """Register an approved volunteer for a published event with pessimistic concurrency locking."""
        async with self._get_event_lock(event_id):
            # 1. Resolve volunteer profile
            volunteer = await volunteer_repository.get_by_user_id(db, requesting_user_id)
            if not volunteer:
                raise NotFoundException("Volunteer profile not found.")

            # 2. Check approval invariant: volunteer user must be APPROVED
            if not volunteer.user or volunteer.user.status != "APPROVED":
                raise DomainException(
                    "Only approved volunteers can register for events.",
                    status_code=400,
                    code="VOLUNTEER_NOT_APPROVED",
                )

            # 3. Pessimistic exclusive row lock on event row
            event = await event_repository.get_by_id_for_update(db, event_id)
            if not event:
                raise NotFoundException("Event not found.")

            # 4. Status validation
            if event.status == "DRAFT":
                raise DomainException(
                    "Cannot register for a draft event.",
                    status_code=400,
                    code="EVENT_NOT_PUBLISHED",
                )
            if event.status in ("REGISTRATION_CLOSED", "ONGOING", "COMPLETED", "CANCELLED"):
                raise DomainException(
                    f"Registration is not open for event with status '{event.status}'.",
                    status_code=400,
                    code="REGISTRATION_CLOSED",
                )

            # 5. Temporal registration deadline check
            now = datetime.now(UTC)
            if now > _ensure_aware_utc(event.registration_deadline):
                raise DomainException(
                    "Registration deadline for this event has passed.",
                    status_code=400,
                    code="DEADLINE_EXPIRED",
                )

            # 6. Schedule conflict detection across overlapping active events
            overlapping = await registration_repository.get_overlapping_registrations(
                db=db,
                volunteer_profile_id=volunteer.id,
                start_time=event.start_time,
                end_time=event.end_time,
                exclude_event_id=event.id,
            )
            if overlapping:
                raise DomainException(
                    "Schedule conflict: You have an active registration for an overlapping event.",
                    status_code=400,
                    code="SCHEDULE_CONFLICT",
                )

            # 7. Check existing registration (idempotency vs reactivation)
            existing = await registration_repository.get_by_volunteer_and_event(
                db=db, volunteer_profile_id=volunteer.id, event_id=event.id
            )
            if existing:
                if existing.status in ("SUBSCRIBED", "SELECTED", "WAITLISTED"):
                    # Idempotent response
                    return self._build_response(existing)
                elif existing.status == "WITHDRAWN":
                    # Re-activate registration
                    subscribed = await registration_repository.count_subscribed_for_event(db, event.id)
                    selected = await registration_repository.count_selected_for_event(db, event.id)
                    active_count = subscribed + selected
                    new_status = (
                        "SUBSCRIBED" if active_count < event.capacity_required else "WAITLISTED"
                    )

                    existing.status = new_status
                    existing.withdrawn_at = None
                    if notes:
                        existing.notes = notes

                    await registration_repository.append_history(
                        db=db,
                        registration_id=existing.id,
                        old_status="WITHDRAWN",
                        new_status=new_status,
                        actor_id=requesting_user_id,
                        reason="Volunteer re-registered",
                    )
                    self._record_audit_log(
                        db=db,
                        actor_id=requesting_user_id,
                        action="EVENT_REGISTRATION_REACTIVATED",
                        resource_type="EVENT_REGISTRATION",
                        resource_id=str(existing.id),
                        old_state={"status": "WITHDRAWN"},
                        new_state={"status": new_status},
                    )
                    await db.commit()
                    # Reload with relations
                    reloaded = await registration_repository.get_by_id(db, existing.id)
                    assert reloaded is not None
                    return self._build_response(reloaded)
                else:
                    raise ConflictException(
                        "Volunteer has an inactive/declined registration for this event."
                    )

            # 8. Capacity evaluation
            subscribed_count = await registration_repository.count_subscribed_for_event(db, event.id)
            selected_count = await registration_repository.count_selected_for_event(db, event.id)
            current_committed = subscribed_count + selected_count

            initial_status = (
                "SUBSCRIBED" if current_committed < event.capacity_required else "WAITLISTED"
            )

            # 9. Create registration record
            reg = await registration_repository.create(
                db=db,
                volunteer_profile_id=volunteer.id,
                event_id=event.id,
                status=initial_status,
                notes=notes,
            )

            # 10. Audit trails
            await registration_repository.append_history(
                db=db,
                registration_id=reg.id,
                old_status="NONE",
                new_status=initial_status,
                actor_id=requesting_user_id,
                reason="Volunteer self-service registration",
            )
            self._record_audit_log(
                db=db,
                actor_id=requesting_user_id,
                action="EVENT_REGISTRATION_CREATED",
                resource_type="EVENT_REGISTRATION",
                resource_id=str(reg.id),
                new_state={"status": initial_status, "event_id": str(event.id)},
            )

            await db.commit()
            reloaded = await registration_repository.get_by_id(db, reg.id)
            assert reloaded is not None
            return self._build_response(reloaded)

    async def select_volunteers(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        registration_ids: list[uuid.UUID],
        admin_user_id: uuid.UUID,
    ) -> BatchSelectionResponse:
        """Batch transition registered volunteers to SELECTED status under strict capacity limits."""
        # 1. Pessimistic lock on event row
        event = await event_repository.get_by_id_for_update(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        if event.status not in ("PUBLISHED", "REGISTRATION_CLOSED"):
            raise DomainException(
                f"Cannot select volunteers for event in status '{event.status}'.",
                status_code=400,
                code="INVALID_EVENT_STATUS",
            )

        # 2. Check capacity limits
        current_selected = await registration_repository.count_selected_for_event(db, event.id)
        available_slots = max(0, event.capacity_required - current_selected)

        # Lock and validate each registration
        to_select: list[EventRegistration] = []
        already_selected: list[EventRegistration] = []

        for reg_id in registration_ids:
            reg = await registration_repository.get_by_id_with_lock(db, reg_id)
            if not reg or reg.event_id != event.id:
                raise NotFoundException(f"Registration '{reg_id}' not found for this event.")

            if reg.status == "SELECTED":
                already_selected.append(reg)
            elif reg.status in ("SUBSCRIBED", "WAITLISTED"):
                to_select.append(reg)
            else:
                raise DomainException(
                    f"Registration '{reg_id}' is in status '{reg.status}', cannot be selected.",
                    status_code=400,
                    code="INVALID_REGISTRATION_STATUS",
                )

        if len(to_select) > available_slots:
            raise DomainException(
                f"Selecting {len(to_select)} volunteers exceeds available capacity ({available_slots} remaining).",
                status_code=400,
                code="CAPACITY_EXCEEDED",
            )

        now = datetime.now(UTC)
        for reg in to_select:
            old_status = reg.status
            reg.status = "SELECTED"
            reg.selected_at = now

            await registration_repository.append_history(
                db=db,
                registration_id=reg.id,
                old_status=old_status,
                new_status="SELECTED",
                actor_id=admin_user_id,
                reason="Selected by administrator",
            )
            self._record_audit_log(
                db=db,
                actor_id=admin_user_id,
                action="REGISTRATION_SELECTED",
                resource_type="EVENT_REGISTRATION",
                resource_id=str(reg.id),
                old_state={"status": old_status},
                new_state={"status": "SELECTED"},
            )

        await db.commit()

        # Reload all
        all_results: list[RegistrationResponse] = []
        for r in already_selected + to_select:
            reloaded = await registration_repository.get_by_id(db, r.id)
            if reloaded:
                all_results.append(self._build_response(reloaded))

        return BatchSelectionResponse(
            selected_count=len(all_results),
            registrations=all_results,
        )

    async def select_single_volunteer(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        registration_id: uuid.UUID,
        admin_user_id: uuid.UUID,
    ) -> RegistrationResponse:
        """Select an individual volunteer for an event."""
        batch_res = await self.select_volunteers(
            db=db,
            event_id=event_id,
            registration_ids=[registration_id],
            admin_user_id=admin_user_id,
        )
        if not batch_res.registrations:
            raise NotFoundException("Registration could not be selected.")
        return batch_res.registrations[0]

    async def promote_from_waitlist(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        registration_id: uuid.UUID,
        admin_user_id: uuid.UUID,
    ) -> RegistrationResponse:
        """Promote a WAITLISTED volunteer to SELECTED via manual administrative action."""
        event = await event_repository.get_by_id_for_update(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        current_selected = await registration_repository.count_selected_for_event(db, event.id)
        if current_selected >= event.capacity_required:
            raise DomainException(
                "Cannot promote volunteer: event is at maximum capacity.",
                status_code=400,
                code="CAPACITY_EXCEEDED",
            )

        reg = await registration_repository.get_by_id_with_lock(db, registration_id)
        if not reg or reg.event_id != event.id:
            raise NotFoundException("Registration not found for event.")

        if reg.status != "WAITLISTED":
            raise DomainException(
                f"Only WAITLISTED volunteers can be promoted. Current status is '{reg.status}'.",
                status_code=400,
                code="INVALID_REGISTRATION_STATUS",
            )

        now = datetime.now(UTC)
        reg.status = "SELECTED"
        reg.selected_at = now

        await registration_repository.append_history(
            db=db,
            registration_id=reg.id,
            old_status="WAITLISTED",
            new_status="SELECTED",
            actor_id=admin_user_id,
            reason="Manual administrative promotion from waitlist",
        )
        self._record_audit_log(
            db=db,
            actor_id=admin_user_id,
            action="WAITLIST_PROMOTED",
            resource_type="EVENT_REGISTRATION",
            resource_id=str(reg.id),
            old_state={"status": "WAITLISTED"},
            new_state={"status": "SELECTED"},
        )

        await db.commit()
        reloaded = await registration_repository.get_by_id(db, reg.id)
        assert reloaded is not None
        return self._build_response(reloaded)

    async def withdraw_registration(
        self,
        db: AsyncSession,
        registration_id: uuid.UUID,
        requesting_user: User,
        reason: str | None = None,
    ) -> RegistrationResponse:
        """Withdraw an active registration subject to withdrawal deadline rules."""
        reg = await registration_repository.get_by_id(db, registration_id)
        if not reg:
            raise NotFoundException("Registration not found.")

        # BOLA Authorization check: must be owner or admin
        is_admin = requesting_user.role in ("ADMIN", "SUPER_ADMIN")
        is_owner = reg.volunteer_profile and reg.volunteer_profile.user_id == requesting_user.id
        if not (is_admin or is_owner):
            raise ForbiddenException("You do not have permission to withdraw this registration.")

        if reg.status == "WITHDRAWN":
            return self._build_response(reg)

        if reg.status not in ("SUBSCRIBED", "WAITLISTED", "SELECTED"):
            raise DomainException(
                f"Cannot withdraw registration with status '{reg.status}'.",
                status_code=400,
                code="INVALID_REGISTRATION_STATUS",
            )

        # Check withdrawal deadline (non-admins subject to cutoff)
        if not is_admin:
            now = datetime.now(UTC)
            event_start = _ensure_aware_utc(reg.event.start_time)
            cutoff_hours = settings.REGISTRATION_WITHDRAWAL_DEADLINE_HOURS_PRIOR
            if event_start - now < timedelta(hours=cutoff_hours):
                raise DomainException(
                    f"Withdrawal deadline has passed (must withdraw at least {cutoff_hours} hours prior to event start).",
                    status_code=400,
                    code="WITHDRAWAL_DEADLINE_PASSED",
                )

        old_status = reg.status
        now = datetime.now(UTC)
        reg.status = "WITHDRAWN"
        reg.withdrawn_at = now

        await registration_repository.append_history(
            db=db,
            registration_id=reg.id,
            old_status=old_status,
            new_status="WITHDRAWN",
            actor_id=requesting_user.id,
            reason=reason or "Volunteer withdrawn",
        )
        self._record_audit_log(
            db=db,
            actor_id=requesting_user.id,
            action="REGISTRATION_WITHDRAWN",
            resource_type="EVENT_REGISTRATION",
            resource_id=str(reg.id),
            old_state={"status": old_status},
            new_state={"status": "WITHDRAWN"},
            reason=reason,
        )

        await db.commit()
        reloaded = await registration_repository.get_by_id(db, reg.id)
        assert reloaded is not None
        return self._build_response(reloaded)

    async def withdraw_by_event(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        requesting_user: User,
        reason: str | None = None,
    ) -> RegistrationResponse:
        """Withdraw registration targeting an event by ID."""
        volunteer = await volunteer_repository.get_by_user_id(db, requesting_user.id)
        if not volunteer:
            raise NotFoundException("Volunteer profile not found.")

        reg = await registration_repository.get_by_volunteer_and_event(
            db=db, volunteer_profile_id=volunteer.id, event_id=event_id
        )
        if not reg:
            raise NotFoundException("No registration found for this event.")

        return await self.withdraw_registration(
            db=db, registration_id=reg.id, requesting_user=requesting_user, reason=reason
        )

    async def decline_registration(
        self,
        db: AsyncSession,
        registration_id: uuid.UUID,
        admin_user_id: uuid.UUID,
        reason: str | None = None,
    ) -> RegistrationResponse:
        """Administratively decline a registration."""
        reg = await registration_repository.get_by_id_with_lock(db, registration_id)
        if not reg:
            raise NotFoundException("Registration not found.")

        if reg.status not in ("SUBSCRIBED", "WAITLISTED", "SELECTED"):
            raise DomainException(
                f"Cannot decline registration in status '{reg.status}'.",
                status_code=400,
                code="INVALID_REGISTRATION_STATUS",
            )

        old_status = reg.status
        reg.status = "DECLINED"

        await registration_repository.append_history(
            db=db,
            registration_id=reg.id,
            old_status=old_status,
            new_status="DECLINED",
            actor_id=admin_user_id,
            reason=reason or "Declined by administrator",
        )
        self._record_audit_log(
            db=db,
            actor_id=admin_user_id,
            action="REGISTRATION_DECLINED",
            resource_type="EVENT_REGISTRATION",
            resource_id=str(reg.id),
            old_state={"status": old_status},
            new_state={"status": "DECLINED"},
            reason=reason,
        )

        await db.commit()
        reloaded = await registration_repository.get_by_id(db, reg.id)
        assert reloaded is not None
        return self._build_response(reloaded)

    async def mark_not_selected(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        registration_id: uuid.UUID,
        admin_user_id: uuid.UUID,
        reason: str | None = None,
    ) -> RegistrationResponse:
        """Administratively mark a volunteer NOT_SELECTED."""
        reg = await registration_repository.get_by_id_with_lock(db, registration_id)
        if not reg or reg.event_id != event_id:
            raise NotFoundException("Registration not found for event.")

        if reg.status not in ("SUBSCRIBED", "WAITLISTED"):
            raise DomainException(
                f"Cannot mark NOT_SELECTED for registration in status '{reg.status}'.",
                status_code=400,
                code="INVALID_REGISTRATION_STATUS",
            )

        old_status = reg.status
        reg.status = "NOT_SELECTED"

        await registration_repository.append_history(
            db=db,
            registration_id=reg.id,
            old_status=old_status,
            new_status="NOT_SELECTED",
            actor_id=admin_user_id,
            reason=reason or "Marked NOT_SELECTED by administrator",
        )
        self._record_audit_log(
            db=db,
            actor_id=admin_user_id,
            action="REGISTRATION_NOT_SELECTED",
            resource_type="EVENT_REGISTRATION",
            resource_id=str(reg.id),
            old_state={"status": old_status},
            new_state={"status": "NOT_SELECTED"},
            reason=reason,
        )

        await db.commit()
        reloaded = await registration_repository.get_by_id(db, reg.id)
        assert reloaded is not None
        return self._build_response(reloaded)

    async def list_event_registrations(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        admin_user: User,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> RegistrationListResponse:
        """List all registrations for a specific event (Admin only)."""
        if admin_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException(
                "Administrative privileges required to list event registrations."
            )

        event = await event_repository.get_by_id(db, event_id)
        if not event:
            raise NotFoundException("Event not found.")

        skip = (page - 1) * page_size
        items, total = await registration_repository.list_by_event(
            db=db, event_id=event_id, status_filter=status, skip=skip, limit=page_size
        )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return RegistrationListResponse(
            items=[self._build_response(r) for r in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_my_registrations(
        self,
        db: AsyncSession,
        requesting_user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> RegistrationListResponse:
        """List all registrations submitted by the authenticated volunteer."""
        volunteer = await volunteer_repository.get_by_user_id(db, requesting_user_id)
        if not volunteer:
            raise NotFoundException("Volunteer profile not found.")

        skip = (page - 1) * page_size
        items, total = await registration_repository.list_by_volunteer(
            db=db, volunteer_profile_id=volunteer.id, skip=skip, limit=page_size
        )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return RegistrationListResponse(
            items=[self._build_response(r) for r in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_registration_by_id(
        self,
        db: AsyncSession,
        registration_id: uuid.UUID,
        requesting_user: User,
    ) -> RegistrationResponse:
        """Get registration detail with BOLA ownership check."""
        reg = await registration_repository.get_by_id(db, registration_id)
        if not reg:
            raise NotFoundException("Registration not found.")

        is_admin = requesting_user.role in ("ADMIN", "SUPER_ADMIN")
        is_owner = reg.volunteer_profile and reg.volunteer_profile.user_id == requesting_user.id
        if not (is_admin or is_owner):
            raise ForbiddenException("You do not have permission to view this registration.")

        return self._build_response(reg)


registration_service = RegistrationService()
