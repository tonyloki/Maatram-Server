# Performance Audit & Optimization Plan — Maatram Volunteering & Gamification Portal

**Document Reference:** `docs/execution-groups/PERFORMANCE_AUDIT_REPORT.md`  
**Execution Phase:** Pre-Deployment Performance Investigation & Diagnostic Audit  
**Audit Date:** November 3, 2026  
**Status:** COMPLETE — Awaiting Optimization Approval  

---

## 1. Executive Summary & Root-Cause Diagnosis

A comprehensive, empirical performance audit was conducted across the full Maatram Volunteering & Gamification Portal stack (Next.js 16 frontend, FastAPI backend, SQLAlchemy 2.0 ORM, and Supabase PostgreSQL). 

While the application code is architecturally sound and functionally complete, **the primary cause of the severe slowness experienced locally is the combination of intercontinental network latency to the cloud database and backend/frontend cascading waterfalls**.

### The Primary Root Cause: Geographic WAN Round-Trip Latency
- **Client Location:** India (`Asia/Kolkata` timezone).
- **Database Location:** AWS Ireland (`eu-west-1`), host: `aws-0-eu-west-1.pooler.supabase.com:6543`.
- **Database Query Execution Time (Inside PostgreSQL):** **0.06 ms – 0.12 ms** (measured via `EXPLAIN ANALYZE`).
- **Network Round-Trip Time (Client to Ireland):** **1,600 ms – 1,920 ms per SQL statement** (measured via raw ping and connection tests).
- **Impact:** Any code pattern that issues queries sequentially or checks out database connections incurs ~1.9 seconds of network latency *per round trip*.

### Top Amplifying Bottlenecks
1. **Database Connection Pool Pre-Ping (`pool_pre_ping: True`):** Every checkout from the SQLAlchemy connection pool issues a synchronous `SELECT 1` ping across the Ireland WAN, injecting **~1,900 ms of latency before executing any business queries**.
2. **Catastrophic N+1 Query Loop in `GET /api/v1/events`:** The event listing endpoint queries 20–50 events, then iterates in a Python `for` loop executing `get_registration_counts(event.id)`. For 20 events, this executes **20 sequential network round trips to Ireland**, yielding **9,063 ms (9.06s median)** and up to **15,051 ms (15.05s)** for 50 events.
3. **Multi-Query Aggregation Waterfall in `GET /api/v1/admin/dashboard`:** The dashboard endpoint issues **11 separate sequential SQL count/group queries** one after another, taking **8,151 ms (8.15s median)**.
4. **Sequential Relation Loading in `GET /api/v1/registrations/me`:** Five separate `selectinload` queries are fired sequentially, resulting in **9,112 ms (9.11s median)**.
5. **Frontend Client-Side Waterfall & Duplicate API Calls:** On every authenticated page visit (`/volunteer/dashboard`, `/volunteer/events`, etc.), the browser fires `/auth/refresh` + two duplicate calls to `/users/me` + two duplicate calls to `/notifications/unread-count` + page-level data calls simultaneously without client-side deduplication, consuming all backend worker slots and delaying LCP to **5,110 ms – 12,200 ms**.
6. **Synchronous CPU-Bound Argon2id Hashing:** Password hashing runs synchronously on the main thread inside `async def` endpoints, freezing the entire Python asyncio event loop and stalling all concurrent requests.

---

## 2. Baseline Environment

