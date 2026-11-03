"""Rate limiting models for PostgreSQL-backed sliding-window rate limiter."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, UUIDPrimaryKeyMixin, utc_now


class RateLimitAttempt(Base, UUIDPrimaryKeyMixin):
    """PostgreSQL-backed sliding window rate limit counter."""

    __tablename__ = "rate_limit_attempts"

    identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    endpoint_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        UniqueConstraint("identifier", "endpoint_key", name="uq_rate_limit_identifier_endpoint"),
    )
