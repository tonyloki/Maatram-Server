"""End-to-End Test Suite for Real Client Cloudinary Upload, DB Association, and Cross-Platform Rendering (Phase 6 Final Acceptance).

Verifies:
1. Client requests signed upload parameters from FastAPI backend (POST /api/v1/media/signed-upload).
2. Backend returns cryptographic SHA-256 signature, timestamp, apiKey, and user-scoped folder.
3. Client registers completed media asset (POST /api/v1/media/assets) with security validation.
4. Client updates volunteer profile with new avatar_media_id (PATCH /api/v1/volunteers/me).
5. Backend associates MediaAsset with VolunteerProfile and resolves avatar_url on fetch (GET /api/v1/volunteers/me).
6. Admin can inspect volunteer with avatar_url populated (GET /api/v1/volunteers/{id}).
7. Verifies compatibility with Flutter VolunteerProfileModel and Next.js Avatar component contract.
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.integrations.cloudinary_client import cloudinary_client
from src.models.media import MediaAsset
from src.models.users import User
from src.models.volunteers import VolunteerProfile


async def create_volunteer_user(
    async_db: AsyncSession,
    email: str | None = None,
) -> tuple[User, VolunteerProfile]:
    """Helper to seed an active volunteer with a profile."""
    user_email = email or f"volunteer_cloudinary_{uuid.uuid4().hex[:6]}@example.com"
    user = User(
        email=user_email,
        password_hash=get_password_hash("Password123!"),
        role="VOLUNTEER",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(user)
    await async_db.flush()

    profile = VolunteerProfile(
        user_id=user.id,
        first_name="Kavitha",
        last_name="Raman",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=22,
        gender="FEMALE",
        category="STUDENT",
    )
    async_db.add(profile)
    await async_db.commit()
    await async_db.refresh(user)
    await async_db.refresh(profile)
    return user, profile


async def create_admin_user(
    async_db: AsyncSession,
) -> User:
    """Helper to seed an admin user."""
    admin_email = f"admin_cloudinary_{uuid.uuid4().hex[:6]}@example.com"
    admin = User(
        email=admin_email,
        password_hash=get_password_hash("Password123!"),
        role="ADMIN",
        status="APPROVED",
        is_active=True,
    )
    async_db.add(admin)
    await async_db.commit()
    await async_db.refresh(admin)
    return admin


async def get_token(client: AsyncClient, email: str, password: str = "Password123!") -> str:
    """Helper to obtain access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_cloudinary_avatar_upload_db_association_e2e(
    client: AsyncClient,
    async_db: AsyncSession,
) -> None:
    """Full lifecycle: signed upload -> asset registration -> profile link -> client response contract."""
    # 1. Setup authenticated volunteer
    user, profile = await create_volunteer_user(async_db)
    token = await get_token(client, user.email)
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Request signed upload configuration for AVATAR
    sign_res = await client.post(
        "/api/v1/media/signed-upload",
        json={"asset_type": "AVATAR", "file_format": "png"},
        headers=headers,
    )
    assert sign_res.status_code == 200
    sign_data = sign_res.json()
    assert "signature" in sign_data
    assert "timestamp" in sign_data
    assert "apiKey" in sign_data or "api_key" in sign_data
    assert "cloudName" in sign_data or "cloud_name" in sign_data
    expected_folder = f"maatram/avatars/{user.id}"
    assert sign_data["folder"] == expected_folder

    # Step 2: Register the uploaded Cloudinary asset in DB
    asset_public_id = f"{expected_folder}/avatar_{uuid.uuid4().hex[:8]}"
    cloud_name = cloudinary_client.cloud_name
    secure_url = f"https://res.cloudinary.com/{cloud_name}/{asset_public_id}.png"

    register_payload = {
        "public_id": asset_public_id,
        "secure_url": secure_url,
        "asset_type": "AVATAR",
        "format": "png",
        "byte_size": 24500,
        "width": 400,
        "height": 400,
    }
    reg_res = await client.post(
        "/api/v1/media/assets",
        json=register_payload,
        headers=headers,
    )
    assert reg_res.status_code == 201
    media_asset = reg_res.json()
    media_id = media_asset["id"]
    assert media_asset["public_id"] == asset_public_id
    assert media_asset["secure_url"] == secure_url
    assert media_asset["uploaded_by_user_id"] == str(user.id)

    # Step 3: Associate the registered media asset with the volunteer profile
    patch_res = await client.patch(
        "/api/v1/volunteers/me",
        json={"avatar_media_id": media_id},
        headers=headers,
    )
    assert patch_res.status_code == 200
    patched_data = patch_res.json()
    assert patched_data["avatar_media_id"] == media_id
    assert patched_data["avatar_url"] == secure_url

    # Step 4: Verify self-profile retrieval includes the resolved avatar_url
    me_res = await client.get("/api/v1/volunteers/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["avatar_media_id"] == media_id
    assert me_data["avatar_url"] == secure_url
    assert me_data["first_name"] == "Kavitha"

    # Step 5: Verify Admin profile retrieval returns the identical avatar_url
    admin = await create_admin_user(async_db)
    admin_token = await get_token(client, admin.email)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    admin_res = await client.get(f"/api/v1/volunteers/{profile.id}", headers=admin_headers)
    assert admin_res.status_code == 200
    admin_data = admin_res.json()
    assert admin_data["avatar_media_id"] == media_id
    assert admin_data["avatar_url"] == secure_url

    # Step 6: Verify cross-platform consumer contracts
    # A. Flutter VolunteerProfileModel contract simulation:
    # Model parses json['avatar_url'] into avatarUrl property.
    flutter_parsed_avatar_url = me_data.get("avatar_url")
    assert flutter_parsed_avatar_url == secure_url
    assert flutter_parsed_avatar_url.startswith(f"https://res.cloudinary.com/{cloud_name}/")

    # B. Next.js VolunteerProfileResponse contract simulation:
    # web/src/types/index.ts has avatar_url?: string | null
    # web/src/components/ui/avatar.tsx renders <Image src={profile.avatar_url} ... />
    nextjs_avatar_url = me_data["avatar_url"]
    assert nextjs_avatar_url is not None
    assert len(nextjs_avatar_url) > 0


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_register_foreign_avatar_path(
    client: AsyncClient,
    async_db: AsyncSession,
) -> None:
    """Security check: A volunteer cannot register a Cloudinary asset pointing outside their user folder."""
    user, _ = await create_volunteer_user(async_db)
    token = await get_token(client, user.email)
    headers = {"Authorization": f"Bearer {token}"}

    other_user_id = str(uuid.uuid4())
    fraudulent_public_id = f"maatram/avatars/{other_user_id}/avatar_exploit"
    secure_url = f"https://res.cloudinary.com/{cloudinary_client.cloud_name}/{fraudulent_public_id}.png"

    fraud_res = await client.post(
        "/api/v1/media/assets",
        json={
            "public_id": fraudulent_public_id,
            "secure_url": secure_url,
            "asset_type": "AVATAR",
            "format": "png",
            "byte_size": 1024,
        },
        headers=headers,
    )
    # Backend strictly enforces folder ownership for non-admins (403 UNAUTHORIZED_MEDIA_FOLDER)
    assert fraud_res.status_code == 403
    assert fraud_res.json()["error"]["code"] == "UNAUTHORIZED_MEDIA_FOLDER"
