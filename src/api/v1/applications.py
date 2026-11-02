"""Volunteer Onboarding Application and Review API endpoints."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_role
from src.models.users import User
from src.schemas.application import (
    ApplicationApproveRequest,
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationRejectRequest,
    ApplicationResponse,
    ParentalConsentVerifyRequest,
)
from src.schemas.volunteer import VolunteerProfileResponse
from src.services.application_service import application_service

router = APIRouter(prefix="/applications", tags=["Volunteer Applications"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ApplicationResponse,
    summary="Get authenticated volunteer's onboarding application",
)
async def get_my_application(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApplicationResponse:
    """Retrieve application status and stage for the currently authenticated volunteer."""
    return await application_service.get_my_application(db=db, user_id=current_user.id)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApplicationListResponse,
    summary="List and filter onboarding applications (Admin only)",
    dependencies=[Depends(require_role("ADMIN", "SUPER_ADMIN"))],
)
async def list_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    app_status: str | None = Query(
        None, alias="status", description="Filter by status: PENDING, APPROVED, REJECTED"
    ),
    category: str | None = Query(
        None, description="Filter by volunteer category: STUDENT, ALUMNI, CORPORATE"
    ),
    date_from: datetime | None = Query(None, description="Submitted at or after UTC timestamp"),
    date_to: datetime | None = Query(None, description="Submitted at or before UTC timestamp"),
    search: str | None = Query(
        None, description="Keyword search across applicant name/email/phone"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ApplicationListResponse:
    """Administrative query for onboarding applications with multi-filter and pagination support."""
    return await application_service.list_applications(
        db=db,
        current_user=current_user,
        status=app_status,
        category=category,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{application_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApplicationDetailResponse,
    summary="Get application details (Admin or applicant)",
)
async def get_application_by_id(
    application_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApplicationDetailResponse:
    """Inspect complete application details including applicant profile and review trail."""
    return await application_service.get_application_by_id(
        db=db,
        application_id=application_id,
        current_user=current_user,
    )


@router.post(
    "/{application_id}/approve",
    status_code=status.HTTP_200_OK,
    response_model=ApplicationResponse,
    summary="Approve volunteer application (Admin only)",
    dependencies=[Depends(require_role("ADMIN", "SUPER_ADMIN"))],
)
async def approve_application(
    application_id: uuid.UUID,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    data: ApplicationApproveRequest | None = None,
) -> ApplicationResponse:
    """Approve application, activate volunteer account, record review decision, and notify applicant."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    notes = data.notes if data else None

    return await application_service.approve_application(
        db=db,
        application_id=application_id,
        reviewer_user=current_user,
        notes=notes,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/{application_id}/reject",
    status_code=status.HTTP_200_OK,
    response_model=ApplicationResponse,
    summary="Reject volunteer application with mandatory reason (Admin only)",
    dependencies=[Depends(require_role("ADMIN", "SUPER_ADMIN"))],
)
async def reject_application(
    application_id: uuid.UUID,
    request: Request,
    data: ApplicationRejectRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApplicationResponse:
    """Reject application with mandatory reason, update account state, and notify applicant."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await application_service.reject_application(
        db=db,
        application_id=application_id,
        reviewer_user=current_user,
        reason=data.reason,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/{application_id}/verify-parental-consent",
    status_code=status.HTTP_200_OK,
    response_model=VolunteerProfileResponse,
    summary="Verify minor applicant parental consent (Admin only)",
    dependencies=[Depends(require_role("ADMIN", "SUPER_ADMIN"))],
)
async def verify_parental_consent(
    application_id: uuid.UUID,
    request: Request,
    data: ParentalConsentVerifyRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VolunteerProfileResponse:
    """Admin documentary review and verification of parental consent for applicants under 18."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    profile = await application_service.verify_parental_consent(
        db=db,
        application_id=application_id,
        reviewer_user=current_user,
        status=data.status,
        notes=data.notes,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    return VolunteerProfileResponse.model_validate(profile)
