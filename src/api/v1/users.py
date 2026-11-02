"""User profile and active session management endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import (
    get_current_session,
    get_current_user,
    get_db,
    verify_csrf,
)
from src.models.users import User, UserSession
from src.schemas.auth import MessageResponse
from src.schemas.user import SessionResponse, UserMeResponse
from src.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users & Sessions"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserMeResponse,
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserMeResponse:
    """Return identity and status attributes of current authenticated user."""
    return await user_service.get_me(current_user)


@router.get(
    "/me/sessions",
    status_code=status.HTTP_200_OK,
    response_model=list[SessionResponse],
    summary="List active sessions for current user",
)
async def list_sessions(
    session_and_payload: Annotated[
        tuple[UserSession, dict[str, str]], Depends(get_current_session)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SessionResponse]:
    """Retrieve all active sessions registered for caller's account across devices."""
    current_session, _ = session_and_payload
    return await user_service.list_active_sessions(
        db=db,
        user_id=current_user.id,
        current_session_id=current_session.id,
    )


@router.delete(
    "/me/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Revoke a specific active session",
    dependencies=[Depends(verify_csrf)],
)
async def revoke_session(
    request: Request,
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Revoke a specific session with tenancy / BOLA ownership verification."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await user_service.revoke_session_by_id(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        client_ip=client_ip,
        user_agent=user_agent,
    )
