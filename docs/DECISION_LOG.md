# DECISION_LOG.md — Architectural Decision Records (ADRs)
**Maatram Volunteering & Gamification Portal**

---

## ADR-001: Backend Framework Selection (Python 3.13 + FastAPI + Pydantic 2)

- **Status**: Accepted
- **Context**: The platform requires a modern, asynchronous, strictly typed backend framework capable of supporting both web and mobile clients with automatic OpenAPI schema generation, exceptional validation performance, and native asynchronous database drivers.
- **Decision**: Adopt Python 3.13, FastAPI, and Pydantic 2.
- **Consequences**:
  - *Positive*: Native async/await support, rapid serialization via Pydantic 2's Rust core, automatic Swagger/OpenAPI documentation for client teams, clean dependency injection.
  - *Negative*: Requires rigorous typing discipline (`mypy`) and asynchronous programming paradigms (`asyncpg`, `asyncio`).

---

## ADR-002: Modular Monolith vs Microservices

- **Status**: Accepted
- **Context**: The platform manages cross-cutting business rules (e.g., event completion awards points, updates attendance, enqueues emails, and updates leaderboards) across volunteers, events, and gamification.
- **Decision**: Build the application as a Layered Modular Monolith within a single FastAPI repository.
- **Consequences**:
  - *Positive*: Simplified local development, transactional consistency across module boundaries without distributed two-phase commits, single deployment target on Render, lower operational costs.
  - *Negative*: Developers must enforce internal module boundaries to prevent tight coupling between services.

---

## ADR-003: Database Engine & Managed Hosting (Supabase PostgreSQL without Supabase Auth)

- **Status**: Accepted
- **Context**: A relational database is required to enforce relational integrity, ACID transactions, and complex aggregations. Supabase is selected as the managed PostgreSQL provider.
- **Decision**: Use Supabase purely as a managed PostgreSQL database. All authentication, session tokens, user roles, business logic, and API access are owned exclusively by FastAPI. Clients never connect directly to Supabase PostgREST or Supabase Auth.
- **Consequences**:
  - *Positive*: Complete ownership over authentication, session revocation, rate limiting, and business validation; eliminates vendor lock-in to Supabase proprietary client libraries.
  - *Negative*: FastAPI must implement full session and authentication management.

---

## ADR-004: Password Hashing Standard (Argon2id)

- **Status**: Accepted
- **Context**: Secure password storage is critical for volunteer and administrative identities.
- **Decision**: Standardize on `Argon2id` (RFC 9106) using memory cost 64 MB, time cost 3 iterations, and parallelism 4 lanes.
- **Consequences**:
  - *Positive*: State-of-the-art resistance to GPU/ASIC brute-force and side-channel timing attacks, exceeding legacy bcrypt or PBKDF2 standards.
  - *Negative*: Slightly higher CPU/memory footprint during authentication operations (mitigated by rate limiting).

---

## ADR-005: Asynchronous Communications via Transactional Outbox (Deferring Redis/Celery)

- **Status**: Accepted
- **Context**: Notifications (email and mobile push) must be sent asynchronously without blocking HTTP request lifecycles. Traditional setups introduce Redis and Celery.
- **Decision**: Use a PostgreSQL-backed Transactional Outbox table (`communication_jobs`) processed by an asynchronous worker task.
- **Consequences**:
  - *Positive*: Guarantees zero message loss across server restarts; maintains atomic consistency between business operations (e.g., event completion) and outbound notifications; avoids managing Redis or Celery infrastructure.
  - *Negative*: Polling query overhead on PostgreSQL (mitigated via `FOR UPDATE SKIP LOCKED` and indexed partial scans).

---

## ADR-006: Direct Signed Cloudinary Upload Architecture

- **Status**: Accepted
- **Context**: High-resolution volunteer photos and event galleries must be stored and served efficiently without routing heavy multipart file streams through the FastAPI application server.
- **Decision**: Implement direct client-to-Cloudinary uploads authorized by backend HMAC-SHA256 signatures. The backend signs upload parameters; client uploads directly; backend registers the returned public asset metadata.
- **Consequences**:
  - *Positive*: Drastically reduces bandwidth and memory utilization on Render web service pods; leverages Cloudinary's global CDN and image transformation pipeline.
  - *Negative*: Requires two client-side network round-trips for upload flows.

---

## ADR-007: Unified Backend for Next.js Web and Flutter Mobile

- **Status**: Accepted
- **Context**: The platform features both a Next.js web application and a Flutter mobile app.
- **Decision**: Both clients consume identical REST APIs (`/api/v1/*`), identical data models, and identical business rules. Web sessions utilize HttpOnly cookies; mobile sessions utilize Bearer tokens.
- **Consequences**:
  - *Positive*: Zero business logic duplication, uniform validation rules, simplified QA and regression testing.
  - *Negative*: Auth middleware must accommodate both Cookie and Bearer token extraction transparently.

