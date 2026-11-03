# MASTER_PLAN.md — 15-Phase Master Development Roadmap
**Maatram Volunteering & Gamification Portal**

---

## 1. Project Phase Topology & Dependency Graph

```
Phase 0: Specifications & Blueprint (Sign-off Candidate - Audited)
   |
   v
Phase 1: FastAPI Foundation, Settings & Configurable Policies
   |
   v
Phase 2: Database Models, Triggers & Alembic Baseline Migration (29 Tables)
   |
   v
Phase 3: Authentication, Dual-Token Sessions, SameSite & CSRF
   |
   v
Phase 4: Volunteer Profiles, Minor Safeguards & Category Schemas
   |
   v
Phase 5: Applications, Approvals & Affirmative Consent Governance
   |
   v
Phase 6: Event Management Lifecycle & Concurrency Safeguards
   |
   v
Phase 7: Event Registrations, Capacity Locking & Volunteer Selection
   |
   v
Phase 8: Attendance Tracking, Duration in Minutes & Corrections
   |
   v
Phase 9: Gamification, Decimal Points & Atomic Event Completion
   |
   v
Phase 10: Notification Engine & FCM Push with Selective Invalidation
   |
   v
Phase 11: Resend Outbox with Lease Recovery & Signed Cloudinary Media
   |
   v
Phase 12: Admin Dashboard, Analytics, Dead-Letter Requeue & CSV Exports
   |
   v
Phase 13: Client API Stabilization & Web/Mobile Integration
   |
   v
Phase 14: Security Hardening, Browser Topology Tests & Render Deployment
```

---

## 2. Phase-by-Phase Detailed Specifications

---

### Phase 0: Requirements, Architecture & Engineering Specification
- **Objective**: Establish foundational architecture, complete technical specifications, database schemas, API inventory, and business rules before writing code.
- **Scope**: Comprehensive documentation across all 15 phases, ADRs 001–012, and open policy question analysis.
- **Dependencies**: None.
- **Implementation Tasks**: Repository inspection, system architecture design, database schema modeling (29 tables), API contract definition, business state machine documentation, OWASP security planning, open questions identification, technical audits, and cross-document reconciliation.
- **Database Changes**: Specification of all 29 relational tables, check constraints, foreign keys, trigger protections, and indexes (no physical migrations yet).
- **APIs**: Full specification of `/api/v1` routes and schemas.
- **Security Requirements**: Definition of Argon2id parameters, session rotation model, SameSite cookie evaluation, CSRF protection, RBAC matrix, and OWASP API Top 10 checklist.
- **Test Requirements**: Verification of architectural consistency and absence of contradictory requirements.
- **Deliverables**: `AGENTS.md`, `docs/MASTER_PLAN.md`, `docs/ARCHITECTURE.md`, `docs/DATABASE_DESIGN.md`, `docs/API_CONTRACT.md`, `docs/BUSINESS_RULES.md`, `docs/SECURITY_POLICY.md`, `docs/DECISION_LOG.md`, `docs/OPEN_QUESTIONS.md`, `docs/PROJECT_REQUIREMENTS.md`, `docs/PHASE_TRACKER.md`, `docs/PHASE_0_FINAL_AUDIT_REPORT.md`, `docs/PHASE_0_SIGNOFF_CANDIDATE.md`, `docs/phases/PHASE_00_SPECIFICATION.md` through `PHASE_14_PRODUCTION.md`.
- **Acceptance Criteria**: All 14 criteria in Section 12 satisfied; independent audit feedback resolved; unresolved policies flagged as UNAPPROVED.
- **Definition of Done (DoD)**: Engineering documentation complete, version-controlled, and ready for Phase 1 execution without ambiguities.

---

