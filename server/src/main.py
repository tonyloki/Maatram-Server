"""Maatram Volunteering & Gamification Portal — FastAPI Master Application."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import api_v1_router
from src.core.config import settings
from src.core.database import AsyncSessionLocal, close_db_connections
from src.core.exceptions import (
    DomainException,
    domain_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from src.core.logging import logger
from src.core.timing_middleware import RequestTimingMiddleware
from src.workers.outbox_worker import outbox_worker


async def _run_outbox_worker_loop() -> None:
    """Background processor for transactional outbox communications."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await outbox_worker.process_batch(db, batch_size=10)
                await outbox_worker.recover_expired_leases(db)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"Background outbox processor notice: {e}")
        await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan context managing startup initialization and graceful shutdown."""
    logger.info(f"Starting {settings.PROJECT_NAME} [Environment: {settings.ENVIRONMENT}]")
    logger.info(f"API documentation accessible at /docs (OpenAPI prefix: {settings.API_V1_STR})")
    worker_task = asyncio.create_task(_run_outbox_worker_loop())
    try:
        yield
    finally:
        logger.info("Initiating graceful shutdown...")
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        await close_db_connections()
        logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Centralized REST API backend for Maatram Volunteering & Gamification Portal.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register Custom Middleware
app.add_middleware(RequestTimingMiddleware)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)

# Mount API Routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root metadata discovery endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_check": f"{settings.API_V1_STR}/health",
    }
