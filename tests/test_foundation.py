"""Foundational application tests for Phase 1 (Milestone A)."""

import pytest
from httpx import AsyncClient

from src.core.config import settings


@pytest.mark.asyncio
async def test_settings_load():
    """Verify application configuration loads with expected defaults and types."""
    assert settings.PROJECT_NAME == "Maatram Volunteering & Gamification Portal"
    assert settings.API_V1_STR == "/api/v1"
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
    assert settings.LEADERBOARD_CYCLE_TYPE == "CALENDAR_YEAR"
    assert settings.HOURS_ROUNDING_MODE == "EXACT_DECIMAL_2"
    assert settings.EVENT_QUALIFICATION_MIN_MINUTES == 60


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Verify root metadata discovery endpoint returns 200 and expected schema."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
    assert data["environment"] == settings.ENVIRONMENT
    assert data["docs_url"] == "/docs"
    assert data["health_check"] == f"{settings.API_V1_STR}/health"


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Verify health check endpoint executes query and returns structured latency data."""
    response = await client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["version"] == settings.VERSION
    assert "database" in data
    assert data["database"]["connected"] is True
    assert "latency_ms" in data["database"]
    assert data["database"]["latency_ms"] >= 0.0


@pytest.mark.asyncio
async def test_openapi_schema(client: AsyncClient):
    """Verify OpenAPI JSON specification is generated properly under /api/v1."""
    response = await client.get(f"{settings.API_V1_STR}/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == settings.PROJECT_NAME
    assert data["info"]["version"] == settings.VERSION
    assert "/api/v1/health" in data["paths"]


@pytest.mark.asyncio
async def test_cors_preflight(client: AsyncClient):
    """Verify CORS middleware responds with correct headers to cross-origin requests."""
    response = await client.options(
        f"{settings.API_V1_STR}/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_domain_exception_handling():
    """Verify DomainException returns uniform structured error response."""
    from starlette.requests import Request

    from src.core.exceptions import DomainException, domain_exception_handler

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/test",
        "headers": [],
    }
    req = Request(scope)
    exc = DomainException(
        message="Duplicate email",
        status_code=409,
        code="DUPLICATE_EMAIL",
        details={"field": "email"},
    )
    res = await domain_exception_handler(req, exc)
    assert res.status_code == 409
    import json

    data = json.loads(res.body)
    assert data["error"]["code"] == "DUPLICATE_EMAIL"
    assert data["error"]["message"] == "Duplicate email"
    assert data["error"]["details"]["field"] == "email"
