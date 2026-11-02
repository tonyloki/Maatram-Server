"""Transactional Outbox Worker engine for reliable asynchronous email & push notification delivery."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.logging import get_logger
from src.integrations.fcm_client import FCMClient, fcm_client
from src.integrations.resend_client import ResendClient, resend_client
from src.models.communications import CommunicationJob, CommunicationLog
from src.models.notifications import DeviceToken

logger = get_logger(__name__)


class OutboxWorker:
    """Outbox worker that claims, delivers, and recovers communication jobs with transactional guarantees."""

    def __init__(
        self,
        worker_id: str | None = None,
        email_client: ResendClient | None = None,
        push_client: FCMClient | None = None,
        lease_timeout_seconds: int | None = None,
    ) -> None:
        self.worker_id = worker_id or f"worker_{uuid.uuid4().hex[:8]}"
        self.email_client = email_client or resend_client
        self.push_client = push_client or fcm_client
        self.lease_timeout_seconds = (
            lease_timeout_seconds
            if lease_timeout_seconds is not None
            else settings.OUTBOX_LEASE_TIMEOUT_SECONDS
        )

    def calculate_backoff_seconds(self, attempts: int) -> int:
        """Calculate exponential backoff delay in seconds: 30 * 2^(attempts-1)."""
        power = max(0, attempts - 1)
        val: int = min(3600, int(30 * (2**power)))
        return val

    async def claim_batch(self, db: AsyncSession, batch_size: int = 10) -> list[CommunicationJob]:
        """Claim a batch of eligible jobs using SELECT ... FOR UPDATE SKIP LOCKED with leased locks."""
        now = datetime.now(UTC)
        lease_cutoff = now - timedelta(seconds=self.lease_timeout_seconds)

        # Eligible condition:
        # 1. status == 'PENDING' and scheduled_at <= now
        # 2. status == 'FAILED' and attempts <= max_retries and scheduled_at <= now and (locked_at is null or locked_at < lease_cutoff)
        stmt = (
            select(CommunicationJob)
            .where(
                or_(
                    (CommunicationJob.status == "PENDING") & (CommunicationJob.scheduled_at <= now),
                    (CommunicationJob.status == "FAILED")
                    & (CommunicationJob.attempts <= CommunicationJob.max_retries)
                    & (CommunicationJob.scheduled_at <= now)
                    & (
                        (CommunicationJob.locked_at.is_(None))
                        | (CommunicationJob.locked_at < lease_cutoff)
                    ),
                )
            )
            .order_by(CommunicationJob.created_at.asc())
            .with_for_update(skip_locked=True)
            .limit(batch_size)
        )

        result = await db.execute(stmt)
        jobs = list(result.scalars().all())

        for job in jobs:
            job.status = "PROCESSING"
            job.attempts += 1
            job.locked_at = now
            job.worker_id = self.worker_id

        if jobs:
            await db.flush()

        return jobs

    async def process_job(self, db: AsyncSession, job: CommunicationJob) -> bool:
        """Process an individual claimed job and record delivery audit log."""
        now = datetime.now(UTC)
        success = False
        provider = "RESEND" if job.channel == "EMAIL" else "FCM"
        provider_message_id: str | None = None
        error_msg: str | None = None

        try:
            if job.channel == "EMAIL":
                subject, html = self.email_client.render_template(job.template_name, job.payload)
                res = await self.email_client.send_email(
                    to=job.recipient,
                    subject=subject,
                    html=html,
                    idempotency_key=str(job.id),
                )
                success = res.success
                provider_message_id = res.message_id
                error_msg = res.error
            elif job.channel == "PUSH":
                title = job.payload.get("title", "Maatram Notification")
                body = job.payload.get("body") or job.payload.get("message", "")
                data = job.payload.get("data", {})

                push_res = await self.push_client.send_push_notification(
                    fcm_token=job.recipient,
                    title=title,
                    body=body,
                    data=data,
                    notification_id=job.id,
                )
                success = push_res.success
                provider_message_id = push_res.message_id
                error_msg = push_res.error_message

                # Deactivate invalid device token if indicated
                if push_res.token_invalid:
                    await db.execute(
                        update(DeviceToken)
                        .where(DeviceToken.fcm_token == job.recipient)
                        .values(is_active=False)
                    )
            else:
                error_msg = f"Unsupported channel: {job.channel}"

        except Exception as exc:
            success = False
            error_msg = f"Worker unexpected error: {exc}"

        # Update job outcome
        if success:
            job.status = "SENT"
            job.sent_at = now
            job.locked_at = None
            job.last_error = None
        else:
            job.last_error = error_msg
            job.locked_at = None
            # Max retries = 3 means:
            # Attempt 1 (initial): failed -> retry 1
            # Attempt 2 (retry 1): failed -> retry 2
            # Attempt 3 (retry 2): failed -> retry 3
            # Attempt 4 (retry 3): failed -> DEAD_LETTER
            if job.attempts >= 4 or job.attempts > job.max_retries:
                job.status = "DEAD_LETTER"
                logger.error(
                    "Outbox job %s transitioned to DEAD_LETTER after %d attempts: %s",
                    str(job.id),
                    job.attempts,
                    error_msg,
                )
            else:
                job.status = "FAILED"
                backoff_delay = self.calculate_backoff_seconds(job.attempts)
                job.scheduled_at = now + timedelta(seconds=backoff_delay)
                logger.warning(
                    "Outbox job %s failed on attempt %d (next retry in %ds): %s",
                    str(job.id),
                    job.attempts,
                    backoff_delay,
                    error_msg,
                )

        # Permanent delivery audit archive
        audit_log = CommunicationLog(
            job_id=job.id,
            channel=job.channel,
            recipient=job.recipient,
            provider=provider,
            provider_message_id=provider_message_id,
            status="DELIVERED" if success else "FAILED",
            error_message=error_msg,
            created_at=now,
        )
        db.add(audit_log)
        return success

    async def process_batch(self, db: AsyncSession, batch_size: int = 10) -> int:
        """Claim and process a batch of outbox jobs atomically."""
        jobs = await self.claim_batch(db, batch_size=batch_size)
        if not jobs:
            return 0

        success_count = 0
        for job in jobs:
            ok = await self.process_job(db, job)
            if ok:
                success_count += 1

        await db.commit()
        return len(jobs)

    async def recover_expired_leases(
        self, db: AsyncSession, lease_timeout_seconds: int | None = None
    ) -> int:
        """Sweeper task: reclaim abandoned PROCESSING jobs whose leases have expired."""
        timeout = lease_timeout_seconds or self.lease_timeout_seconds
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=timeout)

        stmt = (
            select(CommunicationJob)
            .where(
                CommunicationJob.status == "PROCESSING",
                CommunicationJob.locked_at < cutoff,
            )
            .with_for_update(skip_locked=True)
        )
        result = await db.execute(stmt)
        expired_jobs = list(result.scalars().all())

        for job in expired_jobs:
            job.locked_at = None
            job.worker_id = None
            if job.attempts >= 4 or job.attempts > job.max_retries:
                job.status = "DEAD_LETTER"
                job.last_error = (job.last_error or "") + " [Lease expired on max attempts]"
            else:
                job.status = "PENDING"
                job.last_error = (job.last_error or "") + " [Lease expired, recovered to PENDING]"

        if expired_jobs:
            await db.commit()

        return len(expired_jobs)


outbox_worker = OutboxWorker()
