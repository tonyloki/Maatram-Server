# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## PHASE 6 — DATABASE & THIRD-PARTY INTEGRATIONS AUDIT REPORT

**Document ID:** `docs/audits/phase-6/DATABASE_AND_INTEGRATION_AUDIT.md`  
**Milestone:** Phase 6 — Complete System-Wide Quality Assurance, Functional Testing & Integration Audit  
**Date:** November 17, 2026  
**Auditor:** Antigravity Autonomous QA & Architecture Auditor  
**Integrations Covered:** PostgreSQL (Supabase), Resend Email, Cloudinary Media, Firebase Cloud Messaging (FCM)  

---

## 1. Executive Summary

This audit assesses the database architecture, migration mechanics, transactional integrity, and external third-party integrations (Resend, Cloudinary, Firebase FCM) that power the Maatram ecosystem.

**Audit Verdict:** **PASS (All Integrations Operating Behind Abstracted Interfaces with Server-Side Secret Isolation).**

---

## 2. PostgreSQL Database Architecture & Alembic Migrations

### 2.1 Database Overview
- **Database Engine:** PostgreSQL 15+ (Hosted on Supabase).
- **ORM / Driver:** SQLAlchemy 2.0.36 + `asyncpg` 0.30.0.
- **Connection Management:**
  - `DATABASE_URL`: Asynchronous pool connection (`postgresql+asyncpg://...`) utilized by FastAPI workers.
  - `DIRECT_URL`: Direct session connection (`postgresql://...`) utilized by Alembic migrations.
  - Pool configuration: `DB_POOL_SIZE=10`, `DB_MAX_OVERFLOW=5`, `DB_POOL_TIMEOUT=30s`, `DB_POOL_RECYCLE=300s`, `DB_POOL_PRE_PING=True`.

### 2.2 Alembic Schema Evolution
The schema is managed strictly through version-controlled Alembic migrations:
1. `97bb517503d6_initial_schema_baseline.py`: Creates baseline tables, UUID extensions, and initial foreign key relationships.
2. `c8e1f42a9012_rate_limiting_and_parental_consent.py`: Adds `rate_limits` table, `parental_consents` table for minor volunteers, and user lockout attributes.
3. `e4f5a6b7c8d9_performance_composite_indexes.py`: Introduces composite performance indexes:
   - `idx_events_status_category_start` on `events(status, category, start_time)`
   - `idx_registrations_event_status` on `event_registrations(event_id, status)`
   - `idx_attendance_volunteer_event` on `attendance_logs(volunteer_profile_id, event_id)`

**Migration Lifecycle Verification:** Automated verification script `server/tests/test_isolated_migrations.py` applies `alembic upgrade head`, `alembic downgrade base`, and re-upgrades to `head` in an isolated sandbox schema, confirming 100% reversible schema operations without data corruption.

---

## 3. Resend Email Integration & Transactional Outbox

### 3.1 Architecture & Reliable Delivery Pattern
To guarantee that emails are never lost during server crashes or network partitions, the platform implements the **Transactional Outbox Pattern**:
1. Business actions (registration, password reset, event updates) insert an event payload into the `transactional_outbox` table within the same database transaction.
2. The asynchronous outbox background worker (`server/src/workers/outbox_worker.py`) polls pending jobs, leases them with a 300-second timeout, dispatches the email via Resend REST API, and marks them `SENT`.
3. If Resend returns an error, the worker increments `retry_count` and retries up to 3 times before marking `FAILED`.

### 3.2 Supported Email Templates
- **Email Verification:** Dispatches high-entropy URL-safe verification token.
- **Password Reset:** Dispatches 6-digit numeric OTP with 15-minute expiration notice.
- **Volunteer Application Approval:** Welcome onboarding email with portal links.
- **Volunteer Application Rejection:** Compassionate status notice.
- **Event Confirmation & Reminders:** Detailed venue, schedule, and coordinator information.

### 3.3 Security & Secret Isolation
- `RESEND_API_KEY` is strictly confined to server-side environment variables. Clients never have access to Resend credentials.

---

## 4. Cloudinary Media Integration

### 4.1 Server-Side Signed Upload Protocol
Direct client-to-Cloudinary uploads are secured using time-bound server-generated cryptographic signatures:
1. Client requests signed upload parameters via `POST /api/v1/media/signed-upload` with asset type (`AVATAR` or `EVENT_COVER`).
2. FastAPI generates a SHA-1 signature based on `timestamp`, `folder`, `upload_preset`, and `CLOUDINARY_API_SECRET`.
3. Client streams multipart image data directly to Cloudinary edge servers (`https://api.cloudinary.com/v1_1/{cloud_name}/image/upload`).
4. Client notifies backend of upload completion via `POST /api/v1/media/assets`, providing the Cloudinary `public_id`, URL, and secure URL.
5. FastAPI verifies the media asset and links the `avatar_media_id` to the volunteer profile.

### 4.2 Constraints & Validation
- **Max File Size:** Enforced at 10 MB (`CLOUDINARY_MAX_FILE_SIZE_BYTES`).
- **Permitted MIME Types:** `image/jpeg`, `image/png`, `image/webp`.
- **Signature Expiry:** Signatures expire after 15 minutes.
- **Secret Isolation:** `CLOUDINARY_API_SECRET` is never transmitted to mobile or web clients.

---

## 5. Firebase Cloud Messaging (FCM) Integration

### 5.1 Push Notification Architecture
- **Client Registration:** Mobile client obtains native FCM device token on launch and transmits it to `POST /api/v1/notifications/device-token`.
- **Token Persistence:** Stored in `device_tokens` table, scoped to the authenticated volunteer.
- **Notification Dispatch:** `server/src/integrations/fcm_client.py` uses `firebase-admin` Python SDK to format notification messages containing:
  - `title`: Short headline (e.g. "Event Reminder").
  - `body`: Notification content text.
  - `data`: Contextual routing payload (e.g. `{"event_id": "...", "screen": "event_details"}`).
- **Session Revocation:** On logout (`POST /api/v1/auth/logout`), the device token association is revoked to prevent subsequent push notifications from reaching a shared device.
