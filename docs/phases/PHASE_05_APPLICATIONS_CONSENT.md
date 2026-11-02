# PHASE 05 — Applications, Approvals & Consent Governance

## 1. Objective
Implement the 6-stage volunteer onboarding registration flow, administrative application review and approval/rejection workflows, and an auditable, fine-grained affirmative consent management system.

## 2. Scope
- Multi-stage onboarding registration (`POST /api/v1/auth/register`).
- Volunteer application persistence (`volunteer_applications`).
- Administrative application listing, inspection, approval, and rejection with mandatory reasoning.
- Audit history of reviews (`application_reviews`).
- Granular affirmative consent records across 6 privacy dimensions (`consent_records`).
- Immutable differential consent audit logging (`consent_history`).

## 3. Dependencies
- Phase 4 completed.

## 4. Implementation Tasks
1. Implement full registration transaction in `services/auth_service.py` and `services/application_service.py`:
   - Create user identity with `status = 'UNVERIFIED'`.
   - Create base volunteer profile and polymorphic category profile.
   - Initialize affirmative consent record.
   - Create `volunteer_applications` record with `status = 'PENDING'`.
   - Generate email verification token and enqueue verification email job.
2. Build `ApplicationService` handling Admin reviews and Minor Parental Consent Verification:
   - `verify_parental_consent`: For applicants under 18, Admin/Super Admin reviews documentary evidence and sets `parental_consent_status` to `VERIFIED` or `REJECTED`, recording `parental_consent_verified_by_id`, `parental_consent_verified_at`, and verification notes; writes immutable record to `audit_logs`.
   - `approve_application`: If applicant is under 18 and `parental_consent_status != 'VERIFIED'`, block approval with `400 Bad Request`. Otherwise, set status to `APPROVED`, record reviewer, and enqueue welcome email job.
   - `reject_application`: Require non-empty reason, set status to `REJECTED`, enqueue rejection email job.
3. Build `ConsentService`:
   - Self-service consent retrieval and update (`GET /api/v1/consent/me`, `PUT /api/v1/consent/me`).
   - Differential change detection; append changes to `consent_history` with actor, IP, timestamp.
4. Implement API routers in `api/v1/applications.py` and `api/v1/consent.py`.

## 5. Database Changes
Operates on `volunteer_applications`, `application_reviews`, `consent_records`, `consent_history`, `volunteer_profiles`, and `audit_logs`.

## 6. APIs
- `POST /api/v1/auth/register`
- `GET /api/v1/applications`
- `GET /api/v1/applications/{id}`
- `POST /api/v1/applications/{id}/verify-parental-consent`
- `POST /api/v1/applications/{id}/approve`
- `POST /api/v1/applications/{id}/reject`
- `GET /api/v1/consent/me`
- `PUT /api/v1/consent/me`

## 7. Security Requirements
- Administrative review and parental consent verification endpoints restricted strictly to `ADMIN` and `SUPER_ADMIN`.
- Applicant self-attestation cannot set `parental_consent_status = VERIFIED`; minor approvals without admin-verified consent are blocked.
- Rejection without reason rejected with `422 Unprocessable Entity`.
- Consent records cannot be altered on behalf of another volunteer.

## 8. Test Requirements
- End-to-end integration test of 6-stage registration submission.
- Parental consent verification workflow tests: verify minor applicant cannot be approved until `POST /api/v1/applications/{id}/verify-parental-consent` succeeds; verify audit log creation.
- Admin approval and rejection workflow tests, verifying review logs and user status updates.
- Consent modification test verifying differential records written to `consent_history`.

## 9. Deliverables
- Application and consent services, schemas, and routers.
- Integration tests covering the entire onboarding, minor consent verification, and review lifecycle.

## 10. Acceptance Criteria
- Full registration creates user, profile, category, consent, and application records within a single transaction.
- Minor onboarding cannot transition to `APPROVED` without explicit prior Admin parental consent verification.
- Admin approval successfully transitions user and application status to `APPROVED`.
- Updating a consent setting creates a valid audit record in `consent_history`.

## 11. Definition of Done (DoD)
All onboarding and review workflows verified with automated tests; zero database inconsistencies on partial failures.

