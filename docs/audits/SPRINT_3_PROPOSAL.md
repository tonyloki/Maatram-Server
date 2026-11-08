# SPRINT 3 PROPOSAL v3.0.3 — API CONTRACT FREEZING, BACKEND PERFORMANCE & CLIENT INTEGRATION
**Maatram Volunteering & Gamification Portal**  
*Document Version: 3.0.3 — Date: November 8, 2026*  
*Baseline Verified Commit: `8849c05`*  
*Status: PROPOSED — AWAITING EXPLICIT IMPLEMENTATION AUTHORIZATION*

---

## 1. Executive Summary & Sprint Objective

The objective of **Sprint 3** is to transition the Maatram platform from isolated web-backend operation into a **hardened, multi-client enterprise ecosystem** by executing the verified deliverables of **Phase 13 (API Stabilization & Client Integration)** alongside priority backend performance, security, and operational remediations (REM-017 through REM-023).

Sprint 3 addresses six core architectural goals:
1. **Freeze and export the canonical OpenAPI v1 specification**, establishing structural JSON comparison drift validation, sanitizing internal secrets, and aligning client TypeScript types with authoritative backend schemas without renaming backend fields solely for frontend convenience.
2. **Harden health checks and bulk attendance performance**, decoupling liveness (pure in-process check) from readiness (critical service dependency check), and refactoring bulk attendance to atomic batch SQL operations while preserving exact Decimal calculations, row locking, duplicate protection, and audit logs.
3. **Build an automated full-lifecycle end-to-end (E2E) test suite**, validating both sequential volunteer lifecycles and concurrent registration workflows using strictly isolated database fixtures.
4. **Harden rate limiting and standardize pagination across all endpoints**, deploying the existing shared PostgreSQL-backed rate limiter to sensitive authentication endpoints with robust trusted proxy IP parsing, generic anti-enumeration responses, and unified pagination query parameters.
5. **Publish the authoritative Client Integration Handbook (`docs/FRONTEND_INTEGRATION.md`)**, documenting actual backend-supported authentication topologies, token rotation, and error schemas, while clearly distinguishing existing backend capabilities from planned Flutter client implementations.
6. **Scaffold the Flutter mobile application foundation (`mobile/`)**, targeting installed **Flutter 3.44.2** and **Dart 3.12.2**, establishing a thread-safe Dio HTTP client with concurrent 401 refresh queuing and encrypted token storage, without building mock screens or duplicating backend logic.

---

## 2. Work Packages Breakdown

### Work Package 1 (WP-1): OpenAPI v1 Contract Freeze & Structural Drift Verification
- **Roadmap Alignment**: Phase 13 Section 1, REM-019
- **Technical Scope**:
  1. **Canonical Schema Audit & Field Preservation**:
     - Authoritative database columns and Pydantic schemas remain primary:
       - `online_meeting_url` is canonical; frontend TypeScript interfaces (`web/src/types/index.ts`) will be updated to match the backend contract.
       - `capacity_required` is canonical; backend maintains `volunteer_capacity` as a backward-compatible alias.
     - No backend field will be renamed solely to match frontend assumptions.
  2. **Deterministic OpenAPI Export Script**:
     - Implement `server/src/scripts/export_openapi.py`.
     - Recursively sorts dictionary keys (`paths`, `components`, `schemas`, `properties`) to ensure reproducible serialization.
     - Sanitizes environment-specific variables, local filesystem paths, internal server hostnames, and database connection strings.
     - Writes deterministic JSON output to `server/openapi.json`.
  3. **Structural JSON Drift Verification Test**:
     - Implement `server/tests/contract/test_openapi_drift.py` using `pytest`.
     - Normalizes both the live runtime `app.openapi()` dictionary and the committed `server/openapi.json` file.
     - Compares parsed structural objects (deep dictionary and list comparison) rather than raw file bytes, ensuring that formatting, indentation, and key ordering variations never produce false failures.
     - Preserves all meaningful schema semantics during normalization: required fields, property data types, nullable constraints, enum values, default values, request/response body definitions, security schemes, and endpoint parameters.
     - Includes an automated negative test (`test_openapi_drift_negative_detection`) that programmatically mutates a schema property (e.g., changes a required flag or property type) and proves that structural drift is reliably caught with a descriptive assertion failure.
  4. **Frontend Type Synchronization**:
     - Update `web/src/types/index.ts` to strictly reflect the validated OpenAPI contract.
     - Provide computed property accessors where necessary so existing web components render without regressions.
