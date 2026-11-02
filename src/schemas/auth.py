"""Authentication and session request/response DTO schemas."""

import re
import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class StudentDetailsSchema(BaseModel):
    """Student category specific attributes."""

    model_config = ConfigDict(extra="forbid")

    college_name: str = Field(..., min_length=2, max_length=255)
    degree: str = Field(..., min_length=2, max_length=100)
    department: str = Field(..., min_length=2, max_length=100)
    batch_year: int = Field(..., ge=1990, le=2100)
    current_year: int = Field(..., ge=1, le=5)
    maatram_reg_number: str = Field(..., min_length=2, max_length=50)


class AlumniDetailsSchema(BaseModel):
    """Alumni category specific attributes."""

    model_config = ConfigDict(extra="forbid")

    organisation: str = Field(..., min_length=2, max_length=255)
    job_role: str = Field(..., min_length=2, max_length=150)
    years_of_experience: Decimal = Field(..., ge=0, le=70)
    location: str = Field(..., min_length=2, max_length=150)
    skills: list[str] = Field(default_factory=list)
    college_name: str = Field(..., min_length=2, max_length=255)
    degree: str = Field(..., min_length=2, max_length=100)
    department: str = Field(..., min_length=2, max_length=100)
    batch_year: int = Field(..., ge=1970, le=2100)
    graduation_year: int = Field(..., ge=1970, le=2100)


class CorporateDetailsSchema(BaseModel):
    """Corporate panelist specific attributes."""

    model_config = ConfigDict(extra="forbid")

    organisation: str = Field(..., min_length=2, max_length=255)
    designation: str = Field(..., min_length=2, max_length=150)
    years_of_experience: Decimal = Field(..., ge=0, le=70)
    location: str = Field(..., min_length=2, max_length=150)
    skills: list[str] = Field(default_factory=list)


class ConsentSettingsSchema(BaseModel):
    """Privacy and consent affirmative selections."""

    model_config = ConfigDict(extra="forbid")

    leaderboard_visible: bool = False
    name_visible: bool = False
    thank_you_emails: bool = False
    linkedin_content: bool = False
    contact_available: bool = False
    media_usage: bool = False


class RegisterRequest(BaseModel):
    """Volunteer registration request schema."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    mobile_number: str = Field(..., min_length=8, max_length=20)
    age: int = Field(..., gt=0, le=120)
    gender: Literal["MALE", "FEMALE", "OTHER", "PREFER_NOT_TO_SAY"]
    category: Literal["STUDENT", "ALUMNI", "CORPORATE"]

    # Minor Safeguarding Fields
    parent_guardian_name: str | None = None
    parent_guardian_relationship: str | None = None
    parent_guardian_contact: str | None = None
    parental_consent_claimed: bool = False
    parental_consent_submitted: bool = False
    parental_consent_evidence_submitted: bool = False
    parental_consent_document_media_id: uuid.UUID | None = None

    # Category specifics
    student_details: StudentDetailsSchema | None = None
    alumni_details: AlumniDetailsSchema | None = None
    corporate_details: CorporateDetailsSchema | None = None

    # Consent choices
    consent: ConsentSettingsSchema | None = None

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        cleaned = v.strip()
        # E.164-compatible: optional leading +, then digits
        if not re.match(r"^\+?[1-9]\d{6,14}$", cleaned):
            raise ValueError(
                "Mobile number must be in valid international format (e.g. +919876543210)"
            )
        return cleaned

    @model_validator(mode="after")
    def validate_category_and_minors(self) -> "RegisterRequest":
        # Synchronize backward-compatible consent fields
        if self.parental_consent_submitted and not self.parental_consent_claimed:
            self.parental_consent_claimed = True

        # Category detail validation
        if self.category == "STUDENT" and self.student_details is None:
            raise ValueError("student_details are required when category is STUDENT.")
        if self.category == "ALUMNI" and self.alumni_details is None:
            raise ValueError("alumni_details are required when category is ALUMNI.")
        if self.category == "CORPORATE" and self.corporate_details is None:
            raise ValueError("corporate_details are required when category is CORPORATE.")

        return self


class RegisterResponse(BaseModel):
    """Volunteer registration response."""

    user_id: uuid.UUID
    email: str
    status: str
    parental_consent_status: str
    parental_consent_claimed: bool = False
    message: str


class LoginRequest(BaseModel):
    """User authentication login request."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=1)
    client_type: Literal["WEB", "MOBILE"] = "WEB"
    device_info: str | None = None


class UserSummaryResponse(BaseModel):
    """Minimal authenticated user identity summary."""

    id: uuid.UUID
    email: str
    role: str
    status: str


class TokenResponse(BaseModel):
    """Authentication token bundle response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900
    refresh_token: str | None = None
    csrf_token: str | None = None
    user: UserSummaryResponse


class RefreshRequest(BaseModel):
    """Token refresh rotation request."""

    model_config = ConfigDict(extra="forbid")

    refresh_token: str | None = None


class VerifyEmailRequest(BaseModel):
    """Email verification token submission."""

    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., min_length=1)
    email: EmailStr | None = None


class VerifyEmailResponse(BaseModel):
    """Email verification response."""

    status: str
    message: str


class PasswordResetRequest(BaseModel):
    """Initiate password reset OTP request."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Confirm password reset with OTP and new password."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)


class MessageResponse(BaseModel):
    """Generic operation success message."""

    message: str
