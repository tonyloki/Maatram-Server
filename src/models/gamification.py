"""Module 7: Gamification & Points models (Trigger-Protected Immutable Ledger)."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin, utc_now


class PointTransaction(Base, UUIDPrimaryKeyMixin):
    """Append-only ledger recording all awarded gamification points with decimal precision."""

    __tablename__ = "point_transactions"

    volunteer_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_profiles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="RESTRICT"),
        nullable=True,
    )
    related_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("point_transactions.id", ondelete="RESTRICT"),
        nullable=True,
    )
    event_points: Mapped[Decimal] = mapped_column(
        Numeric(8, 2), default=Decimal("0.00"), nullable=False
    )
    hour_points: Mapped[Decimal] = mapped_column(
        Numeric(8, 2), default=Decimal("0.00"), nullable=False
    )
    total_points: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    hours_credited: Mapped[Decimal] = mapped_column(
        Numeric(8, 2), default=Decimal("0.00"), nullable=False
    )
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    awarded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cycle_year: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('EVENT_COMPLETION', 'MANUAL_ADJUSTMENT', 'ACHIEVEMENT_BONUS', 'COMPENSATION_REVERSAL')",
            name="chk_point_transactions_type",
        ),
        CheckConstraint(
            "total_points = event_points + hour_points",
            name="chk_points_sum",
        ),
        Index("ix_points_volunteer_cycle", "volunteer_profile_id", "cycle_year"),
        Index("ix_points_cycle_points", "cycle_year", "total_points"),
    )

    volunteer_profile: Mapped["VolunteerProfile"] = relationship(
        "VolunteerProfile", back_populates="point_transactions"
    )
    event: Mapped["Event | None"] = relationship("Event")
    awarded_by: Mapped["User | None"] = relationship("User", foreign_keys=[awarded_by_user_id])
    related_transaction: Mapped["PointTransaction | None"] = relationship(
        "PointTransaction", remote_side="PointTransaction.id"
    )


class AchievementDefinition(Base, UUIDPrimaryKeyMixin):
    """System catalog of badge and recognition criteria."""

    __tablename__ = "achievement_definitions"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon_url: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    criteria_type: Mapped[str] = mapped_column(String(50), nullable=False)
    criteria_threshold: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "criteria_type IN ('TOTAL_HOURS', 'TOTAL_EVENTS', 'CATEGORY_EVENTS', 'STREAK')",
            name="chk_achievements_criteria_type",
        ),
    )

    awarded_achievements: Mapped[list["VolunteerAchievement"]] = relationship(
        "VolunteerAchievement", back_populates="definition"
    )


class VolunteerAchievement(Base, UUIDPrimaryKeyMixin):
    """Badges earned by volunteers."""

    __tablename__ = "volunteer_achievements"

    volunteer_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("achievement_definitions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    awarded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("volunteer_profile_id", "achievement_id", name="uq_volunteer_achievement"),
    )

    volunteer_profile: Mapped["VolunteerProfile"] = relationship(
        "VolunteerProfile", back_populates="achievements"
    )
    definition: Mapped["AchievementDefinition"] = relationship(
        "AchievementDefinition", back_populates="awarded_achievements"
    )


from src.models.events import Event  # noqa: E402
from src.models.users import User  # noqa: E402
from src.models.volunteers import VolunteerProfile  # noqa: E402