- **Affected Files**:
  - `server/src/scripts/export_openapi.py` (new)
  - `server/openapi.json` (new)
  - `server/tests/contract/test_openapi_drift.py` (new)
  - `server/src/schemas/event.py`
  - `web/src/types/index.ts`

---

### Work Package 4 (WP-4): Security Hardening: Shared Rate Limiting & Pagination Governance
- **Roadmap Alignment**: Phase 14 Security Prep, REM-020, REM-021
- **Prerequisite**: WP-1 Approval (OpenAPI contract frozen)
- **Technical Scope**:
  1. **Shared PostgreSQL-Backed Rate Limiting**:
     - Deploy the existing `PostgreSQLRateLimiter` (`rate_limit_attempts` table) across all application workers, eliminating process-local memory bypasses.
     - Wire `PostgreSQLRateLimiter` to `POST /api/v1/auth/password-reset/request`.
     - Configure threshold: Maximum 5 requests per 15 minutes per client IP.
     - When exceeded, return HTTP 429 Too Many Requests with RFC-compliant `Retry-After: <seconds>` header and body `{"detail": "Rate limit exceeded. Please try again later.", "code": "RATE_LIMIT_EXCEEDED"}`.
  2. **Robust Trusted Proxy IP Extraction**:
     - Add `TRUSTED_PROXY_IPS: list[str]` to `server/src/core/config.py`, supporting explicit IPs and CIDR network blocks.
     - **Deployment Safety Rule**: Loopback addresses (`127.0.0.1`, `::1`) must be trusted **only** when a local reverse proxy (e.g. Nginx, Caddy) is actually deployed in front of the ASGI server; direct connections without a reverse proxy must NOT trust loopback forwarded headers. In production, `TRUSTED_PROXY_IPS` must be explicitly configured to match verified infrastructure subnets (e.g., verified cloud load balancer CIDRs). Never assume Render proxy addresses or Cloudflare trust without empirical verification of the network topology.
     - **Header Traversal Algorithm**:
       - Validate the immediate socket connection peer (`request.client.host`).
       - If `request.client.host` is NOT in `TRUSTED_PROXY_IPS`, completely ignore all forwarded headers and return `request.client.host`.
       - If `request.client.host` IS in `TRUSTED_PROXY_IPS`: parse the `X-Forwarded-For` chain (comma-separated list of IPs).
       - Walk the chain from right to left (from immediate peer toward original client), parsing each address with Python's standard `ipaddress.ip_address` and checking against `TRUSTED_PROXY_IPS` networks via `ipaddress.ip_network`. Discard trusted proxy hops.
       - Select the first untrusted address encountered as the true client IP.
       - If any header value contains malformed, invalid, or ambiguous IP characters, safely reject the header and fall back to `request.client.host`.
       - Do not trust `CF-Connecting-IP` unless the immediate peer is explicitly verified against trusted Cloudflare proxy CIDRs.
     - Implement comprehensive unit tests in `server/tests/test_client_ip.py`: direct connection, single trusted proxy, chained trusted proxies, spoofed header from untrusted peer, malformed IP strings, IPv4, IPv6, and empty forwarded headers.
  3. **Strict Anti-Enumeration Protection**:
     - `POST /api/v1/auth/password-reset/request` must ALWAYS return HTTP 200 `{"message": "If the account exists, a reset code has been sent."}` regardless of account presence.
     - Internal email throttling (3 requests/24h) must NOT raise an exception that reveals account existence; it will return the generic message while safely suppressing email dispatch.
  4. **Comprehensive Pagination Governance Across All Endpoints**:
     - Audit every paginated endpoint in the backend (`admin.py`, `applications.py`, `attendance.py`, `events.py`, `gamification.py`, `notifications.py`, `registrations.py`, `reports.py`, `volunteers.py`).
     - Implement a unified pagination dependency in `server/src/schemas/common.py` that accepts both `limit` (canonical) and `page_size` (backward-compatible alias).
     - Strictly enforce bounds: `page >= 1` and `1 <= limit <= 100`.
     - Requests exceeding 100 must return HTTP 422 Unprocessable Entity or clamp cleanly to 100.
     - Test boundary values: `-1`, `0`, `1`, `50`, `100`, `101`, `1000`, and non-integer inputs.
