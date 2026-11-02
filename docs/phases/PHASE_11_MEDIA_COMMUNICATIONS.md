# PHASE 11 — Email Communications & Cloudinary Media Management

## 1. Objective
Implement the transactional outbox worker with lease tracking, crash recovery, and provider idempotency for reliable email delivery via the Resend API, and build secure direct-to-Cloudinary media upload authorization and asset management.

## 2. Scope
- Background transactional outbox worker polling `communication_jobs` using `SELECT ... FOR UPDATE SKIP LOCKED` (`workers/outbox_worker.py`).
- Worker atomically increments `attempts = attempts + 1` upon claiming a job for `PROCESSING`. Initial failure is attempt 1. With `max_retries = 3`, up to 3 retries are permitted (attempts 2, 3, 4). On the 4th failure, the job transitions to `DEAD_LETTER`.
- Worker lease tracking (`locked_at`, `worker_id`) with 5-minute lease timeout and automated crash recovery sweeper.
- Duplicate dispatch prevention via provider idempotency: pass `Idempotency-Key: {job_id}` to Resend API.
- Exponential backoff ($2^{\text{attempts}} \times 30\text{s}$) between retry attempts.
- Resend API integration client (`integrations/resend_client.py`).
- Transactional email templates (Verification, Welcome, Event Reminder, Thank You).
- Cloudinary client and HMAC-SHA256 signature generator (`integrations/cloudinary_client.py`).
- Direct client upload authorization, file validation, ownership verification, and media registry (`media_assets`, `event_photos`).
- Media management service (`services/media_service.py`) and API routers (`api/v1/media.py`).

## 3. Dependencies
- Phase 10 completed.

## 4. Implementation Tasks
1. Build `ResendClient` wrapping Resend API for transactional email delivery with `Idempotency-Key` headers.
2. Build `OutboxWorker` task running asynchronously:
   - Polls `communication_jobs` with `FOR UPDATE SKIP LOCKED`, atomically increments `attempts = attempts + 1`, sets `status = 'PROCESSING'`, `locked_at = NOW()`, `worker_id`.
   - Dispatches emails with exponential backoff on retry.
   - Implements crash recovery sweeper resetting expired leases (`locked_at < NOW() - 5m`) to `PENDING` if `attempts <= max_retries`, or `DEAD_LETTER` if exhausted.
   - Transitions jobs to `DEAD_LETTER` upon failing on attempt 4 (`attempts > max_retries`).
   - Logs outcomes in `communication_logs`.
3. Build `CloudinaryClient`:
   - Generate HMAC-SHA256 signatures for authorized client uploads with folder and expiration boundaries.
   - Verify uploaded asset metadata, dimensions, and MIME types.
4. Implement `MediaService`:
   - `generate_upload_signature`: Generates parameters for avatars and event galleries.
   - `register_media_asset`: Verifies caller ownership (`uploaded_by_user_id == current_user.id`), saves asset metadata, and binds to volunteer profile or event gallery.
5. Implement API routers in `api/v1/media.py`.

## 5. Database Changes
Operates on `communication_jobs`, `communication_logs`, `media_assets`, and `event_photos`.

## 6. APIs
- `POST /api/v1/media/sign-upload`
- `POST /api/v1/media/register`
- `GET /api/v1/events/{id}/photos`
- `POST /api/v1/events/{id}/photos` (Admin bind photo)

## 7. Security Requirements
- Cloudinary API secret never exposed; upload parameters enforce MIME type, size, and folder boundaries.
- Resend API key protected.
- Invariant: Email delivery errors never roll back or cancel committed business transactions.
- Media usage consent (`consent_records.media_usage`) verified prior to surfacing event photos in public galleries.

## 8. Test Requirements
- Unit tests for HMAC-SHA256 signature generation.
- Integration tests for outbox worker polling, lease acquisition, and lease expiration crash recovery.
- Resend provider idempotency test: verify duplicate network dispatches carry identical idempotency keys.
- State machine boundary tests:
  - Attempt 1: Job claimed (`attempts=1`), fails -> transitions to `PENDING` with backoff.
  - Attempt 2: Job claimed (`attempts=2`), fails -> transitions to `PENDING` with backoff.
  - Attempt 3: Job claimed (`attempts=3`), fails -> transitions to `PENDING` with backoff.
  - Attempt 4: Job claimed (`attempts=4`), fails -> transitions to `DEAD_LETTER`. Exactly 4 total dispatch attempts occur under `max_retries = 3`.
- Dead-letter transition test and mock tests for Resend API dispatch.

## 9. Deliverables
- Transactional outbox worker with lease crash recovery, Resend client, Cloudinary signer, media routers, and tests.

## 10. Acceptance Criteria
- Outbox worker reliably dispatches pending email jobs without duplicate sends upon crashes.
- Failed jobs transition to `DEAD_LETTER` after retries without clogging the active queue.
- Client uploads to Cloudinary are strictly authorized via signed parameters.
- Media assets register cleanly and link to profiles and events.

## 11. Definition of Done (DoD)
Communications and media subsystems verified, ready for administration and reporting in Phase 12.
