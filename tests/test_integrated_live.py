"""Integrated live system tests verifying FastAPI and Supabase database cooperation."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.config import settings
from src.main import app


@pytest.mark.asyncio
async def test_live_supabase_health_check():
    """Verify that the FastAPI application health check connects to live Supabase PostgreSQL."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"]["connected"] is True
        assert data["database"]["dialect"] == "postgresql"
        assert data["database"]["latency_ms"] > 0.0
        assert data["database"]["error"] is None