- **Affected Files**:
  - `server/src/core/config.py`
  - `server/src/core/security.py`
  - `server/src/core/rate_limiter.py`
  - `server/src/schemas/common.py`
  - `server/src/api/v1/auth.py`
  - `server/src/services/auth_service.py`
  - `server/src/api/v1/admin.py`
  - `server/src/api/v1/applications.py`
  - `server/src/api/v1/attendance.py`
  - `server/src/api/v1/events.py`
  - `server/src/api/v1/gamification.py`
  - `server/src/api/v1/notifications.py`
  - `server/src/api/v1/registrations.py`
  - `server/src/api/v1/reports.py`
  - `server/src/api/v1/volunteers.py`
  - `server/tests/test_auth.py`
  - `server/tests/test_client_ip.py` (new)
  - `server/tests/test_pagination.py` (new)

---

### Work Package 2 (WP-2): Health Probes Decoupling & Measured Batch Attendance Performance
- **Roadmap Alignment**: REM-017, REM-018, Phase 14 Production Readiness
- **Prerequisite**: WP-4 Approval (Security & pagination hardened)
- **Technical Scope**:
  1. **Decoupled Health Probes**:
     - `GET /api/v1/health/liveness`: Pure in-process probe. Returns HTTP 200 `{"status": "alive", "timestamp": "..."}` immediately without querying PostgreSQL, Resend, Cloudinary, or any external service. Used for process-level container liveness checks.
     - `GET /api/v1/health/readiness`: Probes only runtime dependencies critical to serving application traffic. Executes a lightweight `SELECT 1` query against the Supabase PostgreSQL connection pool with an explicit 2.0-second timeout. Returns HTTP 200 `{"status": "ready", ...}` when the pool responds, or HTTP 503 `{"status": "unready", ...}` if unreachable.
     - `GET /api/v1/health`: Maintained as a backward-compatible alias to readiness.
     - **Latency Measurement Methodology**: Latency is measured in milliseconds using `time.perf_counter()` strictly for the database query execution block, executed via local loopback httpx/pytest test client to distinguish between database engine execution time and external WAN network transport.
  2. **Batch Attendance Check-In / Check-Out Architecture**:
     - Refactor `attendance_service.check_in_volunteers` and `check_out_volunteers`:
       - Replace iterative single-row `for` loops with batch SQL operations.
       - Deterministic Row Locking: Sort incoming `volunteer_profile_ids` deterministically (`ORDER BY volunteer_profile_id`) before locking to prevent database deadlocks under concurrent requests.
       - Execute batch selection under lock: `SELECT ... WHERE event_id = :event_id AND volunteer_profile_id IN (...) FOR UPDATE`.
       - Execute batch insert/upsert into `attendance_records` preserving unique constraint `(event_id, volunteer_profile_id)`.
       - Record audit entries in `attendance_audit_logs` in a single batch insert.
       - Preserve exact Decimal calculations (`ROUND_HALF_UP`) for credited hours ($H = \text{duration\_minutes} / 60$) and preserve transaction atomicity.
  3. **Benchmarking & Concurrency Instrumentation**:
     - Instrument actual SQL execution/query counts during benchmarking using SQLAlchemy event listeners (`before_cursor_execute` query counter).
     - Benchmark the existing single-row implementation against the optimized implementation on the identical dataset and environment (100 synthetic volunteers).
     - Record actual query counts, elapsed duration, and memory overhead.
     - Formulate performance targets and improvements strictly based on measured evidence rather than premature round-trip claims.
     - Verify concurrent check-in requests execute cleanly without duplicate records, deadlocks, or lost audit entries.
