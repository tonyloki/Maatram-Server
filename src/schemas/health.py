"""Health check response schemas."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.schemas.common import BaseSchema


class DatabaseHealth(BaseModel):
    """Database connectivity and latency details."""

    connected: bool
    dialect: str
    latency_ms: float = Field(..., description="Query roundtrip time in milliseconds")
    error: str | None = None


class HealthResponse(BaseSchema):
    """System health check response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    database: DatabaseHealth
