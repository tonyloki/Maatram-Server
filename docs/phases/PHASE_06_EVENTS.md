# PHASE 06 — Event Management Lifecycle

## 1. Objective
Implement the complete administrative event management subsystem supporting all volunteering categories, online/offline modes, temporal validation, state machine transitions, and volunteer discovery.

## 2. Scope
- Event creation, updates, duplication, and cancellation.
- Event categories: School Visit, BGV, Admissions, Mock Interview, Panel Interview, Other.
- Event modes: `ONLINE` (virtual meeting link) and `OFFLINE` (physical venue).
- Event state transitions: `DRAFT`, `PUBLISHED`, `REGISTRATION_CLOSED`, `ONGOING`, `COMPLETED`, `CANCELLED`.
- Event repository (`repositories/event_repo.py`) and service (`services/event_service.py`).
- Public volunteer event discovery with status and category filters.

## 3. Dependencies
- Phase 5 completed.

## 4. Implementation Tasks
1. Implement Pydantic 2 schemas in `schemas/events.py` with temporal validation (`end_time > start_time`, `deadline <= start_time`, capacity > 0).
2. Implement `EventRepository` with queries for public listings (filtering for `status = 'PUBLISHED'`) and admin listings (all statuses).
3. Implement `EventService` governing state machine rules:
   - `publish_event`: Transitions `DRAFT` -> `PUBLISHED`.
   - `close_registrations`: Transitions `PUBLISHED` -> `REGISTRATION_CLOSED`.
   - `cancel_event`: Sets status `CANCELLED`, records cancellation reason, enqueues volunteer notifications.
   - `duplicate_event`: Clones event metadata with new dates into a `DRAFT` state.
4. Implement API routers in `api/v1/events.py`.

## 5. Database Changes
Operates on `events`.

## 6. APIs
- `GET /api/v1/events` (Public / Volunteer discovery)
- `GET /api/v1/events/{id}`
- `POST /api/v1/events` (Admin create)
- `PATCH /api/v1/events/{id}` (Admin update)
- `POST /api/v1/events/{id}/publish` (Admin publish)
- `POST /api/v1/events/{id}/close-registrations` (Admin close)
- `POST /api/v1/events/{id}/cancel` (Admin cancel)
- `POST /api/v1/events/{id}/duplicate` (Admin duplicate)

## 7. Security Requirements
- Event mutation endpoints restricted to `ADMIN` and `SUPER_ADMIN`.
- Volunteers cannot view events in `DRAFT` status.
- Text descriptions sanitized to prevent Stored XSS.

## 8. Test Requirements
- Unit tests for event timing validation rules in Pydantic schemas.
- Integration tests verifying state transitions (`DRAFT` -> `PUBLISHED` -> `CANCELLED`).
- Filter and search tests verifying past vs upcoming event filtering.

## 9. Deliverables
- Event repository, service, schemas, and API routers.
- Comprehensive event lifecycle test suite.

## 10. Acceptance Criteria
- Valid events created and published cleanly.
- Invalid date/time combinations rejected with clear `422` error messages.
- Draft events hidden from non-admin API requests.

## 11. Definition of Done (DoD)
Event management functional, state transitions validated, and ready for volunteer registration workflows in Phase 7.