- **Affected Files**:
  - `server/src/api/v1/health.py`
  - `server/src/services/attendance_service.py`
  - `server/src/repositories/attendance_repository.py`
  - `server/tests/test_health.py`
  - `server/tests/test_attendance.py`
  - `server/tests/benchmarks/test_attendance_batch_benchmark.py` (new)

---

### Work Package 3 (WP-3): Automated Full-Lifecycle E2E Test Suite with Differentiated Isolation
- **Roadmap Alignment**: Phase 13 Section 2, REM-022, Phase 05 Safeguards
- **Prerequisite**: WP-2 Approval (Attendance & health performance verified)
- **Technical Scope**:
  1. **Consolidated Test Database Isolation Architecture**:
     - **Application Session Architecture**: In `server/src/core/database.py`, `get_db` checks out independent sessions from the connection pool, each executing `await session.commit()` on successful endpoint termination. Nested transactions on a test fixture session alone **do not** guarantee test isolation because independent request sessions commit directly to the database.
     - **Pre-Execution Target Verification Assertion**: Before any test setup or fixture execution, an automated assertion verifies the database connection URL and active schema. If the target points to the remote development or production database (or if schema isolation cannot be verified), the test suite immediately aborts with an explicit error.
     - **Synthetic Identities & Zero Residual Records**: All test accounts use deterministically generated synthetic identities (`test-volunteer-e2e-{uuid}@maatram.test`) with zero real volunteer accounts or production credentials. A post-suite query asserts zero residual test records remain.
     - **Category 1: Sequential Lifecycle E2E Tests (`test_volunteer_lifecycle.py`, `test_safeguard_lifecycle.py`)**:
       - Handled via a single shared `AsyncConnection`.
       - The test fixture establishes an outer transaction: `trans = await connection.begin()`.
       - For each sequential request, `app.dependency_overrides[get_db]` yields an `AsyncSession` explicitly bound to that shared connection using savepoint joining: `session = AsyncSession(bind=connection, join_transaction_mode="create_savepoint")`.
       - When endpoint handlers call `await session.commit()`, SQLAlchemy only commits the inner savepoint without committing the outer test transaction.
       - At test completion, the test harness executes `await trans.rollback()`, cleanly discarding all changes made across all request sessions.
     - **Category 2: Concurrent E2E Tests (`test_concurrent_registration_e2e.py`)**:
       - **Strict Prohibition on Shared Connection**: Asyncpg and SQLAlchemy async connections are single-threaded over a single TCP socket and cannot execute concurrent queries without throwing connection state errors. Parallel HTTP requests must **never** share one single `AsyncConnection`.
       - **Connection-Level Schema Isolation Protocol**:
         - Concurrent suites run against an isolated PostgreSQL test schema (e.g., `test_e2e_<uuid>`).
         - **Pool-Wide Schema Enforcement**: The test schema is selected on **every independent connection** in the engine pool (configured via `connect_args={"server_settings": {"search_path": f"{test_schema}, public"}}` or a pool checkout listener).
         - **Verification on Every Connection**: The harness executes `SELECT current_schema()` on every acquired connection upon checkout, aborting immediately if it returns `public` or falls back.
         - **Clean Teardown**: Upon test completion, all test connections are closed and the engine pool is explicitly disposed (`await test_engine.dispose()`) before executing `DROP SCHEMA test_e2e_<uuid> CASCADE`.
  2. **Scenario A: Complete Adult Volunteer Lifecycle (`test_volunteer_lifecycle.py`)**:
     - Register volunteer account $\to$ Verify email token $\to$ Complete volunteer profile (Student/Alumni) $\to$ Submit 6-stage onboarding application $\to$ Admin reviews and approves application $\to$ Admin creates and publishes event $\to$ Volunteer registers for event $\to$ Concurrency capacity checked $\to$ Admin selects volunteer $\to$ Admin bulk checks-in volunteer $\to$ Admin bulk checks-out volunteer $\to$ Admin completes event $\to$ System calculates points via authoritative formula $P = (E \times 10) + (H \times 2)$ $\to$ System creates immutable ledger entry $\to$ System updates volunteer balance $\to$ System updates affirmative consent leaderboard rank $\to$ Profile reflects updated points and badges.
  3. **Scenario B: Approved Minor Safeguarding Lifecycle (`test_safeguard_lifecycle.py`)**:
     - **Verified API Endpoints & Request Shape**:
       - Register minor volunteer (`age < 18` derived from `date_of_birth`).
       - Submit onboarding application (creates application in `SUBMITTED` status).
       - Admin attempts approval (`PATCH /api/v1/applications/{application_id}/review` with `{"status": "APPROVED"}`).
       - Assert Invariant: Fails with HTTP 400 `MINOR_CONSENT_UNVERIFIED` because `parental_consent_verified == False`.
       - Admin calls verified consent endpoint: `PATCH /api/v1/applications/{application_id}/verify-parental-consent` with payload matching `ParentalConsentVerifyRequest`:
         ```json
         {
           "status": "VERIFIED",
           "notes": "Verified documentary consent from parent."
         }
         ```
       - Admin re-attempts approval (`PATCH /api/v1/applications/{application_id}/review` with `{"status": "APPROVED"}`) $\to$ Approval succeeds.
     - Preserves existing minor safeguarding policy without inventing new rules.
  4. **Scenario C: Concurrent Registration & Capacity Invariant Testing (`test_concurrent_registration_e2e.py`)**:
     - Executed against the pool-isolated test schema with independent connection pool sessions.
     - Dispatches 20 concurrent synthetic volunteer registrations against a published event with `capacity_required = 5`.
     - **Verified Registration Business Rule Invariants**:
       - Exactly 5 registrations transition to `status = "SUBSCRIBED"` (occupying all 5 available spots).
       - The remaining 15 registrations transition to `status = "WAITLISTED"` (the canonical waitlist outcome; no unsupported status like `PENDING` is introduced).
       - Duplicate registrations for the same volunteer return the existing registration idempotently without altering committed counts.
       - Pessimistic row locking (`SELECT ... FOR UPDATE` on the event row) prevents race conditions, deadlocks, and constraint violations.