| Parameter | Specification / Measured Value |
|---|---|
| **CPU Model & Cores** | Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz (4 Physical Cores, 8 Logical Processors) |
| **System Memory** | 7.63 GB Total RAM, 0.86 GB Available (~88% RAM utilization under local load) |
| **Operating System** | Microsoft Windows 11 Enterprise (x64) |
| **Python Runtime** | Python 3.13.9 (`.venv`), Python 3.14.3 (System) |
| **Node.js & npm** | Node.js v22.19.0, npm 10.9.3 |
| **Frontend Framework** | Next.js 16.4.4 (Turbopack, App Router, React 19.3.0, React-DOM 19.3.0) |
| **Backend Framework** | FastAPI 0.115+, Uvicorn 0.32+, Pydantic 2.0+ |
| **Database Server** | PostgreSQL 15.x on Supabase Cloud, Region: AWS Ireland (`eu-west-1`) |
| **Connection Endpoint** | `aws-0-eu-west-1.pooler.supabase.com:6543` (PgBouncer Transaction Pooler) |
| **SQLAlchemy Engine** | `postgresql+asyncpg`, `pool_size: 10`, `max_overflow: 5`, `pool_pre_ping: True` |
| **Uvicorn Worker Config** | 1 worker, single event loop (development launcher) |
| **Frontend Server Config** | `next start -p 3001` (production build running locally) |

---

## 3. Frontend Profiling (13 Required Routes)

All 13 required routes were profiled in production build mode (`next start -p 3001`) using Chrome DevTools Performance traces and W3C Navigation / Resource Timing APIs:

| Route | TTFB | FCP | DOM Ready | LCP | Total Resources | API Requests | Duplicate API Calls Observed |
|---|---|---|---|---|---|---|---|
| `/` (Public Landing) | 13.0 ms | 180 ms | 98 ms | **386 ms** | 14 | 0 | None (Static SSR) |
| `/login` | 5.3 ms | 196 ms | 97 ms | **410 ms** | 16 | 0 | None |
| `/register` | 11.7 ms | 204 ms | 225 ms | **450 ms** | 18 | 0 | None |
| `/volunteer/dashboard` | 27.3 ms | 164 ms | 96 ms | **5,110 ms** | 35 | 8 | `/users/me` (2x), `/notifications/unread-count` (2x) |
| `/volunteer/events` | 34.7 ms | 172 ms | 140 ms | **8,740 ms** | 30 | 7 | `/users/me` (2x), `/notifications/unread-count` (2x) |
| `/volunteer/activity` | 6.3 ms | 172 ms | 135 ms | **9,210 ms** | 24 | 8 | `/users/me` (2x), `/notifications/unread-count` (2x) |
| `/volunteer/leaderboard`| 5.4 ms | 172 ms | 140 ms | **4,460 ms** | 25 | 7 | `/users/me` (2x), `/notifications/unread-count` (2x) |
| `/volunteer/profile` | 56.8 ms | 232 ms | 204 ms | **5,260 ms** | 28 | 9 | `/users/me` (2x), `/notifications/unread-count` (2x) |
| `/admin/dashboard` | 4.1 ms | 168 ms | 101 ms | **12,210 ms**| 24 | 4 | `/users/me` (2x) |
| `/admin/applications` | 5.2 ms | 560 ms | 112 ms | **3,490 ms** | 20 | 4 | `/users/me` (2x) |
| `/admin/events` | 3.9 ms | 160 ms | 58 ms | **15,210 ms**| 26 | 4 | `/users/me` (2x) |
| `/admin/reports` | 5.3 ms | 172 ms | 98 ms | **8,700 ms** | 23 | 4 | `/users/me` (2x) |
| `/admin/operations` | 6.6 ms | 116 ms | 59 ms | **3,600 ms** | 22 | 4 | `/users/me` (2x) |

### Frontend Diagnostics & Observations
1. **Fast Initial Asset Delivery:** TTFB is exceptionally fast (< 15 ms), FCP is under 200 ms, and the initial HTML/JS shell renders instantly.
2. **JavaScript Bundle Size is Healthy:** The largest uncompressed JS chunk is 223.7 KB (~65 KB gzipped). Total application JS bundle is lean.
3. **Client-Side Waterfall Bottleneck:** Authenticated routes are delayed by 4 to 15 seconds purely waiting for client-side API fetches (`"use client"` `useEffect` waterfalls).
4. **Duplicate API Triggering:** On every route change, both the Root Layout / Navbar and the page component fire `/users/me` and `/notifications/unread-count` independently because there is no shared client-side request deduplication or cache.

