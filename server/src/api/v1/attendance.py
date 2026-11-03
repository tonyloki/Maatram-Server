"""Attendance Tracking & Hours Management API router."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_role, verify_csrf
from src.models.users import User
from src.schemas.attendance import (
    AttendanceCorrectionRequest,
    AttendanceListResponse,
    AttendanceRecordResponse,
    BulkAttendanceRequest,
    BulkAttendanceResponse,
    CheckInRequest,
    CheckOutRequest,
)
from src.services.attendance_service import attendance_service

router = APIRouter(tags=["Attendance"])


@router.post(
    "/events/{event_id}/attendance/check-in",
    response_model=list[AttendanceRecordResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_csrf)],
)
async def check_in_volunteers(
    event_id: uuid.UUID,
    data: CheckInRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> list[AttendanceRecordResponse]:
    """Log physical or virtual volunteer check-in for an event."""
    return await attendance_service.check_in_volunteers(
        db=db,
        event_id=event_id,
        volunteer_profile_ids=data.volunteer_profile_ids or [],
        check_in_time=data.check_in_time,
        current_user=current_user,
    )


@router.post(
    "/events/{event_id}/attendance/check-out",
    response_model=list[AttendanceRecordResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_csrf)],
)
async def check_out_volunteers(
    event_id: uuid.UUID,
    data: CheckOutRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> list[AttendanceRecordResponse]:
    """Log volunteer check-out and compute duration in minutes."""
    return await attendance_service.check_out_volunteers(
        db=db,
        event_id=event_id,
        volunteer_profile_ids=data.volunteer_profile_ids or [],
        check_out_time=data.check_out_time,
        current_user=current_user,
    )


@router.get(
    "/events/{event_id}/attendance",
    response_model=AttendanceListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_event_attendance(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> AttendanceListResponse:
    """List attendance roster and status for an event."""
    return await attendance_service.list_event_attendance(
        db=db,
        event_id=event_id,
        status=status_filter,
        page=page,
        page_size=page_size,
        current_user=current_user,
    )


@router.post(
    "/attendance/{record_id}/correct",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_csrf)],
)
async def correct_attendance(
    record_id: uuid.UUID,
    data: AttendanceCorrectionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> AttendanceRecordResponse:
    """Apply an auditable administrative attendance correction with mandatory reason."""
    return await attendance_service.correct_attendance(
        db=db,
        record_id=record_id,
        data=data,
        current_user=current_user,
    )


@router.post(
    "/events/{event_id}/attendance/bulk",
    response_model=BulkAttendanceResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_csrf)],
)
async def bulk_attendance(
    event_id: uuid.UUID,
    data: BulkAttendanceRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> BulkAttendanceResponse:
    """Execute bulk check-in or check-out atomically."""
    return await attendance_service.bulk_attendance(
        db=db,
        event_id=event_id,
        data=data,
        current_user=current_user,
    )


@router.get(
    "/attendance/me",
    response_model=AttendanceListResponse,
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/volunteers/me/attendance",
    response_model=AttendanceListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_attendance(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> AttendanceListResponse:
    """Retrieve authenticated volunteer's own attendance history."""
    return await attendance_service.list_volunteer_attendance(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )
