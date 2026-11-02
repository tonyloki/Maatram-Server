"""Module 1: Identity & Authentication models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, CompatibleINET, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Canonical authentication and base user identity record."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING_VERIFICATION", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "role IN ('VOLUNTEER', 'ADMIN', 'SUPER_ADMIN')",
            name="chk_users_role",
        ),
        CheckConstraint(
            "status IN ('PENDING_VERIFICATION', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'SUSPENDED', 'INACTIVE', 'UNVERIFIED', 'PENDING')",
            name="chk_users_status",
        ),
        CheckConstraint(
            "failed_login_attempts >= 0",
            name="chk_users_failed_attempts_non_negative",
        ),
        Index("ix_users_role_status", "role", "status"),
    )

    # Relationships
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    email_verifications: Mapped[list["EmailVerification"]] = relationship(
        "EmailVerification", back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )
    volunteer_profile: Mapped["VolunteerProfile | None"] = relationship(
        "VolunteerProfile",
        back_populates="user",
        uselist=False,
        foreign_keys="VolunteerProfile.user_id",
    )


class UserSession(Base, UUIDPrimaryKeyMixin):
    """Active server-tracked client session for token rotation and revocation."""

    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(CompatibleINET, nullable=True)
    client_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "client_type IN ('WEB', 'MOBILE')",
            name="chk_user_sessions_client_type",
        ),
        Index("ix_user_sessions_active", "user_id", "is_revoked"),
    )

    user: Mapped["User"] = relationship("User", back_populates="sessions")


class EmailVerification(Base, UUIDPrimaryKeyMixin):
    """One-time email ownership verification tokens."""

    __tablename__ = "email_verifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="email_verifications")


class PasswordResetToken(Base, UUIDPrimaryKeyMixin):
    """Numerical OTP or hashed token for password resets."""

    __tablename__ = "password_reset_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    otp_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        CheckConstraint("attempt_count <= max_attempts", name="chk_password_reset_attempts"),
    )

    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens")


from src.models.volunteers import VolunteerProfile  # noqa: E402