- **Affected Files**:
  - `server/tests/e2e/__init__.py` (new)
  - `server/tests/e2e/test_volunteer_lifecycle.py` (new)
  - `server/tests/e2e/test_safeguard_lifecycle.py` (new)
  - `server/tests/e2e/test_concurrent_registration_e2e.py` (new)
  - `server/tests/conftest.py`

---

### Work Package 5 (WP-5): Cross-Platform Client Integration Handbook
- **Roadmap Alignment**: Phase 13 Section 3 Deliverable
- **Prerequisite**: WP-3 Approval (E2E lifecycle verified)
- **Technical Scope**:
  - Author `docs/FRONTEND_INTEGRATION.md` documenting **actual backend-supported contracts** and clearly distinguishing existing backend capabilities from planned Flutter client implementations:
    1. **Authoritative Backend Authentication Contract (Implemented & Operational)**:
       - **Web Topologies**: SameSite=Lax, HttpOnly cookies (`maatram_access_token`, `maatram_refresh_token`) + CSRF header `X-CSRF-Token` read from `maatram_csrf_token`.
       - **API Token Refresh**: `POST /api/v1/auth/refresh` accepts refresh tokens from HttpOnly cookie or request body and issues new cryptographic pairs (rotating refresh tokens).
       - **Bearer Token Support**: Backend endpoints accept `Authorization: Bearer <access_token>` headers across all protected routes.
       - **Session Management**: Session tracking in database (`user_sessions`), revocable via `POST /api/v1/auth/logout` and `POST /api/v1/auth/sessions/{id}/revoke`.
    2. **Target Mobile Client Architecture (To Be Implemented in WP-6)**:
       - Clearly labeled as *Planned Client Implementation*: Dio HTTP client, `flutter_secure_storage` encrypted token vault, concurrency-locking 401 refresh interceptor, and logout event dispatch.
       - *Distinction Notice*: Mobile client code will be scaffolded exclusively in WP-6.
    3. **Standard API Error Schema**:
       - Specification of error body: `{"detail": string, "code": string, "validation_errors": [{"loc": [], "msg": "", "type": ""}]}`.
    4. **Pagination & Query Conventions**:
       - Query parameters: `page` (1-indexed), `limit` (max 100), `sort_by`, `order` (`asc`/`desc`).
    5. **Media Upload Signature Flow**:
       - Request signature from `POST /api/v1/media/signature`.
       - Client performs direct multipart upload to Cloudinary.
       - Client registers asset record via `POST /api/v1/media` with signed payload.
    6. **Notifications & In-App Polling**:
       - Client polls `GET /api/v1/notifications/unread-count` and `GET /api/v1/notifications`.
       - Transactional outbox background processor dispatches emails/push.
       - *Explicit Notice*: Real-time WebSockets / SSE are deferred and not currently supported.
    7. **Gamification & Points Engine Rules**:
       - Formula: $P = (E \times 10) + (H \times 2)$. Rounding: `ROUND_HALF_UP`.
       - 2-Phase atomic event completion: admin preview $\to$ locked finalization.
