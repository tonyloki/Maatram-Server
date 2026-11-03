"""Persistence abstractions for Notifications, Device Tokens, and Outbox Jobs."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, DomainException, NotFoundException
from src.models.admin import AuditLog
from src.models.communications import CommunicationJob
from src.models.notifications import DeviceToken, Notification


class NotificationRepository:
    """Database persistence for in-app notifications, FCM device tokens, and outbox jobs."""

    async def create_notification(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        message: str,
        type: str,
        action_url: str | None = None,
    ) -> Notification:
        """Create and persist an in-app notification."""
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            action_url=action_url,
            is_read=False,
            created_at=datetime.now(UTC),
        )
        db.add(notif)
        await db.flush()
        await db.refresh(notif)
        return notif

    async def get_by_id(self, db: AsyncSession, notification_id: uuid.UUID) -> Notification | None:
        """Fetch notification by ID."""
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_user_notifications(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Notification], int]:
        """Fetch paginated in-app notifications for user with unread count."""
        stmt = select(Notification).where(Notification.user_id == user_id)
        count_stmt = (
            select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        )

        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
            count_stmt = count_stmt.where(Notification.is_read.is_(False))

        stmt = stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)

        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        res = await db.execute(stmt)
        items = list(res.scalars().all())
        return items, total

    async def count_unread(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        """Count unread notifications for a user."""
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        result = await db.execute(stmt)
        return result.scalar() or 0

    async def mark_as_read(self, db: AsyncSession, notification: Notification) -> Notification:
        """Mark single notification as read."""
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(UTC)
            await db.flush()
            await db.refresh(notification)
        return notification

    async def mark_all_read(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        """Mark all unread notifications as read for a given user."""
        now = datetime.now(UTC)
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True, read_at=now)
        )
        result = await db.execute(stmt)
        await db.flush()
        return int(getattr(result, "rowcount", 0))

    async def upsert_device_token(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        fcm_token: str,
        device_platform: str,
    ) -> DeviceToken:
        """Upsert FCM registration token for authenticated user."""
        now = datetime.now(UTC)
        stmt = select(DeviceToken).where(DeviceToken.fcm_token == fcm_token)
        result = await db.execute(stmt)
        token = result.scalar_one_or_none()

        if token:
            token.user_id = user_id
            token.device_platform = device_platform
            token.is_active = True
            token.last_seen_at = now
        else:
            token = DeviceToken(
                user_id=user_id,
                fcm_token=fcm_token,
                device_platform=device_platform,
                is_active=True,
                last_seen_at=now,
                created_at=now,
            )
            db.add(token)

        await db.flush()
        await db.refresh(token)
        return token

    async def get_device_token(self, db: AsyncSession, fcm_token: str) -> DeviceToken | None:
        """Fetch device token by FCM token string."""
        stmt = select(DeviceToken).where(DeviceToken.fcm_token == fcm_token)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_device_token(self, db: AsyncSession, fcm_token: str) -> bool:
        """Deactivate FCM token."""
        stmt = update(DeviceToken).where(DeviceToken.fcm_token == fcm_token).values(is_active=False)
        res = await db.execute(stmt)
        await db.flush()
        return int(getattr(res, "rowcount", 0)) > 0

    async def get_active_tokens_for_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[DeviceToken]:
        """Fetch all active device tokens for a given user."""
        stmt = select(DeviceToken).where(
            DeviceToken.user_id == user_id, DeviceToken.is_active.is_(True)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    # Outbox Queries
    async def list_outbox_jobs(
        self,
        db: AsyncSession,
        status: str | None = None,
        channel: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[CommunicationJob], int]:
        """Query outbox jobs with status/channel filters and pagination."""
        stmt = select(CommunicationJob)
        count_stmt = select(func.count()).select_from(CommunicationJob)

        if status:
            stmt = stmt.where(CommunicationJob.status == status)
            count_stmt = count_stmt.where(CommunicationJob.status == status)
        if channel:
            stmt = stmt.where(CommunicationJob.channel == channel)
            count_stmt = count_stmt.where(CommunicationJob.channel == channel)

        stmt = stmt.order_by(CommunicationJob.created_at.desc()).offset(skip).limit(limit)

        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        res = await db.execute(stmt)
        jobs = list(res.scalars().all())
        return jobs, total

    async def get_outbox_job_by_id(
        self, db: AsyncSession, job_id: uuid.UUID
    ) -> CommunicationJob | None:
        """Fetch outbox job by ID."""
        stmt = select(CommunicationJob).where(CommunicationJob.id == job_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def requeue_outbox_job(
        self,
        db: AsyncSession,
        job_or_id: CommunicationJob | uuid.UUID,
        actor_user_id: uuid.UUID | None = None,
        reason: str | None = None,
    ) -> CommunicationJob:
        """Acquire row lock NOWAIT, verify terminal/failed state, preserve attempt count in audit log, and reset to PENDING."""
        target_id = job_or_id.id if isinstance(job_or_id, CommunicationJob) else job_or_id

        stmt = (
            select(CommunicationJob)
            .where(CommunicationJob.id == target_id)
            .with_for_update(nowait=True)
        )
        try:
            result = await db.execute(stmt)
            job = result.scalar_one_or_none()
        except Exception as exc:
            raise ConflictException(
                "Job is currently locked by a worker or concurrent operation. Cannot requeue."
            ) from exc

        if not job:
            raise NotFoundException("Outbox job not found.")

        if job.status not in ("FAILED", "DEAD_LETTER"):
            raise DomainException(
                f"Job is in '{job.status}' state and cannot be requeued (only FAILED or DEAD_LETTER).",
                status_code=400,
                code="JOB_NOT_REQUEUEABLE",
            )

        old_status = job.status
        old_attempts = job.attempts
        old_error = job.last_error

        now = datetime.now(UTC)
        job.status = "PENDING"
        job.attempts = 0
        job.locked_at = None
        job.worker_id = None
        job.scheduled_at = now

        # Record immutable audit log
        audit_log = AuditLog(
            actor_user_id=actor_user_id,
            action="OUTBOX_JOB_REQUEUED",
            resource_type="COMMUNICATION_JOB",
            resource_id=str(job.id),
            old_state={
                "status": old_status,
                "attempts": old_attempts,
                "last_error": old_error,
            },
            new_state={
                "status": "PENDING",
                "attempts": 0,
                "scheduled_at": now.isoformat(),
            },
            reason=reason
            or f"Manually requeued outbox job from {old_status} state (previous attempts: {old_attempts})",
        )
        db.add(audit_log)
        await db.flush()
        await db.refresh(job)
        return job


notification_repository = NotificationRepository()
