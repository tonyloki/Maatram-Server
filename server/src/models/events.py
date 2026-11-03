"""Module 5: Events & Registrations models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class Event(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Volunteering opportunities and events."""

    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    capacity_required: Mapped[int] = mapped_column(Integer, nullable=False)
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    cover_media_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        CheckConstraint(
            "category IN ('SCHOOL_VISIT', 'BGV', 'ADMISSIONS', 'MOCK_INTERVIEW', 'PANEL_INTERVIEW', 'OTHER')",
            name="chk_events_category",
        ),
        CheckConstraint(
            "mode IN ('ONLINE', 'OFFLINE')",
            name="chk_events_mode",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'PUBLISHED', 'REGISTRATION_CLOSED', 'ONGOING', 'COMPLETED', 'CANCELLED')",
            name="chk_events_status",
        ),
        CheckConstraint("end_time > start_time", name="chk_events_times"),
        CheckConstraint("registration_deadline <= start_time", name="chk_events_deadline"),
        CheckConstraint("capacity_required > 0", name="chk_events_capacity_positive"),
        Index("ix_events_status_start", "status", "start_time"),
    )

    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])
    registrations: Mapped[list["EventRegistration"]] = relationship(
        "EventRegistration", back_populates="event"
    )
    photos: Mapped[list["EventPhoto"]] = relationship(
        "EventPhoto", back_populates="event", cascade="all, delete-orphan"
    )


class EventRegistration(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Volunteer registration/application to participate in specific events."""

    __tablename__ = "event_registrations"

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="RESTRICT"),
        nullable=False,
    )
    volunteer_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), default="SUBSCRIBED", nullable=False)
    selected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "event_id", "volunteer_profile_id", name="uq_event_registrations_event_volunteer"
        ),
        CheckConstraint(
            "status IN ('SUBSCRIBED', 'SELECTED', 'WAITLISTED', 'NOT_SELECTED', 'DECLINED', 'WITHDRAWN')",
            name="chk_event_registrations_status",
        ),
        Index("ix_registrations_event_status", "event_id", "status"),
        Index("ix_registrations_created_at", "created_at"),
    )

    event: Mapped["Event"] = relationship("Event", back_populates="registrations")
    volunteer_profile: Mapped["VolunteerProfile"] = relationship(
        "VolunteerProfile", back_populates="registrations"
    )
    attendance: Mapped["AttendanceRecord | None"] = relationship(
        "AttendanceRecord", back_populates="registration", uselist=False
    )
    history_entries: Mapped[list["RegistrationHistory"]] = relationship(
        "RegistrationHistory", back_populates="registration", cascade="all, delete-orphan"
    )


class RegistrationHistory(Base, UUIDPrimaryKeyMixin):
    """Audit trail of registration state transitions."""

    __tablename__ = "registration_history"

    registration_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("event_registrations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    old_status: Mapped[str] = mapped_column(String(30), nullable=False)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    registration: Mapped["EventRegistration"] = relationship(
        "EventRegistration", back_populates="history_entries"
    )
    changed_by: Mapped["User"] = relationship("User")


from src.models.attendance import AttendanceRecord  # noqa: E402
from src.models.media import EventPhoto  # noqa: E402
from src.models.users import User  # noqa: E402
from src.models.volunteers import VolunteerProfile  # noqa: E402
