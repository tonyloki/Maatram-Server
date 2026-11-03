"""Verification tokens, password reset OTPs, outbox jobs, and audit logs repository."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.admin import AuditLog
from src.models.communications import CommunicationJob
from src.models.users import EmailVerification, PasswordResetToken


class TokenRepository:
    """Persistence abstraction for email verification, password reset, outbox, and audit logs."""

    async def create_email_verification(
        self, db: AsyncSession, verification: EmailVerification
    ) -> EmailVerification:
        """Persist a new email verification token record."""
        db.add(verification)
        await db.flush()
        return verification

    async def get_email_verification_by_hash(
        self, db: AsyncSession, token_hash: str
    ) -> EmailVerification | None:
        """Find email verification token by its SHA-256 hash."""
        stmt = select(EmailVerification).where(EmailVerification.token_hash == token_hash)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_email_verification_for_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> EmailVerification | None:
        """Get the latest email verification token for a user."""
        stmt = (
            select(EmailVerification)
            .where(EmailVerification.user_id == user_id)
            .order_by(EmailVerification.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_password_reset_token(
        self, db: AsyncSession, reset_token: PasswordResetToken
    ) -> PasswordResetToken:
        """Persist a new password reset OTP token."""
        db.add(reset_token)
        await db.flush()
        return reset_token

    async def get_latest_password_reset_token(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> PasswordResetToken | None:
        """Get the latest unused, unexpired password reset token for a user."""
        now = datetime.now(UTC)
        stmt = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.is_used.is_(False),
                PasswordResetToken.expires_at > now,
            )
            .order_by(PasswordResetToken.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_recent_password_reset_requests(
        self, db: AsyncSession, user_id: uuid.UUID, since: datetime
    ) -> int:
        """Count password reset requests generated for a user since a given timestamp."""
        stmt = select(func.count(PasswordResetToken.id)).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.created_at >= since,
        )
        result = await db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def create_audit_log(
        self,
        db: AsyncSession,
        action: str,
        resource_type: str,
        resource_id: str,
        actor_user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        old_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
        reason: str | None = None,
    ) -> AuditLog:
        """Append an immutable entry to the system audit log."""
        log_entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            ip_address=ip_address,
            user_agent=user_agent,
            old_state=old_state,
            new_state=new_state,
            reason=reason,
        )
        db.add(log_entry)
        await db.flush()
        return log_entry

    async def find_session_by_rotated_token_hash(
        self, db: AsyncSession, token_hash: str
    ) -> uuid.UUID | None:
        """Check if a token hash was previously rotated, indicating token reuse/theft."""
        # Query recent TOKEN_ROTATED audit logs
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.action == "TOKEN_ROTATED",
                AuditLog.resource_type == "user_session",
            )
            .order_by(AuditLog.created_at.desc())
            .limit(100)
        )
        result = await db.execute(stmt)
        logs = result.scalars().all()
        for log in logs:
            if log.old_state and log.old_state.get("token_hash") == token_hash:
                try:
                    return uuid.UUID(log.resource_id)
                except (ValueError, TypeError):
                    return None
        return None

    async def create_communication_job(
        self, db: AsyncSession, job: CommunicationJob
    ) -> CommunicationJob:
        """Enqueue an asynchronous dispatch job into the transactional outbox."""
        db.add(job)
        await db.flush()
        return job


token_repository = TokenRepository()
