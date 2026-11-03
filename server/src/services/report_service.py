"""Core domain service for Administrative Reports, SQL Aggregations, and Excel Exports."""

import asyncio
import io
import math
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import openpyxl
from openpyxl.styles import Font, PatternFill
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import DomainException
from src.core.logging import get_logger
from src.models.reports import ReportExport
from src.models.users import User
from src.repositories.report_repo import ReportRepository, report_repository
from src.schemas.admin import AdminDashboardResponse
from src.schemas.report import (
    AlumniConsistencyItem,
    AlumniConsistencyReportResponse,
    AlumniContributionItem,
    AlumniContributionReportResponse,
    InactiveVolunteerItem,
    InactiveVolunteerReportResponse,
    InterviewAvailabilityItem,
    InterviewAvailabilityReportResponse,
    OrganisationContributionItem,
    OrganisationContributionReportResponse,
    StudentContributionItem,
    StudentContributionReportResponse,
    YearlyConsistencyMetric,
)

logger = get_logger(__name__)


def sanitize_excel_cell(value: Any) -> Any:
    """Formula Injection (CSV/Excel Injection) prevention rule.

    Prepends single quote "'" if any string starts with '=', '+', '-', or '@'.
    """
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


def _generate_excel_bytes(norm_type: str, headers: list[str], data_rows: list[list[Any]]) -> bytes:
    """Synchronous CPU-bound Excel workbook generator with cell styling and formula sanitization."""
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = norm_type[:30]

    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font

    for row in data_rows:
        sanitized_row = [sanitize_excel_cell(c) for c in row]
        ws.append(sanitized_row)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream.getvalue()


