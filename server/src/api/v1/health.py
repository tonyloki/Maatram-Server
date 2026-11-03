"""Health check and readiness endpoints."""

import time
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.logging import logger
from src.schemas.health import DatabaseHealth, HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System and Database Health Check",
    description="Inspect application uptime and live database connectivity with query latency measurement.",
)
async def check_health(db: Annotated[AsyncSession, Depends(get_db)]) -> HealthResponse:
    """Execute live query against database to assess connectivity and roundtrip latency."""
    db_connected = False
    dialect_name = "unknown"
    latency_ms = 0.0
    db_error = None

    try:
        bind = db.get_bind()
        dialect_name = bind.dialect.name if bind else "unknown"

        start_time = time.perf_counter()
        result = await db.execute(text("SELECT 1"))
        _ = result.scalar()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        db_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_error = str(e)

    overall_status: Literal["healthy", "degraded", "unhealthy"] = (
        "healthy" if db_connected else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=DatabaseHealth(
            connected=db_connected,
            dialect=dialect_name,
            latency_ms=latency_ms,
            error=db_error,
        ),
    )
