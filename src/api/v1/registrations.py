"""Standalone Event Registration API routers."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_role, verify_csrf
from src.models.users import User
from src.schemas.registration import (
    DeclineRequest,
    RegistrationListResponse,
    RegistrationResponse,
    WithdrawRequest,
)
from src.services.registration_service import registration_service

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.get(
    "/me",
    response_model=RegistrationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List current volunteer's registrations",
)
async def get_my_registrations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> RegistrationListResponse:
    """Retrieve all event registrations for the authenticated volunteer."""
    return await registration_service.get_my_registrations(
        db=db,
        requesting_user_id=current_user.id,
        page=page,
        page_size=limit,
    )


@router.get(
    "/{registration_id}",
    response_model=RegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get registration details",
)
async def get_registration(
    registration_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RegistrationResponse:
    """Retrieve registration details (BOLA protected: owner or administrator only)."""
    return await registration_service.get_registration_by_id(
        db=db,
        registration_id=registration_id,
        requesting_user=current_user,
    )


@router.post(
    "/{registration_id}/withdraw",
    response_model=RegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Withdraw registration (Volunteer/Admin)",
    dependencies=[Depends(verify_csrf)],
)
async def withdraw_registration(
    registration_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    payload: WithdrawRequest | None = None,
) -> RegistrationResponse:
    """Withdraw an active registration prior to cutoff deadline."""
    reason = payload.reason if payload else None
    return await registration_service.withdraw_registration(
        db=db,
        registration_id=registration_id,
        requesting_user=current_user,
        reason=reason,
    )


@router.post(
    "/{registration_id}/decline",
    response_model=RegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Decline registration (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def decline_registration(
    registration_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    payload: DeclineRequest | None = None,
) -> RegistrationResponse:
    """Administratively mark an event registration DECLINED."""
    reason = payload.reason if payload else None
    return await registration_service.decline_registration(
        db=db,
        registration_id=registration_id,
        admin_user_id=current_user.id,
        reason=reason,
    )
