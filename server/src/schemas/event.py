"""Event Management request and response DTO schemas."""

import uuid
from datetime import UTC, date, datetime, time
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.schemas.common import BaseSchema


class EventCategory(StrEnum):
    """Categorical volunteering engagement categories."""

    SCHOOL_VISIT = "SCHOOL_VISIT"
    BGV = "BGV"
    ADMISSIONS = "ADMISSIONS"
    MOCK_INTERVIEW = "MOCK_INTERVIEW"
    PANEL_INTERVIEW = "PANEL_INTERVIEW"
    OTHER = "OTHER"


class EventMode(StrEnum):
    """Event delivery execution mode."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class EventStatus(StrEnum):
    """Formal event lifecycle state machine states."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    REGISTRATION_CLOSED = "REGISTRATION_CLOSED"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


def _ensure_aware_utc(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware and converted to UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class EventCreateRequest(BaseModel):
    """Payload for creating a new volunteering event."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=1)
    category: EventCategory
    mode: EventMode
    event_date: date | None = None
    start_time: datetime | time
    end_time: datetime | time
    timezone: str = Field(default="Asia/Kolkata", max_length=50)
    location: str | None = Field(default=None, max_length=255)
    online_meeting_url: str | None = Field(default=None, max_length=255)
    capacity_required: int | None = Field(default=None, ge=1)
    volunteer_capacity: int | None = Field(default=None, ge=1)
    registration_deadline: datetime
    cover_media_id: uuid.UUID | None = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_capacity_and_mode_inputs(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Capacity unification
            cap = data.get("capacity_required") or data.get("volunteer_capacity")
            if cap is not None:
                data["capacity_required"] = cap
                data["volunteer_capacity"] = cap
        return data

    @model_validator(mode="after")
    def validate_event_invariants(self) -> "EventCreateRequest":
        # 1. Capacity check
        effective_capacity = self.capacity_required or self.volunteer_capacity
        if effective_capacity is None or effective_capacity < 1:
            raise ValueError("Event capacity must be provided and >= 1.")
        self.capacity_required = effective_capacity
        self.volunteer_capacity = effective_capacity

        # 2. Location / Mode validation
        if self.mode == EventMode.OFFLINE:
            if not self.location or not self.location.strip():
                raise ValueError("Location is required for OFFLINE events.")
        elif self.mode == EventMode.ONLINE:
            meeting_url = self.online_meeting_url or self.location
            if not meeting_url or not meeting_url.strip():
                raise ValueError("Online meeting URL is required for ONLINE events.")
            self.online_meeting_url = meeting_url
            self.location = meeting_url

        # 3. Time resolution
        st: datetime
        if isinstance(self.start_time, time):
            if not self.event_date:
                raise ValueError("event_date is required when start_time is a time of day.")
            st = datetime.combine(self.event_date, self.start_time).replace(tzinfo=UTC)
        else:
            st = _ensure_aware_utc(self.start_time)

        et: datetime
        if isinstance(self.end_time, time):
            if not self.event_date:
                raise ValueError("event_date is required when end_time is a time of day.")
            et = datetime.combine(self.event_date, self.end_time).replace(tzinfo=UTC)
        else:
            et = _ensure_aware_utc(self.end_time)

        rd = _ensure_aware_utc(self.registration_deadline)

        # 4. Temporal constraints
        if et <= st:
            raise ValueError("Event end_time must be strictly after start_time.")
        if rd > st:
            raise ValueError("Registration deadline must be on or before start_time.")

        self.start_time = st
        self.end_time = et
        self.registration_deadline = rd
        return self


class EventUpdateRequest(BaseModel):
    """Payload for updating an existing volunteering event."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    category: EventCategory | None = None
    mode: EventMode | None = None
    event_date: date | None = None
    start_time: datetime | time | None = None
    end_time: datetime | time | None = None
    timezone: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=255)
    online_meeting_url: str | None = Field(default=None, max_length=255)
    capacity_required: int | None = Field(default=None, ge=1)
    volunteer_capacity: int | None = Field(default=None, ge=1)
    registration_deadline: datetime | None = None
    cover_media_id: uuid.UUID | None = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_update_capacity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            cap = data.get("capacity_required") or data.get("volunteer_capacity")
            if cap is not None:
                data["capacity_required"] = cap
                data["volunteer_capacity"] = cap
        return data

    @model_validator(mode="after")
    def validate_update_fields(self) -> "EventUpdateRequest":
        if self.mode == EventMode.OFFLINE and self.location is not None:
            if not self.location.strip():
                raise ValueError("Location cannot be empty for OFFLINE events.")
        elif self.mode == EventMode.ONLINE:
            meeting_url = self.online_meeting_url or self.location
            if meeting_url is not None:
                if not meeting_url.strip():
                    raise ValueError("Online meeting URL cannot be empty for ONLINE events.")
                self.online_meeting_url = meeting_url
                self.location = meeting_url

        if self.start_time is not None and isinstance(self.start_time, datetime):
            self.start_time = _ensure_aware_utc(self.start_time)
        if self.end_time is not None and isinstance(self.end_time, datetime):
            self.end_time = _ensure_aware_utc(self.end_time)
        if self.registration_deadline is not None:
            self.registration_deadline = _ensure_aware_utc(self.registration_deadline)

        if (
            self.start_time is not None
            and self.end_time is not None
            and isinstance(self.start_time, datetime)
            and isinstance(self.end_time, datetime)
            and self.end_time <= self.start_time
        ):
            raise ValueError("Event end_time must be strictly after start_time.")

        if (
            self.start_time is not None
            and self.registration_deadline is not None
            and isinstance(self.start_time, datetime)
            and self.registration_deadline > self.start_time
        ):
            raise ValueError("Registration deadline must be on or before start_time.")

        return self


