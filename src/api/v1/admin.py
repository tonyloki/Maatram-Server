"""Administration, Operational Dashboard, Reports, and Outbox DLQ management routes."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_role
from src.models.users import User
from src.schemas.admin import AdminDashboardResponse, AuditLogListResponse
from src.schemas.notification import (
    OutboxJobListResponse,
    OutboxRetryResponse,
)
from src.schemas.report import (
    AlumniConsistencyReportResponse,
    AlumniContributionReportResponse,
    InactiveVolunteerReportResponse,
    InterviewAvailabilityReportResponse,
    OrganisationContributionReportResponse,
    StudentContributionReportResponse,
)
from src.services.admin_service import admin_service
from src.services.notification_service import notification_service
from src.services.report_service import report_service

router = APIRouter(prefix="/admin", tags=["Administration & Reporting"])


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
    summary="Get aggregated administrator operational dashboard (Admin only)",
)
async def get_admin_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> AdminDashboardResponse:
    """Retrieve comprehensive live statistics across volunteers, applications, events, and engagement."""
    return await report_service.get_admin_dashboard(db)


# Six Production Reports
@router.get(
    "/reports/student-contributions",
    response_model=StudentContributionReportResponse,
    summary="Student Contribution Report (Admin only)",
)
async def get_student_contributions_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
) -> StudentContributionReportResponse:
    """Student contribution report with hours, points, and event attendance."""
    return await report_service.get_student_contributions_report(
        db=db,
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/reports/alumni-contributions",
    response_model=AlumniContributionReportResponse,
    summary="Alumni Contribution Report (Admin only)",
)
async def get_alumni_contributions_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
) -> AlumniContributionReportResponse:
    """Alumni contribution report with employer and hours credited."""
    return await report_service.get_alumni_contributions_report(
        db=db,
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/reports/alumni-consistency",
    response_model=AlumniConsistencyReportResponse,
    summary="Alumni Consistency Report across calendar years (Admin only)",
)
async def get_alumni_consistency_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> AlumniConsistencyReportResponse:
    """Alumni historical consistency analysis across calendar years."""
    return await report_service.get_alumni_consistency_report(
        db=db,
        page=page,
        limit=limit,
    )


@router.get(
    "/reports/inactive-volunteers",
    response_model=InactiveVolunteerReportResponse,
    summary="Inactive Volunteer Report (Admin only)",
)
async def get_inactive_volunteers_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    threshold_days: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> InactiveVolunteerReportResponse:
    """Volunteers with zero attendances in the last N days."""
    return await report_service.get_inactive_volunteers_report(
        db=db,
        threshold_days=threshold_days,
        page=page,
        limit=limit,
    )


@router.get(
    "/reports/interview-availability",
    response_model=InterviewAvailabilityReportResponse,
    summary="Interview Availability Report with privacy contact masking (Admin only)",
)
async def get_interview_availability_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> InterviewAvailabilityReportResponse:
    """Corporate panelists and alumni available for mock interviews with privacy contact masking."""
    return await report_service.get_interview_availability_report(
        db=db,
        page=page,
        limit=limit,
    )


@router.get(
    "/reports/organisation-contributions",
    response_model=OrganisationContributionReportResponse,
    summary="Employer / Organisation Contribution Report (Admin only)",
)
async def get_organisation_contributions_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
) -> OrganisationContributionReportResponse:
    """Grouped contributions by employer/organisation name."""
    return await report_service.get_organisation_contributions_report(
        db=db,
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/reports/{report_type}/export",
    summary="Export report as Excel (.xlsx) file with Formula Injection Sanitization (Admin only)",
)
async def export_report_excel(
    report_type: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> Response:
    """Export report to streaming Excel binary format with formula injection sanitization."""
    file_bytes, filename, _ = await report_service.export_report_to_excel(
        db=db,
        user=current_user,
        report_type=report_type,
    )
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


# Outbox Administration Endpoints
@router.get(
    "/outbox/jobs",
    response_model=OutboxJobListResponse,
    summary="List transactional outbox jobs with status/channel filters (Admin only)",
)
async def list_outbox_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    status: str | None = Query(
        default=None, description="PENDING, PROCESSING, SENT, FAILED, DEAD_LETTER"
    ),
    channel: str | None = Query(default=None, description="EMAIL, PUSH"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> OutboxJobListResponse:
    """List outbox communication jobs with status/channel filters."""
    return await notification_service.list_outbox_jobs(
        db=db,
        status=status,
        channel=channel,
        page=page,
        limit=limit,
    )


@router.get(
    "/outbox/dead-letter",
    response_model=OutboxJobListResponse,
    summary="List dead-lettered communication jobs (Super Admin inspection)",
)
async def list_dead_letter_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("SUPER_ADMIN"))],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> OutboxJobListResponse:
    """Query jobs in DEAD_LETTER status."""
    return await notification_service.list_outbox_jobs(
        db=db,
        status="DEAD_LETTER",
        page=page,
        limit=limit,
    )


@router.post(
    "/outbox/jobs/{job_id}/retry",
    response_model=OutboxRetryResponse,
    summary="Manually retry an outbox job (Admin only)",
)
@router.post(
    "/outbox/{job_id}/requeue",
    response_model=OutboxRetryResponse,
    include_in_schema=False,
)
async def retry_outbox_job(
    job_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> OutboxRetryResponse:
    """Reset failed or dead-letter outbox job to PENDING."""
    return await notification_service.requeue_job(
        db=db,
        job_id=job_id,
    )


# System Audit Logs
@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    summary="Query system security and business audit logs (Super Admin only)",
)
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("SUPER_ADMIN"))],
    actor_id: uuid.UUID | None = Query(default=None),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> AuditLogListResponse:
    """Inspect immutable audit logs across system actions."""
    return await admin_service.list_audit_logs(
        db=db,
        user=current_user,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        from_date=from_date,
        to_date=to_date,
        page=page,
        limit=limit,
    )
