# PHASE 04 — Volunteer Profiles & Category Management

## 1. Objective
Build polymorphic volunteer profile management supporting Student, Alumni, and Corporate Panelist classifications with category-specific attribute validation, self-service updates, minor parental consent governance, and administrative directory queries.

## 2. Scope
- Base volunteer profile creation and retrieval (`volunteer_profiles`).
- Category-specific schemas and models (`student_profiles`, `alumni_profiles`, `corporate_profiles`).
- Minor safeguarding: Strict separation between applicant submission (`parental_consent_submitted`, guardian name/relationship/contact/document) and administrative verification (`parental_consent_status`). If age < 18, submission evidence is mandatory and status defaults to `PENDING_VERIFICATION`. Minimum eligibility age is governed by configurable application policy `MINIMUM_VOLUNTEER_AGE` [POLICY: PENDING_APPROVAL].
- Repository layer for polymorphic volunteer lookups (`repositories/volunteer_repo.py`).
- Service layer enforcing category-specific invariants (`services/volunteer_service.py`).
- Volunteer profile endpoints (`api/v1/volunteers.py`).
- Administrative volunteer search, filtering, and pagination.

## 3. Dependencies
- Phase 3 completed.

## 4. Implementation Tasks
1. Define Pydantic 2 request and response schemas in `schemas/volunteers.py`:
   - Base volunteer schema (name, mobile, age, gender, bio, guardian details, parental consent submission and verification status).
   - Student schema (college, degree, department, batch, current year, Maatram reg number).
   - Alumni schema (org, role, exp, location, skills, college, batch, graduation year).
   - Corporate panelist schema (org, designation, exp, location, skills).
2. Implement `VolunteerRepository` handling polymorphic joins across category tables.
3. Implement `VolunteerService` validating category requirements and uniqueness constraints.
4. Build `GET /api/v1/volunteers/me` and `PATCH /api/v1/volunteers/me` with object-level ownership checks (applicants/volunteers cannot modify `parental_consent_status`).
5. Build `GET /api/v1/volunteers` for Admins with filtering by category, status, college, and employer.

## 5. Database Changes
Operates on `volunteer_profiles`, `student_profiles`, `alumni_profiles`, and `corporate_profiles`.

## 6. APIs
- `GET /api/v1/volunteers/me`
- `PATCH /api/v1/volunteers/me`
- `GET /api/v1/volunteers/{id}`
- `GET /api/v1/volunteers` (Admin list/search/filter)

## 7. Security Requirements
- Object-level authorization: Volunteers can only read or update their own profile (`volunteer.user_id == current_user.id`).
- Admins can query any profile; sensitive credentials (`password_hash`) must never be serialized.
- Mobile numbers validated to international E.164 standard.
- Minor verification: If age < 18, verify `parental_consent_submitted = True` with complete guardian details; self-asserted verified status is rejected.

## 8. Test Requirements
- Unit tests for category-specific Pydantic validation schemas.
- Integration tests for profile creation and polymorphic joins across all 3 categories.
- Security tests verifying cross-user profile modification attempts return `403 Forbidden`.
- Minor applicant tests: verify rejection if age < 18 and guardian submission details are missing; verify applicants cannot set `parental_consent_status = VERIFIED` via self-service PATCH.

## 9. Deliverables
- Volunteer schemas, repository, service, and API routers.
- Test suite validating polymorphic profile persistence.

## 10. Acceptance Criteria
- Volunteers in all 3 categories can inspect and update their respective details.
- Admin search endpoint correctly filters volunteers by category and status with pagination.
- Zero data leakage of sensitive user authentication records.

## 11. Definition of Done (DoD)
All volunteer profile operations tested, passing type checks, and ready for application review workflows in Phase 5.
