"""Pydantic schemas for Notification, FCM Device Tokens, and Outbox Job management."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class DeviceTokenRegister(BaseModel):
    """Payload to register or refresh an FCM device token."""

    fcm_token: str = Field(..., min_length=10, max_length=255, description="FCM registration token")
    device_platform: Literal["ANDROID", "IOS"] = Field(..., description="Device operating system")


class DeviceTokenResponse(BaseModel):
    """Device token representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    fcm_token: str
    device_platform: str
    is_active: bool
    last_seen_at: datetime
    created_at: datetime


class NotificationResponse(BaseModel):
    """In-app notification DTO."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    type: str
    action_url: str | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def body(self) -> str:
        """Alias for message to support multi-client contracts."""
        return self.message

    @computed_field  # type: ignore[prop-decorator]
    @property
    def notification_type(self) -> str:
        """Alias for type to support multi-client contracts."""
        return self.type


class NotificationListResponse(BaseModel):
    """Paginated list of in-app notifications with unread count envelope."""

    items: list[NotificationResponse]
    total: int
    page: int
    limit: int
    total_pages: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    """Unread notifications count."""

    unread_count: int


class MarkReadResponse(BaseModel):
    """Read status update confirmation."""

    id: uuid.UUID
    is_read: bool
    read_at: datetime | None


class MarkAllReadResponse(BaseModel):
    """Bulk read confirmation."""

    marked_count: int
    message: str


class OutboxJobResponse(BaseModel):
    """Outbox communication job representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel: str
    recipient: str
    template_name: str
    payload: dict[str, Any]
    status: str
    attempts: int
    max_retries: int
    last_error: str | None = None
    idempotency_key: str
    scheduled_at: datetime
    locked_at: datetime | None = None
    worker_id: str | None = None
    sent_at: datetime | None = None
    created_at: datetime


class OutboxJobListResponse(BaseModel):
    """Paginated list of outbox communication jobs."""

    items: list[OutboxJobResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class OutboxRetryResponse(BaseModel):
    """Response when manually retrying or requeuing an outbox job."""

    job_id: uuid.UUID
    status: str
    message: str

