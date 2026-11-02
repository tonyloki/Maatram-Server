"""Module 9: Communications & Transactional Outbox models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, CompatibleJSONB, UUIDPrimaryKeyMixin, utc_now


class CommunicationJob(Base, UUIDPrimaryKeyMixin):
    """Transactional outbox table for reliable asynchronous email and push notification dispatch."""

    __tablename__ = "communication_jobs"

    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(CompatibleJSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    worker_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "channel IN ('EMAIL', 'PUSH')",
            name="chk_comm_jobs_channel",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'PROCESSING', 'SENT', 'FAILED', 'DEAD_LETTER')",
            name="chk_comm_jobs_status",
        ),
        Index("ix_comm_jobs_worker_poll", "status", "scheduled_at", "created_at"),
        Index("ix_comm_jobs_lease_recovery", "status", "locked_at"),
        Index("ix_comm_jobs_dead_letter", "status", "created_at"),
    )

    logs: Mapped[list["CommunicationLog"]] = relationship("CommunicationLog", back_populates="job")


class CommunicationLog(Base, UUIDPrimaryKeyMixin):
    """Permanent delivery audit archive."""

    __tablename__ = "communication_logs"

    job_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("communication_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )

    job: Mapped["CommunicationJob | None"] = relationship("CommunicationJob", back_populates="logs")
