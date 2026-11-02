"""Pydantic schemas for Volunteer Onboarding Applications and Reviews."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.volunteer import VolunteerProfileResponse


class ApplicationReviewResponse(BaseModel):
    """Review decision record for an application."""

    id: uuid.UUID
    application_id: uuid.UUID
    reviewer_id: uuid.UUID
    action: Literal["APPROVED", "REJECTED"]
    reason: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationResponse(BaseModel):
    """Volunteer onboarding application status and submission data."""

    id: uuid.UUID
    volunteer_profile_id: uuid.UUID
    status: Literal["PENDING", "APPROVED", "REJECTED"]
    submitted_at: datetime
    current_stage: int
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationDetailResponse(ApplicationResponse):
    """Detailed application view including profile and review history."""

    volunteer_profile: VolunteerProfileResponse
    user_email: str
    user_status: str
    reviews: list[ApplicationReviewResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ApplicationListResponse(BaseModel):
    """Paginated list of volunteer applications for administrative review."""

    items: list[ApplicationDetailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ApplicationApproveRequest(BaseModel):
    """Administrative approval request payload."""

    notes: str | None = Field(None, max_length=1000)


class ApplicationRejectRequest(BaseModel):
    """Administrative rejection request payload requiring mandatory reason."""

    reason: str = Field(
        ..., min_length=3, max_length=1000, description="Mandatory rejection reason"
    )


class ParentalConsentVerifyRequest(BaseModel):
    """Administrative verification decision for minor applicant's parental consent."""

    status: Literal["VERIFIED", "REJECTED"]
    notes: str | None = Field(None, max_length=1000)
