"""Volunteer profile management API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_role, verify_csrf
from src.models.users import User
from src.schemas.registration import RegistrationListResponse
from src.schemas.volunteer import (
    VolunteerListResponse,
    VolunteerProfileResponse,
    VolunteerProfileUpdate,
)
from src.services.registration_service import registration_service
from src.services.volunteer_service import volunteer_service

router = APIRouter(prefix="/volunteers", tags=["Volunteer Profiles"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=VolunteerProfileResponse,
    summary="Get authenticated volunteer profile",
)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VolunteerProfileResponse:
    """Retrieve complete profile and category details for currently authenticated user."""
    profile = await volunteer_service.get_my_profile(db=db, user_id=current_user.id)
    return VolunteerProfileResponse.model_validate(profile)


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=VolunteerProfileResponse,
    summary="Update authenticated volunteer profile",
    dependencies=[Depends(verify_csrf)],
)
async def update_my_profile(
    request: Request,
    data: VolunteerProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VolunteerProfileResponse:
    """Self-service update of volunteer base profile and category-specific attributes."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = await volunteer_service.update_my_profile(
        db=db,
        user_id=current_user.id,
        update_data=data,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    return VolunteerProfileResponse.model_validate(updated)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=VolunteerListResponse,
    summary="Search and filter volunteer directory (Admin only)",
    dependencies=[Depends(require_role("ADMIN", "SUPER_ADMIN"))],
)
async def list_volunteers(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = Query(
        None, description="Filter by category: STUDENT, ALUMNI, CORPORATE"
    ),
    user_status: str | None = Query(None, alias="status", description="Filter by account status"),
    college: str | None = Query(None, description="Search by college name"),
    employer: str | None = Query(None, description="Search by employer/organisation"),
    search: str | None = Query(None, description="Keyword search across name, email, phone"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> VolunteerListResponse:
    """Query volunteer directory with multi-field search, polymorphic filtering, and pagination."""
    return await volunteer_service.list_volunteers(
        db=db,
        current_user=current_user,
        category=category,
        status=user_status,
        college=college,
        employer=employer,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/me/registrations",
    status_code=status.HTTP_200_OK,
    response_model=RegistrationListResponse,
    summary="List authenticated volunteer event registrations",
)
async def get_my_volunteer_registrations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> RegistrationListResponse:
    """Retrieve all event registrations for the authenticated volunteer."""
    return await registration_service.get_my_registrations(
        db=db,
        requesting_user_id=current_user.id,
        page=page,
        page_size=limit,
    )


@router.get(
    "/{profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=VolunteerProfileResponse,
    summary="Get volunteer profile by ID (Admin or Self)",
)
async def get_profile_by_id(
    profile_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VolunteerProfileResponse:
    """Retrieve volunteer profile by profile UUID with strict authorization check."""
    profile = await volunteer_service.get_profile_by_id(
        db=db, profile_id=profile_id, current_user=current_user
    )
    return VolunteerProfileResponse.model_validate(profile)
