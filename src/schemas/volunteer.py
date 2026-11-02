"""Pydantic schemas for Volunteer profiles and polymorphic classifications."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

E164PhoneStr = Annotated[
    str,
    StringConstraints(
        pattern=r"^\+[1-9]\d{6,14}$",
        strip_whitespace=True,
    ),
]


# ==========================================
# Category Specific Schemas
# ==========================================


class StudentProfileBase(BaseModel):
    college_name: str = Field(..., min_length=2, max_length=255)
    degree: str = Field(..., min_length=2, max_length=100)
    department: str = Field(..., min_length=2, max_length=100)
    batch_year: int = Field(..., ge=1990, le=2100)
    current_year: int = Field(..., ge=1, le=5)
    maatram_reg_number: str = Field(..., min_length=3, max_length=50)


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileUpdate(BaseModel):
    college_name: str | None = Field(None, min_length=2, max_length=255)
    degree: str | None = Field(None, min_length=2, max_length=100)
    department: str | None = Field(None, min_length=2, max_length=100)
    batch_year: int | None = Field(None, ge=1990, le=2100)
    current_year: int | None = Field(None, ge=1, le=5)
    maatram_reg_number: str | None = Field(None, min_length=3, max_length=50)


class StudentProfileResponse(StudentProfileBase):
    id: uuid.UUID
    volunteer_profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlumniProfileBase(BaseModel):
    organisation: str = Field(..., min_length=2, max_length=255)
    job_role: str = Field(..., min_length=2, max_length=150)
    years_of_experience: Decimal = Field(..., ge=0, le=50)
    location: str = Field(..., min_length=2, max_length=150)
    skills: list[str] = Field(default_factory=list)
    college_name: str = Field(..., min_length=2, max_length=255)
    degree: str = Field(..., min_length=2, max_length=100)
    department: str = Field(..., min_length=2, max_length=100)
    batch_year: int = Field(..., ge=1990, le=2100)
    graduation_year: int = Field(..., ge=1990, le=2100)


class AlumniProfileCreate(AlumniProfileBase):
    pass


class AlumniProfileUpdate(BaseModel):
    organisation: str | None = Field(None, min_length=2, max_length=255)
    job_role: str | None = Field(None, min_length=2, max_length=150)
    years_of_experience: Decimal | None = Field(None, ge=0, le=50)
    location: str | None = Field(None, min_length=2, max_length=150)
    skills: list[str] | None = None
    college_name: str | None = Field(None, min_length=2, max_length=255)
    degree: str | None = Field(None, min_length=2, max_length=100)
    department: str | None = Field(None, min_length=2, max_length=100)
    batch_year: int | None = Field(None, ge=1990, le=2100)
    graduation_year: int | None = Field(None, ge=1990, le=2100)


class AlumniProfileResponse(AlumniProfileBase):
    id: uuid.UUID
    volunteer_profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CorporateProfileBase(BaseModel):
    organisation: str = Field(..., min_length=2, max_length=255)
    designation: str = Field(..., min_length=2, max_length=150)
    years_of_experience: Decimal = Field(..., ge=0, le=50)
    location: str = Field(..., min_length=2, max_length=150)
    skills: list[str] = Field(default_factory=list)


class CorporateProfileCreate(CorporateProfileBase):
    pass


class CorporateProfileUpdate(BaseModel):
    organisation: str | None = Field(None, min_length=2, max_length=255)
    designation: str | None = Field(None, min_length=2, max_length=150)
    years_of_experience: Decimal | None = Field(None, ge=0, le=50)
    location: str | None = Field(None, min_length=2, max_length=150)
    skills: list[str] | None = None


class CorporateProfileResponse(CorporateProfileBase):
    id: uuid.UUID
    volunteer_profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Base Volunteer Profile Schemas
# ==========================================


class VolunteerProfileUpdate(BaseModel):
    """Self-service volunteer profile update payload."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    mobile_number: E164PhoneStr | None = None
    gender: Literal["MALE", "FEMALE", "OTHER", "PREFER_NOT_TO_SAY"] | None = None
    bio: str | None = Field(None, max_length=1000)
    parent_guardian_name: str | None = Field(None, max_length=150)
    parent_guardian_relationship: str | None = Field(None, max_length=50)
    parent_guardian_contact: E164PhoneStr | None = None
    student_details: StudentProfileUpdate | None = None
    alumni_details: AlumniProfileUpdate | None = None
    corporate_details: CorporateProfileUpdate | None = None


class VolunteerProfileResponse(BaseModel):
    """Complete polymorphic volunteer profile."""

    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    mobile_number: str
    age: int
    gender: str
    category: str
    avatar_media_id: uuid.UUID | None = None
    bio: str | None = None
    parent_guardian_name: str | None = None
    parent_guardian_relationship: str | None = None
    parent_guardian_contact: str | None = None
    parental_consent_claimed: bool = False
    parental_consent_evidence_submitted: bool = False
    parental_consent_verified: bool = False
    parental_consent_status: str
    parental_consent_notes: str | None = None
    student_profile: StudentProfileResponse | None = None
    alumni_profile: AlumniProfileResponse | None = None
    corporate_profile: CorporateProfileResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VolunteerListResponse(BaseModel):
    """Paginated directory listing for administrative searches."""

    items: list[VolunteerProfileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