---

## 4. Backend Profiling (15 Core Endpoints)

Measured against the running FastAPI backend under identical authenticated conditions (cold run vs 5-sample median):

| Endpoint | HTTP Method | Cold Latency | Median Latency | Response Size | Sequential DB Roundtrips | Root Cause of Delay |
|---|---|---|---|---|---|---|
| `/api/v1/health` | GET | 1,756.2 ms | **1,609.2 ms** | 195 B | 1 | Pool pre-ping (`SELECT 1`) across Ireland WAN |
| `/api/v1/auth/login` | POST | 4,065.6 ms | **3,685.8 ms** | 727 B | 2 | Pre-ping + User lookup + Sync Argon2id hash |
| `/api/v1/users/me` | GET | 2,384.2 ms | **2,499.1 ms** | 263 B | 2 | Pre-ping + User query + Revocation check |
| `/api/v1/events` | GET | 9,078.6 ms | **9,063.2 ms** | 9,522 B | 21+ | **N+1 loop:** 1 query for events + 20 queries for counts |
| `/api/v1/registrations/me` | GET | 9,523.0 ms | **9,112.5 ms** | 1,529 B | 6 | Sequential `selectinload` for 5 relationships |
| `/api/v1/gamification/summary` | GET | 4,845.0 ms | **6,138.4 ms** | 187 B | 3 | Points sum + rank + achievements queries |
| `/api/v1/gamification/leaderboard` | GET | 5,156.4 ms | **3,106.4 ms** | 97 B | 3 | Subquery count + multi-join points grouping |
| `/api/v1/gamification/ledger` | GET | 4,224.2 ms | **3,899.5 ms** | 481 B | 2 | Count query + paginated ledger query |
| `/api/v1/attendance/me` | GET | 3,378.1 ms | **3,418.7 ms** | 62 B | 2 | Count query + attendance record query |
| `/api/v1/notifications/me` | GET | 5,407.0 ms | **3,499.8 ms** | 75 B | 2 | Count query + notification list query |
| `/api/v1/admin/dashboard` | GET | 7,445.1 ms | **8,151.9 ms** | 2,728 B | 11 | **11 sequential SQL queries** executed in loop |
| `/api/v1/admin/reports/student-contributions` | GET | 2,914.4 ms | **3,079.0 ms** | 5,041 B | 2 | Count query + multi-join student group query |
| `/api/v1/admin/reports/alumni-contributions` | GET | 3,057.9 ms | **2,800.2 ms** | 58 B | 2 | Count query + alumni report query |
| `/api/v1/admin/reports/organisation-contributions` | GET | 3,366.4 ms | **3,250.7 ms** | 58 B | 2 | Count query + org contribution grouping |
| `/api/v1/admin/reports/interview-availability` | GET | 3,990.5 ms | **4,048.8 ms** | 58 B | 2 | Count query + volunteer profile skills query |

---

## 5. Database & Schema Audit

### PostgreSQL Internal Performance (`EXPLAIN ANALYZE`)
To isolate database execution time from network overhead, `EXPLAIN (ANALYZE, BUFFERS)` was executed directly on canonical queries:
- **Events List Query:** Execution Time: **0.101 ms** (Buffers: `shared hit=2`)
- **Event Registrations Status Count:** Execution Time: **0.106 ms** (Buffers: `shared hit=4`)
- **Leaderboard Multi-Join Query:** Execution Time: **0.118 ms** (Buffers: `shared hit=4`)

**Conclusion:** The database engine executes queries in less than **0.2 milliseconds**. 99.9% of backend latency is network traversal over the Ireland WAN.

### Foreign Key Index Coverage Audit
Of 44 foreign keys in the database:
- **Indexed:** 30
- **Missing Indexes:** 14

