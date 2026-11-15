# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## Production Timeout Architecture & Multi-Layer Audit Report

**Date**: November 15, 2026  
**Status**: APPROVED & IMPLEMENTED  
**Scope**: Full Stack (Next.js Web Frontend, Flutter Mobile App, FastAPI Backend, PostgreSQL/Supabase, Render Infrastructure)

---

## 1. Executive Summary

A comprehensive, end-to-end timeout audit was conducted across all tiers of the Maatram platform. Prior to this initiative, arbitrary and scattered timeout values (e.g., 2.0-second database readiness probes, 15-second hardcoded frontend timeouts, 10-second third-party HTTP client timeouts) posed severe false-positive failure risks under high concurrent load or transient network latency.

All timeouts across the frontend, mobile application, backend, and persistence tiers have been unified, modernized, and made environment-configurable. The system now enforces a clear timeout hierarchy:

```
+-----------------------------------------------------------------------------------+
| Multi-Tier Timeout Budget & Hierarchy                                             |
+-----------------------------------------------------------------------------------+
| 1. Render Proxy Level:            100s Hard Cutoff                                |
| 2. File Upload / Binary Export:    60s Maximum Timeout (Configurable)              |
| 3. Normal API Execution:           30s Maximum Timeout (Configurable)              |
| 4. Database Pool Checkout:         30s Maximum Pool Acquisition Wait               |
| 5. Third-Party Integrations:       15s Strict Bound (Resend, Cloudinary, FCM)      |
| 6. Mobile / Frontend Connect:      10s Connection Handshake Bound                 |
| 7. UI Slow Connection Notice:       5s Non-Blocking Warning Threshold             |
| 8. Database Readiness Probe:        5s Health Probe Bound (Prevents Pod Restarts)  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Comprehensive Timeout Inventory

| Layer | File / Module | Parameter / Configuration | Previous Value | Production Value | Purpose & Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Web Frontend** | `web/src/lib/api-client.ts` | `DEFAULT_TIMEOUT_MS` | `15000` (15s) | `30000` (30s) / Env: `NEXT_PUBLIC_API_TIMEOUT_MS` | Standard API request timeout for CRUD, dashboard, and gamification endpoints. |
| **Web Frontend** | `web/src/lib/api-client.ts` | `DEFAULT_UPLOAD_TIMEOUT_MS` | `30000` (30s) | `60000` (60s) / Env: `NEXT_PUBLIC_API_UPLOAD_TIMEOUT_MS` | Binary Excel report exports and multipart photo uploads. |
| **Web Frontend** | `web/src/lib/api-client.ts` | `SLOW_CONNECTION_THRESHOLD_MS` | *None* | `5000` (5s) / Env: `NEXT_PUBLIC_API_SLOW_WARNING_MS` | Threshold to notify users of network degradation without canceling in-flight request. |
| **Web Frontend** | `web/src/lib/api-client.ts` | GET Retry Strategy | *None* | 2 retries (1s, 2s + jitter) | Bounded exponential backoff on transient 0, 408, 503, 504 errors. |
| **Mobile App** | `mobile/lib/core/config/env_config.dart` | `connectTimeout` | `15s` | `10s` / Env: `API_CONNECT_TIMEOUT_SEC` | Fast failure on dead or unreachable network sockets. |
| **Mobile App** | `mobile/lib/core/config/env_config.dart` | `receiveTimeout` | `15s` | `30s` / Env: `API_RECEIVE_TIMEOUT_SEC` | Accommodates server response processing under load. |
| **Mobile App** | `mobile/lib/core/network/api_client.dart` | GET Retry Strategy | *None* | 2 retries (1s, 2s) | Bounded retry loop for idempotent reads on timeout or 503/504. |
| **Backend API** | `server/src/api/v1/health.py` | `timeout` in `check_readiness` | `2.0s` | `5.0s` / Settings: `DB_READINESS_TIMEOUT_SECONDS` | Prevents false-positive container restarts on cold starts or pool waits. |
| **Backend DB** | `server/src/core/database.py` | `command_timeout` (asyncpg) | `60s` | `60s` | Server-side query execution timeout preventing runaway transactions. |
| **Backend DB** | `server/src/core/config.py` | `DB_POOL_TIMEOUT` | `30s` | `30s` | Maximum time to acquire a connection from the SQLAlchemy connection pool. |
| **Backend DB** | `server/src/core/config.py` | `DB_POOL_RECYCLE` | `300s` (5m) | `300s` (5m) | Recycles idle connections to avoid stale TCP drops by Supabase pooler. |
| **Backend Email**| `server/src/integrations/resend_client.py`| `httpx.AsyncClient(timeout)` | `10.0s` | `15.0s` / Settings: `RESEND_TIMEOUT_SECONDS` | Third-party email API dispatch timeout. |
| **Outbox Worker**| `server/src/workers/outbox_worker.py` | `lease_timeout_seconds` | `300s` (5m) | `300s` (5m) | Protects against dead-worker lock starvation on outbox tasks. |
| **Hosting Proxy**| Render.com Infrastructure | `HTTP Request Timeout` | `100s` | `100s` (Fixed by Render) | Top-level reverse proxy connection termination. |
| **DB Pooler** | Supabase Transaction Pooler | `pool_timeout` | `30s` | `30s` | Prevents transaction hanging in PgBouncer. |

---

## 3. UI/UX Loading & Resilience Enhancements

1. **Zero Premature Cancellation**:
   - The frontend never aborts or displays failure messages simply because an arbitrary 5-second UI threshold passed.
   - Loaders and skeletons remain active throughout the 30-second budget.

2. **Non-Blocking Slow Connection Notification**:
   - If a request remains in-flight beyond 5.0 seconds, `activeSlowRequestsCount` triggers `onSlowConnectionChange` callbacks.
   - Applications can render subtle indicators ("Connecting over a slow network...") while preserving user context.

3. **Strict Idempotency in Retry Strategy**:
   - Auto-retry is strictly restricted to HTTP `GET` requests.
   - Mutating HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`) are **never** retried automatically to prevent duplicate registrations, attendance entries, or points awards.
   - Retries apply bounded exponential backoff ($1000\text{ms} \times 2^{\text{attempt}} + \text{jitter}$) with a maximum of 2 retries (3 total attempts).

4. **Preservation of Previous Data (SWR)**:
   - Read-heavy queries are served immediately from in-memory cache while revalidating in the background, preventing flickering blank screens.

