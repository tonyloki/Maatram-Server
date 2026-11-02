"""Attendance Tracking & Hours Management Pydantic schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.schemas.common import BaseSchema


class CheckInRequest(BaseModel):
    """Payload for volunteer attendance check-in."""

    model_config = ConfigDict(str_strip_whitespace=True)

    volunteer_profile_id: uuid.UUID | None = None
    volunteer_profile_ids: list[uuid.UUID] | None = None
    check_in_time: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_volunteers(self) -> "CheckInRequest":
        """Normalize individual or list of volunteer IDs."""
        ids: list[uuid.UUID] = []
        if self.volunteer_profile_ids:
            ids.extend(self.volunteer_profile_ids)
        if self.volunteer_profile_id and self.volunteer_profile_id not in ids:
            ids.append(self.volunteer_profile_id)

        if not ids:
            raise ValueError("At least one volunteer_profile_id must be provided for check-in.")
        self.volunteer_profile_ids = ids
        return self


class CheckOutRequest(BaseModel):
    """Payload for volunteer attendance check-out."""

    model_config = ConfigDict(str_strip_whitespace=True)

    volunteer_profile_id: uuid.UUID | None = None
    volunteer_profile_ids: list[uuid.UUID] | None = None
    check_out_time: datetime | None = None

    @model_validator(mode="after")
    def validate_volunteers(self) -> "CheckOutRequest":
        """Normalize individual or list of volunteer IDs."""
        ids: list[uuid.UUID] = []
        if self.volunteer_profile_ids:
            ids.extend(self.volunteer_profile_ids)
        if self.volunteer_profile_id and self.volunteer_profile_id not in ids:
            ids.append(self.volunteer_profile_id)

        if not ids:
            raise ValueError("At least one volunteer_profile_id must be provided for check-out.")
        self.volunteer_profile_ids = ids
        return self


class AttendanceCorrectionRequest(BaseModel):
    """Payload for administrative attendance record correction."""

    model_config = ConfigDict(str_strip_whitespace=True)

    new_check_in_time: datetime = Field(..., description="Corrected check-in timestamp (UTC)")
    new_check_out_time: datetime = Field(..., description="Corrected check-out timestamp (UTC)")
    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Mandatory reason justifying the attendance override",
    )

    @model_validator(mode="after")
    def validate_timestamps(self) -> "AttendanceCorrectionRequest":
        """Ensure check-out does not precede check-in."""
        if self.new_check_out_time < self.new_check_in_time:
            raise ValueError("Corrected check-out time cannot precede check-in time.")
        return self


class BulkAttendanceRequest(BaseModel):
    """Payload for administrative bulk attendance processing."""

    model_config = ConfigDict(str_strip_whitespace=True)

    action: Literal["CHECK_IN", "CHECK_OUT"] = Field(..., description="Bulk action to execute")
    volunteer_profile_ids: list[uuid.UUID] = Field(
        ..., min_length=1, description="List of volunteer profile IDs to process"
    )
    timestamp: datetime | None = Field(
        default=None, description="Optional override timestamp (UTC)"
    )


class AttendanceCorrectionResponse(BaseSchema):
    """Response DTO for an attendance correction record."""

    id: uuid.UUID
    attendance_record_id: uuid.UUID
    admin_id: uuid.UUID
    old_check_in_time: datetime
    new_check_in_time: datetime
    old_check_out_time: datetime | None
    new_check_out_time: datetime
    old_duration_minutes: int | None
    new_duration_minutes: int
    reason: str
    super_admin_approved_by: uuid.UUID | None
    created_at: datetime


class AttendanceRecordResponse(BaseSchema):
    """Response DTO representing an individual attendance log."""

    id: uuid.UUID
    event_registration_id: uuid.UUID
    event_id: uuid.UUID
    volunteer_profile_id: uuid.UUID
    volunteer_name: str | None = None
    volunteer_email: str | None = None
    event_title: str | None = None
    check_in_time: datetime
    check_out_time: datetime | None = None
    duration_minutes: int | None = None
    hours_credited: Decimal = Decimal("0.00")
    status: str
    verified_by_user_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    corrections_count: int = 0


class AttendanceListResponse(BaseSchema):
    """Paginated collection of attendance records."""

    items: list[AttendanceRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BulkAttendanceResultItem(BaseSchema):
    """Result of an individual check-in/out within a bulk batch."""

    volunteer_profile_id: uuid.UUID
    success: bool
    status: str | None = None
    attendance_record_id: uuid.UUID | None = None
    error: str | None = None


class BulkAttendanceResponse(BaseSchema):
    """Aggregated response for a bulk attendance operation."""

    action: str
    total_requested: int
    successful_count: int
    failed_count: int
    results: list[BulkAttendanceResultItem]
