# PHASE 07 — Event Registration & Volunteer Selection

## 1. Objective
Implement volunteer event registration, concurrency-safe capacity protection, waitlisting, registration withdrawal, and administrative volunteer selection workflows.

## 2. Scope
- Volunteer self-service event registration (`SUBSCRIBED` or `WAITLISTED`).
- Concurrency-safe capacity evaluation via PostgreSQL pessimistic row locks.
- Overlapping event registration detection and prevention.
- Registration withdrawal prior to cutoff deadline (`WITHDRAWN`).
- Administrative candidate review and selection (`SELECTED`, `NOT_SELECTED`).
- Registration state audit logging in `registration_history`.

## 3. Dependencies
- Phase 6 completed.

## 4. Implementation Tasks
1. Implement Pydantic 2 schemas in `schemas/registrations.py`.
2. Implement `RegistrationRepository` with pessimistic row locking (`SELECT FOR UPDATE`) on events and capacity counts.
3. Implement `RegistrationService`:
   - `register_for_event`: Verify volunteer is `APPROVED`, verify event is `PUBLISHED`, check for schedule conflicts, evaluate capacity; assign `SUBSCRIBED` if under capacity or `WAITLISTED` if full.
   - `withdraw_registration`: Verify withdrawal cutoff (e.g., 24 hours prior to event); update status to `WITHDRAWN`.
   - `select_volunteers`: Admin endpoint to transition subscribed/waitlisted volunteers to `SELECTED`.
4. Implement API routers in `api/v1/registrations.py` and event-nested routes in `api/v1/events.py`.

## 5. Database Changes
Operates on `event_registrations` and `registration_history`.

## 6. APIs
- `POST /api/v1/events/{id}/register`
- `POST /api/v1/events/{id}/withdraw`
- `GET /api/v1/events/{id}/registrations` (Admin list)
- `POST /api/v1/events/{id}/registrations/{reg_id}/select`
- `GET /api/v1/volunteers/me/registrations` (Volunteer history)

## 7. Security Requirements
- Only `APPROVED` volunteers can register for events.
- Volunteers cannot register for events where `NOW() > registration_deadline`.
- Unique constraint (`event_id`, `volunteer_profile_id`) prevents duplicate registrations.

## 8. Test Requirements
- Concurrency test simulating multiple simultaneous registrations against limited capacity.
- Schedule conflict test ensuring a volunteer cannot register for overlapping events.
- Withdrawal deadline test ensuring late withdrawals are rejected.

## 9. Deliverables
- Registration service, repository, routers, and test suite.

## 10. Acceptance Criteria
- Capacity cannot be breached under concurrent load.
- Duplicate and overlapping registrations are rejected cleanly.
- State transitions create audit logs in `registration_history`.

## 11. Definition of Done (DoD)
Registration and selection flows fully verified, tested, and ready for attendance management in Phase 8.

