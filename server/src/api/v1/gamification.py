"""Gamification, Decimal Points & Leaderboards API router."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_role, verify_csrf
from src.models.users import User
from src.schemas.gamification import (
    EventCompletionPreviewResponse,
    EventCompletionResponse,
    GamificationSummaryResponse,
    LeaderboardResponse,
    PointAdjustmentRequest,
    PointLedgerResponse,
    PointTransactionResponse,
    VolunteerAchievementsListResponse,
)
from src.services.gamification_service import gamification_service

router = APIRouter(tags=["Gamification & Leaderboards"])


# ---------------------------------------------------------------------------
# Event Completion & Scoring Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/events/{event_id}/completion-preview",
    response_model=EventCompletionPreviewResponse,
    status_code=status.HTTP_200_OK,
)
async def get_event_completion_preview(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventCompletionPreviewResponse:
    """Generate dry-run completion preview with decimal points, warnings, and LinkedIn copy."""
    return await gamification_service.get_completion_preview(
        db=db,
        event_id=event_id,
        current_user=current_user,
    )


@router.post(
    "/events/{event_id}/complete-and-award",
    response_model=EventCompletionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_csrf)],
)
@router.post(
    "/events/{event_id}/complete",
    response_model=EventCompletionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_csrf)],
)
async def complete_and_award_event(
    event_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("ADMIN", "SUPER_ADMIN"))],
) -> EventCompletionResponse:
    """Atomic event completion finalization with row lock, exactly-once ledger insertion, and outbox jobs."""
    return await gamification_service.complete_and_award_event(
        db=db,
        event_id=event_id,
        current_user=current_user,
    )


# ---------------------------------------------------------------------------
# Volunteer Gamification & Ledger Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/gamification/summary",
    response_model=GamificationSummaryResponse,
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/gamification/summary/me",
    response_model=GamificationSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_gamification_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    cycle_year: Annotated[int | None, Query(description="Filter by cycle year")] = None,
) -> GamificationSummaryResponse:
    """Retrieve personal gamification metrics (points, verified hours, rank, badges)."""
    return await gamification_service.get_my_summary(
        db=db,
        current_user=current_user,
        cycle_year=cycle_year,
    )


@router.get(
    "/gamification/ledger",
    response_model=PointLedgerResponse,
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/gamification/ledger/me",
    response_model=PointLedgerResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_point_ledger(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    cycle_year: Annotated[int | None, Query(description="Filter by cycle year")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> PointLedgerResponse:
    """Fetch itemized append-only point transactions for the authenticated volunteer."""
    return await gamification_service.get_my_ledger(
        db=db,
        current_user=current_user,
        cycle_year=cycle_year,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/gamification/adjust",
    response_model=PointTransactionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_csrf)],
)
async def adjust_points(
    data: PointAdjustmentRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("SUPER_ADMIN"))],
) -> PointTransactionResponse:
    """Execute audited Super Admin point adjustments via compensating ledger entries."""
    return await gamification_service.adjust_points(
        db=db,
        data=data,
        current_user=current_user,
    )


# ---------------------------------------------------------------------------
# Multi-Tier Leaderboard Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/leaderboards",
    response_model=LeaderboardResponse,
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/gamification/leaderboard",
    response_model=LeaderboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_leaderboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    category: Annotated[str | None, Query(description="ALL, STUDENT, ALUMNI, CORPORATE")] = None,
    cycle_year: Annotated[int | None, Query(description="Calendar cycle year")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> LeaderboardResponse:
    """Fetch multi-tier leaderboard rankings respecting volunteer affirmative consent."""
    return await gamification_service.get_leaderboard(
        db=db,
        category=category,
        cycle_year=cycle_year,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/gamification/leaderboard/overall",
    response_model=LeaderboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_overall_leaderboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    cycle_year: Annotated[int | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> LeaderboardResponse:
    """Overall leaderboard rankings across all volunteer categories."""
    return await gamification_service.get_leaderboard(
        db=db, category="ALL", cycle_year=cycle_year, page=page, page_size=page_size
    )


@router.get(
    "/gamification/leaderboard/student",
    response_model=LeaderboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_leaderboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    cycle_year: Annotated[int | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> LeaderboardResponse:
    """Student tier leaderboard rankings."""
    return await gamification_service.get_leaderboard(
        db=db, category="STUDENT", cycle_year=cycle_year, page=page, page_size=page_size
    )


@router.get(
    "/gamification/leaderboard/alumni",
    response_model=LeaderboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_alumni_leaderboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    cycle_year: Annotated[int | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> LeaderboardResponse:
    """Alumni tier leaderboard rankings."""
    return await gamification_service.get_leaderboard(
        db=db, category="ALUMNI", cycle_year=cycle_year, page=page, page_size=page_size
    )


@router.get(
    "/gamification/leaderboard/corporate",
    response_model=LeaderboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_corporate_leaderboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    cycle_year: Annotated[int | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> LeaderboardResponse:
    """Corporate panelist tier leaderboard rankings."""
    return await gamification_service.get_leaderboard(
        db=db, category="CORPORATE", cycle_year=cycle_year, page=page, page_size=page_size
    )


# ---------------------------------------------------------------------------
# Achievements Catalog Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/achievements",
    response_model=VolunteerAchievementsListResponse,
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/gamification/achievements/me",
    response_model=VolunteerAchievementsListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_achievements(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VolunteerAchievementsListResponse:
    """List all available badges and earned achievements for authenticated volunteer."""
    return await gamification_service.get_my_achievements(
        db=db,
        current_user=current_user,
    )
