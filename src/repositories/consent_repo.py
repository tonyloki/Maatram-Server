"""Consent records and history persistence repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.consent import ConsentHistory, ConsentRecord
from src.models.volunteers import VolunteerProfile


class ConsentRepository:
    """Persistence abstraction for ConsentRecord and ConsentHistory."""

    async def get_by_profile_id(
        self, db: AsyncSession, profile_id: uuid.UUID
    ) -> ConsentRecord | None:
        """Fetch consent record for a volunteer profile."""
        stmt = select(ConsentRecord).where(ConsentRecord.volunteer_profile_id == profile_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, db: AsyncSession, user_id: uuid.UUID) -> ConsentRecord | None:
        """Fetch consent record for a user via their volunteer profile."""
        stmt = (
            select(ConsentRecord)
            .join(
                VolunteerProfile,
                ConsentRecord.volunteer_profile_id == VolunteerProfile.id,
            )
            .where(VolunteerProfile.user_id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_consent_record(
        self, db: AsyncSession, consent: ConsentRecord
    ) -> ConsentRecord:
        """Persist affirmative consent record."""
        db.add(consent)
        await db.flush()
        return consent

    async def create_history_entry(self, db: AsyncSession, entry: ConsentHistory) -> ConsentHistory:
        """Persist consent history entry."""
        db.add(entry)
        await db.flush()
        return entry

    async def get_history_by_record_id(
        self, db: AsyncSession, consent_record_id: uuid.UUID
    ) -> list[ConsentHistory]:
        """Fetch immutable history entries for a consent record."""
        stmt = (
            select(ConsentHistory)
            .where(ConsentHistory.consent_record_id == consent_record_id)
            .options(selectinload(ConsentHistory.changed_by))
            .order_by(ConsentHistory.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


consent_repository = ConsentRepository()