The following foreign keys lack explicit indexes:
1. `point_transactions.event_id` *(impacts event-point queries)*
2. `point_transactions.awarded_by_user_id`
3. `point_transactions.related_transaction_id`
4. `attendance_records.verified_by_user_id`
5. `registration_history.changed_by_user_id`
6. `events.cover_media_id`
7. `volunteer_profiles.avatar_media_id`
8. `volunteer_profiles.parental_consent_document_media_id`
9. `volunteer_profiles.parental_consent_verified_by_user_id`
10. `consent_history.changed_by_user_id`
11. `admin_permissions.granted_by_user_id`
12. `attendance_corrections.super_admin_approved_by`
13. `communication_logs.job_id`
14. `report_exports.file_media_id`

### Connection Pool Configuration Audit
- Current settings in `server/src/core/database.py`:
  - `pool_size: 10`, `max_overflow: 5`
  - `pool_pre_ping: True`
  - `statement_cache_size: 0` (required for PgBouncer transaction mode)
- **Critical Finding:** `pool_pre_ping: True` forces SQLAlchemy to emit `SELECT 1` on every connection checkout. Because each round trip to Ireland costs ~1.9s, **every single database session suffers an automatic 1.9s penalty**. When multiple requests arrive concurrently, connections are held for 8–15 seconds, exhausting the 10-connection pool.

---

## 6. Server & Worker Concurrency Audit

1. **Uvicorn Worker Count:**
   - The server runs with **1 worker** (`uvicorn src.main:app`).
   - With 1 worker on a single event loop, any blocking operation freezes all requests across all users.
2. **Synchronous CPU-Bound Argon2id:**
   - In `server/src/core/security.py`, `verify_password` and `get_password_hash` invoke `_argon2_hasher.verify(...)` directly in the async thread.
   - Argon2id consumes 100% of a CPU core for ~150–250 ms, completely halting event loop scheduling during every login or registration.
3. **Synchronous Excel Export File Generation:**
   - In `server/src/services/report_service.py`, `export_report_to_excel` builds `openpyxl.Workbook()`, formats cells, and serializes bytes synchronously on the async event loop.
4. **Transactional Outbox Background Worker:**
   - The outbox worker polls PostgreSQL every 5 seconds. Each poll checks out a connection and runs `SELECT 1` (pre-ping) + outbox query, competing with API traffic for connection slots.

---

## 7. Safe Concurrency & Load Testing

A safe, read-only load test was executed across concurrency levels of 1, 5, 10, and 25 virtual users using persistent HTTP connection pooling (`server/load_test_results.json`):

### 1. `/api/v1/health` (Lightweight DB Ping)
| Concurrency | Requests | Duration | RPS | Median Latency | p95 Latency | Error Rate |
|---|---|---|---|---|---|---|
| **1** | 10 | 20.6 s | 0.48 | 1,881.7 ms | 3,855.7 ms | 0.0% |
| **5** | 10 | 5.1 s | 1.95 | 1,906.2 ms | 3,222.6 ms | 0.0% |
| **10** | 20 | 4.3 s | 4.65 | 1,945.9 ms | 2,417.6 ms | 0.0% |
| **25** | 50 | 7.6 s | 6.56 | 2,962.4 ms | 3,976.1 ms | 0.0% |

### 2. `/api/v1/gamification/leaderboard` (Moderate SQL Query)
| Concurrency | Requests | Duration | RPS | Median Latency | p95 Latency | Error Rate |
|---|---|---|---|---|---|---|
| **1** | 10 | 38.6 s | 0.26 | 3,776.0 ms | 4,667.4 ms | 0.0% |
| **5** | 10 | 6.0 s | 1.67 | 2,446.0 ms | 3,538.5 ms | 0.0% |
| **10** | 20 | 7.5 s | 2.68 | 2,850.5 ms | 4,551.9 ms | 0.0% |
| **25** | 50 | 11.2 s | 4.46 | 4,643.1 ms | 5,665.9 ms | 0.0% |

