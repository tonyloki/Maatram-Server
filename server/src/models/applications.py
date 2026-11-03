"""Module 3: Applications & Review models."""

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


class VolunteerApplication(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Volunteer onboarding application state and submission record."""

    __tablename__ = "volunteer_applications"

    volunteer_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_profiles.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False, index=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    current_stage: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="chk_volunteer_applications_status",
        ),
    )

    volunteer_profile: Mapped["VolunteerProfile"] = relationship(
        "VolunteerProfile", back_populates="applications"
    )
    reviews: Mapped[list["ApplicationReview"]] = relationship(
        "ApplicationReview", back_populates="application"
    )


class ApplicationReview(Base, UUIDPrimaryKeyMixin):
    """Administrative decision history for onboarding applications."""

    __tablename__ = "application_reviews"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_applications.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "action IN ('APPROVED', 'REJECTED')",
            name="chk_application_reviews_action",
        ),
    )

    application: Mapped["VolunteerApplication"] = relationship(
        "VolunteerApplication", back_populates="reviews"
    )
    reviewer: Mapped["User"] = relationship("User")


from src.models.users import User  # noqa: E402
from src.models.volunteers import VolunteerProfile  # noqa: E402
