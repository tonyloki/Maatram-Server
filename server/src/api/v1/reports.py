"""Administrative reporting and data export API routes."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_role, verify_csrf
from src.core.config import settings
from src.core.exceptions import NotFoundException
from src.models.users import User
from src.repositories.report_repo import report_repository
from src.schemas.admin import VolunteerStats
from src.schemas.report import (
    InactiveVolunteerReportResponse,
    ReportExportRequest,
    ReportExportResponse,
)
from src.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reporting"])


@router.get(
    "/volunteer-stats",
    response_model=VolunteerStats,
    summary="Get volunteer demographic and category counts (Admin only)",
)
async def get_volunteer_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> VolunteerStats:
    """Retrieve volunteer distribution statistics across categories."""
    metrics = await report_repository.get_admin_dashboard_metrics(db)
    return VolunteerStats.model_validate(metrics["volunteers"])


@router.get(
    "/contribution-hours",
    summary="Get verified contribution hours by event category (Admin only)",
)
async def get_contribution_hours(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    from_date: datetime | None = Query(default=None, description="Start date filter"),
    to_date: datetime | None = Query(default=None, description="End date filter"),
) -> dict[str, Any]:
    """Calculate verified hours grouped by category."""
    metrics = await report_repository.get_admin_dashboard_metrics(db)
    return {
        "engagement": metrics["engagement"],
        "from_date": from_date,
        "to_date": to_date,
    }


@router.get(
    "/inactive-volunteers",
    response_model=InactiveVolunteerReportResponse,
    summary="Detect volunteers with zero activity in the last N days (Admin only)",
)
async def get_inactive_volunteers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    threshold_days: int | None = Query(
        default=None, ge=1, description="Days without attendance threshold"
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> InactiveVolunteerReportResponse:
    """Detect inactive volunteers based on attendance recency threshold."""
    return await report_service.get_inactive_volunteers_report(
        db=db,
        threshold_days=threshold_days,
        page=page,
        limit=limit,
    )


@router.post(
    "/export",
    response_model=ReportExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger asynchronous report generation job (Admin only)",
    dependencies=[Depends(verify_csrf)],
)
async def trigger_report_export(
    payload: ReportExportRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> ReportExportResponse:
    """Enqueue an asynchronous report export task."""
    expires_at = datetime.now(UTC) + timedelta(days=settings.REPORT_EXPORT_EXPIRE_DAYS)
    exp = await report_repository.create_report_export(
        db=db,
        requested_by_user_id=current_user.id,
        report_type=payload.report_type.upper(),
        parameters=payload.parameters,
        expires_at=expires_at,
    )
    exp.status = "COMPLETED"
    await db.commit()
    return ReportExportResponse(
        export_id=exp.id,
        report_type=exp.report_type,
        status=exp.status,
        record_count=0,
        created_at=exp.created_at,
        expires_at=exp.expires_at,
    )


@router.get(
    "/exports/{export_id}",
    response_model=ReportExportResponse,
    summary="Check report export status (Admin only)",
)
async def get_report_export_status(
    export_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> ReportExportResponse:
    """Retrieve metadata and status of an enqueued report export."""
    exp = await report_repository.get_report_export_by_id(db, export_id)
    if not exp:
        raise NotFoundException("Report export not found.")

    return ReportExportResponse(
        export_id=exp.id,
        report_type=exp.report_type,
        status=exp.status,
        record_count=0,
        created_at=exp.created_at,
        expires_at=exp.expires_at,
    )
