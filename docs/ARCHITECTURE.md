# ARCHITECTURE.md — System Architecture & Technical Design
**Maatram Volunteering & Gamification Portal**

---

## 1. Architectural Style & High-Level System Context

The Maatram Volunteering & Gamification Portal backend is engineered as a **Modular Monolith** using **Python 3.13** and **FastAPI**. Microservices, distributed broker clusters (e.g., Kafka, Celery), and external caching layers (e.g., Redis) have been deliberately excluded in favor of architectural cohesion, operational simplicity, and unified data consistency.

### System Context Diagram

```
       +-----------------------+         +-----------------------+
       |   Next.js Web Client  |         |  Flutter Mobile App   |
       |  (Volunteer & Admin)  |         |  (Volunteer & Admin)  |
       +-----------+-----------+         +-----------+-----------+
                   |                                 |
                   | HTTPS / REST / JSON             | HTTPS / REST / JSON
                   | (HttpOnly Cookies + CSRF)       | (Secure Storage Bearer)
                   +----------------+----------------+
                                    |
                                    v
                     +-----------------------------+
                     |    FastAPI Application      |
                     |  (Render Web Service Pods)  |
                     +--------------+--------------+
                                    |
         +--------------------------+--------------------------+
         |                          |                          |
         v                          v                          v
+------------------+      +-------------------+      +-------------------+
|  Transactional   |      |  Service Layer &  |      |   Integrations    |
|  Outbox Worker   |      | Repository Layer  |      |  (Resend, FCM,    |
| (Async Runner)   |      | (SQLAlchemy 2.0)  |      |   Cloudinary)     |
+--------+---------+      +---------+---------+      +-------------------+
         |                          |
         +--------------------------+
                                    |
                                    v (asyncpg / TLS)
                     +-----------------------------+
                     |    Supabase PostgreSQL      |
                     |  (Managed Database Engine)  |
                     +-----------------------------+
```

---

## 2. Layered Architecture & Boundary Rules

The backend is decomposed into distinct, unidirectional layers:

```
                  [ HTTP Clients (Web / Mobile) ]
                                |
                                v
               +----------------------------------+
               |            API Layer             |
               |  - Routers (/api/v1/*)           |
               |  - Request Validation (Pydantic) |
               |  - Response Serialization        |
               |  - Dependency Injection (deps.py)|
               +----------------+-----------------+
                                |
                                v
               +----------------------------------+
               |          Service Layer           |
               |  - Business Logic & Invariants   |
               |  - Orchestration & Workflows     |
               |  - State Machines & Transitions  |
               |  - Security & Authorization      |
               |  - Transaction Management        |
               +--------+----------------+--------+
                        |                |
             +----------+                +----------+
             v                                      v
+--------------------------+          +--------------------------+
|     Repository Layer     |          |    Integration Layer     |
|  - Data Access Logic     |          |  - Resend Email Client   |
|  - SQLAlchemy 2.0 Models |          |  - Firebase FCM Client   |
|  - Raw Query Filters     |          |  - Cloudinary Signer     |
|  - Aggregations          |          +--------------------------+
+------------+-------------+
             |
             v
+--------------------------+
|   Supabase PostgreSQL    |
+--------------------------+
```

### Architectural Invariants:
1. **Monorepo Layout**: The codebase is organized as a monorepo with `server/` (FastAPI backend), `web/` (Next.js web portal), and `mobile/` (Flutter mobile client).
2. **No Skip-Level Calls**: Routers must never call Repositories or raw SQLAlchemy models directly. Routers interact exclusively with Services.
3. **Encapsulated Data Access**: Only Repositories may construct SQL queries or inspect ORM session state.
4. **Stateless Services**: Services do not hold per-request instance state; they operate on injected sessions and parameters.
5. **Isolated Integrations**: External SDKs (Resend, Firebase Admin, Cloudinary) are isolated inside `server/src/integrations/` behind clean abstraction interfaces. If an external vendor changes, only the adapter in `server/src/integrations/` is modified.

---

## 3. Transactional Outbox Pattern for Asynchronous Communications

To guarantee reliable message delivery without Redis or Celery, the platform uses a **PostgreSQL-backed Transactional Outbox Pattern**.

### 3.1 Outbox State Machine & Unified Attempt Lifecycle

Every communication job follows one deterministic, unified state machine where `attempts` counts every initiated execution attempt:

```
                 [ Business Transaction Commits ]
                                |
                                v
                        +---------------+
                        |    PENDING    | <-----------------------------+
                        |  (attempts=0) |                               |
                        +-------+-------+                               |
                                |                                       |
                +---------------+---------------+                       |
                | Worker Claims Job via SQL:                            |
                | UPDATE communication_jobs                             |
                | SET attempts = attempts + 1,                          |
                |     status = 'PROCESSING',                            |
                |     locked_at = NOW(),                                |
                |     worker_id = :worker_id                            |
                v                                                       |
        +---------------+                                               |
        |  PROCESSING   | ----------------------------------------------+
        |  (attempts=N) | (Lease Expired / Worker Crash Sweeper:
        +-------+-------+  if attempts < 4 -> PENDING
                |          if attempts >= 4 -> DEAD_LETTER)
         +------+------+
         |             |
         v (Success)   v (Execution Failure)
  +-------------+ +-------------+
  |    SENT     | |   FAILED    |
  +-------------+ +------+------+
                         |
          +--------------+--------------+
          | attempts < 4 (max_retries=3)| attempts >= 4 (Exceeded)
          v                             v
  +---------------+             +---------------+
  |    PENDING    |             |  DEAD_LETTER  |
  | (Rescheduled) |             +-------+-------+
  +---------------+                     |
                                        | Super Admin Manual Requeue
                                        v
                                +---------------+
                                |    PENDING    |
                                |  (attempts=0) |
                                +---------------+
```

### 3.2 Outbox Processing Rules, Lease Recovery & Concurrency

1. **Atomic Enqueue**: Communication jobs are written to `communication_jobs` within the **exact same database transaction** that modifies business state. If the event completion rolls back, no jobs are created.
2. **Crash Resilience & Independent Failure**:
   - Outbox processing happens asynchronously.
   - An email delivery failure (e.g., Resend rate limit or network outage) **never rolls back or invalidates** an already committed event completion, registration, or point allocation.
3. **Exact Attempt Increment & Execution Tracking**:
   - The `attempts` integer column starts at `0`.
   - `attempts` is incremented **atomically upon claiming the job**:
     ```sql
     UPDATE communication_jobs
     SET status = 'PROCESSING',
         attempts = attempts + 1,
         locked_at = NOW(),
         worker_id = :worker_id
     WHERE id IN (
         SELECT id
         FROM communication_jobs
         WHERE status = 'PENDING' AND scheduled_at <= NOW()
         ORDER BY scheduled_at ASC
         LIMIT 50
         FOR UPDATE SKIP LOCKED
     )
     RETURNING id, channel, recipient, template_name, payload, attempts, max_retries, idempotency_key;
     ```
4. **Exact Total Attempt Calculation**:
   - Policy: `max_retries = 3` defines the maximum allowed retries *after* the initial failure.
   - Under this rule, a job is granted **exactly four total dispatch attempts**:
     - Attempt 1: Initial dispatch. If failed, schedule retry 1.
     - Attempt 2: First retry ($T + 30\text{s}$). If failed, schedule retry 2.
     - Attempt 3: Second retry ($T + 60\text{s}$). If failed, schedule retry 3.
     - Attempt 4: Third and final retry ($T + 120\text{s}$). If failed, transition directly to `DEAD_LETTER`.