- **Affected Files**:
  - `docs/FRONTEND_INTEGRATION.md` (new)

---

### Work Package 6 (WP-6): Flutter Mobile Application Scaffolding & Architecture Blueprint
- **Roadmap Alignment**: Phase 13 Section 4 Foundation
- **Prerequisite**: WP-5 Approval (Integration handbook completed and reviewed)
- **Technical Scope**:
  1. **SDK & Workspace Verification**:
     - Verify existing `mobile/` directory containing only `README.md`.
     - Detect and target installed system SDKs: **Flutter 3.44.2** and **Dart 3.12.2**.
  2. **Foundation Only (Zero Full Screens, Zero Duplicated Business Logic)**:
     - Scaffold standard Flutter project files in `mobile/`:
       - `mobile/pubspec.yaml` with production dependencies: `dio: ^5.7.0`, `flutter_secure_storage: ^9.2.2`, `flutter_riverpod: ^2.6.1`.
       - `mobile/lib/main.dart`: App entry point with initialization check.
       - `mobile/lib/core/config/env_config.dart`: Environment configuration (API base URL, timeout durations).
       - `mobile/lib/core/storage/token_storage.dart`: Encrypted key-value storage using `FlutterSecureStorage` (never plain `SharedPreferences` or source files).
  3. **Thread-Safe Auth Refresh Interceptor (`auth_interceptor.dart`)**:
     - Intercepts outgoing requests to attach `Authorization: Bearer <access_token>`.
     - Intercepts HTTP 401 Unauthorized responses.
     - Concurrency Lock: If multiple requests fail simultaneously with 401, the interceptor locks subsequent requests into a queue and executes exactly ONE refresh call to `/api/v1/auth/refresh`.
     - On Refresh Success: Updates stored tokens, retries all queued requests with the new token.
     - On Refresh Failure: Clears all stored tokens from secure storage, flushes queue with errors, and emits an unauthenticated session state event.
  4. **Automated Unit Tests**:
     - `mobile/test/network/auth_interceptor_test.dart`: Mocks concurrent 401 requests and verifies only one refresh HTTP call is made.
     - `mobile/test/storage/token_storage_test.dart`: Verifies encrypted read, write, and clear operations.
- **Affected Files**:
  - `mobile/pubspec.yaml` (new)
  - `mobile/lib/main.dart` (new)
  - `mobile/lib/core/config/env_config.dart` (new)
  - `mobile/lib/core/network/api_client.dart` (new)
  - `mobile/lib/core/network/auth_interceptor.dart` (new)
  - `mobile/lib/core/storage/token_storage.dart` (new)
  - `mobile/test/network/auth_interceptor_test.dart` (new)
  - `mobile/test/storage/token_storage_test.dart` (new)

