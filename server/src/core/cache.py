"""In-memory TTL cache with prefix-based invalidation for high-throughput read endpoints."""

import asyncio
import time
from dataclasses import dataclass
from typing import Any

from src.core.config import settings
from src.core.logging import logger


@dataclass
class CacheEntry:
    data: Any
    expires_at: float


class InMemoryTtlCache:
    """Thread-safe and async-compatible in-memory cache supporting TTL expiry
    and prefix-based cache invalidation for public listings and leaderboards.

    Disabled by default when ENABLE_IN_MEMORY_CACHE is False to prevent stale
    data across multi-worker Uvicorn processes.
    """

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Retrieve value if cache is enabled, key exists, and has not expired."""
        if not getattr(settings, "ENABLE_IN_MEMORY_CACHE", False):
            return None
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if time.monotonic() > entry.expires_at:
                del self._store[key]
                return None
            return entry.data

    async def set(self, key: str, value: Any, ttl_seconds: float = 60.0) -> None:
        """Store value with explicit TTL duration if cache is enabled."""
        if not getattr(settings, "ENABLE_IN_MEMORY_CACHE", False):
            return
        async with self._lock:
            self._store[key] = CacheEntry(
                data=value,
                expires_at=time.monotonic() + ttl_seconds,
            )

    async def invalidate_prefix(self, prefix: str) -> int:
        """Remove all cache keys matching the given prefix."""
        async with self._lock:
            matching_keys = [k for k in self._store if k.startswith(prefix)]
            for k in matching_keys:
                del self._store[k]
            if matching_keys:
                logger.debug(f"Invalidated {len(matching_keys)} cache entries for prefix: {prefix}")
            return len(matching_keys)

    async def clear(self) -> None:
        """Purge all entries from the cache."""
        async with self._lock:
            self._store.clear()


# Global in-memory cache singleton
cache = InMemoryTtlCache()

