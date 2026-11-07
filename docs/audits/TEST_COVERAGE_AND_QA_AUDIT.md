# Test Coverage & Quality Assurance Audit Report
**Maatram Volunteering & Mentorship Portal**  
**Audit Stream 4: Test Suite Verification, Business Rule Coverage, Concurrency QA, and Frontend Quality**  
**Conducted**: November 5, 2026  
**Auditor**: Independent DeepMind Production-Readiness Agent  
**Status**: COMPLETE  

---

## 1. Executive Summary

This audit delivers an empirical evaluation of the test suite quality, automated test coverage, regression prevention, static type safety, and code quality across both the FastAPI backend (`server/`) and the Next.js web application (`web/`).

### Overall QA Verdict
- **Backend Test Suite Execution**:
  - **144 unit and integration tests** collected and executed across 17 test modules.
  - **144 tests passed** (0 failures, 0 errors) in **132.29 seconds**.
  - Strong coverage of critical authentication workflows (Argon2id hashing, JWT expiry, replay-resistant refresh token rotation, account lockouts), affirmative privacy consent differential logging, gamification formula arithmetic, attendance state machines, and fine-grained administrative reporting.
- **Frontend Quality Assurance**:
  - `npx tsc --noEmit` executed with **0 errors**. TypeScript type-checking passes cleanly across all pages, components, hooks, and utilities.
  - `npx eslint src/app/volunteer src/app/page.tsx` executed with **0 errors and 29 warnings** (react-hooks linting and unused variables).
- **QA & Test Gaps Identified**:
  - **Medium [P2]**: 14 concurrency tests (`test_concurrency.py` and `test_concurrency_group5.py`) require native PostgreSQL row-level locks (`SELECT ... FOR UPDATE`) and cannot execute against the standard SQLite in-memory test runner.
  - **Medium [P2]**: Configurable policy settings in `config.py` (`LEADERBOARD_CYCLE_TYPE`, `HOURS_ROUNDING_MODE`, `WAITLIST_PROMOTION_MODE`) have 0% test coverage for non-default values.
  - **Medium [P2]**: CSRF test suites only test omitting the `X-CSRF-Token` header; no test exercises submitting an invalid/forged signature, leaving a massive testing blind spot.
  - **Low [P3]**: Pytest generates 1,462 deprecation warnings from SQLite `StaticPool` and Python 3.13 datetime adapters.
  - **Low [P3]**: 29 React hook purity and state synchronization warnings on the volunteer portal pages.

---

## 2. Test Suite Execution & Collection Inventory

### 2.1 Pytest Execution Metrics
- **Command Executed**:
  ```powershell
  cd server
  ..\.venv\Scripts\python.exe -m pytest tests/ --ignore=tests/test_concurrency.py --ignore=tests/test_concurrency_group5.py -q
  ```
- **Execution Output**:
  ```text
  ................................................................................ [ 55%]
  ................................................................                 [100%]
  1462 warnings, 144 passed in 132.29s (0:02:12)
  ```
- **Pass Rate**: **100.0%** (144 / 144 tests passing).

### 2.2 Test Module Breakdown

