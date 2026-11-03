"""Rate limiting utilities for authentication and sensitive endpoints.

Includes:
- PostgreSQLRateLimiter: Canonical PostgreSQL-backed sliding-window counter using atomic UPSERT.
- InMemoryRateLimiter: Development/test fallback limiter.
"""

import asyncio
import uuid
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import RateLimitExceededException


class InMemoryRateLimiter:
    """Development/test only. Not suitable for multi-worker production deployments."""

    def __init__(self) -> None:
        self._records: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        error_message: str = "Too many requests. Please try again later.",
    ) -> None:
        """Check and record request timestamp, raising RateLimitExceededException if exceeded."""
        now = datetime.now(UTC).timestamp()
        window_start = now - window_seconds

        async with self._lock:
            # Purge expired timestamps
            timestamps = [ts for ts in self._records[key] if ts > window_start]
            if len(timestamps) >= max_requests:
                self._records[key] = timestamps
                raise RateLimitExceededException(message=error_message)

            timestamps.append(now)
            self._records[key] = timestamps

    async def reset(self) -> None:
        """Clear all rate limit tracking (useful in automated tests)."""
        async with self._lock:
            self._records.clear()


class PostgreSQLRateLimiter:
    """Canonical PostgreSQL-backed sliding-window rate limiter for multi-worker deployments.

    Uses atomic `INSERT ... ON CONFLICT DO UPDATE` for thread-safe sliding window tracking.
    """

    async def check_and_increment(
        self,
        db: AsyncSession,
        identifier: str,
        endpoint_key: str,
        max_attempts: int,
        window_seconds: int,
    ) -> bool:
        """Check current attempt count within window and increment atomically.

        Returns:
            True if request is allowed (count <= max_attempts).
            False if rate limited (count > max_attempts).
        """
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=window_seconds)

        upsert_stmt = text("""
            INSERT INTO rate_limit_attempts (id, identifier, endpoint_key, window_start, attempt_count)
            VALUES (:id, :identifier, :endpoint_key, :now, 1)
            ON CONFLICT (identifier, endpoint_key) DO UPDATE
            SET 
              attempt_count = CASE 
                WHEN rate_limit_attempts.window_start < :cutoff THEN 1
                ELSE rate_limit_attempts.attempt_count + 1
              END,
              window_start = CASE 
                WHEN rate_limit_attempts.window_start < :cutoff THEN :now
                ELSE rate_limit_attempts.window_start
              END
            RETURNING attempt_count;
        """)

        result = await db.execute(
            upsert_stmt,
            {
                "id": str(uuid.uuid4()),
                "identifier": identifier,
                "endpoint_key": endpoint_key,
                "now": now,
                "cutoff": cutoff,
            },
        )
        attempt_count = result.scalar_one()

        # Opportunistic cleanup of expired windows older than 24 hours
        try:
            old_cutoff = now - timedelta(hours=24)
            await db.execute(
                text("DELETE FROM rate_limit_attempts WHERE window_start < :old_cutoff"),
                {"old_cutoff": old_cutoff},
            )
        except Exception:
            pass

        return bool(attempt_count <= max_attempts)

    async def reset(self, db: AsyncSession) -> None:
        """Clear all rate limit records (useful in automated tests)."""
        await db.execute(text("DELETE FROM rate_limit_attempts"))
        await db.commit()


rate_limiter = InMemoryRateLimiter()
pg_rate_limiter = PostgreSQLRateLimiter()