---

## 3. Sprint Execution Gates & Non-Destructive Quality Control

Advancing from one work package to the next requires explicit completion verification and user authorization.

```
[WP-1: OpenAPI Contract] ──(Gate 1 Approval)──> [WP-4: Security & Pagination] ──(Gate 2 Approval)──>
[WP-2: Performance & Health] ──(Gate 3 Approval)──> [WP-3: E2E Lifecycle Tests] ──(Gate 4 Approval)──>
[WP-5: Integration Handbook] ──(Gate 5 Approval)──> [WP-6: Flutter Foundation] ──(Gate 6 Sign-Off)
```

### Detailed Execution Gate Matrix

| Work Package | Prerequisites | Exact Scope | Positive Test Cases | Negative Test Cases | Regression Commands | Acceptance Evidence | Targeted Rollback Procedure | Completion Condition |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **WP-1** | Baseline commit `8849c05` | OpenAPI export, structural drift test, schema alignment, TS types | Export valid JSON, runtime schema matches committed structure | Structural drift caught on mutated field; negative test passes | `pytest server/tests/contract/`<br>`npm --prefix web run typecheck` | `server/openapi.json` generated; 0 structural diffs; 0 TS errors | Inspect `git status`. Remove only `server/src/scripts/export_openapi.py`, `server/openapi.json`, `server/tests/contract/test_openapi_drift.py`. Revert specific commit via `git revert <hash>`. | Structural drift test passes; static JSON committed |
| **WP-4** | WP-1 approval | Shared PG rate limit on reset, proxy validation, pagination bounds | Normal password reset returns generic 200; valid limits succeed; proxy chain correctly traversed | 6th reset in 15m returns 429 with `Retry-After`; `limit=500` returns 422; spoofed proxy IP rejected | `pytest server/tests/test_auth.py`<br>`pytest server/tests/test_client_ip.py`<br>`pytest server/tests/test_pagination.py` | 429 response includes `Retry-After`; client IP unit tests 100% passing; all paginated modules enforce bounds | Inspect `git status`. Revert specific commit via `git revert <hash>`. Remove only newly created test files `test_client_ip.py` and `test_pagination.py`. | Rate limit, proxy extraction, and pagination suites passing |
| **WP-2** | WP-4 approval | Decoupled liveness/readiness, batch attendance check-in/out | Liveness responds without DB; batch check-in 100 vols succeeds with exact Decimal hours | Readiness returns 503 on DB disconnect; invalid status blocked; deadlock prevented | `pytest server/tests/test_health.py`<br>`pytest server/tests/test_attendance.py`<br>`pytest server/tests/benchmarks/` | Benchmark report with measured query counts and duration; liveness decoupled from DB | Inspect `git status`. Revert specific commit via `git revert <hash>`. Remove only `test_attendance_batch_benchmark.py`. | Attendance tests pass; batch benchmark report generated |
| **WP-3** | WP-2 approval | Automated sequential lifecycle & concurrent registration suites with pool-verified DB isolation | Sequential adult/minor lifecycle completes; concurrent burst yields exactly 5 SUBSCRIBED and 15 WAITLISTED; zero deadlocks; zero residual test records | Minor approved without consent fails with 400; over-capacity registration waitlisted; target DB assertion aborts if prod; current_schema assertion fails if unisolated | `pytest server/tests/e2e/` | E2E test report showing sequential lifecycle and concurrent bursts verified; zero residual records; dev/prod DB untouched | Inspect `git status`. Revert specific commit via `git revert <hash>`. Remove only `server/tests/e2e/` files. | All lifecycle assertions pass in isolated test environment |
| **WP-5** | WP-3 approval | Author `docs/FRONTEND_INTEGRATION.md` | Accurate code snippets for Web Fetch and Flutter Dio; exact error schemas | None (documentation artifact) | Markdown link validation | `docs/FRONTEND_INTEGRATION.md` created with verified schemas | Inspect `git status`. Remove only `docs/FRONTEND_INTEGRATION.md`. | Architect sign-off on handbook completeness |
| **WP-6** | WP-5 approval | Flutter foundation: pubspec, Dio client, secure storage, concurrency lock | Single refresh dispatches; queued requests succeed; credentials stored securely | Refresh failure flushes queue with error and clears storage | `flutter analyze`<br>`flutter test` | Flutter analyze passes 0 errors; concurrency unit test proves 1 refresh per burst | Inspect `git status`. Revert specific commit via `git revert <hash>`. Remove only scaffolded files in `mobile/`. | Flutter tests pass; zero UI screens scaffolded |

