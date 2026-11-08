# SPRINT 3 READINESS AUDIT & ROADMAP INSPECTION (REVISED)
**Maatram Volunteering & Gamification Portal**  
*Document Version: 2.0.0 — Date: November 8, 2026*  
*Target Verification Commit: `8849c05`*

---

## Executive Summary

This revised readiness audit reviews the complete engineering and product roadmap for the **Maatram Volunteering & Gamification Portal**. It cross-examines the 15 canonical phase specifications (`docs/phases/PHASE_00` to `PHASE_14`), the Milestone tracker (`docs/PHASE_TRACKER.md`), and the physical repository state.

This revision reconciles all previously reported technology version discrepancies with the exact installed runtime and lockfile reality, establishes verified baseline commands, audits actual backend schemas and endpoints, and provides an unassailable factual foundation for Sprint 3 planning.

---

## 1. Verified Technology Baseline & Runtime Versions

To eliminate any ambiguity between documentation summaries and installed software, the actual repository manifests, installed `node_modules`, Python virtual environments, and system SDKs were directly inspected via command execution:

| Component | Manifest / Source | Installed Runtime Version | Verification Command Executed |
| :--- | :--- | :--- | :--- |
| **Next.js** | `web/package.json` (`"16.4.4"`) | **`16.4.4`** | `node -e "console.log(require('./web/node_modules/next/package.json').version)"` |
| **Tailwind CSS** | `web/package.json` (`"^4"`) | **`4.3.4`** (v4.3.4) | `node -e "console.log(require('./web/node_modules/tailwindcss/package.json').version)"` |
| **Tailwind Turbopack** | `web/package.json` (`"^4"`) | **`4.3.4`** (`@tailwindcss/turbopack`) | Installed in `web/node_modules/@tailwindcss/turbopack` |
| **React** | `web/package.json` (`"19.3.0"`) | **`19.3.0`** | `node -e "console.log(require('./web/node_modules/react/package.json').version)"` |
| **React DOM** | `web/package.json` (`"19.3.0"`) | **`19.3.0`** | `node -e "console.log(require('./web/node_modules/react-dom/package.json').version)"` |
| **TypeScript** | `web/package.json` (`"^5"`) | **`5.8.2`** | `node -e "console.log(require('./web/node_modules/typescript/package.json').version)"` |
| **Python** | `.venv` | **`3.13.9`** | `.\.venv\Scripts\python.exe -c "import sys; print(sys.version.split()[0])"` |
| **FastAPI** | `server/pyproject.toml` | **`0.162.0`** | `.\.venv\Scripts\python.exe -c "import fastapi; print(fastapi.__version__)"` |
| **SQLAlchemy** | `server/pyproject.toml` | **`2.1.6`** | `.\.venv\Scripts\python.exe -c "import sqlalchemy; print(sqlalchemy.__version__)"` |
| **Pydantic** | `server/pyproject.toml` | **`2.14.2`** | `.\.venv\Scripts\python.exe -c "import pydantic; print(pydantic.__version__)"` |
| **Alembic** | `server/pyproject.toml` | **`1.20.1`** | `.\.venv\Scripts\python.exe -c "import alembic; print(alembic.__version__)"` |
| **Flutter SDK** | System PATH | **`3.44.2`** (channel stable, revision `c9a6c48423`) | `flutter --version` |
| **Dart SDK** | Flutter bundle | **`3.12.2`** (stable, windows_x64) | `dart --version` |

> **Baseline Directive**: The project runs on **Next.js 16.4.4** and **Tailwind CSS v4 (4.3.4)**. Any earlier references to "16.0.1" or "3.4" were stale documentation artifacts. No dependencies shall be upgraded or downgraded during Sprint 3.

---

## 2. Actual Backend Schema & Runtime OpenAPI Inspection

Direct programmatic inspection of the running FastAPI application in `server/src/main.py` yields the following contract metrics:
- **OpenAPI Specification Version**: `3.1.0`
- **Application Title**: `Maatram Volunteering & Gamification Portal`
- **Total Registered Endpoint Paths**: **94 distinct HTTP paths** across 14 route modules (`src/api/v1/*.py`).
- **Total Component Schemas**: **120 Pydantic models** registered in OpenAPI components.