class EventStatusTransitionRequest(BaseModel):
    """Payload for transitioning event lifecycle status."""

    model_config = ConfigDict(str_strip_whitespace=True)

    reason: str | None = Field(default=None, max_length=500)


class EventDuplicateRequest(BaseModel):
    """Payload for duplicating an event with adjusted schedule."""

    model_config = ConfigDict(str_strip_whitespace=True)

    new_start_time: datetime
    new_end_time: datetime
    new_registration_deadline: datetime

    @model_validator(mode="after")
    def validate_times(self) -> "EventDuplicateRequest":
        st = _ensure_aware_utc(self.new_start_time)
        et = _ensure_aware_utc(self.new_end_time)
        rd = _ensure_aware_utc(self.new_registration_deadline)

        if et <= st:
            raise ValueError("new_end_time must be strictly after new_start_time.")
        if rd > st:
            raise ValueError("new_registration_deadline must be on or before new_start_time.")

        self.new_start_time = st
        self.new_end_time = et
        self.new_registration_deadline = rd
        return self


class EventResponse(BaseSchema):
    """Comprehensive event detail response."""

    id: uuid.UUID
    title: str
    description: str
    category: str
    mode: str
    location: str
    online_meeting_url: str | None = None
    start_time: datetime
    end_time: datetime
    timezone: str
    capacity_required: int
    volunteer_capacity: int
    registration_deadline: datetime
    status: str
    cover_media_id: uuid.UUID | None = None
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    registered_count: int = 0
    selected_count: int = 0
    waitlisted_count: int = 0
    available_spots: int = 0


class EventListItem(BaseSchema):
    """Concise event summary item for directory and volunteer discovery listings."""

    id: uuid.UUID
    title: str
    category: str
    mode: str
    location: str
    online_meeting_url: str | None = None
    start_time: datetime
    end_time: datetime
    timezone: str
    capacity_required: int
    volunteer_capacity: int
    registration_deadline: datetime
    status: str
    registered_count: int = 0
    selected_count: int = 0
    available_spots: int = 0


class EventListResponse(BaseSchema):
    """Paginated collection of event summaries."""

    items: list[EventListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
