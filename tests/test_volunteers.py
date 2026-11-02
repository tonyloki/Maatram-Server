"""Integration test suite for Volunteer Profiles & Category Management (Phase 4)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.admin import AuditLog
from src.models.users import User
from src.models.volunteers import VolunteerProfile


async def create_approved_user(
    async_db: AsyncSession,
    email: str,
    password: str = "SecurePassword123!",
    role: str = "VOLUNTEER",
) -> User:
    """Helper to seed an approved user account directly in the DB."""
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        status="APPROVED",
        is_active=True,
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user


async def get_auth_token(
    client: AsyncClient, email: str, password: str = "SecurePassword123!"
) -> str:
    """Helper to log in and retrieve access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_get_my_volunteer_profile_student(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify Student volunteer can retrieve their own polymorphic profile."""
    email = f"student_{uuid.uuid4().hex[:6]}@example.com"
    mobile = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg_num = f"MAAT-{uuid.uuid4().hex[:6].upper()}"

    reg_payload = {
        "email": email,
        "password": "SecurePassword123!",
        "first_name": "Karthik",
        "last_name": "Raman",
        "mobile_number": mobile,
        "age": 21,
        "gender": "MALE",
        "category": "STUDENT",
        "student_details": {
            "college_name": "Anna University",
            "degree": "B.E.",
            "department": "ECE",
            "batch_year": 2025,
            "current_year": 4,
            "maatram_reg_number": reg_num,
        },
    }
    res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res_reg.status_code == 201

    # Approve user directly for login
    stmt = select(User).where(User.email == email)
    user_res = await async_db.execute(stmt)
    user = user_res.scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    token = await get_auth_token(client, email, "SecurePassword123!")

    # Fetch self profile
    res = await client.get("/api/v1/volunteers/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["first_name"] == "Karthik"
    assert data["category"] == "STUDENT"
    assert data["student_profile"] is not None
    assert data["student_profile"]["college_name"] == "Anna University"
    assert data["student_profile"]["maatram_reg_number"] == reg_num
    assert data["alumni_profile"] is None
    assert data["corporate_profile"] is None


@pytest.mark.asyncio
async def test_update_my_volunteer_profile_success(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify volunteer can self-update base fields and category attributes with audit logging."""
    email = f"student_upd_{uuid.uuid4().hex[:6]}@example.com"
    mobile = f"+9198{uuid.uuid4().int % 100000000:08d}"
    reg_num = f"MAAT-{uuid.uuid4().hex[:6].upper()}"

    reg_payload = {
        "email": email,
        "password": "SecurePassword123!",
        "first_name": "Deepa",
        "last_name": "S",
        "mobile_number": mobile,
        "age": 20,
        "gender": "FEMALE",
        "category": "STUDENT",
        "student_details": {
            "college_name": "PSG Tech",
            "degree": "B.Tech",
            "department": "IT",
            "batch_year": 2026,
            "current_year": 3,
            "maatram_reg_number": reg_num,
        },
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # Approve user
    stmt = select(User).where(User.email == email)
    user = (await async_db.execute(stmt)).scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    token = await get_auth_token(client, email, "SecurePassword123!")

    update_payload = {
        "bio": "Passionate educational volunteer and mentor.",
        "student_details": {
            "current_year": 4,
            "department": "Information Technology",
        },
    }
    res_patch = await client.patch(
        "/api/v1/volunteers/me",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_patch.status_code == 200
    updated_data = res_patch.json()
    assert updated_data["bio"] == "Passionate educational volunteer and mentor."
    assert updated_data["student_profile"]["current_year"] == 4
    assert updated_data["student_profile"]["department"] == "Information Technology"

    # Verify audit log was recorded
    audit_stmt = select(AuditLog).where(
        AuditLog.action == "VOLUNTEER_PROFILE_UPDATED",
        AuditLog.actor_user_id == user.id,
    )
    audit = (await async_db.execute(audit_stmt)).scalar_one_or_none()
    assert audit is not None


@pytest.mark.asyncio
async def test_update_student_duplicate_reg_number_conflict(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify modifying Maatram reg number to an already-assigned one raises 409 Conflict."""
    reg1 = f"MAAT-{uuid.uuid4().hex[:6].upper()}"
    reg2 = f"MAAT-{uuid.uuid4().hex[:6].upper()}"

    email1 = f"s1_{uuid.uuid4().hex[:6]}@example.com"
    email2 = f"s2_{uuid.uuid4().hex[:6]}@example.com"

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email1,
            "password": "SecurePassword123!",
            "first_name": "Student",
            "last_name": "One",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 20,
            "gender": "MALE",
            "category": "STUDENT",
            "student_details": {
                "college_name": "College A",
                "degree": "B.Sc",
                "department": "Maths",
                "batch_year": 2026,
                "current_year": 2,
                "maatram_reg_number": reg1,
            },
        },
    )

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email2,
            "password": "SecurePassword123!",
            "first_name": "Student",
            "last_name": "Two",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 21,
            "gender": "MALE",
            "category": "STUDENT",
            "student_details": {
                "college_name": "College B",
                "degree": "B.Sc",
                "department": "Physics",
                "batch_year": 2025,
                "current_year": 3,
                "maatram_reg_number": reg2,
            },
        },
    )

    # Approve user2
    user2 = (await async_db.execute(select(User).where(User.email == email2))).scalar_one()
    user2.status = "APPROVED"
    await async_db.commit()

    token2 = await get_auth_token(client, email2, "SecurePassword123!")

    # Attempt to update user2's reg number to reg1
    res = await client.patch(
        "/api/v1/volunteers/me",
        json={"student_details": {"maatram_reg_number": reg1}},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert res.status_code == 409
    assert "already in use" in res.json()["message"]


@pytest.mark.asyncio
async def test_volunteer_profile_ownership_bola(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify BOLA protection: non-admin volunteers cannot access other volunteers' profiles."""
    email1 = f"v1_{uuid.uuid4().hex[:6]}@example.com"
    email2 = f"v2_{uuid.uuid4().hex[:6]}@example.com"

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email1,
            "password": "SecurePassword123!",
            "first_name": "Alice",
            "last_name": "A",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 22,
            "gender": "FEMALE",
            "category": "STUDENT",
            "student_details": {
                "college_name": "College 1",
                "degree": "B.A.",
                "department": "English",
                "batch_year": 2024,
                "current_year": 3,
                "maatram_reg_number": f"MAAT-{uuid.uuid4().hex[:6].upper()}",
            },
        },
    )

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email2,
            "password": "SecurePassword123!",
            "first_name": "Bob",
            "last_name": "B",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 23,
            "gender": "MALE",
            "category": "STUDENT",
            "student_details": {
                "college_name": "College 2",
                "degree": "B.Com",
                "department": "Commerce",
                "batch_year": 2024,
                "current_year": 3,
                "maatram_reg_number": f"MAAT-{uuid.uuid4().hex[:6].upper()}",
            },
        },
    )

    u1 = (await async_db.execute(select(User).where(User.email == email1))).scalar_one()
    u2 = (await async_db.execute(select(User).where(User.email == email2))).scalar_one()
    u1.status = "APPROVED"
    u2.status = "APPROVED"
    await async_db.commit()

    token1 = await get_auth_token(client, email1, "SecurePassword123!")

    # Get profile 2 ID
    prof2 = (
        await async_db.execute(select(VolunteerProfile).where(VolunteerProfile.user_id == u2.id))
    ).scalar_one()

    # User 1 attempts to read Profile 2 -> 403 Forbidden
    res = await client.get(
        f"/api/v1/volunteers/{prof2.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert res.status_code == 403
    assert "permission" in res.json()["message"].lower()


@pytest.mark.asyncio
async def test_admin_directory_listing_and_filtering(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify admin directory queries support filtering and unauthorized volunteers are rejected."""
    # 1. Non-admin volunteer attempt -> 403 Forbidden
    vol_user = await create_approved_user(async_db, f"vol_{uuid.uuid4().hex[:6]}@example.com")
    vol_token = await get_auth_token(client, vol_user.email)

    res_forbidden = await client.get(
        "/api/v1/volunteers", headers={"Authorization": f"Bearer {vol_token}"}
    )
    assert res_forbidden.status_code == 403

    # 2. Admin queries
    admin_user = await create_approved_user(
        async_db, f"admin_{uuid.uuid4().hex[:6]}@maatram.org", role="ADMIN"
    )
    admin_token = await get_auth_token(client, admin_user.email)

    # Register a student volunteer to find in directory
    student_email = f"target_student_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": student_email,
            "password": "SecurePassword123!",
            "first_name": "Siddharth",
            "last_name": "Narayanan",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 20,
            "gender": "MALE",
            "category": "STUDENT",
            "student_details": {
                "college_name": "Loyola College",
                "degree": "B.Sc",
                "department": "Visual Comm",
                "batch_year": 2026,
                "current_year": 2,
                "maatram_reg_number": f"MAAT-{uuid.uuid4().hex[:6].upper()}",
            },
        },
    )

    res_admin = await client.get(
        "/api/v1/volunteers",
        params={"category": "STUDENT", "search": "Siddharth"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 200
    dir_data = res_admin.json()
    assert dir_data["total"] >= 1
    assert any(item["first_name"] == "Siddharth" for item in dir_data["items"])


@pytest.mark.asyncio
async def test_polymorphic_alumni_and_corporate_profiles(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify Alumni and Corporate profiles are correctly populated and updatable."""
    # Alumni registration
    alumni_email = f"alumni_{uuid.uuid4().hex[:6]}@example.com"
    alumni_payload = {
        "email": alumni_email,
        "password": "SecurePassword123!",
        "first_name": "Meera",
        "last_name": "Krishnan",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "age": 28,
        "gender": "FEMALE",
        "category": "ALUMNI",
        "alumni_details": {
            "organisation": "Zoho Corporation",
            "job_role": "Product Manager",
            "years_of_experience": 5.0,
            "location": "Chennai",
            "skills": ["Product Strategy", "Mentorship"],
            "college_name": "CEG Guindy",
            "degree": "B.E.",
            "department": "CSE",
            "batch_year": 2018,
            "graduation_year": 2022,
        },
    }
    res_alumni = await client.post("/api/v1/auth/register", json=alumni_payload)
    assert res_alumni.status_code == 201

    u_alumni = (await async_db.execute(select(User).where(User.email == alumni_email))).scalar_one()
    u_alumni.status = "APPROVED"
    await async_db.commit()

    token_alumni = await get_auth_token(client, alumni_email)
    res_get_alumni = await client.get(
        "/api/v1/volunteers/me", headers={"Authorization": f"Bearer {token_alumni}"}
    )
    assert res_get_alumni.status_code == 200
    a_data = res_get_alumni.json()
    assert a_data["category"] == "ALUMNI"
    assert a_data["alumni_profile"]["organisation"] == "Zoho Corporation"
    assert a_data["alumni_profile"]["job_role"] == "Product Manager"

    # Corporate Panelist registration
    corp_email = f"corp_{uuid.uuid4().hex[:6]}@example.com"
    corp_payload = {
        "email": corp_email,
        "password": "SecurePassword123!",
        "first_name": "Rajesh",
        "last_name": "Varma",
        "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
        "age": 35,
        "gender": "MALE",
        "category": "CORPORATE",
        "corporate_details": {
            "organisation": "Amazon Web Services",
            "designation": "Solutions Architect",
            "years_of_experience": 11.5,
            "location": "Bengaluru",
            "skills": ["Cloud Architecture", "System Design"],
        },
    }
    res_corp = await client.post("/api/v1/auth/register", json=corp_payload)
    assert res_corp.status_code == 201

    u_corp = (await async_db.execute(select(User).where(User.email == corp_email))).scalar_one()
    u_corp.status = "APPROVED"
    await async_db.commit()

    token_corp = await get_auth_token(client, corp_email)
    res_patch_corp = await client.patch(
        "/api/v1/volunteers/me",
        json={
            "corporate_details": {
                "designation": "Principal Solutions Architect",
                "skills": ["Cloud Architecture", "System Design", "Leadership"],
            }
        },
        headers={"Authorization": f"Bearer {token_corp}"},
    )
    assert res_patch_corp.status_code == 200
    c_updated = res_patch_corp.json()
    assert c_updated["corporate_profile"]["designation"] == "Principal Solutions Architect"
    assert "Leadership" in c_updated["corporate_profile"]["skills"]
