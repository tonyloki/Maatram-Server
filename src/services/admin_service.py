"""Service for Super Admin operations: audit trail inspection and dead-letter recovery."""

import math
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DomainException, ForbiddenException, NotFoundException
from src.core.logging import get_logger
from src.models.users import User
from src.repositories.notification_repo import (
    NotificationRepository,
    notification_repository,
)
from src.repositories.report_repo import ReportRepository, report_repository
from src.schemas.admin import AuditLogListResponse, AuditLogResponse
from src.schemas.notification import OutboxRetryResponse

logger = get_logger(__name__)


class AdminService:
    """Administrative service handling high-privilege operations."""

    def __init__(
        self,
        report_repo: ReportRepository | None = None,
        notif_repo: NotificationRepository | None = None,
    ) -> None:
        self.report_repo = report_repo or report_repository
        self.notif_repo = notif_repo or notification_repository

    async def list_audit_logs(
        self,
        db: AsyncSession,
        user: User,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> AuditLogListResponse:
        """Inspect system audit trail. Restricted to SUPER_ADMIN."""
        if user.role != "SUPER_ADMIN":
            raise ForbiddenException(
                "Only Super Administrators can inspect the system audit trail."
            )

        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        logs, total = await self.report_repo.list_audit_logs(
            db=db,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=limit,
        )
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1

        dtos = [
            AuditLogResponse(
                id=log_entry.id,
                actor_user_id=log_entry.actor_user_id,
                actor_email=log_entry.actor.email if log_entry.actor else None,
                action=log_entry.action,
                resource_type=log_entry.resource_type,
                resource_id=log_entry.resource_id,
                old_state=log_entry.old_state,
                new_state=log_entry.new_state,
                reason=log_entry.reason,
                created_at=log_entry.created_at,
            )
            for log_entry in logs
        ]
        return AuditLogListResponse(
            items=dtos,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def requeue_dead_letter_job(
        self,
        db: AsyncSession,
        user: User,
        job_id: uuid.UUID,
    ) -> OutboxRetryResponse:
        """Manually requeue a dead-letter communication job. Restricted to SUPER_ADMIN."""
        if user.role != "SUPER_ADMIN":
            raise ForbiddenException(
                "Only Super Administrators can requeue dead-letter communication jobs."
            )

        job = await self.notif_repo.get_outbox_job_by_id(db, job_id)
        if not job:
            raise NotFoundException("Outbox job not found.")

        if job.status != "DEAD_LETTER":
            raise DomainException(
                f"Job is in '{job.status}' state, not DEAD_LETTER.",
                status_code=400,
                code="JOB_NOT_IN_DEAD_LETTER_STATE",
            )

        updated = await self.notif_repo.requeue_outbox_job(db, job)
        await db.commit()
        return OutboxRetryResponse(
            job_id=updated.id,
            status=updated.status,
            message="Dead-letter job successfully requeued to PENDING.",
        )


admin_service = AdminService()
