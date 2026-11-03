"""Consent records and differential audit history service."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundException
from src.models.consent import ConsentHistory, ConsentRecord
from src.repositories.consent_repo import consent_repository
from src.schemas.consent import (
    ConsentHistoryItem,
    ConsentHistoryResponse,
    ConsentUpdate,
)

CONSENT_DIMENSIONS: list[str] = [
    "leaderboard_visible",
    "name_visible",
    "thank_you_emails",
    "linkedin_content",
    "contact_available",
    "media_usage",
]


class ConsentService:
    """Core domain service orchestrating affirmative consent state and immutable differential history."""

    async def get_consent_me(self, db: AsyncSession, user_id: uuid.UUID) -> ConsentRecord:
        """Fetch active affirmative consent settings for authenticated volunteer."""
        record = await consent_repository.get_by_user_id(db, user_id)
        if not record:
            raise NotFoundException("Consent record not found.")
        return record

    async def update_consent_me(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        update_data: ConsentUpdate,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentRecord:
        """Update consent settings and record differential change history per altered dimension."""
        record = await consent_repository.get_by_user_id(db, user_id)
        if not record:
            raise NotFoundException("Consent record not found.")

        has_changes = False

        for dim in CONSENT_DIMENSIONS:
            new_val = getattr(update_data, dim)
            if new_val is not None:
                old_val = getattr(record, dim)
                if old_val != new_val:
                    has_changes = True
                    setattr(record, dim, new_val)
                    # Persist differential history
                    history_entry = ConsentHistory(
                        consent_record_id=record.id,
                        dimension=dim,
                        old_value=old_val,
                        new_value=new_val,
                        changed_by_user_id=user_id,
                        ip_address=client_ip,
                        user_agent=user_agent,
                    )
                    await consent_repository.create_history_entry(db, history_entry)

        if has_changes:
            record.version += 1
            record.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(record)

        return record

    async def get_consent_history_me(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> ConsentHistoryResponse:
        """Fetch immutable chronological history of all consent changes for authenticated volunteer."""
        record = await consent_repository.get_by_user_id(db, user_id)
        if not record:
            raise NotFoundException("Consent record not found.")

        entries = await consent_repository.get_history_by_record_id(db, record.id)
        items = [ConsentHistoryItem.model_validate(e) for e in entries]

        return ConsentHistoryResponse(items=items, total=len(items))


consent_service = ConsentService()
