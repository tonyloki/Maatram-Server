"""Media management, Cloudinary signed direct uploads, and event photo gallery routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_role
from src.models.users import User
from src.schemas.media import (
    EventGalleryResponse,
    EventPhotoCreate,
    EventPhotoResponse,
    LinkedInDraftResponse,
    MediaAssetCreate,
    MediaAssetResponse,
    SignedUploadResponse,
    SignUploadRequest,
)
from src.services.media_service import media_service

router = APIRouter(tags=["Media & Communications"])


@router.post(
    "/media/signed-upload",
    response_model=SignedUploadResponse,
    summary="Generate HMAC-SHA256 signed parameters for direct Cloudinary upload",
)
@router.post(
    "/media/sign-upload",
    response_model=SignedUploadResponse,
    include_in_schema=False,
)
async def generate_signed_upload(
    payload: SignUploadRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> SignedUploadResponse:
    """Generate authorized upload parameters for client-to-Cloudinary upload."""
    return media_service.generate_signed_upload(
        user=current_user,
        asset_type=payload.asset_type,
        file_format=payload.file_format,
        custom_folder=payload.folder,
    )


@router.post(
    "/media/assets",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register uploaded media asset into canonical database",
)
@router.post(
    "/media/register",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def register_media_asset(
    payload: MediaAssetCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MediaAssetResponse:
    """Register completed Cloudinary asset with caller ownership."""
    return await media_service.register_media_asset(
        db=db,
        user=current_user,
        payload=payload,
    )


@router.delete(
    "/media/assets/{asset_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete media asset",
)
async def delete_media_asset(
    asset_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete media asset with object-level authorization."""
    await media_service.delete_media_asset(
        db=db,
        user=current_user,
        asset_id=asset_id,
    )
    return {"message": "Media asset deleted successfully."}


@router.get(
    "/events/{event_id}/photos",
    response_model=EventGalleryResponse,
    summary="Get event photo gallery",
)
async def get_event_photos(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventGalleryResponse:
    """Retrieve gallery photos associated with an event."""
    return await media_service.get_event_gallery(db=db, event_id=event_id)


@router.post(
    "/events/{event_id}/photos",
    response_model=EventPhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bind media asset to event gallery (Admin only)",
)
async def add_event_photo(
    event_id: uuid.UUID,
    payload: EventPhotoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventPhotoResponse:
    """Bind photo to event gallery with Media Consent Governance enforcement."""
    return await media_service.add_event_photo(
        db=db,
        user=current_user,
        event_id=event_id,
        payload=payload,
    )


@router.get(
    "/events/{event_id}/communications/linkedin-draft",
    response_model=LinkedInDraftResponse,
    summary="Retrieve pre-drafted LinkedIn celebration post honoring volunteer name consent",
)
async def get_linkedin_draft(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LinkedInDraftResponse:
    """Generate pre-drafted LinkedIn celebration post honoring affirmative volunteer consent."""
    return await media_service.generate_linkedin_draft(db=db, event_id=event_id)
