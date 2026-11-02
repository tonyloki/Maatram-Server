"""Module 10: Media Assets & Event Photos models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin, utc_now


class MediaAsset(Base, UUIDPrimaryKeyMixin):
    """Cloudinary uploaded media registry with ownership and metadata."""

    __tablename__ = "media_assets"

    public_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    secure_url: Mapped[str] = mapped_column(String(512), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "asset_type IN ('AVATAR', 'EVENT_COVER', 'EVENT_GALLERY', 'DOCUMENT', 'PARENTAL_CONSENT')",
            name="chk_media_assets_type",
        ),
    )

    uploaded_by: Mapped["User"] = relationship("User")
    event_photos: Mapped[list["EventPhoto"]] = relationship(
        "EventPhoto", back_populates="media_asset"
    )


class EventPhoto(Base, UUIDPrimaryKeyMixin):
    """Associative gallery linking media assets to events."""

    __tablename__ = "event_photos"

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_asset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    caption: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (UniqueConstraint("event_id", "media_asset_id", name="uq_event_photos_pair"),)

    event: Mapped["Event"] = relationship("Event", back_populates="photos")
    media_asset: Mapped["MediaAsset"] = relationship("MediaAsset", back_populates="event_photos")


from src.models.events import Event  # noqa: E402
from src.models.users import User  # noqa: E402