### 2.1 Canonical Field Naming vs Frontend Assumptions
A detailed audit of `server/src/schemas/event.py` and `server/src/models/event.py` confirms:
1. **Capacity Fields**:
   - Backend canonical database column: `capacity_required` (INTEGER).
   - Backend Pydantic schema (`EventResponse`, `EventListItem`, `EventCreateRequest`) provides `capacity_required` as primary, and `volunteer_capacity` as a dual-field alias for client compatibility.
2. **Meeting URL Fields**:
   - Backend canonical database column and Pydantic field: `online_meeting_url` (VARCHAR(500), nullable).
   - Frontend TypeScript currently uses `meeting_url` in certain components.
   - **Resolution Policy**: Backend canonical field names (`online_meeting_url`, `capacity_required`) will remain authoritative as defined in Phase 06. The frontend types must align with the backend canonical contract, while the backend maintains backward-compatible aliases during client transition.

### 2.2 Pagination Parameter Audit Across All Endpoints
An exhaustive audit of all paginated endpoints across `server/src/api/v1/*.py` revealed a naming discrepancy:
- **Endpoints using `limit`**: `admin.py` (9 endpoints), `events.py` (2 endpoints), `notifications.py` (1 endpoint), `registrations.py` (1 endpoint), `reports.py` (1 endpoint), `volunteers.py` (1 endpoint). All enforce `limit: int = Query(default=20, ge=1, le=100)`.
- **Endpoints using `page_size`**: `applications.py` (1 endpoint), `attendance.py` (2 endpoints), `gamification.py` (6 endpoints). These enforce `page_size: int = Query(default=20/50, ge=1, le=100)`.
- **Finding**: While all endpoints enforce an upper bound of 100, the parameter name varies between `limit` and `page_size`. A unified pagination dependency supporting `limit` as canonical and `page_size` as an alias is required for client consistency.

### 2.3 Existing PostgreSQL Rate Limiter Audit
Inspection of `server/src/core/rate_limiter.py` reveals that a multi-worker PostgreSQL-backed rate limiter (`PostgreSQLRateLimiter`) **already exists**:
- Uses table `rate_limit_attempts (id, identifier, endpoint_key, window_start, attempt_count)`.
- Executes atomic `INSERT ... ON CONFLICT (identifier, endpoint_key) DO UPDATE` to track sliding windows without cross-process race conditions.
- **Defect Identified**: While `PostgreSQLRateLimiter` is implemented, it is currently wired only to login attempt counters. The sensitive endpoint `POST /api/v1/auth/password-reset/request` does NOT invoke `PostgreSQLRateLimiter` for the incoming client IP. Furthermore, `server/src/core/config.py` does not currently define a `TRUSTED_PROXY_IPS` CIDR list, leaving `request.headers.get("x-forwarded-for")` vulnerable to spoofing if behind a proxy.

### 2.4 Existing Minor Safeguarding & Consent Rules
Inspection of `server/src/services/application_service.py` (lines 169–173) and `server/src/models/volunteer.py` confirms the existing, approved minor safeguarding policy:
- **Minor Age Threshold**: `profile.age < 18` (derived from `date_of_birth`).
- **Safeguard Invariant**: Approval of an onboarding application is strictly blocked if `profile.age < 18` and `not profile.parental_consent_verified`.
- **Exception**: Raises `DomainException("Minor applicant cannot be approved without verified parental consent.", code="MINOR_CONSENT_UNVERIFIED")`.
- **Verification Workflow**: An administrator must review and call `verify_parental_consent(status="VERIFIED")` before the application can transition to `APPROVED`.
- No new age or consent rule may be invented.

---

## 3. Original 15-Phase Roadmap Status & Physical Audit

