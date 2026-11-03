"""Comprehensive test suite for Media Assets, Cloudinary Signed Uploads, and Communications (Phase 11)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.models.attendance import AttendanceRecord
from src.models.consent import ConsentRecord
from src.models.events import Event, EventRegistration
from src.models.media import MediaAsset
from src.models.users import User
from src.models.volunteers import VolunteerProfile


async def create_test_user(
    async_db: AsyncSession,
    role: str = "VOLUNTEER",
    status: str = "APPROVED",
    email: str | None = None,
) -> tuple[User, VolunteerProfile | None]:
    """Helper to seed user and optional volunteer profile."""
    user_email = email or f"{role.lower()}_{uuid.uuid4().hex[:6]}@example.com"
    user = User(
        email=user_email,
        password_hash=get_password_hash("Password123!"),
        role=role,
        status=status,
        is_active=True,
    )
    async_db.add(user)
    await async_db.flush()

    profile: VolunteerProfile | None = None
    if role == "VOLUNTEER":
        profile = VolunteerProfile(
            user_id=user.id,
            first_name="Test",
            last_name="Volunteer",
            mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
            age=24,
            gender="MALE",
            category="STUDENT",
        )
        async_db.add(profile)

    await async_db.commit()
    await async_db.refresh(user)
    if profile:
        await async_db.refresh(profile)
    return user, profile


async def get_token(client: AsyncClient, email: str, password: str = "Password123!") -> str:
    """Helper to obtain access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]  # type: ignore[no-any-return]


