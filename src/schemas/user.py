"""User profile and session DTO schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    """Client session metadata representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device_info: str | None
    ip_address: str | None
    client_type: str
    is_revoked: bool
    created_at: datetime
    last_used_at: datetime
    is_current: bool = False


class UserMeResponse(BaseModel):
    """Detailed authenticated user profile representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    status: str
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