| Phase | Title | Roadmap Spec | Status | Physical Repository Verification |
| :---: | :--- | :--- | :---: | :--- |
| **00** | Requirements, Architecture & Engineering Spec | `docs/phases/PHASE_00_REQUIREMENTS.md` | **COMPLETED** | Verified. Architecture standards, data dictionaries, and modular monolith principles established. |
| **01** | Project Initialization, Settings & FastAPI | `docs/phases/PHASE_01_INITIALIZATION.md` | **COMPLETED** | Verified. Pydantic v2 Settings, centralized exceptions, structured logging, CORS in `server/src/core/`. |
| **02** | Database Engineering & Alembic Migrations | `docs/phases/PHASE_02_DATABASE.md` | **COMPLETED** | Verified. All 29 tables active in Supabase PostgreSQL; migrations tracked in `server/alembic/versions/`. |
| **03** | Auth, Dual-Token Sessions, SameSite & CSRF | `docs/phases/PHASE_03_AUTHENTICATION.md` | **COMPLETED** | Verified. Argon2id password hashing, dual-token rotation in HttpOnly cookies, session tracking in `server/src/services/auth_service.py`. |
| **04** | Volunteer Profiles, Minor Safeguards & Schemas | `docs/phases/PHASE_04_VOLUNTEER_PROFILES.md` | **COMPLETED** | Verified. Polymorphic profile types (Student, Alumni, Corporate), DPDP Act minor age checks (<18), and BOLA access checks in `server/src/services/profile_service.py`. |
| **05** | Applications, Approvals & Consent Governance | `docs/phases/PHASE_05_APPLICATIONS.md` | **COMPLETED** | Verified. 6-stage application lifecycle, parental consent gating for minors, 6 affirmative consent dimensions in `server/src/services/application_service.py`. |
| **06** | Event Management Lifecycle | `docs/phases/PHASE_06_EVENTS.md` | **COMPLETED** | Verified. 6 event categories, online/offline validation rules, 6-state event lifecycle machine in `server/src/services/event_service.py`. |
| **07** | Event Registrations & Volunteer Selection | `docs/phases/PHASE_07_REGISTRATIONS.md` | **COMPLETED** | Verified. Concurrency-safe capacity management (`SELECT ... FOR UPDATE`), automated waitlists, admin selection workflows in `server/src/services/registration_service.py`. |
| **08** | Attendance Tracking & Hours Management | `docs/phases/PHASE_08_ATTENDANCE.md` | **COMPLETED** | Verified. Exact duration calculation in integer minutes, Decimal credited hours calculation (ROUND_HALF_UP), auditable correction flows in `server/src/services/attendance_service.py`. |
| **09** | Gamification, Decimal Points & Leaderboards | `docs/phases/PHASE_09_GAMIFICATION.md` | **COMPLETED** | Verified. Canonical formula $P = (E \times 10) + (H \times 2)$, trigger-protected immutable ledger, 2-phase event finalization, achievements in `server/src/services/gamification_service.py`. |
| **10** | Notification System & FCM Push Setup | `docs/phases/PHASE_10_NOTIFICATIONS.md` | **COMPLETED** | Verified. Transactional outbox background processor (`server/src/workers/outbox_worker.py`), heartbeat leases, Resend email client, FCM notification dispatch. |
| **11** | Email Communications & Cloudinary Media | `docs/phases/PHASE_11_EMAIL_MEDIA.md` | **COMPLETED** | Verified. Cloudinary signed upload signatures, canonical URL validation, media asset records with BOLA verification in `server/src/services/media_service.py`. |
| **12** | Administration, Dashboard & Reporting APIs | `docs/phases/PHASE_12_ADMIN_REPORTING.md` | **COMPLETED** | Verified. Executive KPI dashboard aggregations, 6 canonical Excel reports via `openpyxl`, formula injection prevention, outbox dead-letter retry in `server/src/services/admin_service.py`. |
| **13** | API Stabilization & Web/Flutter Integration | `docs/phases/PHASE_13_CLIENT_INTEGRATION.md` | **NOT_STARTED** | **Open Gap**. Web application implemented via M1-M6; static `openapi.json` contract freeze, mobile Flutter scaffolding, and full-lifecycle automated E2E suites remain pending. |
| **14** | Security Hardening, Browser Tests & Render Deploy | `docs/phases/PHASE_14_PRODUCTION.md` | **NOT_STARTED** | **Open Gap**. Multi-stage `Dockerfile`, `render.yaml` deployment blueprint, Locust performance testing, and production cookie topology tests remain unexecuted. |

