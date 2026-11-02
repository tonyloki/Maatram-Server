"""Volunteer profiles and polymorphic category service."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from src.models.users import User
from src.models.volunteers import (
    AlumniProfile,
    CorporateProfile,
    StudentProfile,
    VolunteerProfile,
)
from src.repositories.token_repo import token_repository
from src.repositories.volunteer_repo import volunteer_repository
from src.schemas.volunteer import (
    VolunteerListResponse,
    VolunteerProfileResponse,
    VolunteerProfileUpdate,
)


class VolunteerService:
    """Core domain service orchestrating volunteer profiles, category details, and directories."""

    async def get_my_profile(self, db: AsyncSession, user_id: uuid.UUID) -> VolunteerProfile:
        """Fetch active volunteer profile for authenticated user."""
        profile = await volunteer_repository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundException("Volunteer profile not found.")
        return profile

    async def get_profile_by_id(
        self, db: AsyncSession, profile_id: uuid.UUID, current_user: User
    ) -> VolunteerProfile:
        """Fetch volunteer profile by ID with strict ownership/RBAC authorization."""
        profile = await volunteer_repository.get_by_id(db, profile_id)
        if not profile:
            raise NotFoundException("Volunteer profile not found.")

        # BOLA Authorization: Admin or self only
        if current_user.role not in ("ADMIN", "SUPER_ADMIN") and profile.user_id != current_user.id:
            raise ForbiddenException("You do not have permission to view this volunteer profile.")

        return profile

    async def update_my_profile(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        update_data: VolunteerProfileUpdate,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> VolunteerProfile:
        """Apply self-service updates to base and category profile details."""
        profile = await volunteer_repository.get_by_user_id(db, user_id)
        if not profile:
            raise NotFoundException("Volunteer profile not found.")

        old_state = {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "mobile_number": profile.mobile_number,
            "bio": profile.bio,
        }

        # Update base fields if provided
        if update_data.first_name is not None:
            profile.first_name = update_data.first_name.strip()
        if update_data.last_name is not None:
            profile.last_name = update_data.last_name.strip()
        if update_data.gender is not None:
            profile.gender = update_data.gender
        if update_data.bio is not None:
            profile.bio = update_data.bio.strip()
        if update_data.parent_guardian_name is not None:
            profile.parent_guardian_name = update_data.parent_guardian_name.strip()
        if update_data.parent_guardian_relationship is not None:
            profile.parent_guardian_relationship = update_data.parent_guardian_relationship.strip()
        if update_data.parent_guardian_contact is not None:
            profile.parent_guardian_contact = update_data.parent_guardian_contact.strip()

        # Update mobile with uniqueness check
        if update_data.mobile_number and update_data.mobile_number != profile.mobile_number:
            existing = await volunteer_repository.get_by_mobile(db, update_data.mobile_number)
            if existing and existing.id != profile.id:
                raise ConflictException("Mobile number is already registered.")
            profile.mobile_number = update_data.mobile_number

        # Update category-specific details
        if profile.category == "STUDENT" and update_data.student_details:
            details = update_data.student_details
            student = profile.student_profile
            if not student:
                student = StudentProfile(
                    volunteer_profile_id=profile.id,
                    college_name=details.college_name or "",
                    degree=details.degree or "",
                    department=details.department or "",
                    batch_year=details.batch_year or 2026,
                    current_year=details.current_year or 1,
                    maatram_reg_number=details.maatram_reg_number or "",
                )
                await volunteer_repository.create_student_profile(db, student)
            else:
                if (
                    details.maatram_reg_number
                    and details.maatram_reg_number != student.maatram_reg_number
                ):
                    existing_reg = await volunteer_repository.get_student_by_reg_number(
                        db, details.maatram_reg_number
                    )
                    if existing_reg and existing_reg.id != student.id:
                        raise ConflictException("Maatram registration number already in use.")
                    student.maatram_reg_number = details.maatram_reg_number.strip()
                if details.college_name is not None:
                    student.college_name = details.college_name.strip()
                if details.degree is not None:
                    student.degree = details.degree.strip()
                if details.department is not None:
                    student.department = details.department.strip()
                if details.batch_year is not None:
                    student.batch_year = details.batch_year
                if details.current_year is not None:
                    student.current_year = details.current_year

        elif profile.category == "ALUMNI" and update_data.alumni_details:
            a_details = update_data.alumni_details
            alumni = profile.alumni_profile
            if not alumni:
                alumni = AlumniProfile(
                    volunteer_profile_id=profile.id,
                    organisation=a_details.organisation or "",
                    job_role=a_details.job_role or "",
                    years_of_experience=a_details.years_of_experience or 0,
                    location=a_details.location or "",
                    skills=a_details.skills or [],
                    college_name=a_details.college_name or "",
                    degree=a_details.degree or "",
                    department=a_details.department or "",
                    batch_year=a_details.batch_year or 2020,
                    graduation_year=a_details.graduation_year or 2024,
                )
                await volunteer_repository.create_alumni_profile(db, alumni)
            else:
                if a_details.organisation is not None:
                    alumni.organisation = a_details.organisation.strip()
                if a_details.job_role is not None:
                    alumni.job_role = a_details.job_role.strip()
                if a_details.years_of_experience is not None:
                    alumni.years_of_experience = a_details.years_of_experience
                if a_details.location is not None:
                    alumni.location = a_details.location.strip()
                if a_details.skills is not None:
                    alumni.skills = a_details.skills
                if a_details.college_name is not None:
                    alumni.college_name = a_details.college_name.strip()
                if a_details.degree is not None:
                    alumni.degree = a_details.degree.strip()
                if a_details.department is not None:
                    alumni.department = a_details.department.strip()
                if a_details.batch_year is not None:
                    alumni.batch_year = a_details.batch_year
                if a_details.graduation_year is not None:
                    alumni.graduation_year = a_details.graduation_year

        elif profile.category == "CORPORATE" and update_data.corporate_details:
            c_details = update_data.corporate_details
            corporate = profile.corporate_profile
            if not corporate:
                corporate = CorporateProfile(
                    volunteer_profile_id=profile.id,
                    organisation=c_details.organisation or "",
                    designation=c_details.designation or "",
                    years_of_experience=c_details.years_of_experience or 0,
                    location=c_details.location or "",
                    skills=c_details.skills or [],
                )
                await volunteer_repository.create_corporate_profile(db, corporate)
            else:
                if c_details.organisation is not None:
                    corporate.organisation = c_details.organisation.strip()
                if c_details.designation is not None:
                    corporate.designation = c_details.designation.strip()
                if c_details.years_of_experience is not None:
                    corporate.years_of_experience = c_details.years_of_experience
                if c_details.location is not None:
                    corporate.location = c_details.location.strip()
                if c_details.skills is not None:
                    corporate.skills = c_details.skills

        # Record audit log
        await token_repository.create_audit_log(
            db,
            action="VOLUNTEER_PROFILE_UPDATED",
            resource_type="volunteer_profile",
            resource_id=str(profile.id),
            actor_user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
            old_state=old_state,
            new_state={
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "mobile_number": profile.mobile_number,
                "bio": profile.bio,
            },
        )

        await db.commit()
        # Refetch profile with relations loaded
        refreshed = await volunteer_repository.get_by_id(db, profile.id)
        assert refreshed is not None
        return refreshed

    async def list_volunteers(
        self,
        db: AsyncSession,
        current_user: User,
        category: str | None = None,
        status: str | None = None,
        college: str | None = None,
        employer: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> VolunteerListResponse:
        """Administrative directory search for volunteers with pagination."""
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise ForbiddenException("Directory search requires administrative privileges.")

        items, total = await volunteer_repository.list_volunteers(
            db=db,
            category=category,
            status=status,
            college=college,
            employer=employer,
            search=search,
            page=page,
            page_size=page_size,
        )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return VolunteerListResponse(
            items=[VolunteerProfileResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


volunteer_service = VolunteerService()