5. **Worker Crash & Lease Timeout Recovery Sweeper**:
   - Lease duration: 5 minutes (`OUTBOX_LEASE_TIMEOUT_SECONDS = 300`).
   - If a worker crashes while processing a job, `locked_at` stops updating.
   - The recovery sweeper runs every 60 seconds:
     ```sql
     UPDATE communication_jobs
     SET status = CASE 
                    WHEN attempts < 4 THEN 'PENDING' 
                    ELSE 'DEAD_LETTER' 
                  END,
         locked_at = NULL,
         worker_id = NULL,
         last_error = 'Worker lease expired; crash recovery reset'
     WHERE status = 'PROCESSING'
       AND locked_at < NOW() - INTERVAL '5 minutes';
     ```
   - This ensures initial failures, retry failures, and worker crashes follow **one unified, deterministic state machine**.
6. **Duplicate Dispatch Prevention via Provider Idempotency**:
   - To guard against duplicate email delivery if a worker crashes after Resend accepts the request but before the database commits `status = 'SENT'`, the worker passes `Idempotency-Key: {communication_jobs.id}` to the Resend API.
   - Resend guarantees deduplication of requests with identical idempotency keys within a 24-hour window.
7. **Dead-Letter Inspection & Administrative Requeue**:
   - Jobs in `DEAD_LETTER` are logged as critical events in `communication_logs` and surfaced on the Super Admin dashboard via `GET /api/v1/admin/outbox/dead-letter`.
   - Super Admin invocation of `POST /api/v1/admin/outbox/{id}/requeue` resets `status = 'PENDING', attempts = 0, locked_at = NULL, scheduled_at = NOW()`.

---

## 4. Push Notification Delivery Semantics & Firebase FCM

### 4.1 At-Least-Once Delivery & Lack of Push Exactly-Once Guarantee
The system **does not and cannot claim exactly-once push notification delivery**. Network topologies between Firebase Cloud Messaging, Apple Push Notification service (APNs), cellular carriers, and client OS daemons operate on an **at-least-once / best-effort delivery model**. Push notifications can be duplicated due to:
- Mobile device roaming between Wi-Fi and cellular networks during push acknowledgement.
- Provider gateway retries when the mobile device acknowledges the push slowly.
- Operating system notification service restarts.

### 4.2 In-App Database as Canonical Source of Truth
The canonical source of truth for notifications is **exclusively the PostgreSQL database**:
- Every notification is permanently stored in `notifications` with a unique UUID (`id`), payload, read status (`is_read`), and creation timestamp.
- The Flutter mobile client treats FCM push notifications purely as a **real-time wake-up or display ping**. The authoritative inbox view is always populated by querying `GET /api/v1/notifications`.

### 4.3 Durable Client-Side Deduplication & Background Crash Window
To prevent duplicate visual notifications in the mobile system tray:
1. **Durable Local Cache**:
   - The Flutter client maintains a local, persistent deduplication table (using SQLite via `sqflite` or Hive) storing received `notification_id` and `fcm_message_id` with a 7-day Time-to-Live (TTL).
   - Upon receiving an FCM data message in the background or foreground handler, the Flutter app queries its local deduplication cache:
     - If the ID is already present, the incoming push is silently dropped.
     - If the ID is new, the client inserts the ID into local storage and displays the system notification.
2. **Mobile Background Crash Window**:
   - A microscopic crash window exists if the mobile OS background worker terminates (e.g. OS memory pressure or battery killer) *after* the system notification is rendered but *before* the local deduplication cache transaction completes.
   - In this rare edge case, a duplicate push arriving from an APNs/FCM reconnect could display a second tray alert.
   - However, when the user opens the app, the in-app notification inbox queries the PostgreSQL backend and displays the canonical, deduplicated notification record without corruption.

### 4.4 FCM Error Handling & Selective Device Token Invalidation

To maintain push notification reliability without erroneously discarding valid mobile devices:

#### Confirmed Token-Specific Errors (Deactivate Token):
When Firebase Admin SDK returns confirmed invalid-token error codes, the worker automatically deactivates the specific token (`UPDATE device_tokens SET is_active = FALSE WHERE fcm_token = :token`):
- `messaging/registration-token-not-registered` (`UnregisteredError`): The app was uninstalled from the device, or the token was rotated by the OS.
- `messaging/invalid-registration-token`: The token format itself is unrecognized or invalid.