---

## ADR-008: Cookie Policy & CSRF Strategy Across Deployment Topologies

- **Status**: Accepted
- **Context**:
  - `portal.maatram.org` and `api.maatram.org` share scheme (`https`) and registrable apex domain (`maatram.org`), making them strictly **same-site**, even though their hostnames differ (**cross-origin**).
  - Browsers evaluate `SameSite` restrictions based on **site (eTLD+1)**, not origin. In a same-site cross-origin setup, `SameSite=Strict` is technically transmitted by browsers on asynchronous fetch calls with credentials.
  - However, `SameSite=Strict` strips cookies when navigating from external email links (Gmail, Outlook) to the portal.
  - In multi-SaaS staging (`vercel.app` vs `onrender.com`), the domains are **cross-site**, requiring `SameSite=None; Secure`.
- **Decision**:
  - Adopt `SameSite=Lax; Secure; HttpOnly; Domain=.maatram.org; Path=/api/v1/auth` for production. This permits safe top-level navigations from external links while blocking cross-site CSRF on mutative sub-requests.
  - Use `SameSite=None; Secure` for cross-SaaS staging environments.
  - Enforce Double-Submit Anti-CSRF headers (`X-CSRF-Token`) and Origin validation on all state-modifying requests.
- **Consequences**:
  - *Positive*: Preserves seamless authentication on external email link arrivals without compromising CSRF protection.
  - *Negative*: Staging on cross-SaaS domains requires HTTPS and strict origin filtering.

---

## ADR-009: Configurable Policy Architecture for Unapproved Governance Decisions

- **Status**: Accepted
- **Context**: Several business policies (leaderboard cycles, hour rounding, partial attendance thresholds, correction approval thresholds, inactivity limits, consent defaults, minimum volunteer eligibility age) are pending formal Maatram Foundation ratification.
- **Decision**: Do not hardcode any unapproved business rule in code or database schemas. Implement all pending policies as typed configuration parameters in `core/config.py` (with safe, privacy-preserving defaults) and ensure schemas support dynamic definitions.
- **Consequences**:
  - *Positive*: Zero code refactoring required when Maatram ratifies or alters thresholds; avoids premature lock-in to unapproved assumptions.
  - *Negative*: Requires comprehensive configuration documentation in `OPEN_QUESTIONS.md`.

---

## ADR-010: Transactional Outbox Lease Recovery, Concurrency & Dead-Letter Handling

- **Status**: Accepted
- **Context**: Outbox jobs can fail repeatedly due to external service outages or worker pod crashes. Without lease tracking, worker crashes could leave jobs stranded in `PROCESSING`. Without provider idempotency keys, crash recovery could cause duplicate email dispatches.
- **Decision**:
  - Track worker leases using `locked_at` and `worker_id` with a 5-minute lease timeout.
  - Worker atomically increments `attempts = attempts + 1` upon claiming a job for `PROCESSING`. Initial dispatch failure is attempt 1. With `max_retries = 3`, up to 3 retries are permitted (attempts 2, 3, 4). On the 4th failure, the job transitions to `DEAD_LETTER`.
  - Implement crash recovery sweeper resetting expired leases (`locked_at < NOW() - INTERVAL '5 minutes'`) to `PENDING` if `attempts <= max_retries`, or `DEAD_LETTER` if exhausted.
  - Pass `Idempotency-Key: {job_id}` to external providers (Resend) to prevent duplicate delivery upon recovery.
  - Provide administrative dead-letter inspection and requeue endpoints (`POST /api/v1/admin/outbox/{job_id}/requeue`).
- **Consequences**:
  - *Positive*: Eliminates stranded jobs and duplicate email dispatches; provides visibility into delivery failures on the Admin dashboard.
  - *Negative*: Requires periodic sweep task execution.

---

## ADR-011: Database-Enforced Immutable Point Ledger & Role Privilege Isolation

