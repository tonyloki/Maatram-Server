"""Affirmative Consent Management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, verify_csrf
from src.models.users import User
from src.schemas.consent import (
    ConsentHistoryResponse,
    ConsentResponse,
    ConsentUpdate,
)
from src.services.consent_service import consent_service

router = APIRouter(prefix="/consent", tags=["Consent Governance"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ConsentResponse,
    summary="Get authenticated volunteer affirmative consent settings",
)
async def get_my_consent(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConsentResponse:
    """Retrieve affirmative privacy and communication preferences across all 6 dimensions."""
    record = await consent_service.get_consent_me(db=db, user_id=current_user.id)
    return ConsentResponse.model_validate(record)


@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ConsentResponse,
    summary="Update affirmative consent settings with differential audit logging",
    dependencies=[Depends(verify_csrf)],
)
async def update_my_consent(
    request: Request,
    data: ConsentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConsentResponse:
    """Self-service update of consent settings with immutable differential logging per modified dimension."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = await consent_service.update_consent_me(
        db=db,
        user_id=current_user.id,
        update_data=data,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    return ConsentResponse.model_validate(updated)


@router.get(
    "/me/history",
    status_code=status.HTTP_200_OK,
    response_model=ConsentHistoryResponse,
    summary="Get immutable consent change history for authenticated volunteer",
)
async def get_my_consent_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConsentHistoryResponse:
    """Retrieve immutable chronological audit trail of all previous consent adjustments."""
    return await consent_service.get_consent_history_me(db=db, user_id=current_user.id)
