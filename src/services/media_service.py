"""Core domain service for Cloudinary signed media uploads, asset registration, and event galleries."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import (
    ConflictException,
    DomainException,
    ForbiddenException,
    NotFoundException,
)
from src.core.logging import get_logger
from src.integrations.cloudinary_client import cloudinary_client
from src.models.attendance import AttendanceRecord
from src.models.consent import ConsentRecord
from src.models.events import Event, EventRegistration
from src.models.users import User
from src.models.volunteers import VolunteerProfile
from src.repositories.media_repo import MediaRepository, media_repository
from src.schemas.media import (
    EventGalleryResponse,
    EventPhotoCreate,
    EventPhotoResponse,
    LinkedInDraftResponse,
    MediaAssetCreate,
    MediaAssetResponse,
    SignedUploadResponse,
)

logger = get_logger(__name__)


class MediaService:
    """Service managing Cloudinary signatures, media metadata, event galleries, and LinkedIn content drafts."""

    def __init__(self, repo: MediaRepository | None = None) -> None:
        self.repo = repo or media_repository

    def generate_signed_upload(
        self,
        user: User,
        asset_type: str,
        file_format: str,
        custom_folder: str | None = None,
    ) -> SignedUploadResponse:
        """Generate authorized signed parameters for direct client upload to Cloudinary."""
        params = cloudinary_client.generate_signed_upload_params(
            asset_type=asset_type,
            file_format=file_format,
            user_id=str(user.id),
            custom_folder=custom_folder,
        )
        return SignedUploadResponse(
            upload_url=params["upload_url"],
            api_key=params["api_key"],
            cloud_name=params["cloud_name"],
            timestamp=params["timestamp"],
            signature=params["signature"],
            folder=params["folder"],
        )

    async def register_media_asset(
        self,
        db: AsyncSession,
        user: User,
        payload: MediaAssetCreate,
    ) -> MediaAssetResponse:
        """Register completed Cloudinary asset with ownership and validation."""
        # Verify Cloudinary upload metadata, folder boundary, and URL authenticity
        is_admin = user.role in ("ADMIN", "SUPER_ADMIN")
        cloudinary_client.verify_uploaded_asset(
            public_id=payload.public_id,
            secure_url=payload.secure_url,
            asset_type=payload.asset_type,
            file_format=payload.format,
            byte_size=payload.byte_size,
            user_id=str(user.id),
            is_admin=is_admin,
        )

        # Check uniqueness of public_id
        existing = await self.repo.get_asset_by_public_id(db, payload.public_id)
        if existing:
            if existing.uploaded_by_user_id == user.id:
                return MediaAssetResponse.model_validate(existing)
            raise ConflictException(
                f"Asset with public_id '{payload.public_id}' already registered."
            )

        asset = await self.repo.create_asset(
            db=db,
            public_id=payload.public_id,
            secure_url=payload.secure_url,
            asset_type=payload.asset_type,
            format=payload.format,
            byte_size=payload.byte_size,
            uploader_user_id=user.id,
            width=payload.width,
            height=payload.height,
        )
        await db.commit()
        return MediaAssetResponse.model_validate(asset)

    async def delete_media_asset(
        self,
        db: AsyncSession,
        user: User,
        asset_id: uuid.UUID,
    ) -> bool:
        """Delete media asset with object-level authorization."""
        asset = await self.repo.get_asset_by_id(db, asset_id)
        if not asset:
            raise NotFoundException("Media asset not found.")

        # BOLA Authorization: owner or admin only
        if user.role not in ("ADMIN", "SUPER_ADMIN") and asset.uploaded_by_user_id != user.id:
            raise ForbiddenException("You cannot delete media assets uploaded by another user.")

        public_id = asset.public_id
        await self.repo.delete_asset(db, asset)
        await db.commit()

        # Remote destruction
        await cloudinary_client.destroy_asset(public_id)
        return True

    async def add_event_photo(
        self,
        db: AsyncSession,
        user: User,
        event_id: uuid.UUID,
        payload: EventPhotoCreate,
    ) -> EventPhotoResponse:
        """Add photo to event gallery with Media Consent Governance enforcement."""
        if user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Only administrators can manage event gallery photos.")

        # Verify event exists
        event_stmt = select(Event).where(Event.id == event_id)
        ev_res = await db.execute(event_stmt)
        event = ev_res.scalar_one_or_none()
        if not event:
            raise NotFoundException("Event not found.")

        # Verify media asset exists
        asset = await self.repo.get_asset_by_id(db, payload.media_asset_id)
        if not asset:
            raise NotFoundException("Media asset not found.")

        # Check existing binding
        pair = await self.repo.get_event_photo_pair(db, event_id, payload.media_asset_id)
        if pair:
            return EventPhotoResponse.model_validate(pair)

        # Media Consent Governance for tagged volunteers
        if payload.tagged_volunteer_ids:
            consent_stmt = select(ConsentRecord).where(
                ConsentRecord.volunteer_profile_id.in_(payload.tagged_volunteer_ids)
            )
            consents = list((await db.execute(consent_stmt)).scalars().all())
            consent_map = {c.volunteer_profile_id: c.media_usage for c in consents}

            for vid in payload.tagged_volunteer_ids:
                media_allowed = consent_map.get(vid, False)
                if not media_allowed:
                    raise DomainException(
                        f"Volunteer '{vid}' has opted out of media usage. Cannot tag in event photo.",
                        status_code=400,
                        code="MEDIA_CONSENT_REQUIRED",
                    )

        await self.repo.add_event_photo(
            db=db,
            event_id=event_id,
            media_asset_id=payload.media_asset_id,
            caption=payload.caption,
            is_featured=payload.is_featured,
        )
        await db.commit()
        # Reload with asset relation
        reloaded = await self.repo.get_event_photo_pair(db, event_id, payload.media_asset_id)
        assert reloaded is not None
        return EventPhotoResponse(
            id=reloaded.id,
            event_id=reloaded.event_id,
            media_asset_id=reloaded.media_asset_id,
            caption=reloaded.caption,
            is_featured=reloaded.is_featured,
            created_at=reloaded.created_at,
            media_asset=MediaAssetResponse.model_validate(asset),
        )

    async def get_event_gallery(
        self, db: AsyncSession, event_id: uuid.UUID
    ) -> EventGalleryResponse:
        """Fetch all photos in event gallery."""
        photos = await self.repo.get_event_photos(db, event_id)
        dtos: list[EventPhotoResponse] = []
        for p in photos:
            asset_dto = MediaAssetResponse.model_validate(p.media_asset) if p.media_asset else None
            dtos.append(
                EventPhotoResponse(
                    id=p.id,
                    event_id=p.event_id,
                    media_asset_id=p.media_asset_id,
                    caption=p.caption,
                    is_featured=p.is_featured,
                    created_at=p.created_at,
                    media_asset=asset_dto,
                )
            )
        return EventGalleryResponse(
            event_id=event_id,
            photos=dtos,
            total=len(dtos),
        )

    async def generate_linkedin_draft(
        self, db: AsyncSession, event_id: uuid.UUID
    ) -> LinkedInDraftResponse:
        """Generate pre-drafted LinkedIn celebration post honoring volunteer name visibility consent."""
        event_stmt = select(Event).where(Event.id == event_id)
        event = (await db.execute(event_stmt)).scalar_one_or_none()
        if not event:
            raise NotFoundException("Event not found.")

        # Fetch attended volunteers and consent
        stmt = (
            select(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                ConsentRecord.name_visible,
                ConsentRecord.linkedin_content,
                AttendanceRecord.duration_minutes,
            )
            .join(
                EventRegistration,
                EventRegistration.volunteer_profile_id == VolunteerProfile.id,
            )
            .join(
                AttendanceRecord,
                AttendanceRecord.event_registration_id == EventRegistration.id,
            )
            .outerjoin(
                ConsentRecord,
                ConsentRecord.volunteer_profile_id == VolunteerProfile.id,
            )
            .where(
                EventRegistration.event_id == event_id,
                AttendanceRecord.status == "COMPLETED",
            )
        )
        rows = (await db.execute(stmt)).all()

        featured_names: list[str] = []
        anonymous_count = 0
        total_hours = sum((r[5] or 0) / 60.0 for r in rows)

        for r in rows:
            name_visible = bool(r[3])
            linkedin_content = bool(r[4])

            # CRITICAL PRIVACY RULE: Only volunteers with affirmative linkedin_content consent
            # can be referenced in social media drafts.
            if not linkedin_content:
                continue

            if name_visible:
                featured_names.append(f"{r[1]} {r[2]}".strip())
            else:
                anonymous_count += 1

        # Compose draft copy
        consented_volunteers_count = len(featured_names) + anonymous_count
        vol_summary = (
            f"{consented_volunteers_count} incredible volunteers"
            if consented_volunteers_count > 0
            else f"{len(rows)} incredible volunteers"
        )
        if featured_names:
            featured_str = f"Special kudos to: {', '.join(featured_names[:5])}"
            if len(featured_names) > 5 or anonymous_count > 0:
                rem = (len(featured_names) - 5) + anonymous_count
                featured_str += f" and {rem} more dedicated contributors!"
        elif anonymous_count > 0:
            featured_str = f"Special thanks to our {anonymous_count} dedicated volunteers who made this possible!"
        else:
            featured_str = "Huge gratitude to all our participants!"

        draft_text = (
            f"🌟 Transforming lives through education & community service! 🌟\n\n"
            f"We are proud to share the completion of our event: {event.title}.\n"
            f"Together, {vol_summary} contributed over {total_hours:.1f} hours of impactful volunteering service.\n\n"
            f"{featured_str}\n\n"
            f"Together, we build brighter futures! 🚀\n\n"
            f"#MaatramFoundation #Volunteering #CommunityImpact #YouthEmpowerment"
        )

        return LinkedInDraftResponse(
            event_id=event.id,
            draft_text=draft_text,
            featured_volunteers=featured_names,
            anonymous_count=anonymous_count,
            hashtags=[
                "#MaatramFoundation",
                "#Volunteering",
                "#CommunityImpact",
                "#YouthEmpowerment",
            ],
        )


media_service = MediaService()
