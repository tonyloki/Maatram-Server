"""Volunteer profiles and polymorphic category repositories."""

import uuid
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.users import User
from src.models.volunteers import (
    AlumniProfile,
    CorporateProfile,
    StudentProfile,
    VolunteerProfile,
)


class VolunteerRepository:
    """Persistence abstraction for polymorphic volunteer profiles."""

    async def get_by_id(self, db: AsyncSession, profile_id: uuid.UUID) -> VolunteerProfile | None:
        """Fetch volunteer profile with polymorphic category relations loaded."""
        stmt = (
            select(VolunteerProfile)
            .where(VolunteerProfile.id == profile_id)
            .options(
                selectinload(VolunteerProfile.student_profile),
                selectinload(VolunteerProfile.alumni_profile),
                selectinload(VolunteerProfile.corporate_profile),
                selectinload(VolunteerProfile.user),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, db: AsyncSession, user_id: uuid.UUID) -> VolunteerProfile | None:
        """Fetch volunteer profile by user id with polymorphic category relations loaded."""
        stmt = (
            select(VolunteerProfile)
            .where(VolunteerProfile.user_id == user_id)
            .options(
                selectinload(VolunteerProfile.student_profile),
                selectinload(VolunteerProfile.alumni_profile),
                selectinload(VolunteerProfile.corporate_profile),
                selectinload(VolunteerProfile.user),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_mobile(self, db: AsyncSession, mobile_number: str) -> VolunteerProfile | None:
        """Fetch volunteer profile by mobile number."""
        stmt = select(VolunteerProfile).where(VolunteerProfile.mobile_number == mobile_number)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_student_by_reg_number(
        self, db: AsyncSession, maatram_reg_number: str
    ) -> StudentProfile | None:
        """Fetch student profile by unique Maatram registration number."""
        stmt = select(StudentProfile).where(StudentProfile.maatram_reg_number == maatram_reg_number)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_volunteer_profile(
        self, db: AsyncSession, profile: VolunteerProfile
    ) -> VolunteerProfile:
        """Persist base volunteer profile."""
        db.add(profile)
        await db.flush()
        return profile

    async def create_student_profile(
        self, db: AsyncSession, student: StudentProfile
    ) -> StudentProfile:
        """Persist student category profile."""
        db.add(student)
        await db.flush()
        return student

    async def create_alumni_profile(self, db: AsyncSession, alumni: AlumniProfile) -> AlumniProfile:
        """Persist alumni category profile."""
        db.add(alumni)
        await db.flush()
        return alumni

    async def create_corporate_profile(
        self, db: AsyncSession, corporate: CorporateProfile
    ) -> CorporateProfile:
        """Persist corporate panelist category profile."""
        db.add(corporate)
        await db.flush()
        return corporate

    async def list_volunteers(
        self,
        db: AsyncSession,
        category: str | None = None,
        status: str | None = None,
        college: str | None = None,
        employer: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[VolunteerProfile], int]:
        """Query volunteers with filters, joins, and pagination."""
        base_query = (
            select(VolunteerProfile)
            .join(User, VolunteerProfile.user_id == User.id)
            .outerjoin(StudentProfile, VolunteerProfile.id == StudentProfile.volunteer_profile_id)
            .outerjoin(AlumniProfile, VolunteerProfile.id == AlumniProfile.volunteer_profile_id)
            .outerjoin(
                CorporateProfile, VolunteerProfile.id == CorporateProfile.volunteer_profile_id
            )
        )

        filters: list[Any] = []

        if category:
            filters.append(VolunteerProfile.category == category.upper())
        if status:
            filters.append(User.status == status.upper())
        if college:
            filters.append(
                or_(
                    StudentProfile.college_name.ilike(f"%{college}%"),
                    AlumniProfile.college_name.ilike(f"%{college}%"),
                )
            )
        if employer:
            filters.append(
                or_(
                    AlumniProfile.organisation.ilike(f"%{employer}%"),
                    CorporateProfile.organisation.ilike(f"%{employer}%"),
                )
            )
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    VolunteerProfile.first_name.ilike(search_pattern),
                    VolunteerProfile.last_name.ilike(search_pattern),
                    VolunteerProfile.mobile_number.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                )
            )

        if filters:
            base_query = base_query.where(*filters)

        # Count total
        subq = base_query.subquery()
        count_query = select(func.count(func.distinct(subq.c.id)))
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Paginated fetch with eager-loaded relations
        offset = (page - 1) * page_size
        items_query = (
            base_query.options(
                selectinload(VolunteerProfile.student_profile),
                selectinload(VolunteerProfile.alumni_profile),
                selectinload(VolunteerProfile.corporate_profile),
                selectinload(VolunteerProfile.user),
            )
            .order_by(VolunteerProfile.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        items_result = await db.execute(items_query)
        items = list(items_result.scalars().all())

        return items, total


volunteer_repository = VolunteerRepository()