### Phase 1: Project Initialization, Settings & FastAPI Foundation
- **Objective**: Initialize clean Python 3.13 project structure, dependencies, configurable policy settings (`core/config.py`), logging, exception handling, and deploy a responsive health check endpoint.
- **Scope**: Project scaffolding, `pyproject.toml`, Pydantic Settings (including unapproved policy switches: `LEADERBOARD_CYCLE_TYPE`, `HOURS_ROUNDING_MODE`, `EVENT_QUALIFICATION_MIN_MINUTES`, `MINIMUM_VOLUNTEER_AGE`, `COOKIE_SAMESITE`), CORS middleware, standard error handling, health check endpoint.
- **Dependencies**: Phase 0 completed and approved.
- **Implementation Tasks**: Setup virtual environment, configure `ruff`, create `src/` directory tree, implement `core/config.py`, `core/logging.py`, `core/exceptions.py`, initialize FastAPI app in `src/main.py`.
- **Database Changes**: Setup async database engine factory (`core/database.py`) using `asyncpg`.
- **APIs**: `GET /api/v1/health`.
- **Security Requirements**: Restrict CORS origins via config; hide debug traces in production; securely load `.env`.
- **Test Requirements**: Unit test for configuration loader, health check API test with `pytest-asyncio`.
- **Deliverables**: Working FastAPI application, passing health check test, lint configuration.
- **Acceptance Criteria**: Application boots locally; `/api/v1/health` returns `200 OK` with JSON status; zero lint errors.
- **DoD**: Test suite passes; code adheres to `AGENTS.md`.

---

### Phase 2: Database Engineering & Alembic Migrations
- **Objective**: Implement SQLAlchemy 2.x declarative models, database-level triggers for immutable point ledgers, and execute initial Alembic baseline migration for all 29 tables.
- **Scope**: Base model classes, model definitions in `src/models/`, Alembic setup with `env.py`, `NUMERIC(8, 2)` decimal point fields, trigger `trg_prevent_point_ledger_mutation`, `communication_jobs` lease tracking columns, baseline migration script.
- **Dependencies**: Phase 1 completed.
- **Implementation Tasks**: Configure Alembic for async migrations; create models for Identity, Profiles, Applications, Privacy, Events, Registrations, Attendance, Gamification, Notifications, Communications, Media, Admin, Reports; implement engine-level trigger preventing updates/deletes on `point_transactions`; verify PostgreSQL constraints.
- **Database Changes**: Initial migration creating all 29 tables with UUID PKs, FKs (`ON DELETE RESTRICT` on historical data), indexes, and constraints.
- **APIs**: None.
- **Security Requirements**: Restrict database user privileges; verify foreign keys enforce deletion protections on historical volunteering tables; trigger protects ledger immutability.
- **Test Requirements**: Migration upgrade and downgrade integration test against a test PostgreSQL database; trigger test verifying `UPDATE` and `DELETE` on `point_transactions` fail.
- **Deliverables**: SQLAlchemy model classes, Alembic migration scripts, migration verification tests.
- **Acceptance Criteria**: `alembic upgrade head` succeeds cleanly on clean DB; `alembic downgrade base` succeeds cleanly; ledger trigger active.
- **DoD**: All tables, relationships, and constraints match `docs/DATABASE_DESIGN.md`.

---