#### Non-Deactivating Errors (Payload, Quota or System Errors):
The following provider responses **must not** deactivate the device token:
- `messaging/invalid-argument` due to payload errors (e.g. notification title/body too long, invalid data JSON structure, missing required notification fields): This represents a payload formatting bug, **not** an invalid device. Deactivating device tokens for payload errors would erroneously disconnect valid users.
- `messaging/quota-exceeded`: Provider rate limit; must back off and retry.
- `messaging/internal-error`, `messaging/server-unavailable`: Transient server error; must back off and retry.
- Network timeouts: Must back off and retry.

---

## 5. Media Management Architecture (Cloudinary)

To minimize backend server load and avoid streaming large multipart binary files through FastAPI pods, the platform uses **Direct Client-to-Cloudinary Uploads authorized by Backend Signatures**.

```
Web / Mobile Client              FastAPI Backend                Cloudinary
        |                               |                            |
        | 1. Request Upload Signature   |                            |
        |    (folder, asset_type, format|                            |
        |------------------------------>|                            |
        |                               | 2. Verify Auth & Consent   |
        |                               | 3. Generate HMAC-SHA256    |
        |                               |    Signature using Secret  |
        | 4. Return Signature, API Key, |                            |
        |    Timestamp, Upload URL      |                            |
        |<------------------------------|                            |
        |                                                            |
        | 5. Direct Multipart Upload (File + Signature)             |
        |----------------------------------------------------------->|
        |                                                            |
        | 6. Upload Confirmation (Asset ID, Secure URL, Dimensions)  |
        |<-----------------------------------------------------------|
        |                               |                            |
        | 7. Register Media Asset       |                            |
        |    (public_id, secure_url)    |                            |
        |------------------------------>|                            |
        |                               | 8. Verify Ownership & Save |
        | 9. 201 Created                |    Link to Profile / Event |
        |<------------------------------|                            |
```

### 5.1 Security Guardrails & Verification:
1. **Master Secret Isolation**: `CLOUDINARY_API_SECRET` is never shared with mobile or web clients; it resides strictly in backend environment variables.
2. **Signature Constraints**: Upload signatures enforce:
   - Target folder paths: `avatars/{user_id}/` for profiles; `events/{event_id}/` for event galleries; `consent/{user_id}/` for minor parental consent documents.
   - Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`, `application/pdf` (documents only).
   - Expiration timestamp ($T + 10\text{ minutes}$).
3. **File Size & Dimension Verification**:
   - Avatars: Maximum $5\text{ MB}$; recommended minimum $200 \times 200\text{ px}$.
   - Event Photos: Maximum $10\text{ MB}$.
   - Consent Documents: Maximum $10\text{ MB}$.
4. **Ownership & Access Validation**:
   - In `POST /api/v1/media/register`, the backend verifies that `uploaded_by_user_id == current_user.id` (or user is `ADMIN`).
   - For event photos, caller must possess `ADMIN` role.
5. **Asset Replacement & Deletion**:
   - When a volunteer uploads a new avatar, the previous `media_assets` record is marked superseded and an asynchronous job calls Cloudinary's Admin API (`destroy(public_id)`) to remove the orphaned asset.

---

## 6. Deployment Topology & Environments

The backend is deployed as a Docker container on **Render**:

- **Web Service Pods**: FastAPI running with Uvicorn (ASGI) behind Render's managed reverse proxy with automatic TLS termination and HTTP/2 support.
- **Async Outbox Runner**: Lightweight background task loop running within the service container.
- **Database Engine**: Supabase PostgreSQL 16+ located in AWS `ap-south-1` (Mumbai) for low-latency connectivity to Indian user infrastructure.
- **Connection Management**: `asyncpg` connection pool with pre-ping validation, pool size 20, max overflow 10, and 300-second recycling.