| Test File | Test Count | Domain / Feature Under Test | Status |
| :--- | :---: | :--- | :--- |
| `tests/test_admin_reporting.py` | 6 | Dashboard metrics, student/alumni contribution reports, inactive volunteer exports, interview privacy masking, Excel CSV injection sanitization, super-admin audit log restrictions | PASSED |
| `tests/test_applications.py` | 6 | Application submission, self-service retrieval, BOLA ownership guards, minor safeguarding parental consent validation, administrative rejection | PASSED |
| `tests/test_attendance.py` | 11 | Volunteer check-in, unselected volunteer rejection, check-in on inactive events, duplicate check-in prevention, hours calculation, checkout before checkin, checkout without checkin, correction workflows (<120m and >120m), bulk attendance processing, self-service history | PASSED |
| `tests/test_auth_security.py` | 8 | Argon2id verification, password complexity, JWT access token lifecycle, token expiration, malformed tokens, refresh token hashing, CSRF HMAC generation/verification, OTP hashing | PASSED |
| `tests/test_auth_workflows.py` | 24 | Registration (student, minor safeguarding, email/mobile conflicts), web login (cookies + CSRF), mobile login (bearer tokens), password lockouts, suspended accounts, token rotation, token replay detection, session revocation, logout/logout all, email verification, password reset, rate limiter persistence | PASSED |
| `tests/test_consent.py` | 4 | Initial affirmative consent defaults, differential mutation history logging, idempotent no-op updates, unauthenticated access rejection (401) | PASSED |
| `tests/test_database_models.py` | 6 | Model instantiation, foreign key integrity, cascade vs restrict behaviors, UTC datetime persistence | PASSED |
| `tests/test_event_completion.py`| 4 | Event finalization, automatic attendance lock, point award batching, thank-you email dispatch filtering based on affirmative consent | PASSED |
| `tests/test_events.py` | 18 | Event creation, updating, state transitions (`DRAFT` -> `PUBLISHED` -> `COMPLETED`), cancellation, capacity rules, skill tagging, public vs authenticated filtering, completed event registration blocking | PASSED |
| `tests/test_foundation.py` | 6 | Settings loader, root metadata, health check, OpenAPI JSON discovery, CORS preflight headers, global domain exception handling | PASSED |
| `tests/test_gamification.py` | 5 | Scoring formula exact decimal arithmetic, point ledgers, super-admin manual adjustments, leaderboard privacy masking (`name_visible`), achievement triggers | PASSED |
| `tests/test_integrated_live.py` | 1 | Live Supabase PostgreSQL pooler connectivity check | PASSED |
| `tests/test_media.py` | 5 | Cloudinary signed upload generation, file format and size limits, asset registration, photo gallery privacy consent (`media_usage`), LinkedIn celebration post generator (`linkedin_content`) | PASSED |
| `tests/test_notifications.py` | 10 | FCM device token registration/deactivation, token ownership, FCM selective error classification, in-app notifications, outbox worker leasing, crash recovery, stale lease reclamation | PASSED |
| `tests/test_performance_optimizations.py` | 6 | Argon2id thread pool parity, concurrent crypto execution, batch registration counts, consolidated dashboard metrics, Excel offloading, database pool settings | PASSED |
| `tests/test_registrations.py` | 18 | Published event registration, unapproved volunteer blocking, registration deadlines, draft/cancelled event registration blocking, idempotent registrations, admin selection/waitlist promotion, 24-hour withdrawal deadline cutoff, registration history tracking | PASSED |
| `tests/test_volunteers.py` | 6 | Volunteer profile retrieval, profile updates, registration number duplicate conflict, BOLA ownership checks, admin directory filtering, polymorphic profiles | PASSED |
| **Total Passed** | **144** | | **100%** |

---

## 3. Business Rule Test Coverage Analysis

### 3.1 Well-Tested Business Invariants
1. **Gamification Scoring Formula**: $P = (E \times 10) + (H \times 2)$ is rigorously tested with sub-60-minute disqualification, fractional minute rounding, and exact decimal arithmetic in `tests/test_gamification.py:test_scoring_formula_exact_decimal_arithmetic`.
2. **Attendance Chronology & Invariants**:
   - `test_checkout_before_checkin_rejected`: Asserts checkout earlier than checkin fails with domain exception.
   - `test_checkout_without_checkin_rejected`: Asserts checkout on un-checked-in volunteer fails.
   - `test_duplicate_check_in_rejected`: Asserts checking in twice raises conflict.
3. **Minor Safeguarding & Parental Consent**:
   - `test_register_minor_volunteer_safeguarding`: Asserts volunteers under 18 require parental consent.
   - `test_minor_safeguarding_approval_blocked_without_verified_consent`: Asserts admin cannot approve minor application without verified consent flag.
4. **Registration Withdrawal Cutoff**:
   - `test_volunteer_can_withdraw_registration`: Asserts withdrawal deadline ($<24$ hours prior to event start) prevents self-service cancellation.
5. **Privacy Consent Enforcement**:
   - `leaderboard_visible` tested in `test_gamification.py`.
   - `name_visible` tested in `test_gamification.py` and `test_media.py`.
   - `thank_you_emails` tested in `test_event_completion.py`.
   - `linkedin_content` tested in `test_media.py`.
   - `contact_available` tested in `test_admin_reporting.py`.
   - `media_usage` tested in `test_media.py`.

### 3.2 Untested Business Invariants & Coverage Gaps
1. **Configurable Policy Alternatives**:
   - `config.py` allows `LEADERBOARD_CYCLE_TYPE` to be `"FINANCIAL_YEAR"` or `"ACADEMIC_YEAR"`, but 0 tests verify either mode.
   - `config.py` allows `HOURS_ROUNDING_MODE` to be `"NEAREST_15_MIN"` or `"FLOOR_HALF_HOUR"`, but 0 tests verify non-default rounding.
   - `config.py` allows `WAITLIST_PROMOTION_MODE` to be `"FIFO_AUTOMATIC"` or `"HYBRID"`, but 0 tests verify automated FIFO promotion.