- **Status**: Accepted
- **Context**: Volunteering gamification points must be immutable and mathematically auditable. If points could be updated, deleted, or truncated, volunteer trust and audit integrity would be compromised. Application-level guards alone are insufficient against SQL injection or rogue scripts.
- **Decision**:
  - Enforce immutability of `point_transactions` at the database engine level via PostgreSQL trigger `trg_prevent_point_ledger_mutation` that prevents all `UPDATE` and `DELETE` operations.
  - Enforce database role privilege isolation: Application runtime user (`maatram_app_user`) is granted strictly `SELECT, INSERT` on `point_transactions`. Privileges for `UPDATE`, `DELETE`, `TRUNCATE`, and `TRIGGER` are explicitly revoked.
  - The table is owned by `maatram_migration_admin`, preventing `maatram_app_user` from executing `ALTER TABLE ... DISABLE TRIGGER` or `TRUNCATE`.
  - Represent all corrections, point adjustments, and cancellations as **compensating transactions** (`COMPENSATION_REVERSAL`) with negative values and explicit references to `related_transaction_id`.
  - Use `NUMERIC(8, 2)` for all point metrics (`event_points`, `hour_points`, `total_points`, `hours_credited`) to natively support fractional calculations (e.g., $1.50\text{ points}$), while raw attendance duration is recorded in integer minutes. All point arithmetic uses Python `Decimal` strictly with no float conversions.
- **Consequences**:
  - *Positive*: Zero possibility of ledger tampering even via direct administrative updates or compromised application credentials; mathematically verifiable audit trail.
  - *Negative*: Points calculations must always sum ledger entries rather than updating single balance cells; schema migrations require distinct administrative credentials.

---

## ADR-012: FCM Error Classification & Selective Device Token Invalidation

- **Status**: Accepted
- **Context**: When dispatching mobile push notifications via Firebase Cloud Messaging, various errors can occur. Inappropriately deactivating tokens upon payload or service errors would log out or disconnect valid volunteer devices.
- **Decision**:
  - Deactivate `device_tokens.is_active = FALSE` **only** upon confirmed token-specific error codes: `messaging/registration-token-not-registered` (`UnregisteredError`) and `messaging/invalid-registration-token`.
  - Do **not** deactivate tokens for payload errors (e.g., `messaging/invalid-argument` due to payload schema defects) or transient infrastructure errors (`quota-exceeded`, `internal-error`, timeouts). Treat payload/system errors as job failures subject to standard retry and dead-lettering.
- **Consequences**:
  - *Positive*: Prevents false-positive token deactivations; isolates push payload bugs from device registration records.
  - *Negative*: Requires granular error code pattern matching in the FCM integration adapter.

---

## ADR-013: FCM At-Least-Once Semantics, DB Source of Truth & Durable Client Deduplication

- **Status**: Accepted
- **Context**: Push notification protocols (FCM/APNs) are inherently at-least-once, best-effort delivery mechanisms. Push messages can be duplicated during cellular tower handoffs, provider retries, or app lifecycle restarts. Claiming exactly-once push delivery is architecturally false.
- **Decision**:
  - The canonical, authoritative notification store is the PostgreSQL `notifications` table on the backend.
  - FCM push notifications are treated as ephemeral wakeup hints and out-of-app alerting mechanisms.
  - Every push payload contains an immutable UUID `notification_id`.
  - The Flutter client maintains a durable SQLite deduplication cache (`processed_push_notifications`) with a 7-day sliding TTL. If a push arrives with an existing `notification_id`, the system suppresses banner display and audio alerts.
  - The crash window between push receipt in background isolate and SQLite persistence is acknowledged: if OS kills the isolate prior to SQLite write, duplicate presentation may occur on OS retry, but opening the notification triggers sync with the PostgreSQL backend which is idempotent.
- **Consequences**:
  - *Positive*: Honest, robust messaging architecture; eliminates duplicate UI banners for end users during network blips.
  - *Negative*: Requires local SQLite management and periodic vacuuming on the Flutter client.

---

## ADR-014: Parental Consent Multi-Step Verification & Minor Safeguarding

- **Status**: Accepted
- **Context**: Volunteering by applicants under 18 invokes statutory minor safeguarding (Indian DPDP Act). A self-asserted boolean checkbox from an applicant cannot serve as legal proof of parental consent.
- **Decision**:
  - Strictly decouple consent submission from administrative verification.
  - Onboarding registration accepts guardian information (`guardian_name`, `guardian_relationship`, `guardian_contact`) and optional consent document upload (`parental_consent_media_id`), marking `parental_consent_submitted = TRUE`.
  - The initial status is set to `PENDING_VERIFICATION` (or `NOT_REQUIRED` if age $\ge 18$).
  - Only an authorized Admin or Super Admin can verify the documentary evidence via `POST /api/v1/applications/{id}/verify-parental-consent` and transition the status to `VERIFIED` or `REJECTED`.
  - The verification action generates an immutable entry in `audit_logs` recording the verifying admin, timestamp, and notes.
- **Consequences**:
  - *Positive*: Satisfies legal safeguarding; prevents minors from self-certifying consent; full auditability for compliance reviews.
  - *Negative*: Adds an administrative verification step prior to onboarding approval for minor applicants.