---

## 4. Dependencies & Risk Mitigation

| Work Package | Dependency / Prerequisite | Risk | Mitigation |
| :--- | :--- | :--- | :--- |
| **WP-1** | Baseline commit `8849c05` | Schema renaming breaks web UI | Keep backend field canonical (`online_meeting_url`); update web TypeScript types; verify `npm run build`. |
| **WP-4** | **WP-1 Approval** | IP spoofing via manipulated `X-Forwarded-For` | Strictly validate `request.client.host` against `TRUSTED_PROXY_IPS` CIDRs; walk forwarded chain from right to left using standard `ipaddress` module; do not blindly trust loopback or Cloudflare headers. |
| **WP-2** | **WP-4 Approval** | Batch SQL deadlocks under concurrent check-ins | Sort volunteer IDs deterministically (`ORDER BY volunteer_profile_id`) before locking. |
| **WP-3** | **WP-2 Approval** | Destructive data pollution in development database / Connection state errors under concurrent tests | Enforce test database target verification assertion; sequential tests use shared connection with savepoint joining (`join_transaction_mode="create_savepoint"`); concurrent tests use dedicated schema with pool-wide `search_path` configuration, `current_schema()` assertion on checkout, and pool disposal before teardown. |
| **WP-5** | **WP-3 Approval** | Documentation drifting from implementation | Generate endpoint schemas directly from validated OpenAPI models; clearly distinguish implemented backend contracts from planned WP-6 mobile code. |
| **WP-6** | **WP-5 Approval** | SDK version incompatibility | Target exact system runtime versions: Flutter 3.44.2 and Dart 3.12.2. |

---

## 5. Explicit Out-of-Scope Items for Sprint 3

To maintain strict phase boundaries and avoid scope creep, the following tasks are strictly deferred to **Sprint 4 / Phase 14**:
1. **Render Cloud Deployment**: Production `Dockerfile` and `render.yaml` configuration.
2. **Locust Concurrency Stress Testing**: Formal 500-user distributed load testing.
3. **Domain, DNS & SSL Configuration**: Production domain routing for `api.maatramfoundation.com`.
4. **Third-Party Distributed Cache (Redis)**: Prohibited by Project Rule 4 (Modular Monolith Simplicity); PostgreSQL handles all caching and queuing.
5. **Full Flutter Mobile UI**: Screen designs, widgets, animations, or forms in Flutter (foundation only).
6. **Web UI Redesigns**: Visual layouts accepted in Sprint 2 remain unchanged.

---

## 6. Implementation Sequence & Authorization Directive

```
WP-1: OpenAPI Contract Freeze & Structural Drift Verification
  └─ [Gate 1 Approval Required]
WP-4: Security Hardening: Shared Rate Limiting & Pagination Governance
  └─ [Gate 2 Approval Required]
WP-2: Decoupled Health Probes & Measured Batch Attendance Performance
  └─ [Gate 3 Approval Required]
WP-3: Automated Full-Lifecycle E2E Test Suite with Differentiated Isolation
  └─ [Gate 4 Approval Required]
WP-5: Cross-Platform Client Integration Handbook
  └─ [Gate 5 Approval Required]
WP-6: Flutter Mobile Application Foundation
  └─ [Final Gate 6 Sign-Off]
```

> **Mandatory Hold**: **Sprint 3 implementation is NOT authorized.** Do not create implementation branches, execute migrations, alter database records, modify backend code, or push commits to GitHub. Await explicit user authorization.
