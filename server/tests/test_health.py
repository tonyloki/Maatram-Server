"""Unit and integration tests for decoupled liveness, readiness, and composite health probes."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_liveness_probe_instant(client: AsyncClient):
    """Liveness probe must return instant 200 alive without database dependencies."""
    res = await client.get("/api/v1/health/liveness")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "alive"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_readiness_probe_success(client: AsyncClient, async_db: AsyncSession):
    """Readiness probe verifies live database connectivity within timeout."""
    res = await client.get("/api/v1/health/readiness")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"]["connected"] is True
    assert data["database"]["latency_ms"] >= 0.0


@pytest.mark.asyncio
async def test_composite_health_probe(client: AsyncClient, async_db: AsyncSession):
    """Backward-compatible health endpoint reports healthy database status."""
    res = await client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"]["connected"] is True
