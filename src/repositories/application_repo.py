"""Application and Review persistence repository."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.applications import ApplicationReview, VolunteerApplication
from src.models.users import User
from src.models.volunteers import VolunteerProfile


class ApplicationRepository:
    """Persistence abstraction for VolunteerApplication and ApplicationReview."""

    async def get_by_id(
        self, db: AsyncSession, application_id: uuid.UUID
    ) -> VolunteerApplication | None:
        """Fetch volunteer application by ID with profile and review details eager loaded."""
        stmt = (
            select(VolunteerApplication)
            .where(VolunteerApplication.id == application_id)
            .options(
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.student_profile
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.alumni_profile
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.corporate_profile
                ),
                selectinload(VolunteerApplication.reviews).selectinload(ApplicationReview.reviewer),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> VolunteerApplication | None:
        """Fetch volunteer application for a specific user."""
        stmt = (
            select(VolunteerApplication)
            .join(
                VolunteerProfile,
                VolunteerApplication.volunteer_profile_id == VolunteerProfile.id,
            )
            .where(VolunteerProfile.user_id == user_id)
            .options(
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.student_profile
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.alumni_profile
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.corporate_profile
                ),
                selectinload(VolunteerApplication.reviews).selectinload(ApplicationReview.reviewer),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_volunteer_profile_id(
        self, db: AsyncSession, profile_id: uuid.UUID
    ) -> VolunteerApplication | None:
        """Fetch volunteer application by volunteer profile ID."""
        stmt = (
            select(VolunteerApplication)
            .where(VolunteerApplication.volunteer_profile_id == profile_id)
            .options(
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(VolunteerApplication.reviews).selectinload(ApplicationReview.reviewer),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_application(
        self, db: AsyncSession, application: VolunteerApplication
    ) -> VolunteerApplication:
        """Persist volunteer application."""
        db.add(application)
        await db.flush()
        return application

    async def create_review(self, db: AsyncSession, review: ApplicationReview) -> ApplicationReview:
        """Persist application review."""
        db.add(review)
        await db.flush()
        return review

    async def list_applications(
        self,
        db: AsyncSession,
        status: str | None = None,
        category: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[VolunteerApplication], int]:
        """Query applications with administrative filtering, multi-field search, and pagination."""
        base_query = (
            select(VolunteerApplication)
            .join(
                VolunteerProfile,
                VolunteerApplication.volunteer_profile_id == VolunteerProfile.id,
            )
            .join(User, VolunteerProfile.user_id == User.id)
        )

        filters: list[Any] = []
        if status:
            filters.append(VolunteerApplication.status == status.upper())
        if category:
            filters.append(VolunteerProfile.category == category.upper())
        if date_from:
            filters.append(VolunteerApplication.submitted_at >= date_from)
        if date_to:
            filters.append(VolunteerApplication.submitted_at <= date_to)
        if search:
            pattern = f"%{search}%"
            filters.append(
                or_(
                    VolunteerProfile.first_name.ilike(pattern),
                    VolunteerProfile.last_name.ilike(pattern),
                    VolunteerProfile.mobile_number.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )

        if filters:
            base_query = base_query.where(*filters)

        # Count total
        subq = base_query.subquery()
        count_query = select(func.count(func.distinct(subq.c.id)))
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Paginated items
        offset = (page - 1) * page_size
        items_query = (
            base_query.options(
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.user
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.student_profile
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.alumni_profile
                ),
                selectinload(VolunteerApplication.volunteer_profile).selectinload(
                    VolunteerProfile.corporate_profile
                ),
                selectinload(VolunteerApplication.reviews).selectinload(ApplicationReview.reviewer),
            )
            .order_by(VolunteerApplication.submitted_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        items_result = await db.execute(items_query)
        items = list(items_result.scalars().all())

        return items, total


application_repository = ApplicationRepository()
