"""Notifications, FCM Push Device Token, and Outbox management API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.users import User
from src.schemas.notification import (
    DeviceTokenRegister,
    DeviceTokenResponse,
    MarkAllReadResponse,
    MarkReadResponse,
    NotificationListResponse,
    UnreadCountResponse,
)
from src.services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "/me",
    response_model=NotificationListResponse,
    summary="List in-app notifications for authenticated user",
)
@router.get(
    "",
    response_model=NotificationListResponse,
    include_in_schema=False,
)
async def list_my_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    unread_only: bool = Query(default=False, description="Filter unread notifications only"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> NotificationListResponse:
    """Retrieve paginated in-app notification inbox."""
    return await notification_service.get_my_notifications(
        db=db,
        user=current_user,
        unread_only=unread_only,
        page=page,
        limit=limit,
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    summary="Get count of unread in-app notifications",
)
async def get_unread_count(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UnreadCountResponse:
    """Get total unread notifications count for badge display."""
    return await notification_service.get_unread_count(db=db, user=current_user)


@router.patch(
    "/{notification_id}/read",
    response_model=MarkReadResponse,
    summary="Mark single in-app notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MarkReadResponse:
    """Mark an individual notification as read."""
    return await notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user=current_user,
    )


@router.post(
    "/read-all",
    response_model=MarkAllReadResponse,
    summary="Mark all in-app notifications as read",
)
async def mark_all_notifications_read(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MarkAllReadResponse:
    """Mark all unread in-app notifications as read for current user."""
    return await notification_service.mark_all_read(db=db, user=current_user)


@router.post(
    "/device-token",
    response_model=DeviceTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register FCM device token for push notifications",
)
@router.post(
    "/devices",
    response_model=DeviceTokenResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def register_device_token(
    payload: DeviceTokenRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DeviceTokenResponse:
    """Upsert an FCM push device token."""
    token = await notification_service.register_device_token(
        db=db,
        user=current_user,
        fcm_token=payload.fcm_token,
        device_platform=payload.device_platform,
    )
    return DeviceTokenResponse.model_validate(token)


@router.delete(
    "/devices/{fcm_token}",
    status_code=status.HTTP_200_OK,
    summary="Deactivate FCM device token",
)
async def deactivate_device_token(
    fcm_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """Deactivate device token on sign-out or uninstall."""
    await notification_service.deactivate_device_token(
        db=db,
        fcm_token=fcm_token,
        user=current_user,
    )
    return {"message": "Device token deactivated successfully."}
