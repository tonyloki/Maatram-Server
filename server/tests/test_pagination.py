"""Unit tests for pagination parameters and query bounds governance."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import create_access_token, get_password_hash
from src.models.users import User
from src.schemas.common import PaginationParams


def test_pagination_params_defaults():
    """Verify default values for PaginationParams."""
    p = PaginationParams()
    assert p.page == 1
    assert p.limit == 20
    assert p.page_size == 20
    assert p.offset == 0


def test_pagination_params_explicit():
    """Verify explicit page and limit compute correct offset."""
    p = PaginationParams(page=3, limit=50)
    assert p.page == 3
    assert p.limit == 50
    assert p.page_size == 50
    assert p.offset == 100


def test_pagination_params_alias():
    """Verify page_size alias maps correctly to limit."""
    p = PaginationParams(page=2, page_size=25)
    assert p.page == 2
    assert p.limit == 25
    assert p.page_size == 25
    assert p.offset == 25


@pytest.mark.asyncio
async def test_endpoint_pagination_bounds_rejection(client: AsyncClient, async_db: AsyncSession):
    """Verify that requests exceeding max items (100) or below min (1) are rejected with 422."""
    password = "Password123!"
    email = f"pag_test_{uuid.uuid4().hex[:6]}@maatram.org"
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role="VOLUNTEER",
        status="APPROVED",
    )
    async_db.add(user)
    await async_db.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test on events list endpoint
    res_over = await client.get("/api/v1/events?limit=101", headers=headers)
    assert res_over.status_code == 422

    res_zero = await client.get("/api/v1/events?limit=0", headers=headers)
    assert res_zero.status_code == 422

    res_negative = await client.get("/api/v1/events?limit=-5", headers=headers)
    assert res_negative.status_code == 422

    res_page_zero = await client.get("/api/v1/events?page=0", headers=headers)
    assert res_page_zero.status_code == 422

    # Valid boundary limits should pass validation
    res_valid_1 = await client.get("/api/v1/events?limit=1&page=1", headers=headers)
    assert res_valid_1.status_code == 200

    res_valid_100 = await client.get("/api/v1/events?limit=100&page=1", headers=headers)
    assert res_valid_100.status_code == 200
