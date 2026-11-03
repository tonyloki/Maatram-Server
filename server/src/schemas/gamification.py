"""Gamification, Decimal Points & Leaderboards Pydantic schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.common import BaseSchema


class AttendeeCompletionPreview(BaseSchema):
    """Preview metrics for a single event attendee prior to finalization."""

    volunteer_profile_id: uuid.UUID
    volunteer_name: str
    category: str
    attendance_status: str
    duration_minutes: int | None
    hours_credited: Decimal = Decimal("0.00")
    event_points: Decimal = Decimal("0.00")
    hour_points: Decimal = Decimal("0.00")
    total_points: Decimal = Decimal("0.00")
    is_qualifying: bool = False
    warnings: list[str] = Field(default_factory=list)


class EventCompletionPreviewResponse(BaseSchema):
    """Comprehensive preview of point awards and communication jobs prior to event finalization."""

    event_id: uuid.UUID
    event_title: str
    event_status: str
    total_selected: int
    total_attended: int
    total_incomplete: int
    total_absent: int
    total_hours_credited: Decimal = Decimal("0.00")
    total_points_to_award: Decimal = Decimal("0.00")
    thank_you_recipients_count: int
    attendees: list[AttendeeCompletionPreview]
    draft_linkedin_copy: str


class EventCompletionResponse(BaseSchema):
    """Result of atomic event completion and gamification point allocation."""

    event_id: uuid.UUID
    status: str
    completed_at: datetime
    total_volunteers_awarded: int
    total_points_awarded: Decimal = Decimal("0.00")
    total_hours_credited: Decimal = Decimal("0.00")
    outbox_jobs_created: int
    achievements_awarded_count: int


class PointTransactionResponse(BaseSchema):
    """Single item in the immutable point transactions ledger."""

    id: uuid.UUID
    volunteer_profile_id: uuid.UUID
    event_id: uuid.UUID | None = None
    related_transaction_id: uuid.UUID | None = None
    event_points: Decimal = Decimal("0.00")
    hour_points: Decimal = Decimal("0.00")
    total_points: Decimal = Decimal("0.00")
    hours_credited: Decimal = Decimal("0.00")
    transaction_type: str
    reason: str | None = None
    cycle_year: int
    created_at: datetime


class PointLedgerResponse(BaseSchema):
    """Paginated collection of ledger point transactions."""

    items: list[PointTransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    net_points: Decimal = Decimal("0.00")


class PointAdjustmentRequest(BaseModel):
    """Payload for administrative compensating point ledger adjustments."""

    model_config = ConfigDict(str_strip_whitespace=True)

    volunteer_profile_id: uuid.UUID
    event_id: uuid.UUID | None = None
    related_transaction_id: uuid.UUID | None = None
    event_points: Decimal = Field(default=Decimal("0.00"), description="Event points delta")
    hour_points: Decimal = Field(default=Decimal("0.00"), description="Hour points delta")
    hours_credited: Decimal = Field(default=Decimal("0.00"), description="Credited hours delta")
    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Mandatory justification for compensating adjustment",
    )
    cycle_year: int | None = None


class GamificationSummaryResponse(BaseSchema):
    """Volunteer gamification overview (points, hours, events, badges)."""

    volunteer_profile_id: uuid.UUID
    total_points: Decimal = Decimal("0.00")
    total_hours: Decimal = Decimal("0.00")
    completed_events_count: int = 0
    badges_earned_count: int = 0
    rank: int | None = None
    cycle_year: int


class LeaderboardItemResponse(BaseSchema):
    """Single entry in multi-tier leaderboard rankings."""

    rank: int
    volunteer_profile_id: uuid.UUID | None = None
    volunteer_name: str
    category: str
    total_points: Decimal = Decimal("0.00")
    events_attended: int = 0
    total_hours: Decimal = Decimal("0.00")
    is_anonymous: bool = False
    avatar_url: str | None = None


class LeaderboardResponse(BaseSchema):
    """Paginated leaderboard ranking response."""

    cycle_year: int
    category: str
    items: list[LeaderboardItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AchievementDefinitionResponse(BaseSchema):
    """Achievement badge definition and earned status."""

    id: uuid.UUID
    code: str
    title: str
    description: str
    icon_url: str
    category: str
    criteria_type: str
    criteria_threshold: Decimal
    is_active: bool
    is_earned: bool = False
    awarded_at: datetime | None = None


class VolunteerAchievementsListResponse(BaseSchema):
    """List of all available and earned achievements for a volunteer."""

    items: list[AchievementDefinitionResponse]
    total_earned: int
    total_available: int
