# Maatram Portal — Performance & Reliability: Remaining Risks & Mitigations

**Document Version**: 1.1  
**Date**: 2026-11-15  
**Context**: Final Operational Risk Assessment after Performance Initiative Closure

---

## 1. Overview

Following the completion and verification of the Performance and Timeout Reliability initiatives, the codebase is in a hardened, low-latency state. This document maintains the operational risk registry for the production rollout.

---

## 2. Updated Risk Matrix

| Risk ID | Category | Description | Likelihood | Impact | Severity | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | Database | Supabase connection exhaustion if direct port (5432) is used with $>2$ workers | High | High | **CRITICAL** | Action Required in Production Env |
| **RSK-02** | Database | Suboptimal index definition on `consent_records` in staged migration | None | None | **RESOLVED** | Fixed in Migration `e4f5a6b7c8d9` |
| **RSK-03** | Testing | In-process ASGI test does not simulate external TLS/proxy network latency | Medium | Medium | **MEDIUM** | Mitigated via `STAGING_LOAD_TEST_PLAN.md` |
| **RSK-04** | Performance | In-memory cache disabled by default leaves direct DB queries under high spike | Low | Medium | **LOW** | Direct DB queries $<25$ms |
| **RSK-05** | Network | Large media uploads on rural/slow 3G connections exceeding 60s | Medium | Low | **LOW** | Client-side compression planned |

---

## 3. Analysis & Actionable Mitigations

### 3.1 RSK-01: Supabase Connection Pool Exhaustion on Direct Port (Critical)
* **Risk Description**:
  The Supabase Free/Starter plan allows a maximum of **60 direct PostgreSQL connections** (port 5432). FastAPI’s SQLAlchemy engine is configured with `pool_size = 10` and `max_overflow = 5` per Uvicorn worker ($15\text{ connections/worker}$). If production is configured with 4 Uvicorn workers, peak connection demand is $4 \times 15 = 60\text{ connections}$ ($100\%$ of the database limit), risking `FATAL: remaining connection slots are reserved for non-replication superuser connections`.
* **Actionable Mitigation**:
  1. In production Render environment variables, configure `DATABASE_URL` to route through the **Supabase Transaction Pooler (PgBouncer, Port 6543)** rather than the direct port (5432).
  2. Set `connect_args={"prepared_statement_cache_size": 0}` in `create_async_engine` when using PgBouncer in transaction mode to prevent prepared statement conflicts.

---

### 3.2 RSK-02: Staged Migration Index Refinement — RESOLVED
* **Resolution**:
  In `e4f5a6b7c8d9_performance_composite_indexes.py`, the ineffective `ix_consent_records_volunteer_visible` index was **removed**.
  - The existing unique index `uq_consent_records_volunteer_profile_id` satisfies $O(1)$ single-volunteer lookups.
  - The migration now contains exactly the 2 high-impact composite indexes:
    1. `ix_volunteer_applications_status_submitted` on `volunteer_applications (status, submitted_at)`.
    2. `ix_point_transactions_volunteer_created` on `point_transactions (volunteer_profile_id, created_at)`.
  - Offline `--sql` upgrade and downgrade operations verified with zero errors.

---

### 3.3 RSK-03: Real-World Network & Reverse Proxy Latency
* **Risk Description**:
  The 50-user concurrent load test was executed in-process using ASGI transport. Real production traffic experiences TCP handshakes, TLS termination, Render reverse proxy buffer limits, and ISP cellular latency.
* **Actionable Mitigation**:
  - Execute the dedicated load testing specification detailed in [`docs/performance/STAGING_LOAD_TEST_PLAN.md`](file:///c:/Users/Logesh/Documents/Maatram_Gamification/docs/performance/STAGING_LOAD_TEST_PLAN.md) using k6 against an isolated staging environment across 50, 100, and 200 virtual user ramps before production launch.

---

### 3.4 RSK-04: Caching Strategy at Scale (Multi-Worker Consistency)
* **Risk Description**:
  To protect against stale data across multiple Uvicorn workers without introducing unnecessary distributed infrastructure, `ENABLE_IN_MEMORY_CACHE` was set to `False` by default. While single-query latencies are currently $<25$ ms on PostgreSQL, sustained concurrent traffic of $>500$ users querying published events simultaneously may increase database CPU usage.
* **Actionable Mitigation**:
  - For public read-only event discovery, leverage **HTTP-level edge caching** (e.g. Cloudflare / CDN caching on `/api/v1/events?status=PUBLISHED` with `Cache-Control: public, max-age=30, stale-while-revalidate=60`).
  - Edge caching requires zero code changes in the monolith, zero Redis infrastructure, and shields the database entirely during viral social media traffic spikes.

---

### 3.5 RSK-05: Uploading Media Over Rural Mobile Connections
* **Risk Description**:
  While the upload timeout was increased to 60 seconds, volunteer event photo uploads from rural colleges in Tamil Nadu using 2G/3G mobile networks may still encounter timeouts if uploading raw, uncompressed 10 MB+ photos.
* **Actionable Mitigation**:
  - In the Flutter mobile client (`mobile/`), enforce client-side image compression (down to 1080p, quality 85%, $<800$ KB) before dispatching the `apiUpload` multipart request.
  - This ensures uploads complete in under 5 seconds even on constrained 3G cellular connections.
