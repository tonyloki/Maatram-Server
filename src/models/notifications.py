"""Module 8: Notifications & Push Devices models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin, utc_now


class Notification(Base, UUIDPrimaryKeyMixin):
    """In-app notifications inbox. Canonical source of truth for read status."""

    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (Index("ix_notifications_user_unread", "user_id", "is_read", "created_at"),)

    user: Mapped["User"] = relationship("User")


class DeviceToken(Base, UUIDPrimaryKeyMixin):
    """Registered Firebase Cloud Messaging (FCM) tokens for Flutter clients."""

    __tablename__ = "device_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    fcm_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_platform: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "device_platform IN ('ANDROID', 'IOS')",
            name="chk_device_tokens_platform",
        ),
        Index("ix_device_tokens_user_active", "user_id", "is_active"),
    )

    user: Mapped["User"] = relationship("User")


from src.models.users import User  # noqa: E402
