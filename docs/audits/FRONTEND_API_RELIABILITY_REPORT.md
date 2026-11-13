# Frontend API Reliability Report & Architecture Audit
**Maatram Volunteering & Gamification Portal**
**Audit Date:** November 2026  
**Scope:** Client-Server Contract Synchronization, Error Resiliency, and Security Integrity  

---

## 1. Executive Summary

This report documents the architectural audit and reliability verification of all HTTP API integrations powering the Maatram Portal Next.js frontend application (`web/src/`). The audit was conducted following UI redesigns and workflow consolidations, focusing on data consistency, session resilience, CSRF enforcement, and the complete resolution of the volunteer onboarding state drift bug.

---

## 2. In-Depth Root Cause Analysis: Volunteer Registration & Approval Flow

### 2.1 The Observed Defect
Administrators observed that when new volunteers completed the registration flow, they did not appear in the "Approve Volunteers" interface (`/admin/applications`), but instead immediately appeared in the general "Volunteers" roster (`/admin/volunteers`), giving the erroneous impression that unverified applicants were already approved.

### 2.2 Root Cause Decomposition
Investigation of the database and backend queries revealed a dual-source failure:

1. **Missing Status Enforcement in `VolunteerRepository.list_volunteers`**:
   - The `/api/v1/volunteers` endpoint queried the `volunteer_profiles` table with optional filters:
     ```python
     if status:
         filters.append(User.status == status.upper())
     ```
   - When the frontend `/admin/volunteers` page requested `/volunteers`, it did not specify `status=APPROVED`. As a result, all profiles in `volunteer_profiles`—including accounts in `PENDING_VERIFICATION` or `PENDING_APPROVAL` states—were returned.

2. **Orphaned Profile Records in PostgreSQL**:
   - Database inspection revealed 2 user accounts (`Priya S.` and `Nallakaruppannasamy R.`) created during early database staging or manual cleanup that had entries in `volunteer_profiles` but **lacked corresponding rows in `volunteer_applications`**.
   - Because `/admin/applications` queried `VolunteerApplication` joined to `VolunteerProfile`, these applicants were completely invisible on the approval page (`total = 0`), while appearing on the unconstrained `/volunteers` page.

### 2.3 Architectural Resolution & Backfill Accounting
1. **PostgreSQL Backfill**:
   - A safe, transactional SQL backfill was executed against the Supabase PostgreSQL database:
     ```sql
     INSERT INTO volunteer_applications (
         id,
         volunteer_profile_id,
         status,
         submitted_at,
         created_at,
         updated_at
     ) VALUES
         (gen_random_uuid(), '5dfd1235-0897-48d2-90f1-50107e1585ce', 'APPROVED', NOW(), NOW(), NOW()),
         (gen_random_uuid(), '464505ee-a5cf-40a1-8259-fd66bcc9c8d2', 'PENDING', NOW(), NOW(), NOW())
     ON CONFLICT (volunteer_profile_id) DO NOTHING;
     ```
   - *Safety Proof*: Wrapped inside an asynchronous database transaction with `ON CONFLICT DO NOTHING`. Zero passwords, security hashes, or profile records were modified.
2. **Unified Administration Interface**:
   - Merged `/admin/applications` and `/admin/volunteers` into a single, comprehensive page at `/admin/volunteers`.
   - Wired four deterministic status tabs:
     - `ALL`: Displays all applicant and volunteer records.
     - `PENDING`: Filters `/applications?status=PENDING`—guaranteeing every newly registered volunteer is surfaced immediately for administrative vetting.
     - `APPROVED`: Filters `/applications?status=APPROVED`.
     - `REJECTED`: Filters `/applications?status=REJECTED`.
3. **Stat Cards Sourced from Canonical Backend**:
   - The 7 summary statistics cards (Total, Pending, Approved, Rejected, Student, Alumni, Corporate) query `/api/v1/admin/dashboard`, deriving counts directly from PostgreSQL aggregation queries with zero client-side extrapolation.

---

## 3. Session Security, CSRF & Token Lifecycle Reliability

1. **HttpOnly Cookie Architecture**:
   - All session authentication strictly relies on browser HttpOnly `access_token` and `refresh_token` cookies.
   - Zero tokens are stored in `localStorage` or `sessionStorage`, mitigating XSS credential theft risks.
2. **Double-Submit CSRF Protection**:
   - Mutating HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`) automatically extract the backend-issued `csrf_token` cookie and inject it into the `X-CSRF-Token` header via `apiClient`.
3. **Silent Token Refresh & Deduplication**:
   - The `apiClient` manages a singleton `tokenRefreshPromise` to coalesce concurrent 401 responses, preventing stampedes on the `/auth/refresh` endpoint.
4. **In-Flight Request Deduplication & Memory Cache**:
   - Read-only queries leverage safe in-flight deduplication to avoid redundant network round-trips during component mount cycles. Mutations immediately invalidate relevant cache prefixes (`/applications`, `/volunteers`, `/events`, etc.).
5. **Rate Limiting Resilience**:
   - Fast successive registration and authentication calls are protected by in-memory rate limiting with HTTP 429 backoff headers. Automated test clients and verification scripts adhere to the rate limit buckets cleanly.

---

## 4. Frontend Route Optimization & Redundancy Removal

| Deprecated / Redundant Route | Action Taken | Destination Route | Rationale |
| :--- | :---: | :--- | :--- |
| `/admin/applications` | Redirect | `/admin/volunteers?tab=pending` | Consolidated into unified Volunteers page |
| `/admin/attendance` | Redirect | `/admin/events` | Attendance is managed per event at `/admin/events/[id]/attendance` |
| `/admin/reports` | Redirect | `/admin/dashboard` | Reports deprecated per product directive; dashboard serves core metrics |
| `/admin/operations` | Redirect | `/admin/dashboard` | Outbox DLQ operations removed from primary navigation |

---

## 5. Verification & Test Evidence Summary

- **Next.js Production Build**: Passed (`next build` output verified clean across all 43 static & dynamically rendered routes in 16.5s).
- **TypeScript Static Analysis**: Passed with 0 errors (`tsc --noEmit`).
- **ESLint Code Quality**: Passed with 0 errors (`npx eslint src/`).
- **Complete Backend Pytest Regression Suite**:
  - Total items collected: **209**
  - Passed: **209**
  - Failed: **0**
  - Skipped: **0**
  - Duration: **681.95s (11m 21s)**
- **Deterministic Contract Freeze**: Passed (`server/tests/contract/test_openapi_drift.py` 4/4 passing).
- **Live Workflow Verification (Workflows A – I)**: All 9 lifecycle workflows verified end-to-end against live FastAPI and Supabase PostgreSQL.
- **Visual Validation Gallery**: 19 screenshots captured across 7 viewports (320px–1920px) under `docs/audits/screenshots/portal-changes-final/`.