---

## 4. Current Implementation & Technical Debt Matrix

| Ref ID | Category | Component | Description of Observed Gap | Target Remediation in Sprint 3 |
| :---: | :--- | :--- | :--- | :--- |
| **REM-017** | Performance / SLA | `api/v1/health.py` | `/health` synchronously queries remote Supabase PostgreSQL, introducing network latency spikes. No lightweight liveness probe exists for container orchestrators. | Decouple into `/health/liveness` (pure process check, no DB) and `/health/readiness` (DB connection check with 2s timeout). Keep `/health` as backward-compatible alias. |
| **REM-018** | Performance / DB | `services/attendance_service.py` | `check_in_volunteers` iterates row-by-row over volunteers, executing individual `SELECT ... FOR UPDATE` and `INSERT/UPDATE` queries. Risks timeouts during 100+ volunteer check-ins. | Refactor to batch SQL operations with deterministic row ordering to prevent deadlocks while preserving Decimal calculations and audit logs. |
| **REM-019** | Contract / Types | `server/openapi.json` & `web/types` | No static version-controlled `openapi.json` exists. Client types in `web/src/types/index.ts` are manually maintained without automated schema drift verification. | Export static `openapi.json` with sorted keys and sanitized environment details. Create automated regression test `test_openapi_drift.py`. Synchronize TypeScript DTOs. |
| **REM-020** | Security / Auth | `api/v1/auth.py` | `POST /password-reset/request` does not enforce IP-based rate limiting via `PostgreSQLRateLimiter`, allowing email enumeration / flooding. `config.py` lacks trusted proxy CIDR validation. | Apply `PostgreSQLRateLimiter` by client IP (5 requests / 15 min). Validate trusted proxy headers. Ensure response message is strictly generic regardless of account existence. |
| **REM-021** | API Standards | `api/v1/*.py` | Endpoints inconsistently name pagination parameters (`limit` vs `page_size`), though all enforce `le=100`. | Standardize pagination dependency supporting `limit` as canonical and `page_size` as an alias with bounds `ge=1, le=100`. |
| **REM-022** | Testing / QA | `server/tests/` | No automated test verifies the entire multi-stage volunteer lifecycle from registration through leaderboard crediting in a single transactional flow. | Implement `tests/e2e/test_volunteer_lifecycle.py` and `test_safeguard_lifecycle.py` using isolated rollback fixtures against a test database. |
| **REM-023** | Mobile / Architecture | `mobile/` | Directory contains only placeholder `README.md`. No Flutter configuration, API client, or token storage exists. | Scaffold foundation in `mobile/` (Dio client, secure storage, concurrent 401 refresh queueing, unit tests) without building full UI screens. |

---

## 5. Verification of Sprint 2 Delivery State

A strict audit of Git commit `8849c05` confirms:
1. **Commit HEAD**: `8849c0583f458a540eaa77dae81b721d950d55e6` on branch `main`.
2. **Working Tree**: Completely clean prior to audit doc generation (`nothing to commit, working tree clean`).
3. **Remote Synchronization**: Strictly **unpushed** (local is ahead of `origin/main` by 1 commit).
4. **Ignored Patterns**: `git check-ignore` confirms `web/.env.local`, `server/.env`, `node_modules`, `web/.next`, `server/.venv`, `.venv`, and `test_credentials.local.json` are properly ignored.
5. **Secret Audit**: Zero plain-text credentials, tokens, or OTPs present in commit history or tracked files.
6. **Integrity Rule**: No application code, database schema migrations, or dependencies were altered.

---

## 6. Readiness Conclusion

The repository is fully stabilized and verified. The baseline technology stack is definitively documented as **Next.js 16.4.4**, **Tailwind CSS v4 (4.3.4)**, **Python 3.13.9**, **FastAPI 0.162.0**, **Flutter 3.44.2**, and **Dart 3.12.2**.

Sprint 3 planning can proceed with precision using the verified facts recorded in this audit.
