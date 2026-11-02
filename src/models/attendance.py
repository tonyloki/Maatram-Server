"""Module 6: Attendance Tracking & Corrections models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class AttendanceRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Attendance log for selected event volunteers."""

    __tablename__ = "attendance_records"

    event_registration_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("event_registrations.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
    )
    check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    check_out_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default="IN_PROGRESS", nullable=False, index=True
    )
    verified_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('IN_PROGRESS', 'COMPLETED', 'INCOMPLETE', 'ABSENT')",
            name="chk_attendance_status",
        ),
        CheckConstraint(
            "check_out_time IS NULL OR check_out_time >= check_in_time",
            name="chk_attendance_checkout_after_checkin",
        ),
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes >= 0",
            name="chk_attendance_duration_non_negative",
        ),
    )

    registration: Mapped["EventRegistration"] = relationship(
        "EventRegistration", back_populates="attendance"
    )
    verified_by: Mapped["User | None"] = relationship("User", foreign_keys=[verified_by_user_id])
    corrections: Mapped[list["AttendanceCorrection"]] = relationship(
        "AttendanceCorrection", back_populates="attendance_record"
    )


class AttendanceCorrection(Base, UUIDPrimaryKeyMixin):
    """Auditable administrative overrides of attendance durations."""

    __tablename__ = "attendance_corrections"

    attendance_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("attendance_records.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    admin_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    old_check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    new_check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    old_check_out_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    new_check_out_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    old_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    super_admin_approved_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    attendance_record: Mapped["AttendanceRecord"] = relationship(
        "AttendanceRecord", back_populates="corrections"
    )
    admin: Mapped["User"] = relationship("User", foreign_keys=[admin_id])
    super_admin_approver: Mapped["User | None"] = relationship(
        "User", foreign_keys=[super_admin_approved_by]
    )


from src.models.events import EventRegistration  # noqa: E402
from src.models.users import User  # noqa: E402
