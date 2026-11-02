"""Event Management & Nested Registration API routers."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_role, verify_csrf
from src.models.users import User
from src.schemas.event import (
    EventCreateRequest,
    EventDuplicateRequest,
    EventListResponse,
    EventResponse,
    EventStatusTransitionRequest,
    EventUpdateRequest,
)
from src.schemas.registration import (
    BatchSelectionResponse,
    RegistrationCreateRequest,
    RegistrationListResponse,
    RegistrationResponse,
    SelectionRequest,
    WithdrawRequest,
)
from src.services.event_service import event_service
from src.services.registration_service import registration_service

router = APIRouter(prefix="/events", tags=["Events"])


# =====================================================================
# EVENT MANAGEMENT (PHASE 6)
# =====================================================================


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create volunteering event (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def create_event(
    payload: EventCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventResponse:
    """Create a new volunteering event opportunity in DRAFT status."""
    return await event_service.create_event(db=db, data=payload, current_user=current_user)


@router.get(
    "",
    response_model=EventListResponse,
    status_code=status.HTTP_200_OK,
    summary="List events (Volunteers view PUBLISHED; Admins view all)",
)
async def list_events(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    status: str | None = Query(default=None, description="Filter by event status (Admin only)"),
    category: str | None = Query(default=None, description="Filter by event category"),
    mode: str | None = Query(default=None, description="Filter by ONLINE or OFFLINE"),
    from_date: datetime | None = Query(default=None, description="Filter start time on or after"),
    to_date: datetime | None = Query(default=None, description="Filter start time on or before"),
    search: str | None = Query(
        default=None, description="Keyword search in title, description, location"
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> EventListResponse:
    """List volunteering events with role-based visibility rules."""
    return await event_service.list_events(
        db=db,
        current_user=current_user,
        status=status,
        category=category,
        mode=mode,
        from_date=from_date,
        to_date=to_date,
        search=search,
        page=page,
        page_size=limit,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Get event details",
)
async def get_event(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventResponse:
    """Get full event details. Volunteers cannot view DRAFT events."""
    return await event_service.get_event(db=db, event_id=event_id, current_user=current_user)


@router.patch(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Update event details (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def update_event(
    event_id: uuid.UUID,
    payload: EventUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventResponse:
    """Update event metadata, schedule, or capacity."""
    return await event_service.update_event(
        db=db, event_id=event_id, data=payload, current_user=current_user
    )


@router.post(
    "/{event_id}/publish",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Publish draft event to volunteers (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def publish_event(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventResponse:
    """Transition event status from DRAFT to PUBLISHED."""
    return await event_service.publish_event(db=db, event_id=event_id, current_user=current_user)


@router.post(
    "/{event_id}/close-registration",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Close registrations for event (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def close_registration(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventResponse:
    """Transition event status from PUBLISHED to REGISTRATION_CLOSED."""
    return await event_service.close_registration(
        db=db, event_id=event_id, current_user=current_user
    )


@router.post(
    "/{event_id}/close-registrations",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Alias for close-registration (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def close_registrations_alias(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventResponse:
    """Plural endpoint alias for close-registration."""
    return await event_service.close_registration(
        db=db, event_id=event_id, current_user=current_user
    )


@router.post(
    "/{event_id}/cancel",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel event (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def cancel_event(
    event_id: uuid.UUID,
    payload: EventStatusTransitionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventResponse:
    """Cancel event with mandatory reason. Marks active registrations as DECLINED."""
    return await event_service.cancel_event(
        db=db,
        event_id=event_id,
        reason=payload.reason or "",
        current_user=current_user,
    )


@router.post(
    "/{event_id}/complete",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete event (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def complete_event(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventResponse:
    """Transition event status from ONGOING to COMPLETED."""
    return await event_service.complete_event(db=db, event_id=event_id, current_user=current_user)


@router.post(
    "/{event_id}/duplicate",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate event into DRAFT with new dates (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def duplicate_event(
    event_id: uuid.UUID,
    payload: EventDuplicateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventResponse:
    """Duplicate existing event metadata into a new DRAFT event with adjusted dates."""
    return await event_service.duplicate_event(
        db=db,
        event_id=event_id,
        data=payload,
        current_user=current_user,
    )


# =====================================================================
# EVENT REGISTRATIONS & SELECTION (PHASE 7 - NESTED ROUTES)
# =====================================================================


@router.post(
    "/{event_id}/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register for an open event (Volunteer)",
    dependencies=[Depends(verify_csrf)],
)
async def register_for_event(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    payload: RegistrationCreateRequest | None = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> RegistrationResponse:
    """Register the authenticated approved volunteer for a published event."""
    notes = payload.notes if payload else None
    return await registration_service.register_volunteer(
        db=db,
        event_id=event_id,
        requesting_user_id=current_user.id,
        notes=notes,
    )


@router.post(
    "/{event_id}/withdraw",
    response_model=RegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Withdraw event registration by event ID (Volunteer)",
    dependencies=[Depends(verify_csrf)],
)
async def withdraw_by_event(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    payload: WithdrawRequest | None = None,
) -> RegistrationResponse:
    """Withdraw from an event prior to the withdrawal deadline."""
    reason = payload.reason if payload else None
    return await registration_service.withdraw_by_event(
        db=db,
        event_id=event_id,
        requesting_user=current_user,
        reason=reason,
    )


@router.get(
    "/{event_id}/registrations",
    response_model=RegistrationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List event registrations (Admin only)",
)
async def list_event_registrations(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    status: str | None = Query(default=None, description="Filter by registration status"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> RegistrationListResponse:
    """List all volunteer registrations for an event."""
    return await registration_service.list_event_registrations(
        db=db,
        event_id=event_id,
        admin_user=current_user,
        status=status,
        page=page,
        page_size=limit,
    )


@router.post(
    "/{event_id}/select",
    response_model=BatchSelectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch select volunteers for event (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def batch_select_volunteers(
    event_id: uuid.UUID,
    payload: SelectionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> BatchSelectionResponse:
    """Transition registered volunteers to SELECTED under strict capacity validation."""
    return await registration_service.select_volunteers(
        db=db,
        event_id=event_id,
        registration_ids=payload.registration_ids,
        admin_user_id=current_user.id,
    )


@router.post(
    "/{event_id}/registrations/{registration_id}/select",
    response_model=RegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Select a single volunteer for event (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def select_single_volunteer(
    event_id: uuid.UUID,
    registration_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> RegistrationResponse:
    """Select a specific volunteer registration for the event."""
    return await registration_service.select_single_volunteer(
        db=db,
        event_id=event_id,
        registration_id=registration_id,
        admin_user_id=current_user.id,
    )


@router.post(
    "/{event_id}/waitlist/{registration_id}/promote",
    response_model=RegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Manually promote volunteer from waitlist (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def promote_from_waitlist(
    event_id: uuid.UUID,
    registration_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> RegistrationResponse:
    """Manually promote a WAITLISTED registration to SELECTED."""
    return await registration_service.promote_from_waitlist(
        db=db,
        event_id=event_id,
        registration_id=registration_id,
        admin_user_id=current_user.id,
    )


@router.post(
    "/{event_id}/registrations/{registration_id}/not-selected",
    response_model=RegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark registration NOT_SELECTED (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def mark_registration_not_selected(
    event_id: uuid.UUID,
    registration_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    payload: WithdrawRequest | None = None,
) -> RegistrationResponse:
    """Administratively mark a volunteer NOT_SELECTED."""
    reason = payload.reason if payload else None
    return await registration_service.mark_not_selected(
        db=db,
        event_id=event_id,
        registration_id=registration_id,
        admin_user_id=current_user.id,
        reason=reason,
    )
