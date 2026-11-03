"""Event Registration & Volunteer Selection DTO schemas."""

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.common import BaseSchema


class RegistrationStatus(StrEnum):
    """Event registration lifecycle status machine states."""

    SUBSCRIBED = "SUBSCRIBED"
    SELECTED = "SELECTED"
    WAITLISTED = "WAITLISTED"
    NOT_SELECTED = "NOT_SELECTED"
    DECLINED = "DECLINED"
    WITHDRAWN = "WITHDRAWN"


class RegistrationCreateRequest(BaseModel):
    """Payload for volunteer event registration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    event_id: uuid.UUID | None = None
    notes: str | None = Field(default=None, max_length=1000)


class SelectionRequest(BaseModel):
    """Payload for administrative batch volunteer selection."""

    model_config = ConfigDict(str_strip_whitespace=True)

    registration_ids: list[uuid.UUID] = Field(..., min_length=1)


class WithdrawRequest(BaseModel):
    """Payload for volunteer registration withdrawal."""

    model_config = ConfigDict(str_strip_whitespace=True)

    reason: str | None = Field(default=None, max_length=500)


class DeclineRequest(BaseModel):
    """Payload for administrative registration decline."""

    model_config = ConfigDict(str_strip_whitespace=True)

    reason: str | None = Field(default=None, max_length=500)


class RegistrationHistoryItem(BaseSchema):
    """Immutable audit trail item for registration status changes."""

    id: uuid.UUID
    registration_id: uuid.UUID
    old_status: str
    new_status: str
    changed_by_user_id: uuid.UUID
    reason: str | None = None
    created_at: datetime


class VolunteerSummary(BaseSchema):
    """Volunteer profile summary attached to registration responses."""

    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    mobile_number: str
    category: str
    email: str | None = None


class EventSummary(BaseSchema):
    """Event summary attached to registration responses."""

    id: uuid.UUID
    title: str
    category: str
    mode: str
    location: str
    start_time: datetime
    end_time: datetime
    status: str


class RegistrationResponse(BaseSchema):
    """Full detail of an event registration."""

    id: uuid.UUID
    event_id: uuid.UUID
    volunteer_profile_id: uuid.UUID
    status: str
    selected_at: datetime | None = None
    withdrawn_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    volunteer: VolunteerSummary | None = None
    event: EventSummary | None = None
    history_entries: list[RegistrationHistoryItem] = Field(default_factory=list)


class RegistrationListResponse(BaseSchema):
    """Paginated collection of registration responses."""

    items: list[RegistrationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BatchSelectionResponse(BaseSchema):
    """Response payload for administrative batch selection."""

    selected_count: int
    registrations: list[RegistrationResponse]