2. **Invalid CSRF Token Submission**:
   - `test_auth_workflows.py:test_csrf_protection_on_cookie_authenticated_requests` only tests:
     - Missing `X-CSRF-Token` header -> 403 Forbidden.
     - Malicious `Origin` header -> 403 Forbidden.
     - Bearer token exempt -> 200 OK.
   - **Critical Gap**: It never tests submitting `headers={"X-CSRF-Token": "tampered_token"}`. Because `verify_csrf` only checks non-emptiness, submitting `"tampered_token"` passes in production, but tests never detected this flaw.
3. **Password Reset Token Exhaustion**:
   - No test verifies account lockout or status oracle behavior on repeated password reset requests.

---

## 4. Concurrency & Database-Dependent Test Assessment

The test suite includes two dedicated concurrency test files that were excluded from the local test run:
1. `server/tests/test_concurrency.py` (8 test functions)
2. `server/tests/test_concurrency_group5.py` (6 test functions)

### Why Concurrency Tests Were Excluded
The default test harness in `server/tests/conftest.py` configures an in-memory SQLite database:
```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?mode=memory&cache=shared"
```
SQLite does not support:
- PostgreSQL row-level locks (`SELECT ... FOR UPDATE`).
- PostgreSQL advisory locks.
- True concurrent transaction isolation (SQLite serializes writes or raises `database is locked`).
- Native JSONB operators and concurrent sequence increments.

When `test_concurrency.py` is run against SQLite, tests fail with locking conflicts or timeout exceptions. These 14 concurrency tests are designed strictly for a live PostgreSQL environment.

---

## 5. Frontend Quality & Static Analysis Audit

### 5.1 TypeScript Compilation (`web/`)
- **Command**: `cd web; npx tsc --noEmit`
- **Result**: **0 errors** (Process exited with code 0).
- **Assessment**: Strict TypeScript checks pass completely across all Next.js pages, client components, API client abstractions, and layout hierarchies.

### 5.2 ESLint Code Quality (`web/`)
- **Command**: `cd web; npx eslint src/app/volunteer src/app/page.tsx`
- **Result**: **0 errors, 29 warnings**.
- **Warning Categorization**:
  1. `react-hooks/set-state-in-effect` (12 occurrences): State setters invoked inside `useEffect` without functional updates or dependency stabilization in dashboard/profile widgets.
  2. `react-hooks/purity` (8 occurrences): Calling non-deterministic `Date.now()` during component render phase instead of inside lifecycle effects.
  3. `@typescript-eslint/no-unused-vars` (9 occurrences): Unused imports and destructuring parameters in page headers and navigation tabs.

---

## 6. Detailed QA & Coverage Findings

### ISSUE-QA-001 [P2 - Medium]
- **Route/File**: `server/tests/test_concurrency.py`, `server/tests/test_concurrency_group5.py`, `server/tests/conftest.py`
- **Description**: Concurrency Test Suite Cannot Execute in Standard Test Environment
- **Evidence**:
  The local SQLite in-memory test harness lacks row locking capabilities. Attempting to run `pytest tests/test_concurrency.py` against SQLite fails due to lack of `FOR UPDATE` support. Consequently, 14 critical concurrency tests verifying atomic point awards, outbox worker leasing, and simultaneous registrations are skipped in routine developer test runs.
- **Impact**: Concurrency regressions, race conditions, and deadlocks in the PostgreSQL outbox and registration services may go undetected during local development.
- **Recommendation**: Provide a docker-compose test runner or dedicated PostgreSQL test container (`postgresql+asyncpg://...`) for running the full 158-test suite in CI/CD pipelines.

---

### ISSUE-QA-002 [P2 - Medium]
- **Route/File**: `server/src/core/config.py:91-109`, `server/tests/test_gamification.py`, `server/tests/test_registrations.py`
- **Description**: Zero Test Coverage for Configurable Business Policy Alternatives
- **Evidence**:
  `config.py` defines multiple operational policies:
  - `LEADERBOARD_CYCLE_TYPE` ("CALENDAR_YEAR", "FINANCIAL_YEAR", "ACADEMIC_YEAR")
  - `HOURS_ROUNDING_MODE` ("EXACT_DECIMAL_2", "NEAREST_15_MIN", "FLOOR_HALF_HOUR")
  - `WAITLIST_PROMOTION_MODE` ("MANUAL", "FIFO_AUTOMATIC", "HYBRID")
  None of the alternative policies have unit or integration tests. Because these alternatives are also not implemented in the service layer (see `ISSUE-DB-001`), no regression safety exists if an operator switches these flags.