### Phase 3: Authentication, Dual-Token Sessions, SameSite & CSRF
- **Objective**: Implement secure FastAPI-managed authentication with Argon2id, JWT access tokens, rotating refresh tokens in `user_sessions`, session revocation, topology-aware SameSite cookie handlers, Double-Submit CSRF protection, and RBAC dependencies.
- **Scope**: Password hashing, token generation/validation, login/logout, session tracking, token reuse detection, email verification token logic, password reset OTP, cookie vs bearer handlers, anti-CSRF double-submit validation.
- **Dependencies**: Phase 2 completed.
- **Implementation Tasks**: Implement `core/security.py`, `services/auth_service.py`, `repositories/user_repo.py`, `api/v1/auth.py`, `api/deps.py` (auth, CSRF, and RBAC dependencies).
- **Database Changes**: Operates on `users`, `user_sessions`, `email_verifications`, `password_reset_tokens`.
- **APIs**: `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `POST /api/v1/auth/verify-email`, `POST /api/v1/auth/password-reset/request`, `POST /api/v1/auth/password-reset/confirm`, `GET /api/v1/users/me`.
- **Security Requirements**: Argon2id hashing; HttpOnly SameSite cookie configuration (Lax for apex domain `.maatram.org`, None for cross-SaaS staging); brute-force login rate limiting; refresh token rotation and reuse detection; CSRF token validation on cookie requests.
- **Test Requirements**: Unit tests for password hasher; integration tests for login, token refresh, token rotation, reuse detection session invalidation, and CSRF rejection; browser test plan across topologies.
- **Deliverables**: Auth service, API endpoints, dependency guards, test suite.
- **Acceptance Criteria**: Dual-token flow functional; invalid/expired tokens rejected; session revocation invalidates tokens; reuse detection revokes lineage; CSRF guarded.
- **DoD**: Auth endpoints documented in Swagger; 100% test pass rate on auth flows.

---

### Phase 4: Volunteer Profiles, Minor Safeguards & Category Schemas
- **Objective**: Build polymorphic volunteer profile management supporting Student, Alumni, and Corporate Panelist categories with minor parental consent governance.
- **Scope**: Profile schemas, category-specific tables, profile CRUD, avatar associations, minor parental consent validation (`parental_consent_verified` required if age < 18).
- **Dependencies**: Phase 3 completed.
- **Implementation Tasks**: Implement `services/volunteer_service.py`, `repositories/volunteer_repo.py`, `schemas/volunteers.py`, `api/v1/volunteers.py`.
- **Database Changes**: Operates on `volunteer_profiles`, `student_profiles`, `alumni_profiles`, `corporate_profiles`.
- **APIs**: `GET /api/v1/volunteers/me`, `PATCH /api/v1/volunteers/me`, `GET /api/v1/volunteers/{id}`, `GET /api/v1/volunteers` (Admin search/filter).
- **Security Requirements**: Object-level authorization (volunteers can only edit own profile); Pydantic schema validation for category fields; minor parental consent checks.
- **Test Requirements**: Tests for student/alumni/corporate profile creation, partial updates, admin listing filters, and minor applicant validation.
- **Deliverables**: Volunteer profile services, schemas, endpoints, tests.
- **Acceptance Criteria**: All 3 volunteer categories persist correctly; unauthorized profile access attempts return `403 Forbidden`.
- **DoD**: Fully typed schemas; all profile operations covered by integration tests.

---

### Phase 5: Applications, Approvals & Affirmative Consent Governance
- **Objective**: Implement multi-stage registration submission, administrative review workflows, and fine-grained affirmative consent audit logs.
- **Scope**: Onboarding submission, application review history, affirmative consent toggles (default `False`), and immutable consent history tracking.
- **Dependencies**: Phase 4 completed.
- **Implementation Tasks**: Implement `services/consent_service.py`, `services/application_service.py`, `api/v1/applications.py`, `api/v1/consent.py`.
- **Database Changes**: Operates on `volunteer_applications`, `application_reviews`, `consent_records`, `consent_history`.
- **APIs**: `POST /api/v1/auth/register`, `GET /api/v1/applications`, `GET /api/v1/applications/{id}`, `POST /api/v1/applications/{id}/approve`, `POST /api/v1/applications/{id}/reject`, `GET /api/v1/consent/me`, `PUT /api/v1/consent/me`.
- **Security Requirements**: RBAC for review endpoints (Admin only); mandatory rejection reasons; consent history immutability.
- **Test Requirements**: Integration tests for registration flow, admin approval/rejection, and consent change auditing.
- **Deliverables**: Application review system, consent tracking module, automated tests.
- **Acceptance Criteria**: Rejection requires reason; approved application transitions user status to `APPROVED`; consent edits append to `consent_history`.
- **DoD**: Review history fully traceable; zero unverified access to approved-only routes.

---

### Phase 6: Event Management Lifecycle & Concurrency Safeguards
- **Objective**: Deliver complete administrative event management across all categories and lifecycle states with schedule validation.
- **Scope**: Event creation, updates, publishing, cancellation, scheduling validation, and public discovery.
- **Dependencies**: Phase 5 completed.
- **Implementation Tasks**: Implement `services/event_service.py`, `repositories/event_repo.py`, `schemas/events.py`, `api/v1/events.py`.
- **Database Changes**: Operates on `events`.
- **APIs**: `GET /api/v1/events`, `GET /api/v1/events/{id}`, `POST /api/v1/events`, `PATCH /api/v1/events/{id}`, `POST /api/v1/events/{id}/publish`, `POST /api/v1/events/{id}/cancel`.
- **Security Requirements**: Admin/Super Admin only for mutation endpoints; public volunteers see only `PUBLISHED` events; input sanitization on rich text descriptions.
- **Test Requirements**: State transition validation tests (`DRAFT` -> `PUBLISHED` -> `CANCELLED`); timing validation tests (`end_time > start_time`).
- **Deliverables**: Event service, repository, routers, validation schemas, tests.
- **Acceptance Criteria**: Event lifecycle transitions validated; invalid date ranges rejected; draft events hidden from volunteers.
- **DoD**: Event CRUD functional and documented in OpenAPI.

---

### Phase 7: Event Registrations, Capacity Locking & Volunteer Selection
- **Objective**: Manage volunteer registrations, concurrency-safe capacity protection, waitlisting, and administrative selection.
- **Scope**: Volunteer self-service registration/withdrawal, admin selection/waitlisting, capacity concurrency locking (`SELECT FOR UPDATE`).
- **Dependencies**: Phase 6 completed.
- **Implementation Tasks**: Implement `services/registration_service.py`, `repositories/registration_repo.py`, `api/v1/registrations.py`.
- **Database Changes**: Operates on `event_registrations`, `registration_history`.
- **APIs**: `POST /api/v1/events/{id}/register`, `POST /api/v1/events/{id}/withdraw`, `GET /api/v1/events/{id}/registrations`, `POST /api/v1/events/{id}/registrations/{reg_id}/select`.
- **Security Requirements**: Prevent duplicate registrations; prevent registration if event deadline passed or volunteer status is not `APPROVED`.
- **Test Requirements**: Concurrency test for capacity limit; overlapping event registration rejection test; withdrawal tests.
- **Deliverables**: Registration engine, selection workflows, integration tests.
- **Acceptance Criteria**: Concurrent registrations cannot exceed event capacity; withdrawals update status to `WITHDRAWN`.
- **DoD**: All registration transitions audit-logged in `registration_history`.

---

### Phase 8: Attendance Tracking & Hours Management
- **Objective**: Real-time volunteer check-in, check-out, duration calculation in minutes, and auditable administrative corrections.
- **Scope**: Individual and bulk check-in/out, missing checkout detection, duration in minutes, multi-tier attendance corrections audit.
- **Dependencies**: Phase 7 completed.
- **Implementation Tasks**: Implement `services/attendance_service.py`, `repositories/attendance_repo.py`, `api/v1/attendance.py`.
- **Database Changes**: Operates on `attendance_records`, `attendance_corrections`.
- **APIs**: `POST /api/v1/events/{id}/attendance/check-in`, `POST /api/v1/events/{id}/attendance/check-out`, `GET /api/v1/events/{id}/attendance`, `POST /api/v1/attendance/{id}/correct`.
- **Security Requirements**: Admin/Super Admin only; check-out requires existing check-in; mandatory correction reasons; corrections $> 2\text{ hours}$ require Super Admin approval.
- **Test Requirements**: Duplicate check-in rejection test; duration calculation test; attendance correction auditing test.
- **Deliverables**: Attendance management service, APIs, tests.
- **Acceptance Criteria**: Check-out calculates duration in minutes; missing checkout flags `INCOMPLETE`; corrections logged.
- **DoD**: Attendance rules match `docs/BUSINESS_RULES.md` exactly.

---

### Phase 9: Gamification, Decimal Points & Atomic Event Completion
- **Objective**: Implement official scoring formula $P = (E \times 10) + (H \times 2)$ with exact decimal precision (`NUMERIC(8, 2)`), trigger-protected append-only point ledgers, compensating transactions for adjustments, atomic event completion preview and finalization, and multi-tier leaderboards.
- **Scope**: Point calculations, decimal ledger persistence, completion preview & finalization, compensating transactions, leaderboards (Global, Student, Alumni, Corporate), anonymity toggles.
- **Dependencies**: Phase 8 completed.
- **Implementation Tasks**: Implement `services/gamification_service.py`, `repositories/gamification_repo.py`, `api/v1/gamification.py`, `api/v1/leaderboards.py`.
- **Database Changes**: Operates on `point_transactions`, `achievement_definitions`, `volunteer_achievements`.
- **APIs**: `GET /api/v1/events/{id}/completion-preview`, `POST /api/v1/events/{id}/complete`, `GET /api/v1/gamification/summary`, `GET /api/v1/gamification/ledger`, `GET /api/v1/leaderboards`.
- **Security Requirements**: Points can only be awarded via atomic event completion or audited Super Admin compensating adjustment; unique constraint prevents duplicate event point awards; mandatory `Idempotency-Key` header on completion; engine trigger protects ledger.
- **Test Requirements**: Unit tests for formula calculation with fractional points; integration test for atomic completion transaction and rollback; ledger trigger protection test; compensating transaction test.
- **Deliverables**: Gamification engine, completion workflow, leaderboard APIs, tests.
- **Acceptance Criteria**: Points calculated accurately with exact decimal precision; event completion is atomic and idempotent; ledger cannot be modified by UPDATE/DELETE; anonymous volunteers displayed correctly.
- **DoD**: All gamification invariants verified.

---

### Phase 10: Notification Engine & Firebase FCM Push Integration
- **Objective**: In-app notifications inbox and Firebase Cloud Messaging (FCM) push notification integration for Flutter clients with selective token invalidation.
- **Scope**: In-app notification creation/retrieval, device token registration, FCM client wrapper, push dispatch, selective token deactivation (deactivate only on confirmed token errors; never on payload formatting errors).
- **Dependencies**: Phase 9 completed.
- **Implementation Tasks**: Implement `integrations/fcm_client.py`, `services/notification_service.py`, `api/v1/notifications.py`.
- **Database Changes**: Operates on `notifications`, `device_tokens`.
- **APIs**: `GET /api/v1/notifications`, `POST /api/v1/notifications/{id}/read`, `POST /api/v1/notifications/devices`.
- **Security Requirements**: Volunteers can only read/dismiss their own notifications; device token validation.
- **Test Requirements**: In-app notification read/unread filtering tests; mock FCM push notification tests; selective token deactivation vs payload error tests.
- **Deliverables**: Notification service, FCM integration client, routers, tests.
- **Acceptance Criteria**: Mobile tokens registered and updated; notifications deliverable to in-app inbox and FCM; stale tokens automatically deactivated without false-positive deactivations.
- **DoD**: FCM integration clean with mock fallback for local testing without Firebase credentials.

---

### Phase 11: Resend Outbox with Lease Recovery & Signed Cloudinary Media
- **Objective**: Implement transactional outbox email dispatcher with Resend (including worker lease tracking, crash recovery sweeper, provider idempotency, and dead-letter handling) and secure signed Cloudinary media upload workflows.
- **Scope**: Outbox background worker (`FOR UPDATE SKIP LOCKED`), worker lease recovery (5-minute timeout), provider idempotency (`Idempotency-Key` to Resend), Resend API client, email templates, dead-letter state, Cloudinary signature generator and media registry.
- **Dependencies**: Phase 10 completed.
- **Implementation Tasks**: Implement `integrations/resend_client.py`, `integrations/cloudinary_client.py`, `workers/outbox_worker.py`, `services/media_service.py`, `api/v1/media.py`.
- **Database Changes**: Operates on `communication_jobs`, `communication_logs`, `media_assets`, `event_photos`.
- **APIs**: `POST /api/v1/media/sign-upload`, `POST /api/v1/media/register`, `GET /api/v1/events/{id}/photos`.
- **Security Requirements**: Cloudinary API secret never exposed; upload parameters enforce MIME type, size, and folder boundaries; Resend API key protected; email delivery errors never rollback committed business data.
- **Test Requirements**: Outbox worker polling and retry test; worker lease crash recovery sweeper test; Resend idempotency deduplication test; Cloudinary HMAC signature generation test.
- **Deliverables**: Transactional outbox worker with lease recovery, Resend client, Cloudinary signer, media routers, tests.
- **Acceptance Criteria**: Outbox worker dispatches emails and handles retries; failed jobs transition to `DEAD_LETTER` after retries without duplicate sends; signed Cloudinary upload params validated.
- **DoD**: End-to-end media upload and email delivery workflows verified.

---

### Phase 12: Admin Dashboard, Analytics, Dead-Letter Requeue & CSV Exports
- **Objective**: Real-time SQL-driven administrative analytics, volunteer metrics, contribution tracking, asynchronous CSV/Excel report exports, and outbox dead-letter queue management.
- **Scope**: Volunteer demographics, college/employer metrics, inactive volunteer detection, hours aggregations, CSV/Excel export workers, dead-letter inspection and requeue.
- **Dependencies**: Phase 11 completed.
- **Implementation Tasks**: Implement `services/report_service.py`, `repositories/report_repo.py`, `api/v1/reports.py`, `api/v1/admin.py`.
- **Database Changes**: Operates on `report_exports`, `audit_logs`, `communication_jobs`.
- **APIs**: `GET /api/v1/reports/volunteer-stats`, `GET /api/v1/reports/contribution-hours`, `POST /api/v1/reports/export`, `GET /api/v1/admin/audit-logs`, `GET /api/v1/admin/outbox/dead-letter`, `POST /api/v1/admin/outbox/{job_id}/requeue`.
- **Security Requirements**: Admin/Super Admin only; export parameters validated against SQL injection; rate limiting on export endpoints; dead-letter requeue restricted to Super Admin.
- **Test Requirements**: Metric aggregation query tests against test datasets; CSV export generation test; dead-letter requeue test.
- **Deliverables**: Reporting engine, export generator, dead-letter management tools, admin APIs, tests.
- **Acceptance Criteria**: All statistics computed from live database records (no mock/static data); export generates downloadable file; dead-letter jobs can be inspected and requeued.
- **DoD**: Full administrative suite verified and documented.

---

### Phase 13: Client API Stabilization & Web/Flutter Integration
- **Objective**: Monorepo client integration, OpenAPI contract freeze, client SDK/type generation support, CORS optimization, and unified error mapping for Next.js (`web/`) and Flutter (`mobile/`) applications.
- **Repository Context**: Backend isolated to `server/`; application directories `web/` and `mobile/` ready for client development.
- **Scope**: OpenAPI specification export, end-to-end integration test suite, API documentation polishing, integration guide for frontend teams.
- **Dependencies**: Phase 12 completed.
- **Implementation Tasks**: Export `openapi.json`, verify all schemas match frontend requirements, implement cross-platform integration tests covering complete volunteer journey (Register -> Verify -> Approve -> Register Event -> Check-in -> Check-out -> Complete Event -> Verify Points & Leaderboard).
- **Database Changes**: None.
- **APIs**: All `/api/v1/*` endpoints stabilized.
- **Security Requirements**: Final CORS auditing; cookie domain configuration for production vs local dev.
- **Test Requirements**: Full-lifecycle end-to-end integration test suite.
- **Deliverables**: Clean `openapi.json`, end-to-end integration test suite, Frontend Integration Guide (`docs/FRONTEND_INTEGRATION.md`).
- **Acceptance Criteria**: E2E integration test passes completely from registration through leaderboard ranking; zero schema discrepancies.
- **DoD**: Both web and mobile frontend teams can integrate seamlessly.

---

### Phase 14: Security Hardening, Browser Topology Tests & Render Deployment
- **Objective**: Security audits, browser integration testing across cookie topologies, load testing with Locust, containerization, and production deployment on Render with Supabase PostgreSQL.
- **Scope**: Penetration testing, OWASP API compliance check, automated browser integration tests across cookie topologies (SameSite=Lax on apex domain, SameSite=None on staging), Locust load testing, production Dockerfile, Render blueprint, environment secrets audit.
- **Dependencies**: Phase 13 completed.
- **Implementation Tasks**: Create production multi-stage `Dockerfile` and `docker-compose.yml`, configure Render service definitions, execute browser topology tests, execute Locust load test simulating 1,000 concurrent volunteers, verify database connection pooling and query timeouts.
- **Database Changes**: Production migration run on Supabase PostgreSQL with trigger protections.
- **APIs**: All production endpoints verified under load.
- **Security Requirements**: All secrets stored in Render environment variables; HTTPS enforced; HSTS headers; database connections over TLS with certificate verification.
- **Test Requirements**: Browser topology tests; load test achieving $P_{95} < 200\text{ ms}$; OWASP security scanning.
- **Deliverables**: Production Dockerfile, Render deployment config, Load test report, Production operations runbook.
- **Acceptance Criteria**: Zero high/critical security vulnerabilities; sustained throughput under load; successful deployment on Render.
- **DoD**: Production backend live in production, securely configured, monitored, and operational.