### 3. `/api/v1/events` (N+1 Bottleneck Endpoint)
| Concurrency | Requests | Duration | RPS | Median Latency | p95 Latency | Error Rate |
|---|---|---|---|---|---|---|
| **1** | 6 | 55.4 s | 0.11 | 9,372.5 ms | 10,606.1 ms | 0.0% |
| **5** | 10 | 17.0 s | 0.59 | 8,261.6 ms | 8,718.2 ms | 0.0% |
| **10** | 20 | 18.5 s | 1.08 | 8,371.3 ms | 10,110.5 ms | 0.0% |

**Key Takeaway:** The backend can handle concurrent requests without errors (0.0% error rate), but throughput is severely throttled (0.11 to 6.56 RPS) purely because connections are tied up waiting for 8–10 seconds of round-trip network hops per request.

---

## 8. Prioritized Findings & Optimization Plan

We have classified all findings into **P0 (Critical / Mandatory)**, **P1 (High Impact)**, **P2 (Medium Impact)**, and **P3 (Housekeeping / Polish)**.

### Priority P0: Critical Bottlenecks (5x to 10x Speedup)

#### 1. Fix N+1 Query in `GET /api/v1/events`
- **Root Cause:** `event_service.py` calls `await event_repository.get_registration_counts(db, ev.id)` inside a sequential `for ev in events:` loop. Each event adds 1 Ireland network round trip (~1.9s).
- **Proposed Solution:** Replace the loop with a single grouped batch query:
  `SELECT event_id, status, count(*) FROM event_registrations WHERE event_id = ANY(:event_ids) GROUP BY event_id, status;`
- **Expected Benefit:** Latency drops from **9,063 ms to ~2,100 ms** (a ~77% latency reduction).
- **Regression Risk:** Low. Return dictionary mapping preserves identical schema format.

#### 2. Combine 11 Queries in `GET /api/v1/admin/dashboard` into a Single SQL CTE
- **Root Cause:** `report_repo.py` executes 11 separate SQL queries sequentially (total volunteers, approved applications, events published, total hours, points, monthly trends, donut breakdown, etc.).
- **Proposed Solution:** Combine the scalar counts into a single CTE query:
  ```sql
  WITH counts AS (
      SELECT 
          (SELECT count(*) FROM users WHERE role = 'VOLUNTEER') AS total_volunteers,
          (SELECT count(*) FROM applications WHERE status = 'PENDING') AS pending_applications,
          (SELECT count(*) FROM events WHERE status = 'PUBLISHED') AS active_events,
          ...
  )
  SELECT * FROM counts;
  ```
- **Expected Benefit:** Latency drops from **8,151 ms to ~2,000 ms** (a ~75% reduction).
- **Regression Risk:** Low. Returns exact same metric fields.

#### 3. Eliminate Connection Checkout Penalty (`pool_pre_ping`)
- **Root Cause:** `pool_pre_ping: True` in `server/src/core/database.py` issues a `SELECT 1` ping across the Ireland WAN on every single request checkout, adding ~1,900 ms to every endpoint.
- **Proposed Solution:** Disable `pool_pre_ping: False` for pooled PgBouncer connections, relying instead on asyncpg connection error recycling with `pool_recycle: 300` and graceful retry.
- **Expected Benefit:** Strips **~1,900 ms off EVERY endpoint across the entire application**.
- **Regression Risk:** Low, provided stale connection exceptions trigger pool retry.

