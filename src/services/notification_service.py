"""Service orchestrating in-app notifications, FCM push dispatches, and outbox operations."""

import math
import uuid
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import (
    DomainException,
    ForbiddenException,
    NotFoundException,
)
from src.core.logging import get_logger
from src.integrations.fcm_client import fcm_client
from src.models.notifications import DeviceToken, Notification
from src.models.users import User
from src.repositories.notification_repo import (
    NotificationRepository,
    notification_repository,
)
from src.schemas.notification import (
    MarkAllReadResponse,
    MarkReadResponse,
    NotificationListResponse,
    NotificationResponse,
    OutboxJobListResponse,
    OutboxJobResponse,
    OutboxRetryResponse,
    UnreadCountResponse,
)

logger = get_logger(__name__)


class NotificationService:
    """Core domain service for persistent in-app notifications, device tokens, and outbox delivery."""

    def __init__(self, repo: NotificationRepository | None = None) -> None:
        self.repo = repo or notification_repository

    async def create_in_app_notification(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        message: str,
        type: str,
        action_url: str | None = None,
        dispatch_push: bool = True,
    ) -> Notification:
        """Create an in-app notification and optionally trigger real-time FCM push to registered devices."""
        notif = await self.repo.create_notification(
            db=db,
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            action_url=action_url,
        )

        if dispatch_push:
            # Dispatch push to all active registered devices for this user
            tokens = await self.repo.get_active_tokens_for_user(db, user_id)
            for dt in tokens:
                push_res = await fcm_client.send_push_notification(
                    fcm_token=dt.fcm_token,
                    title=title,
                    body=message,
                    data={"action_url": action_url or "", "type": type},
                    notification_id=notif.id,
                )
                if push_res.token_invalid:
                    logger.info("Deactivating invalid FCM token: %s", dt.fcm_token[:15])
                    await self.repo.deactivate_device_token(db, dt.fcm_token)

        return notif

    async def register_device_token(
        self,
        db: AsyncSession,
        user: User,
        fcm_token: str,
        device_platform: Literal["ANDROID", "IOS"],
    ) -> DeviceToken:
        """Register or update an FCM device token for an authenticated user."""
        token_clean = fcm_token.strip()
        if not token_clean or len(token_clean) < 10:
            raise DomainException(
                "Malformed or empty device registration token.",
                status_code=400,
                code="INVALID_DEVICE_TOKEN",
            )

        token = await self.repo.upsert_device_token(
            db=db,
            user_id=user.id,
            fcm_token=token_clean,
            device_platform=device_platform,
        )
        await db.commit()
        return token

    async def deactivate_device_token(
        self,
        db: AsyncSession,
        fcm_token: str,
        user: User,
    ) -> bool:
        """Deactivate device token with object-level authorization."""
        token = await self.repo.get_device_token(db, fcm_token)
        if not token:
            raise NotFoundException("Device token not found.")

        # Object-level authorization check: user owns token unless admin
        if user.role not in ("ADMIN", "SUPER_ADMIN") and token.user_id != user.id:
            raise ForbiddenException(
                "You cannot deactivate device tokens belonging to other users."
            )

        success = await self.repo.deactivate_device_token(db, fcm_token)
        await db.commit()
        return success

    async def mark_as_read(
        self,
        db: AsyncSession,
        notification_id: uuid.UUID,
        user: User,
    ) -> MarkReadResponse:
        """Mark single notification as read with BOLA ownership verification."""
        notif = await self.repo.get_by_id(db, notification_id)
        if not notif:
            raise NotFoundException("Notification not found.")

        if user.role not in ("ADMIN", "SUPER_ADMIN") and notif.user_id != user.id:
            raise ForbiddenException("You cannot access notifications of another user.")

        updated = await self.repo.mark_as_read(db, notif)
        await db.commit()
        return MarkReadResponse(
            id=updated.id,
            is_read=updated.is_read,
            read_at=updated.read_at,
        )

    async def mark_all_read(
        self,
        db: AsyncSession,
        user: User,
    ) -> MarkAllReadResponse:
        """Mark all in-app notifications read for the authenticated user."""
        count = await self.repo.mark_all_read(db, user.id)
        await db.commit()
        return MarkAllReadResponse(
            marked_count=count,
            message=f"Successfully marked {count} notifications as read.",
        )

    async def get_my_notifications(
        self,
        db: AsyncSession,
        user: User,
        unread_only: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> NotificationListResponse:
        """Get paginated in-app notifications for authenticated user."""
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        items, total = await self.repo.list_user_notifications(
            db=db,
            user_id=user.id,
            unread_only=unread_only,
            skip=skip,
            limit=limit,
        )
        unread_count = await self.repo.count_unread(db, user.id)
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1

        dtos = [NotificationResponse.model_validate(n) for n in items]
        return NotificationListResponse(
            items=dtos,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            unread_count=unread_count,
        )

    async def get_unread_count(self, db: AsyncSession, user: User) -> UnreadCountResponse:
        """Get total unread notifications count for current user."""
        count = await self.repo.count_unread(db, user.id)
        return UnreadCountResponse(unread_count=count)

    # Outbox Administration
    async def list_outbox_jobs(
        self,
        db: AsyncSession,
        status: str | None = None,
        channel: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> OutboxJobListResponse:
        """List outbox jobs with status and channel filters."""
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        jobs, total = await self.repo.list_outbox_jobs(
            db=db,
            status=status,
            channel=channel,
            skip=skip,
            limit=limit,
        )
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1

        dtos = [OutboxJobResponse.model_validate(j) for j in jobs]
        return OutboxJobListResponse(
            items=dtos,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def requeue_job(
        self,
        db: AsyncSession,
        job_id: uuid.UUID,
        actor_user_id: uuid.UUID | None = None,
    ) -> OutboxRetryResponse:
        """Requeue a failed or dead-letter outbox communication job with row locking and audit logging."""
        updated = await self.repo.requeue_outbox_job(
            db=db,
            job_or_id=job_id,
            actor_user_id=actor_user_id,
        )
        await db.commit()
        return OutboxRetryResponse(
            job_id=updated.id,
            status=updated.status,
            message="Outbox job successfully requeued to PENDING.",
        )


notification_service = NotificationService()
