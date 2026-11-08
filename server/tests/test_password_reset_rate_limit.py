"""Integration tests for password reset rate limiting and anti-enumeration protection."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.rate_limiter import pg_rate_limiter
from src.core.security import get_password_hash
from src.models.users import User


@pytest.mark.asyncio
async def test_password_reset_anti_enumeration(client: AsyncClient, async_db: AsyncSession):
    """Verify that password reset requests for non-existent and existing emails return identical generic responses."""
    # 1. Non-existent email
    res_non_existent = await client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": f"nonexistent_{uuid.uuid4().hex[:6]}@example.com"},
    )
    assert res_non_existent.status_code == 200
    msg1 = res_non_existent.json()["message"]
    assert "If the account exists, a reset code has been sent." in msg1

    # 2. Existing email
    email = f"user_{uuid.uuid4().hex[:6]}@maatram.org"
    user = User(
        email=email,
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    res_existing = await client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": email},
    )
    assert res_existing.status_code == 200
    msg2 = res_existing.json()["message"]
    assert msg1 == msg2


@pytest.mark.asyncio
async def test_password_reset_ip_rate_limiting(client: AsyncClient, async_db: AsyncSession):
    """Verify that exceeding 5 password reset requests within the window triggers HTTP 429 with Retry-After header."""
    # Reset limiter records for clean test
    await pg_rate_limiter.reset(async_db)

    email = f"ratelimit_{uuid.uuid4().hex[:6]}@example.com"

    # Send 5 allowed requests
    for i in range(5):
        res = await client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": email},
        )
        assert res.status_code == 200, f"Request {i+1} failed unexpectedly"

    # 6th request must trigger rate limit
    res_blocked = await client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": email},
    )
    assert res_blocked.status_code == 429
    assert res_blocked.headers.get("Retry-After") == "900"
    data = res_blocked.json()
    assert data.get("error_code") == "RATE_LIMIT_EXCEEDED" or data.get("error", {}).get("code") == "RATE_LIMIT_EXCEEDED"

    # Clean up limiter records
    await pg_rate_limiter.reset(async_db)
