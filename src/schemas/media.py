"""Pydantic schemas for Cloudinary media uploads, assets, event photos, and communications."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SignUploadRequest(BaseModel):
    """Payload to request signed direct upload parameters."""

    asset_type: Literal[
        "AVATAR", "EVENT_COVER", "EVENT_GALLERY", "DOCUMENT", "PARENTAL_CONSENT"
    ] = Field(..., description="Classification category of the media upload")
    file_format: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="MIME file extension (e.g. jpg, png, webp, pdf)",
    )
    folder: str | None = Field(default=None, description="Optional custom destination directory")


class SignedUploadResponse(BaseModel):
    """Signed upload parameters for direct client-to-Cloudinary upload."""

    model_config = ConfigDict(populate_by_name=True)

    upload_url: str = Field(..., serialization_alias="uploadUrl")
    api_key: str = Field(..., serialization_alias="apiKey")
    cloud_name: str = Field(..., serialization_alias="cloudName")
    timestamp: int
    signature: str
    folder: str

    @property
    def uploadUrl(self) -> str:  # noqa: N802
        """CamelCase alias for mobile & web clients."""
        return self.upload_url

    @property
    def apiKey(self) -> str:  # noqa: N802
        """CamelCase alias for mobile & web clients."""
        return self.api_key

    @property
    def cloudName(self) -> str:  # noqa: N802
        """CamelCase alias for mobile & web clients."""
        return self.cloud_name


class MediaAssetCreate(BaseModel):
    """Payload to register a completed Cloudinary upload into PostgreSQL."""

    model_config = ConfigDict(populate_by_name=True)

    public_id: str = Field(..., min_length=3, max_length=255)
    secure_url: str = Field(..., min_length=10, max_length=512)
    asset_type: Literal["AVATAR", "EVENT_COVER", "EVENT_GALLERY", "DOCUMENT", "PARENTAL_CONSENT"]
    format: str = Field(..., min_length=2, max_length=20)
    byte_size: int = Field(default=0, alias="bytes")
    width: int | None = None
    height: int | None = None


class MediaAssetResponse(BaseModel):
    """Media asset persistence representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    public_id: str
    secure_url: str
    asset_type: str
    format: str
    byte_size: int
    width: int | None = None
    height: int | None = None
    uploaded_by_user_id: uuid.UUID
    created_at: datetime


class EventPhotoCreate(BaseModel):
    """Payload to bind a registered media asset to an event gallery."""

    media_asset_id: uuid.UUID
    caption: str | None = Field(default=None, max_length=255)
    is_featured: bool = False
    tagged_volunteer_ids: list[uuid.UUID] = Field(
        default_factory=list,
        description="Volunteer profiles to tag; requires affirmative media_usage consent",
    )


class EventPhotoResponse(BaseModel):
    """Event gallery photo DTO."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_id: uuid.UUID
    media_asset_id: uuid.UUID
    caption: str | None = None
    is_featured: bool
    created_at: datetime
    media_asset: MediaAssetResponse | None = None


class EventGalleryResponse(BaseModel):
    """Event gallery list envelope."""

    event_id: uuid.UUID
    photos: list[EventPhotoResponse]
    total: int


class LinkedInDraftResponse(BaseModel):
    """Generated LinkedIn celebration post draft honoring volunteer consent."""

    event_id: uuid.UUID
    draft_text: str
    featured_volunteers: list[str]
    anonymous_count: int
    hashtags: list[str]
