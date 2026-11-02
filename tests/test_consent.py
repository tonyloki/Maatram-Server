"""Integration test suite for Affirmative Consent Governance & Differential Audit History (Phase 5)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User


async def get_token(client: AsyncClient, email: str, password: str = "SecurePassword123!") -> str:
    """Helper to log in and retrieve access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_get_my_consent_initial(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify volunteer can retrieve their initial affirmative consent record."""
    email = f"consent_init_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "SecurePassword123!",
        "first_name": "Divya",
        "last_name": "R",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "age": 22,
        "gender": "FEMALE",
        "category": "CORPORATE",
        "corporate_details": {
            "organisation": "Wipro",
            "designation": "Engineer",
            "years_of_experience": 1.5,
            "location": "Chennai",
            "skills": [],
        },
        "consent": {
            "leaderboard_visible": True,
            "name_visible": True,
            "thank_you_emails": False,
            "linkedin_content": False,
            "contact_available": False,
            "media_usage": False,
        },
    }
    res_reg = await client.post("/api/v1/auth/register", json=payload)
    assert res_reg.status_code == 201

    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    token = await get_token(client, email)

    res = await client.get("/api/v1/consent/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["leaderboard_visible"] is True
    assert data["name_visible"] is True
    assert data["thank_you_emails"] is False
    assert data["media_usage"] is False
    assert data["version"] == 1


@pytest.mark.asyncio
async def test_update_my_consent_creates_differential_history(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify modifying consent settings generates differential entries in consent_history."""
    email = f"consent_diff_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Kavitha",
            "last_name": "N",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 23,
            "gender": "FEMALE",
            "category": "CORPORATE",
            "corporate_details": {
                "organisation": "Infosys",
                "designation": "Consultant",
                "years_of_experience": 2.0,
                "location": "Chennai",
                "skills": [],
            },
            "consent": {
                "leaderboard_visible": False,
                "name_visible": False,
                "thank_you_emails": False,
                "linkedin_content": False,
                "contact_available": False,
                "media_usage": False,
            },
        },
    )

    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    token = await get_token(client, email)

    # 1. Update two dimensions: leaderboard_visible and media_usage
    update_payload = {
        "leaderboard_visible": True,
        "media_usage": True,
    }
    res_update = await client.put(
        "/api/v1/consent/me",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_update.status_code == 200
    upd_data = res_update.json()
    assert upd_data["leaderboard_visible"] is True
    assert upd_data["media_usage"] is True
    assert upd_data["version"] == 2

    # 2. Query differential history
    res_hist = await client.get(
        "/api/v1/consent/me/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert res_hist.status_code == 200
    hist_data = res_hist.json()
    assert hist_data["total"] == 2
    dims_changed = {item["dimension"] for item in hist_data["items"]}
    assert dims_changed == {"leaderboard_visible", "media_usage"}

    for item in hist_data["items"]:
        assert item["old_value"] is False
        assert item["new_value"] is True
        assert item["changed_by_user_id"] == str(user.id)


@pytest.mark.asyncio
async def test_update_consent_no_op_does_not_create_history(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify sending identical consent values does not increment version or write history."""
    email = f"consent_noop_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Prabhu",
            "last_name": "K",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 25,
            "gender": "MALE",
            "category": "CORPORATE",
            "corporate_details": {
                "organisation": "HCL",
                "designation": "Developer",
                "years_of_experience": 3.0,
                "location": "Chennai",
                "skills": [],
            },
            "consent": {
                "leaderboard_visible": True,
                "name_visible": True,
            },
        },
    )

    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    token = await get_token(client, email)

    # Send identical value
    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["version"] == 1

    # History should be empty
    res_hist = await client.get(
        "/api/v1/consent/me/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert res_hist.status_code == 200
    assert res_hist.json()["total"] == 0


@pytest.mark.asyncio
async def test_consent_unauthenticated_returns_401(client: AsyncClient) -> None:
    """Verify unauthenticated requests to consent endpoints return 401 Unauthorized."""
    res_get = await client.get("/api/v1/consent/me")
    assert res_get.status_code == 401

    res_put = await client.put("/api/v1/consent/me", json={"leaderboard_visible": True})
    assert res_put.status_code == 401

    res_hist = await client.get("/api/v1/consent/me/history")
    assert res_hist.status_code == 401
