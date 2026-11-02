"""Module 4: Privacy & Consent models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, CompatibleINET, UUIDPrimaryKeyMixin, utc_now


class ConsentRecord(Base, UUIDPrimaryKeyMixin):
    """Current affirmative consent status across all privacy dimensions."""

    __tablename__ = "consent_records"

    volunteer_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    leaderboard_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    name_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    thank_you_emails: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    linkedin_content: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contact_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    media_usage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    volunteer_profile: Mapped["VolunteerProfile"] = relationship(
        "VolunteerProfile", back_populates="consent_record"
    )
    history_entries: Mapped[list["ConsentHistory"]] = relationship(
        "ConsentHistory", back_populates="consent_record", cascade="all, delete-orphan"
    )


class ConsentHistory(Base, UUIDPrimaryKeyMixin):
    """Immutable audit log of all consent modifications."""

    __tablename__ = "consent_history"

    consent_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("consent_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dimension: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[bool] = mapped_column(Boolean, nullable=False)
    new_value: Mapped[bool] = mapped_column(Boolean, nullable=False)
    changed_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ip_address: Mapped[str | None] = mapped_column(CompatibleINET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    consent_record: Mapped["ConsentRecord"] = relationship(
        "ConsentRecord", back_populates="history_entries"
    )
    changed_by: Mapped["User"] = relationship("User")


from src.models.users import User  # noqa: E402
from src.models.volunteers import VolunteerProfile  # noqa: E402
