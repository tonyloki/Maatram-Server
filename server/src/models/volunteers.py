"""Module 2: Volunteer Profiles & Classifications models."""

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
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import (
    Base,
    CompatibleTextArray,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class VolunteerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Base volunteer profile shared across student, alumni, and corporate panelists."""

    __tablename__ = "volunteer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    mobile_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    avatar_media_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Minor Safeguarding Fields
    parent_guardian_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    parent_guardian_relationship: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_guardian_contact: Mapped[str | None] = mapped_column(String(20), nullable=True)
    parental_consent_submitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parental_consent_claimed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parental_consent_evidence_submitted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    parental_consent_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parental_consent_document_media_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    parental_consent_status: Mapped[str] = mapped_column(
        String(30),
        default="NOT_REQUIRED",
        nullable=False,
        index=True,
    )
    parental_consent_verified_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    parental_consent_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    parental_consent_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "gender IN ('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY')",
            name="chk_volunteer_profiles_gender",
        ),
        CheckConstraint(
            "category IN ('STUDENT', 'ALUMNI', 'CORPORATE')",
            name="chk_volunteer_profiles_category",
        ),
        CheckConstraint(
            "parental_consent_status IN ('NOT_REQUIRED', 'PENDING_VERIFICATION', 'VERIFIED', 'REJECTED')",
            name="chk_volunteer_profiles_consent_status",
        ),
        CheckConstraint(
            "age > 0 AND age <= 120",
            name="chk_volunteer_age_sanity",
        ),
        Index("ix_volunteer_profiles_names", "last_name", "first_name"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="volunteer_profile", foreign_keys=[user_id]
    )
    parental_consent_verified_by: Mapped["User | None"] = relationship(
        "User", foreign_keys=[parental_consent_verified_by_user_id]
    )
    student_profile: Mapped["StudentProfile | None"] = relationship(
        "StudentProfile",
        back_populates="volunteer_profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    alumni_profile: Mapped["AlumniProfile | None"] = relationship(
        "AlumniProfile",
        back_populates="volunteer_profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    corporate_profile: Mapped["CorporateProfile | None"] = relationship(
        "CorporateProfile",
        back_populates="volunteer_profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    consent_record: Mapped["ConsentRecord | None"] = relationship(
        "ConsentRecord",
        back_populates="volunteer_profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    applications: Mapped[list["VolunteerApplication"]] = relationship(
        "VolunteerApplication", back_populates="volunteer_profile"
    )
    registrations: Mapped[list["EventRegistration"]] = relationship(
        "EventRegistration", back_populates="volunteer_profile"
    )
    point_transactions: Mapped[list["PointTransaction"]] = relationship(
        "PointTransaction", back_populates="volunteer_profile"
    )
    achievements: Mapped[list["VolunteerAchievement"]] = relationship(
        "VolunteerAchievement", back_populates="volunteer_profile"
    )


class StudentProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Specific attributes for active student volunteers."""

    __tablename__ = "student_profiles"

    volunteer_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    college_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    batch_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    current_year: Mapped[int] = mapped_column(Integer, nullable=False)
    maatram_reg_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    __table_args__ = (
        CheckConstraint("current_year BETWEEN 1 AND 5", name="chk_student_current_year"),
    )

    volunteer_profile: Mapped["VolunteerProfile"] = relationship(
        "VolunteerProfile", back_populates="student_profile"
    )


class AlumniProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Specific attributes for graduated alumni volunteers."""

    __tablename__ = "alumni_profiles"

    volunteer_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    organisation: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    job_role: Mapped[str] = mapped_column(String(150), nullable=False)
    years_of_experience: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    skills: Mapped[list[str]] = mapped_column(CompatibleTextArray, default=list, nullable=False)
    college_name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    batch_year: Mapped[int] = mapped_column(Integer, nullable=False)
    graduation_year: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("years_of_experience >= 0", name="chk_alumni_years_exp_non_negative"),
    )

    volunteer_profile: Mapped["VolunteerProfile"] = relationship(
        "VolunteerProfile", back_populates="alumni_profile"
    )


class CorporateProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Specific attributes for corporate panelist volunteers."""

    __tablename__ = "corporate_profiles"

    volunteer_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("volunteer_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    organisation: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    designation: Mapped[str] = mapped_column(String(150), nullable=False)
    years_of_experience: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    skills: Mapped[list[str]] = mapped_column(CompatibleTextArray, default=list, nullable=False)

    __table_args__ = (
        CheckConstraint("years_of_experience >= 0", name="chk_corporate_years_exp_non_negative"),
    )

    volunteer_profile: Mapped["VolunteerProfile"] = relationship(
        "VolunteerProfile", back_populates="corporate_profile"
    )


from src.models.applications import VolunteerApplication  # noqa: E402
from src.models.consent import ConsentRecord  # noqa: E402
from src.models.events import EventRegistration  # noqa: E402
from src.models.gamification import PointTransaction, VolunteerAchievement  # noqa: E402
from src.models.users import User  # noqa: E402