#### 4. Frontend Request Deduplication & In-Memory Client Cache
- **Root Cause:** Both the layout/navbar and the page components fire separate fetch calls to `/users/me` and `/notifications/unread-count` simultaneously on every navigation.
- **Proposed Solution:** Implement a lightweight in-flight promise deduplicator and 30-second stale-while-revalidate memory cache in `web/src/lib/api-client.ts`. If a request for an endpoint is already pending, return the existing promise.
- **Expected Benefit:** Eliminates 3 to 5 redundant backend calls per page navigation, reducing client network requests by 50% and cutting LCP by 2–4 seconds.
- **Regression Risk:** None. Purely client-side cache for read-only metadata.

---

### Priority P1: High Impact Optimizations (2x to 3x Speedup)

#### 5. Offload Argon2id Hashing to `asyncio.to_thread`
- **Root Cause:** `_argon2_hasher.verify` blocks the Python GIL and event loop during authentication.
- **Proposed Solution:** Wrap calls with `await asyncio.to_thread(security.verify_password, ...)` and `await asyncio.to_thread(security.get_password_hash, ...)`.
- **Expected Benefit:** Prevents event loop freezing during logins and user registrations; allows other concurrent requests to proceed smoothly.
- **Regression Risk:** Very low. Standard asyncio best practice for CPU-bound hashing.

#### 6. Optimize Relation Loading in `GET /api/v1/registrations/me`
- **Root Cause:** SQLAlchemy issues 5 sequential `selectinload` queries to load `event`, `cover_media`, `location`, `attendance_record`, and `cancellation_reason`.
- **Proposed Solution:** Use `joinedload` on the 1-to-1 relations (`event`, `event.cover_media`) in a single query instead of 5 separate round trips.
- **Expected Benefit:** Latency drops from **9,112 ms to ~2,500 ms**.
- **Regression Risk:** Low. Verify ORM schema relationships.

#### 7. Offload Excel Export to `asyncio.to_thread`
- **Root Cause:** `export_report_to_excel` builds `openpyxl` workbooks synchronously in the async event loop.
- **Proposed Solution:** Move the Excel workbook generation function into a separate sync helper and run it via `await asyncio.to_thread(generate_workbook, ...)`.
- **Expected Benefit:** Prevents server freeze during admin report exports.
- **Regression Risk:** None.

---

### Priority P2: Medium Impact Database & Connection Tuning

#### 8. Add Missing Foreign Key Indexes
- **Root Cause:** 14 foreign keys lack PostgreSQL indexes, notably `point_transactions.event_id`.
- **Proposed Solution:** Create an Alembic migration adding indexes on `point_transactions.event_id`, `attendance_records.verified_by_user_id`, etc.
- **Expected Benefit:** Ensures query planning remains sub-millisecond as table row counts scale into tens of thousands.
- **Regression Risk:** Low. Safe non-breaking index creation.

#### 9. Increase Uvicorn Worker Count in Production
- **Root Cause:** 1 worker limits concurrency to single-core processing.
- **Proposed Solution:** Configure Uvicorn with `workers: 4` in production mode (matching the 4 physical CPU cores).
- **Expected Benefit:** Increases server throughput (RPS) by ~300% under concurrent traffic.
- **Regression Risk:** None on production servers.

---

### Priority P3: Polish & Client-Side Hydration Smoothing

#### 10. Skeleton Loaders & Optimistic SWR in Frontend
- **Root Cause:** Loading states show full-page spinner or blank layout until all API promises resolve.
- **Proposed Solution:** Retain instant UI navigation using cached user profile and render subtle card skeletons while background SWR data refreshes.
- **Expected Benefit:** Perceived load time drops to under 300 ms.
- **Regression Risk:** None.

---

## 9. Verification & Stop Gate

In accordance with strict project guidelines:
- **No changes to schemas, business logic, or code have been executed during this audit.**
- **No new infrastructure dependencies (such as Redis or Celery) have been introduced.**
- **All 15 canonical phase documents in `docs/phases/` remain strictly untouched.**

**Next Action:** Await user review and explicit approval of the prioritized optimization plan (P0, P1, P2) before implementing any code changes.

