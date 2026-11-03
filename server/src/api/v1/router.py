"""API v1 master router aggregator."""

from fastapi import APIRouter

from src.api.v1 import (
    admin,
    applications,
    attendance,
    auth,
    consent,
    events,
    gamification,
    health,
    media,
    notifications,
    registrations,
    reports,
    users,
    volunteers,
)

api_v1_router = APIRouter()

# Include Phase 1-12 routes
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(volunteers.router)
api_v1_router.include_router(applications.router)
api_v1_router.include_router(consent.router)
api_v1_router.include_router(events.router)
api_v1_router.include_router(registrations.router)
api_v1_router.include_router(attendance.router)
api_v1_router.include_router(gamification.router)
api_v1_router.include_router(notifications.router)
api_v1_router.include_router(media.router)
api_v1_router.include_router(reports.router)
api_v1_router.include_router(admin.router)