@pytest.mark.asyncio
async def test_signed_upload_parameter_generation(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify Cloudinary direct upload signature generation."""
    user, _ = await create_test_user(async_db, role="VOLUNTEER")
    token_str = await get_token(client, user.email)
    headers = {"Authorization": f"Bearer {token_str}"}

    res = await client.post(
        "/api/v1/media/signed-upload",
        json={"asset_type": "AVATAR", "file_format": "jpg"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert "signature" in data
    assert "uploadUrl" in data or "upload_url" in data
    assert "apiKey" in data or "api_key" in data
    assert "timestamp" in data
    assert "folder" in data
    assert str(user.id) in data["folder"]


@pytest.mark.asyncio
async def test_media_validation_format_and_size(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify file format validation and max size constraint checks."""
    user, _ = await create_test_user(async_db, role="VOLUNTEER")
    token_str = await get_token(client, user.email)
    headers = {"Authorization": f"Bearer {token_str}"}

    # 1. Invalid file format
    res_bad_fmt = await client.post(
        "/api/v1/media/signed-upload",
        json={"asset_type": "AVATAR", "file_format": "exe"},
        headers=headers,
    )
    assert res_bad_fmt.status_code == 400

    # 2. File size exceeds 10MB ceiling
    too_large_bytes = 11 * 1024 * 1024
    res_bad_size = await client.post(
        "/api/v1/media/assets",
        json={
            "public_id": f"test_pub_{uuid.uuid4().hex[:8]}",
            "secure_url": "https://res.cloudinary.com/test/image/upload/sample.jpg",
            "asset_type": "AVATAR",
            "format": "jpg",
            "bytes": too_large_bytes,
        },
        headers=headers,
    )
    assert res_bad_size.status_code == 400


@pytest.mark.asyncio
async def test_media_asset_registration_and_bola(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify media asset registration, path validation, URL integrity, and BOLA deletion protection."""
    user_a, _ = await create_test_user(async_db, role="VOLUNTEER")
    user_b, _ = await create_test_user(async_db, role="VOLUNTEER")

    token_a = await get_token(client, user_a.email)
    token_b = await get_token(client, user_b.email)

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Security Check: Non-admin trying to register into another user's folder -> 403 Forbidden
    forged_prefix_id = f"maatram/avatars/{user_b.id}/forged_{uuid.uuid4().hex[:8]}"
    bad_folder_res = await client.post(
        "/api/v1/media/assets",
        json={
            "public_id": forged_prefix_id,
            "secure_url": f"https://res.cloudinary.com/maatram/image/upload/{forged_prefix_id}.jpg",
            "asset_type": "AVATAR",
            "format": "jpg",
            "bytes": 250000,
        },
        headers=headers_a,
    )
    assert bad_folder_res.status_code == 403

    # 2. Security Check: Non-Cloudinary domain rejected -> 400 Bad Request
    valid_pub_id = f"maatram/avatars/{user_a.id}/avatar_{uuid.uuid4().hex[:8]}"
    bad_domain_res = await client.post(
        "/api/v1/media/assets",
        json={
            "public_id": valid_pub_id,
            "secure_url": f"https://malicious-site.com/{valid_pub_id}.jpg",
            "asset_type": "AVATAR",
            "format": "jpg",
            "bytes": 250000,
        },
        headers=headers_a,
    )
    assert bad_domain_res.status_code == 400

    # 3. Security Check: URL public_id mismatch rejected -> 400 Bad Request
    mismatch_res = await client.post(
        "/api/v1/media/assets",
        json={
            "public_id": valid_pub_id,
            "secure_url": "https://res.cloudinary.com/maatram/image/upload/other_file.jpg",
            "asset_type": "AVATAR",
            "format": "jpg",
            "bytes": 250000,
        },
        headers=headers_a,
    )
    assert mismatch_res.status_code == 400

    # 4. User A registers legitimate media asset
    create_res = await client.post(
        "/api/v1/media/assets",
        json={
            "public_id": valid_pub_id,
            "secure_url": f"https://res.cloudinary.com/maatram/image/upload/{valid_pub_id}.jpg",
            "asset_type": "AVATAR",
            "format": "jpg",
            "bytes": 250000,
        },
        headers=headers_a,
    )
    assert create_res.status_code == 201
    asset_id = create_res.json()["id"]

    # 5. Idempotent re-registration by same user returns 200/201 existing asset
    re_register_res = await client.post(
        "/api/v1/media/assets",
        json={
            "public_id": valid_pub_id,
            "secure_url": f"https://res.cloudinary.com/maatram/image/upload/{valid_pub_id}.jpg",
            "asset_type": "AVATAR",
            "format": "jpg",
            "bytes": 250000,
        },
        headers=headers_a,
    )
    assert re_register_res.status_code in (200, 201)
    assert re_register_res.json()["id"] == asset_id

    # 6. User B attempts to delete User A's asset -> 403 Forbidden
    del_forbidden = await client.delete(
        f"/api/v1/media/assets/{asset_id}",
        headers=headers_b,
    )
    assert del_forbidden.status_code == 403

    # 7. User A deletes own asset -> 200 OK
    del_ok = await client.delete(
        f"/api/v1/media/assets/{asset_id}",
        headers=headers_a,
    )
    assert del_ok.status_code == 200


@pytest.mark.asyncio
async def test_event_photo_gallery_and_media_consent(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify media usage consent enforcement when binding photos to event galleries."""
    admin, _ = await create_test_user(async_db, role="ADMIN")
    vol_consented, prof_consented = await create_test_user(async_db, role="VOLUNTEER")
    vol_opted_out, prof_opted_out = await create_test_user(async_db, role="VOLUNTEER")

    assert prof_consented is not None and prof_opted_out is not None

    # Set media consent records
    c_yes = ConsentRecord(
        volunteer_profile_id=prof_consented.id,
        media_usage=True,
    )
    c_no = ConsentRecord(
        volunteer_profile_id=prof_opted_out.id,
        media_usage=False,
    )
    async_db.add(c_yes)
    async_db.add(c_no)

    # Seed event
    now = datetime.now(UTC)
    event = Event(
        title="Youth Leadership Summit",
        description="Inspiring youth.",
        category="SCHOOL_VISIT",
        mode="OFFLINE",
        location="Hall A",
        start_time=now + timedelta(days=2),
        end_time=now + timedelta(days=2, hours=3),
        capacity_required=10,
        registration_deadline=now + timedelta(days=1),
        status="PUBLISHED",
        created_by_user_id=admin.id,
    )
    async_db.add(event)

    # Seed media asset
    asset = MediaAsset(
        public_id=f"events/gallery_{uuid.uuid4().hex[:8]}",
        secure_url="https://res.cloudinary.com/test/image/upload/summit.jpg",
        asset_type="EVENT_GALLERY",
        format="jpg",
        byte_size=500000,
        uploaded_by_user_id=admin.id,
        created_at=now,
    )
    async_db.add(asset)
    await async_db.commit()

    admin_token = await get_token(client, admin.email)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Admin attempts to tag opted-out volunteer -> rejected with MEDIA_CONSENT_REQUIRED
    res_rejected = await client.post(
        f"/api/v1/events/{event.id}/photos",
        json={
            "media_asset_id": str(asset.id),
            "caption": "Volunteers at Summit",
            "is_featured": True,
            "tagged_volunteer_ids": [str(prof_opted_out.id)],
        },
        headers=headers,
    )
    assert res_rejected.status_code == 400
    assert "media usage" in res_rejected.text.lower()

    # 2. Admin tags consented volunteer -> succeeds!
    res_ok = await client.post(
        f"/api/v1/events/{event.id}/photos",
        json={
            "media_asset_id": str(asset.id),
            "caption": "Volunteers at Summit",
            "is_featured": True,
            "tagged_volunteer_ids": [str(prof_consented.id)],
        },
        headers=headers,
    )
    assert res_ok.status_code == 201

    # 3. Retrieve event gallery
    gal_res = await client.get(f"/api/v1/events/{event.id}/photos", headers=headers)
    assert gal_res.status_code == 200
    assert gal_res.json()["total"] == 1
    assert gal_res.json()["photos"][0]["caption"] == "Volunteers at Summit"


@pytest.mark.asyncio
async def test_linkedin_celebration_draft_consent(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Verify LinkedIn draft post generation honors volunteer linkedin_content and name_visible consent."""
    admin, _ = await create_test_user(async_db, role="ADMIN")

    # Volunteer 1: Visible Name & Consented to LinkedIn
    user_vis, prof_vis = await create_test_user(async_db, role="VOLUNTEER")
    assert prof_vis is not None
    prof_vis.first_name = "Kavitha"
    prof_vis.last_name = "Raman"
    c_vis = ConsentRecord(
        volunteer_profile_id=prof_vis.id,
        name_visible=True,
        linkedin_content=True,
    )
    async_db.add(c_vis)

    # Volunteer 2: Hidden Name (Anonymous) & Consented to LinkedIn
    user_anon, prof_anon = await create_test_user(async_db, role="VOLUNTEER")
    assert prof_anon is not None
    prof_anon.first_name = "Secret"
    prof_anon.last_name = "Contributor"
    c_anon = ConsentRecord(
        volunteer_profile_id=prof_anon.id,
        name_visible=False,
        linkedin_content=True,
    )
    async_db.add(c_anon)

    # Volunteer 3: Opted Out of LinkedIn Content Entirely (even if name_visible=True)
    user_no_li, prof_no_li = await create_test_user(async_db, role="VOLUNTEER")
    assert prof_no_li is not None
    prof_no_li.first_name = "Private"
    prof_no_li.last_name = "Person"
    c_no_li = ConsentRecord(
        volunteer_profile_id=prof_no_li.id,
        name_visible=True,
        linkedin_content=False,
    )
    async_db.add(c_no_li)

    # Seed completed event with attendances
    now = datetime.now(UTC)
    event = Event(
        title="College Mentorship Drive",
        description="Mentoring students.",
        category="MOCK_INTERVIEW",
        mode="OFFLINE",
        location="Campus",
        start_time=now - timedelta(hours=4),
        end_time=now - timedelta(hours=1),
        capacity_required=5,
        registration_deadline=now - timedelta(days=1),
        status="COMPLETED",
        created_by_user_id=admin.id,
    )
    async_db.add(event)
    await async_db.flush()

    reg1 = EventRegistration(
        event_id=event.id,
        volunteer_profile_id=prof_vis.id,
        status="SELECTED",
    )
    reg2 = EventRegistration(
        event_id=event.id,
        volunteer_profile_id=prof_anon.id,
        status="SELECTED",
    )
    reg3 = EventRegistration(
        event_id=event.id,
        volunteer_profile_id=prof_no_li.id,
        status="SELECTED",
    )
    async_db.add(reg1)
    async_db.add(reg2)
    async_db.add(reg3)
    await async_db.flush()

    att1 = AttendanceRecord(
        event_registration_id=reg1.id,
        check_in_time=now - timedelta(hours=4),
        check_out_time=now - timedelta(hours=1),
        duration_minutes=180,
        status="COMPLETED",
    )
    att2 = AttendanceRecord(
        event_registration_id=reg2.id,
        check_in_time=now - timedelta(hours=4),
        check_out_time=now - timedelta(hours=1),
        duration_minutes=180,
        status="COMPLETED",
    )
    att3 = AttendanceRecord(
        event_registration_id=reg3.id,
        check_in_time=now - timedelta(hours=4),
        check_out_time=now - timedelta(hours=1),
        duration_minutes=180,
        status="COMPLETED",
    )
    async_db.add(att1)
    async_db.add(att2)
    async_db.add(att3)
    await async_db.commit()

    admin_token = await get_token(client, admin.email)
    headers = {"Authorization": f"Bearer {admin_token}"}

    res = await client.get(
        f"/api/v1/events/{event.id}/communications/linkedin-draft",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    # 1. Kavitha Raman opted in to LinkedIn AND name visibility -> included
    assert "Kavitha Raman" in data["draft_text"]
    assert "Kavitha Raman" in data["featured_volunteers"]

    # 2. Secret Contributor opted in to LinkedIn, but opted out of name visibility -> counted in anonymous
    assert "Secret Contributor" not in data["draft_text"]
    assert "Secret Contributor" not in data["featured_volunteers"]
    assert data["anonymous_count"] == 1

    # 3. Private Person opted OUT of LinkedIn content -> completely excluded
    assert "Private Person" not in data["draft_text"]
    assert "Private Person" not in data["featured_volunteers"]
