"""User, session, and profile persistence repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.consent import ConsentRecord
from src.models.users import User, UserSession
from src.models.volunteers import (
    AlumniProfile,
    CorporateProfile,
    StudentProfile,
    VolunteerProfile,
)


class UserRepository:
    """Persistence abstraction for User, UserSession, and Volunteer registration entities."""

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User | None:
        """Fetch user by primary key UUID."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Fetch user by unique lowercased email address."""
        stmt = select(User).where(func.lower(User.email) == func.lower(email))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def check_email_exists(self, db: AsyncSession, email: str) -> bool:
        """Check if email address is already registered."""
        stmt = select(User.id).where(func.lower(User.email) == func.lower(email))
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def check_mobile_exists(self, db: AsyncSession, mobile_number: str) -> bool:
        """Check if mobile number is already registered."""
        stmt = select(VolunteerProfile.id).where(VolunteerProfile.mobile_number == mobile_number)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create_user(self, db: AsyncSession, user: User) -> User:
        """Persist a new User record."""
        db.add(user)
        await db.flush()
        return user

    async def update_user(self, db: AsyncSession, user: User) -> User:
        """Flush changes to an existing user."""
        await db.flush()
        return user

    async def create_volunteer_profile(
        self, db: AsyncSession, profile: VolunteerProfile
    ) -> VolunteerProfile:
        """Persist a base VolunteerProfile record."""
        db.add(profile)
        await db.flush()
        return profile

    async def create_student_profile(
        self, db: AsyncSession, profile: StudentProfile
    ) -> StudentProfile:
        """Persist a StudentProfile record."""
        db.add(profile)
        await db.flush()
        return profile

    async def create_alumni_profile(
        self, db: AsyncSession, profile: AlumniProfile
    ) -> AlumniProfile:
        """Persist an AlumniProfile record."""
        db.add(profile)
        await db.flush()
        return profile

    async def create_corporate_profile(
        self, db: AsyncSession, profile: CorporateProfile
    ) -> CorporateProfile:
        """Persist a CorporateProfile record."""
        db.add(profile)
        await db.flush()
        return profile

    async def create_consent_record(
        self, db: AsyncSession, consent: ConsentRecord
    ) -> ConsentRecord:
        """Persist affirmative ConsentRecord."""
        db.add(consent)
        await db.flush()
        return consent

    async def create_session(self, db: AsyncSession, session: UserSession) -> UserSession:
        """Persist a new UserSession record."""
        db.add(session)
        await db.flush()
        return session

    async def get_session_by_id(
        self, db: AsyncSession, session_id: uuid.UUID
    ) -> UserSession | None:
        """Retrieve user session by primary key."""
        stmt = select(UserSession).where(UserSession.id == session_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_session_by_token_hash(
        self, db: AsyncSession, token_hash: str
    ) -> UserSession | None:
        """Find session by active refresh token SHA-256 hash."""
        stmt = select(UserSession).where(UserSession.refresh_token_hash == token_hash)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_session_by_token_hash_for_update(
        self, db: AsyncSession, token_hash: str
    ) -> UserSession | None:
        """Find session by active refresh token hash with row lock (FOR UPDATE NOWAIT) to prevent concurrent refresh races."""
        stmt = (
            select(UserSession)
            .where(UserSession.refresh_token_hash == token_hash)
            .with_for_update(nowait=True)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_sessions(
        self, db: AsyncSession, user_id: uuid.UUID, only_active: bool = True
    ) -> list[UserSession]:
        """Fetch all sessions for a specific user."""
        stmt = select(UserSession).where(UserSession.user_id == user_id)
        if only_active:
            now = datetime.now(UTC)
            stmt = stmt.where(
                UserSession.is_revoked.is_(False),
                UserSession.expires_at > now,
            )
        stmt = stmt.order_by(UserSession.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def revoke_session(self, db: AsyncSession, session_id: uuid.UUID) -> None:
        """Revoke a single session by primary key."""
        stmt = update(UserSession).where(UserSession.id == session_id).values(is_revoked=True)
        await db.execute(stmt)
        await db.flush()

    async def revoke_all_sessions(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        """Revoke all active sessions for a user (e.g. on password reset or logout-all)."""
        stmt = (
            update(UserSession)
            .where(UserSession.user_id == user_id, UserSession.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        await db.execute(stmt)
        await db.flush()


user_repository = UserRepository()
