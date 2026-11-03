"""Module 12: Reporting & Data Exports models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, CompatibleJSONB, UUIDPrimaryKeyMixin, utc_now


class ReportExport(Base, UUIDPrimaryKeyMixin):
    """Tracking asynchronous report and CSV generation jobs."""

    __tablename__ = "report_exports"

    requested_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[dict[str, Any]] = mapped_column(
        CompatibleJSONB, default=dict, nullable=False
    )
    file_media_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')",
            name="chk_report_exports_status",
        ),
    )

    requested_by: Mapped["User"] = relationship("User")
    file_media: Mapped["MediaAsset | None"] = relationship("MediaAsset")


from src.models.media import MediaAsset  # noqa: E402
from src.models.users import User  # noqa: E402
