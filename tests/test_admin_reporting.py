"""Comprehensive test suite for Admin Dashboard, Reporting APIs, Excel Export & Security (Phase 12)."""

import io
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import openpyxl
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.consent import ConsentRecord
from src.models.gamification import PointTransaction
from src.models.users import User
from src.models.volunteers import (
    AlumniProfile,
    CorporateProfile,
    StudentProfile,
    VolunteerProfile,
)


async def create_user_with_role(
    async_db: AsyncSession,
    role: str = "VOLUNTEER",
    status: str = "APPROVED",
    email: str | None = None,
) -> User:
    """Helper to seed user with specific role."""
    user_email = email or f"{role.lower()}_{uuid.uuid4().hex[:6]}@example.com"
    user = User(
        email=user_email,
        password_hash=get_password_hash("Password123!"),
        role=role,
        status=status,
        is_active=True,
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user


async def get_token(client: AsyncClient, email: str, password: str = "Password123!") -> str:
    """Helper to obtain access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]  # type: ignore[no-any-return]


@pytest.mark.asyncio
async def test_admin_dashboard_summary_metrics(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify Admin Dashboard aggregates real database metrics accurately."""
    admin = await create_user_with_role(async_db, role="ADMIN")
    admin_token = await get_token(client, admin.email)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Seed Student Volunteer
    vol_user = await create_user_with_role(async_db, role="VOLUNTEER")
    prof = VolunteerProfile(
        user_id=vol_user.id,
        first_name="Priya",
        last_name="Sundar",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=21,
        gender="FEMALE",
        category="STUDENT",
    )
    async_db.add(prof)
    await async_db.flush()

    stu = StudentProfile(
        volunteer_profile_id=prof.id,
        college_name="Madras Christian College",
        degree="B.Sc",
        department="Computer Science",
        batch_year=2025,
        current_year=3,
        maatram_reg_number=f"MAAT-STU-{uuid.uuid4().hex[:6].upper()}",
    )
    async_db.add(stu)

    # Seed Point Transaction
    pt = PointTransaction(
        volunteer_profile_id=prof.id,
        transaction_type="EVENT_COMPLETION",
        event_points=Decimal("10.00"),
        hour_points=Decimal("6.00"),
        total_points=Decimal("16.00"),
        hours_credited=Decimal("3.00"),
        cycle_year=2026,
    )
    async_db.add(pt)
    await async_db.commit()

    # Query dashboard
    res = await client.get("/api/v1/admin/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["volunteers"]["total_volunteers"] >= 1
    assert data["volunteers"]["active_volunteers"] >= 1
    assert data["volunteers"]["by_category"]["STUDENT"] >= 1
    assert float(data["engagement"]["total_hours_credited"]) >= 3.0
    assert float(data["engagement"]["total_points_allocated"]) >= 16.0


@pytest.mark.asyncio
async def test_student_and_alumni_contribution_reports(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify Student and Alumni Contribution Reports query accurate relational data."""
    admin = await create_user_with_role(async_db, role="ADMIN")
    admin_token = await get_token(client, admin.email)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Student Contribution Report
    res_stu = await client.get("/api/v1/admin/reports/student-contributions", headers=headers)
    assert res_stu.status_code == 200
    stu_data = res_stu.json()
    assert "items" in stu_data
    assert "total" in stu_data

    # 2. Alumni Contribution Report
    res_alumni = await client.get("/api/v1/admin/reports/alumni-contributions", headers=headers)
    assert res_alumni.status_code == 200
    alumni_data = res_alumni.json()
    assert "items" in alumni_data


@pytest.mark.asyncio
async def test_inactive_volunteer_report(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify inactive volunteer detection using configurable attendance recency threshold."""
    admin = await create_user_with_role(async_db, role="ADMIN")
    admin_token = await get_token(client, admin.email)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Inactive volunteer: never attended any event
    vol_inactive = await create_user_with_role(async_db, role="VOLUNTEER")
    prof_inactive = VolunteerProfile(
        user_id=vol_inactive.id,
        first_name="Inactive",
        last_name="User",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=28,
        gender="MALE",
        category="ALUMNI",
        created_at=datetime.now(UTC) - timedelta(days=200),
    )
    async_db.add(prof_inactive)
    await async_db.commit()

    res = await client.get(
        "/api/v1/admin/reports/inactive-volunteers?threshold_days=180",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["threshold_days"] == 180
    assert data["total"] >= 1
    assert any(item["name"] == "Inactive User" for item in data["items"])


@pytest.mark.asyncio
async def test_interview_availability_report_privacy_masking(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify contact details are masked strictly when contact_available == False."""
    admin = await create_user_with_role(async_db, role="ADMIN")
    admin_token = await get_token(client, admin.email)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Volunteer A: Consented to contact
    u_open = await create_user_with_role(async_db, role="VOLUNTEER")
    p_open = VolunteerProfile(
        user_id=u_open.id,
        first_name="Open",
        last_name="Panelist",
        mobile_number="+919840112233",
        age=32,
        gender="FEMALE",
        category="CORPORATE",
    )
    async_db.add(p_open)
    await async_db.flush()

    c_open = ConsentRecord(volunteer_profile_id=p_open.id, contact_available=True)
    corp_open = CorporateProfile(
        volunteer_profile_id=p_open.id,
        organisation="Infosys",
        designation="Lead Architect",
        years_of_experience=Decimal("8.5"),
        location="Chennai",
        skills=["Python", "System Design"],
    )
    async_db.add(c_open)
    async_db.add(corp_open)

    # Volunteer B: Contact Opted-Out (Private)
    u_priv = await create_user_with_role(async_db, role="VOLUNTEER")
    p_priv = VolunteerProfile(
        user_id=u_priv.id,
        first_name="Private",
        last_name="Alumni",
        mobile_number="+919840998877",
        age=30,
        gender="MALE",
        category="ALUMNI",
    )
    async_db.add(p_priv)
    await async_db.flush()

    c_priv = ConsentRecord(volunteer_profile_id=p_priv.id, contact_available=False)
    alumni_priv = AlumniProfile(
        volunteer_profile_id=p_priv.id,
        organisation="TCS",
        job_role="Senior Consultant",
        years_of_experience=Decimal("6.0"),
        location="Bengaluru",
        skills=["Management", "Cloud"],
        college_name="PSG Tech",
        degree="B.E",
        department="ECE",
        batch_year=2018,
        graduation_year=2018,
    )
    async_db.add(c_priv)
    async_db.add(alumni_priv)
    await async_db.commit()

    res = await client.get("/api/v1/admin/reports/interview-availability", headers=headers)
    assert res.status_code == 200
    data = res.json()

    open_item = next((i for i in data["items"] if i["name"] == "Open Panelist"), None)
    priv_item = next((i for i in data["items"] if i["name"] == "Private Alumni"), None)

    assert open_item is not None
    assert priv_item is not None

    # Open panelist: real contact info is visible
    assert open_item["is_contact_masked"] is False
    assert open_item["phone_number"] == "+919840112233"
    assert open_item["email"] == u_open.email

    # Private panelist: contact info is STRICTLY masked
    assert priv_item["is_contact_masked"] is True
    assert priv_item["phone_number"] == "[MASKED]"
    assert priv_item["email"] == "[MASKED]"


@pytest.mark.asyncio
async def test_excel_export_and_formula_injection_sanitization(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify Excel report export streaming and Formula Injection sanitization."""
    admin = await create_user_with_role(async_db, role="ADMIN")
    admin_token = await get_token(client, admin.email)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Seed malicious student name attempting Excel formula injection
    malicious_user = await create_user_with_role(async_db, role="VOLUNTEER")
    malicious_prof = VolunteerProfile(
        user_id=malicious_user.id,
        first_name="=CMD|' /C calc'!A0",
        last_name="+SUM(1+1)",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=20,
        gender="MALE",
        category="STUDENT",
    )
    async_db.add(malicious_prof)
    await async_db.flush()

    malicious_stu = StudentProfile(
        volunteer_profile_id=malicious_prof.id,
        college_name="@InjectUniversity",
        degree="B.Tech",
        department="IT",
        batch_year=2026,
        current_year=3,
        maatram_reg_number=f"MAAT-MAL-{uuid.uuid4().hex[:6].upper()}",
    )
    async_db.add(malicious_stu)
    await async_db.commit()

    # Request Excel export
    res = await client.get(
        "/api/v1/admin/reports/student-contributions/export",
        headers=headers,
    )
    assert res.status_code == 200
    assert (
        res.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Inspect exported Excel binary in-memory
    excel_bytes = res.content
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    ws = wb.active
    assert ws is not None

    found_sanitized = False
    for row in ws.iter_rows(values_only=True):
        for cell in row:
            if cell and isinstance(cell, str):
                # If formula payload was present, it must be escaped with leading single quote
                if "=CMD" in cell or "+SUM" in cell or "@InjectUniversity" in cell:
                    assert cell.startswith("'"), (
                        f"Formula injection vulnerability! Value was: {cell}"
                    )
                    found_sanitized = True

    assert found_sanitized is True


@pytest.mark.asyncio
async def test_audit_logs_super_admin_restriction(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify system audit trail endpoint is restricted strictly to SUPER_ADMIN."""
    admin = await create_user_with_role(async_db, role="ADMIN")
    super_admin = await create_user_with_role(async_db, role="SUPER_ADMIN")

    admin_token = await get_token(client, admin.email)
    super_token = await get_token(client, super_admin.email)

    # Standard Admin rejected with 403 Forbidden
    res_admin = await client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 403

    # Super Admin allowed with 200 OK
    res_super = await client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {super_token}"},
    )
    assert res_super.status_code == 200
    assert "items" in res_super.json()
