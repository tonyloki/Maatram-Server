"""Persistence abstractions for Cloudinary media assets and event photos."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.media import EventPhoto, MediaAsset


class MediaRepository:
    """Database persistence for registered media assets and event galleries."""

    async def create_asset(
        self,
        db: AsyncSession,
        public_id: str,
        secure_url: str,
        asset_type: str,
        format: str,
        byte_size: int,
        uploader_user_id: uuid.UUID,
        width: int | None = None,
        height: int | None = None,
    ) -> MediaAsset:
        """Create and persist a media asset metadata record."""
        asset = MediaAsset(
            public_id=public_id,
            secure_url=secure_url,
            asset_type=asset_type,
            format=format,
            byte_size=byte_size,
            width=width,
            height=height,
            uploaded_by_user_id=uploader_user_id,
            created_at=datetime.now(UTC),
        )
        db.add(asset)
        await db.flush()
        await db.refresh(asset)
        return asset

    async def get_asset_by_id(self, db: AsyncSession, asset_id: uuid.UUID) -> MediaAsset | None:
        """Fetch media asset by ID."""
        stmt = (
            select(MediaAsset)
            .where(MediaAsset.id == asset_id)
            .options(selectinload(MediaAsset.uploaded_by))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_asset_by_public_id(self, db: AsyncSession, public_id: str) -> MediaAsset | None:
        """Fetch media asset by Cloudinary public_id."""
        stmt = select(MediaAsset).where(MediaAsset.public_id == public_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_asset(self, db: AsyncSession, asset: MediaAsset) -> None:
        """Remove media asset from database."""
        await db.delete(asset)
        await db.flush()

    async def add_event_photo(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
        media_asset_id: uuid.UUID,
        caption: str | None = None,
        is_featured: bool = False,
    ) -> EventPhoto:
        """Bind a media asset into an event gallery."""
        photo = EventPhoto(
            event_id=event_id,
            media_asset_id=media_asset_id,
            caption=caption,
            is_featured=is_featured,
            created_at=datetime.now(UTC),
        )
        db.add(photo)
        await db.flush()
        await db.refresh(photo)
        return photo

    async def get_event_photos(self, db: AsyncSession, event_id: uuid.UUID) -> list[EventPhoto]:
        """Fetch all gallery photos for an event ordered by creation."""
        stmt = (
            select(EventPhoto)
            .where(EventPhoto.event_id == event_id)
            .options(selectinload(EventPhoto.media_asset))
            .order_by(EventPhoto.is_featured.desc(), EventPhoto.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_event_photo_pair(
        self, db: AsyncSession, event_id: uuid.UUID, media_asset_id: uuid.UUID
    ) -> EventPhoto | None:
        """Fetch event photo by event and media asset pair."""
        stmt = select(EventPhoto).where(
            EventPhoto.event_id == event_id,
            EventPhoto.media_asset_id == media_asset_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


media_repository = MediaRepository()