class ReportService:
    """Service generating administrative reports, computing dashboard metrics, and exporting Excel workbooks."""

    def __init__(self, repo: ReportRepository | None = None) -> None:
        self.repo = repo or report_repository

    async def get_admin_dashboard(self, db: AsyncSession) -> AdminDashboardResponse:
        """Fetch unified admin dashboard statistics."""
        data = await self.repo.get_admin_dashboard_metrics(db)
        return AdminDashboardResponse.model_validate(data)

    async def get_student_contributions_report(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> StudentContributionReportResponse:
        """Student Contribution Report with pagination."""
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        items_raw, total = await self.repo.get_student_contributions(
            db, skip=skip, limit=limit, start_date=start_date, end_date=end_date
        )
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1
        items = [StudentContributionItem.model_validate(i) for i in items_raw]
        return StudentContributionReportResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_alumni_contributions_report(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> AlumniContributionReportResponse:
        """Alumni Contribution Report with pagination."""
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        items_raw, total = await self.repo.get_alumni_contributions(
            db, skip=skip, limit=limit, start_date=start_date, end_date=end_date
        )
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1
        items = [AlumniContributionItem.model_validate(i) for i in items_raw]
        return AlumniContributionReportResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_alumni_consistency_report(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
    ) -> AlumniConsistencyReportResponse:
        """Alumni Participation Consistency Report with pagination."""
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        items_raw, total = await self.repo.get_alumni_consistency(db, skip=skip, limit=limit)
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1
        items = [
            AlumniConsistencyItem(
                volunteer_id=i["volunteer_id"],
                alumni_name=i["alumni_name"],
                graduation_batch=i["graduation_batch"],
                employer=i["employer"],
                yearly_metrics=[YearlyConsistencyMetric(**m) for m in i["yearly_metrics"]],
                years_active_count=i["years_active_count"],
                is_consistent=i["is_consistent"],
            )
            for i in items_raw
        ]
        return AlumniConsistencyReportResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_inactive_volunteers_report(
        self,
        db: AsyncSession,
        threshold_days: int | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> InactiveVolunteerReportResponse:
        """Inactive Volunteer Report with configurable threshold.

        Note: settings.INACTIVE_VOLUNTEER_DAYS_THRESHOLD (180 days) is a provisional
        technical default pending official Maatram governance ratification.
        """
        days = threshold_days or settings.INACTIVE_VOLUNTEER_DAYS_THRESHOLD
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        items_raw, total = await self.repo.get_inactive_volunteers(
            db, threshold_days=days, skip=skip, limit=limit
        )
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1
        items = [InactiveVolunteerItem.model_validate(i) for i in items_raw]
        return InactiveVolunteerReportResponse(
            threshold_days=days,
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_interview_availability_report(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
    ) -> InterviewAvailabilityReportResponse:
        """Interview Availability Report with contact masking."""
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        items_raw, total = await self.repo.get_interview_availability(db, skip=skip, limit=limit)
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1
        items = [InterviewAvailabilityItem.model_validate(i) for i in items_raw]
        return InterviewAvailabilityReportResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_organisation_contributions_report(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> OrganisationContributionReportResponse:
        """Organisation Contribution Report with pagination."""
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit

        items_raw, total = await self.repo.get_organisation_contributions(
            db, skip=skip, limit=limit, start_date=start_date, end_date=end_date
        )
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1
        items = [OrganisationContributionItem.model_validate(i) for i in items_raw]
        return OrganisationContributionReportResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def export_report_to_excel(
        self,
        db: AsyncSession,
        user: User,
        report_type: str,
        parameters: dict[str, Any] | None = None,
    ) -> tuple[bytes, str, ReportExport]:
        """Generate Excel workbook (.xlsx) with Formula Injection Sanitization."""
        params = parameters or {}
        norm_type = report_type.upper().replace("-", "_")

        headers: list[str] = []
        data_rows: list[list[Any]] = []

        if norm_type in ("STUDENT_CONTRIBUTIONS", "STUDENT_CONTRIBUTION"):
            res_student = await self.get_student_contributions_report(db, page=1, limit=5000)
            headers = [
                "Volunteer ID",
                "Student Name",
                "College",
                "Department",
                "Batch Year",
                "Maatram Reg No",
                "Events Attended",
                "Hours Credited",
                "Points Earned",
            ]
            for s_itm in res_student.items:
                data_rows.append(
                    [
                        str(s_itm.volunteer_id),
                        s_itm.student_name,
                        s_itm.college_name,
                        s_itm.department,
                        s_itm.batch_year or "",
                        s_itm.maatram_reg_number or "",
                        s_itm.events_attended,
                        s_itm.hours_credited,
                        s_itm.points_earned,
                    ]
                )

        elif norm_type in ("ALUMNI_CONTRIBUTIONS", "ALUMNI_CONTRIBUTION"):
            res_alumni = await self.get_alumni_contributions_report(db, page=1, limit=5000)
            headers = [
                "Volunteer ID",
                "Alumni Name",
                "Graduation Batch",
                "Employer",
                "Designation",
                "Events Attended",
                "Hours Credited",
                "Points Earned",
            ]
            for a_itm in res_alumni.items:
                data_rows.append(
                    [
                        str(a_itm.volunteer_id),
                        a_itm.alumni_name,
                        a_itm.graduation_batch or "",
                        a_itm.employer or "",
                        a_itm.designation or "",
                        a_itm.events_attended,
                        a_itm.hours_credited,
                        a_itm.points_earned,
                    ]
                )

        elif norm_type in ("ALUMNI_CONSISTENCY", "ALUMNI_CONSISTENCY_REPORT"):
            res_consistency = await self.get_alumni_consistency_report(db, page=1, limit=5000)
            headers = [
                "Volunteer ID",
                "Alumni Name",
                "Batch",
                "Employer",
                "Years Active",
                "Consistent Volunteer",
            ]
            for c_itm in res_consistency.items:
                data_rows.append(
                    [
                        str(c_itm.volunteer_id),
                        c_itm.alumni_name,
                        c_itm.graduation_batch or "",
                        c_itm.employer or "",
                        c_itm.years_active_count,
                        "YES" if c_itm.is_consistent else "NO",
                    ]
                )

        elif norm_type in ("INACTIVE_VOLUNTEERS", "INACTIVE_VOLUNTEER"):
            res_inactive = await self.get_inactive_volunteers_report(db, page=1, limit=5000)
            headers = [
                "Volunteer ID",
                "Name",
                "Email",
                "Category",
                "Registration Date",
                "Last Activity Date",
                "Days Inactive",
            ]
            for in_itm in res_inactive.items:
                data_rows.append(
                    [
                        str(in_itm.volunteer_id),
                        in_itm.name,
                        in_itm.email,
                        in_itm.category,
                        in_itm.registration_date.strftime("%Y-%m-%d"),
                        (
                            in_itm.last_activity_date.strftime("%Y-%m-%d")
                            if in_itm.last_activity_date
                            else "Never"
                        ),
                        in_itm.days_inactive,
                    ]
                )

        elif norm_type in ("INTERVIEW_AVAILABILITY", "INTERVIEW_AVAILABILITY_REPORT"):
            res_interview = await self.get_interview_availability_report(db, page=1, limit=5000)
            headers = [
                "Volunteer ID",
                "Name",
                "Category",
                "Employer",
                "Designation",
                "Skills",
                "Years Experience",
                "Phone",
                "Email",
                "Contact Masked",
            ]
            for iv_itm in res_interview.items:
                data_rows.append(
                    [
                        str(iv_itm.volunteer_id),
                        iv_itm.name,
                        iv_itm.category,
                        iv_itm.employer or "",
                        iv_itm.designation or "",
                        ", ".join(iv_itm.skills),
                        iv_itm.experience_years or "",
                        iv_itm.phone_number,
                        iv_itm.email,
                        "YES" if iv_itm.is_contact_masked else "NO",
                    ]
                )

        elif norm_type in ("ORGANISATION_CONTRIBUTIONS", "ORGANISATION_CONTRIBUTION"):
            res_org = await self.get_organisation_contributions_report(db, page=1, limit=5000)
            headers = [
                "Organisation",
                "Volunteers Count",
                "Events Attended",
                "Hours Credited",
                "Points Earned",
            ]
            for org_itm in res_org.items:
                data_rows.append(
                    [
                        org_itm.organisation_name,
                        org_itm.volunteer_count,
                        org_itm.total_events_attended,
                        org_itm.total_hours_credited,
                        org_itm.total_points_earned,
                    ]
                )
        else:
            raise DomainException(
                f"Unknown report type: '{report_type}'.",
                status_code=400,
                code="INVALID_REPORT_TYPE",
            )

        # Generate Excel workbook off the event loop in threadpool
        file_bytes = await asyncio.to_thread(_generate_excel_bytes, norm_type, headers, data_rows)

        # Track export record
        expires_at = datetime.now(UTC) + timedelta(days=settings.REPORT_EXPORT_EXPIRE_DAYS)
        export_record = await self.repo.create_report_export(
            db=db,
            requested_by_user_id=user.id,
            report_type=norm_type,
            parameters=params,
            expires_at=expires_at,
        )
        export_record.status = "COMPLETED"
        await db.commit()

        filename = f"{norm_type.lower()}_{int(time.time())}.xlsx"
        return file_bytes, filename, export_record


report_service = ReportService()