- **Impact**: Setting non-default operational policies in `.env` could cause silent unexpected behavior without test alerts.
- **Recommendation**: Create unit tests in `test_gamification.py` and `test_registrations.py` testing each policy branch once implemented.

---

### ISSUE-QA-003 [P2 - Medium]
- **Route/File**: `server/tests/test_auth_workflows.py:700-737`
- **Description**: CSRF Test Suite Fails to Verify Invalid / Forged CSRF Tokens
- **Evidence**:
  In `tests/test_auth_workflows.py:test_csrf_protection_on_cookie_authenticated_requests`:
  ```python
  # 1. Mutative request with cookie but WITHOUT X-CSRF-Token header -> 403 Forbidden
  ...
  # 2. Mutative request with cookie but with MALICIOUS Origin header -> 403 Forbidden
  ...
  # 3. Mobile request with Bearer authorization header is EXEMPT from CSRF and succeeds
  ```
  The test suite asserts that omitting `X-CSRF-Token` triggers 403. However, it never tests passing an invalid or forged string (e.g., `headers={"X-CSRF-Token": "bogus"}`). This gap directly masked `ISSUE-SEC-001`, where `verify_csrf` only checks for string presence without validating the token HMAC or matching the cookie.
- **Impact**: Broken security defenses were masked by incomplete assertions, giving false confidence in automated test passes.
- **Recommendation**: Add explicit test cases verifying that sending an invalid, tampered, or mismatched `X-CSRF-Token` header raises `403 Forbidden`.

---

### ISSUE-QA-004 [P3 - Low]
- **Route/File**: `server/tests/conftest.py:17`, `server/tests/`
- **Description**: High Volume of Deprecation Warnings in Pytest Execution (1,462 Warnings)
- **Evidence**:
  Running pytest outputs `1462 warnings, 144 passed in 132.29s`.
  The primary sources are:
  - SQLAlchemy 2.0 `SADeprecationWarning`: `Selection of the StaticPool pool class based on the 'mode=memory' query string argument is deprecated; a future release will use AsyncAdaptedQueuePool for this URL. Indicate the intended pool class using create_engine.poolclass parameter.`
  - Python 3.13 deprecation: `Passing format strings to Date/Time/Timestamp converters is deprecated since Python 3.12 and will be removed in Python 3.15.`
- **Impact**: Warning noise obscures real issues and warns of breaking changes upon upgrading to Python 3.14/3.15 or SQLAlchemy 2.1.
- **Recommendation**: Update `conftest.py` to specify `poolclass=StaticPool` explicitly in `create_async_engine()`, and update `aiosqlite` datetime adapter configurations.

---

### ISSUE-QA-005 [P3 - Low]
- **Route/File**: `web/src/app/volunteer/dashboard/page.tsx`, `web/src/app/volunteer/profile/page.tsx`
- **Description**: React Hook Purity & State Synchronization ESLint Warnings
- **Evidence**:
  Running `npx eslint src/app/volunteer src/app/page.tsx` produces 29 warnings:
  - 12 warnings for `react-hooks/set-state-in-effect` (calling `setState` directly inside effect body without dependency guard).
  - 8 warnings for `react-hooks/purity` (evaluating `Date.now()` during component render).
  - 9 warnings for unused variable declarations.
- **Impact**: Risk of cascading re-renders and React 19 hydration mismatches between server-rendered HTML and client hydration.
- **Recommendation**: Refactor direct `setState` calls into event handlers or wrapped state machines, and compute relative timestamps within `useEffect` or memoized hooks.

---

## 7. Summary Table of Test Coverage & QA Issues

| Issue ID | Severity | File / Component | Title | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-QA-001** | P2 (Medium) | `server/tests/test_concurrency.py` | Concurrency Test Suite Cannot Execute in Standard Test Environment | OPEN |
| **ISSUE-QA-002** | P2 (Medium) | `server/src/core/config.py:91` | Zero Test Coverage for Configurable Business Policy Alternatives | OPEN |
| **ISSUE-QA-003** | P2 (Medium) | `server/tests/test_auth_workflows.py:714`| CSRF Test Suite Fails to Verify Invalid / Forged CSRF Tokens | OPEN |
| **ISSUE-QA-004** | P3 (Low) | `server/tests/conftest.py:17` | High Volume of Deprecation Warnings in Pytest Execution (1,462 Warnings)| OPEN |
| **ISSUE-QA-005** | P3 (Low) | `web/src/app/volunteer/` | React Hook Purity & State Synchronization ESLint Warnings (29 Warnings) | OPEN |
