"""Module 11: Administration, Permissions & Audit Logging models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, CompatibleINET, CompatibleJSONB, UUIDPrimaryKeyMixin, utc_now


class AdminPermission(Base, UUIDPrimaryKeyMixin):
    """Granular privilege assignments for Admin and Super Admin users."""

    __tablename__ = "admin_permissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_key: Mapped[str] = mapped_column(String(100), nullable=False)
    granted_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "permission_key", name="uq_admin_permissions_user_key"),
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    granted_by: Mapped["User"] = relationship("User", foreign_keys=[granted_by_user_id])


class AuditLog(Base, UUIDPrimaryKeyMixin):
    """Immutable security and administrative activity log."""

    __tablename__ = "audit_logs"

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(CompatibleINET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    old_state: Mapped[dict[str, Any] | None] = mapped_column(CompatibleJSONB, nullable=True)
    new_state: Mapped[dict[str, Any] | None] = mapped_column(CompatibleJSONB, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )

    __table_args__ = (Index("ix_audit_logs_resource", "resource_type", "resource_id"),)

    actor: Mapped["User | None"] = relationship("User", foreign_keys=[actor_user_id])


from src.models.users import User  # noqa: E402
