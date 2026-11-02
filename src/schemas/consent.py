"""Pydantic schemas for Affirmative Consent records and differential audit history."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConsentResponse(BaseModel):
    """Current affirmative consent settings across 6 privacy dimensions."""

    id: uuid.UUID
    volunteer_profile_id: uuid.UUID
    leaderboard_visible: bool
    name_visible: bool
    thank_you_emails: bool
    linkedin_content: bool
    contact_available: bool
    media_usage: bool
    version: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsentUpdate(BaseModel):
    """Self-service payload for modifying affirmative consent settings."""

    leaderboard_visible: bool | None = None
    name_visible: bool | None = None
    thank_you_emails: bool | None = None
    linkedin_content: bool | None = None
    contact_available: bool | None = None
    media_usage: bool | None = None


class ConsentHistoryItem(BaseModel):
    """Immutable audit trail entry of a single consent dimension alteration."""

    id: uuid.UUID
    consent_record_id: uuid.UUID
    dimension: str
    old_value: bool
    new_value: bool
    changed_by_user_id: uuid.UUID
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsentHistoryResponse(BaseModel):
    """Full differential history of consent modifications for a volunteer."""

    items: list[ConsentHistoryItem]
    total: int
