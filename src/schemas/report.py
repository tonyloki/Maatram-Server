"""Pydantic schemas for Administrative Reports and Excel Export."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StudentContributionItem(BaseModel):
    """Row item in Student Contribution Report."""

    volunteer_id: uuid.UUID
    student_name: str
    college_name: str
    department: str
    batch_year: int | None = None
    maatram_reg_number: str | None = None
    events_attended: int
    hours_credited: str
    points_earned: str


class StudentContributionReportResponse(BaseModel):
    """Envelope for Student Contribution Report."""

    items: list[StudentContributionItem]
    total: int
    page: int
    limit: int
    total_pages: int


class AlumniContributionItem(BaseModel):
    """Row item in Alumni Contribution Report."""

    volunteer_id: uuid.UUID
    alumni_name: str
    graduation_batch: int | None = None
    employer: str | None = None
    designation: str | None = None
    events_attended: int
    hours_credited: str
    points_earned: str


class AlumniContributionReportResponse(BaseModel):
    """Envelope for Alumni Contribution Report."""

    items: list[AlumniContributionItem]
    total: int
    page: int
    limit: int
    total_pages: int


class YearlyConsistencyMetric(BaseModel):
    """Annual breakdown for alumni volunteerism."""

    year: int
    events_attended: int
    hours_credited: str


class AlumniConsistencyItem(BaseModel):
    """Row item in Alumni Consistency Report."""

    volunteer_id: uuid.UUID
    alumni_name: str
    graduation_batch: int | None = None
    employer: str | None = None
    yearly_metrics: list[YearlyConsistencyMetric]
    years_active_count: int
    is_consistent: bool


class AlumniConsistencyReportResponse(BaseModel):
    """Envelope for Alumni Consistency Report."""

    items: list[AlumniConsistencyItem]
    total: int
    page: int
    limit: int
    total_pages: int


class InactiveVolunteerItem(BaseModel):
    """Row item in Inactive Volunteer Report."""

    volunteer_id: uuid.UUID
    name: str
    email: str
    category: str
    registration_date: datetime
    last_activity_date: datetime | None = None
    days_inactive: int


class InactiveVolunteerReportResponse(BaseModel):
    """Envelope for Inactive Volunteer Report."""

    threshold_days: int
    items: list[InactiveVolunteerItem]
    total: int
    page: int
    limit: int
    total_pages: int


class InterviewAvailabilityItem(BaseModel):
    """Row item in Interview Availability Report with privacy contact masking."""

    volunteer_id: uuid.UUID
    name: str
    category: str
    employer: str | None = None
    designation: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: float | None = None
    phone_number: str
    email: str
    is_contact_masked: bool


class InterviewAvailabilityReportResponse(BaseModel):
    """Envelope for Interview Availability Report."""

    items: list[InterviewAvailabilityItem]
    total: int
    page: int
    limit: int
    total_pages: int


class OrganisationContributionItem(BaseModel):
    """Row item in Employer / Organisation Contribution Report."""

    organisation_name: str
    volunteer_count: int
    total_events_attended: int
    total_hours_credited: str
    total_points_earned: str


class OrganisationContributionReportResponse(BaseModel):
    """Envelope for Employer / Organisation Contribution Report."""

    items: list[OrganisationContributionItem]
    total: int
    page: int
    limit: int
    total_pages: int


class ReportExportRequest(BaseModel):
    """Payload to trigger asynchronous or streaming report export."""

    report_type: str = Field(
        ...,
        description="STUDENT_CONTRIBUTIONS, ALUMNI_CONTRIBUTIONS, ALUMNI_CONSISTENCY, INACTIVE_VOLUNTEERS, INTERVIEW_AVAILABILITY, ORGANISATION_CONTRIBUTIONS",
    )
    parameters: dict[str, Any] = Field(default_factory=dict)


class ReportExportResponse(BaseModel):
    """Metadata response when triggering a report export."""

    export_id: uuid.UUID
    report_type: str
    status: str
    record_count: int = 0
    created_at: datetime
    expires_at: datetime
