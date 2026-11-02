"""Pydantic schemas for Admin Dashboard analytics and Audit Logs."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class VolunteerStats(BaseModel):
    """Volunteer category & status aggregation."""

    total_volunteers: int
    active_volunteers: int
    by_category: dict[str, int]


class ApplicationPipelineStats(BaseModel):
    """Volunteer onboarding application status counts."""

    pending: int
    approved: int
    rejected: int
    total: int


class EventStats(BaseModel):
    """Event management operational statistics."""

    total_events: int
    by_status: dict[str, int]
    completed_events: int


class EngagementMetrics(BaseModel):
    """Aggregated volunteer hours and points metrics."""

    total_registrations: int
    total_hours_credited: str
    total_points_allocated: str


class ActivityItem(BaseModel):
    """Audit log item in recent activity stream."""

    id: uuid.UUID
    action: str
    actor_email: str | None = None
    resource_type: str
    resource_id: str
    created_at: datetime


class AdminDashboardResponse(BaseModel):
    """Comprehensive Admin Dashboard aggregation."""

    volunteers: VolunteerStats
    applications: ApplicationPipelineStats
    events: EventStats
    engagement: EngagementMetrics
    recent_activity: list[ActivityItem]


class AuditLogResponse(BaseModel):
    """Immutable administrative and security audit trail record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_user_id: uuid.UUID | None = None
    actor_email: str | None = None
    action: str
    resource_type: str
    resource_id: str
    old_state: dict[str, Any] | None = None
    new_state: dict[str, Any] | None = None
    reason: str | None = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Paginated list of audit trail entries."""

    items: list[AuditLogResponse]
    total: int
    page: int
    limit: int
    total_pages: int
