# Backend & API Production-Readiness Audit
**Maatram Volunteering & Mentorship Portal**  
**Audit Stream**: Stream 1 — Backend & API Infrastructure  
**Target Environment**: FastAPI Backend (`http://127.0.0.1:8000`), Python 3.13.9, PostgreSQL (Supabase Pooler/Direct)  
**Status**: AUDIT COMPLETE  

---

## 1. Executive Summary

This independent, evidence-based audit provides a systematic inspection of all FastAPI v1 routes, request/response DTO schemas, repository query efficiency, pagination policies, error-handling conventions, and sensitive data protections in the Maatram Volunteering & Mentorship Portal backend.

The backend implementation exhibits high architectural discipline adhering to the modular monolith pattern, strict Pydantic v2 data models, centralized dependency injection for RBAC/BOLA, and zero exposure of password hashes or raw secrets. However, the audit identified key production risks:
- Inconsistent pagination parameter nomenclature (`page_size` vs `limit`) and unbounded list endpoints.
- N+1 query patterns in high-throughput administrative batch operations (`check_in_volunteers`, `select_volunteers_batch`).
- Schema property drift between FastAPI models and Next.js TypeScript definitions (`EventResponse` vs `EventItem`).
- Dual error envelope structures where native Starlette 404/405 errors return `{"detail": "..."}` while domain errors return `{"error_code": "...", "message": "..."}`.

---

## 2. API Route & Method Inventory

The backend router registry aggregates 14 sub-routers mounted at `/api/v1` via `server/src/api/v1/router.py`. Inspection of the live OpenAPI specification (`/api/v1/openapi.json`) and AST parsing of `server/src/api/v1/*.py` confirms **94 unique URI paths** representing **104 endpoint operations**.

### Master Route Inventory Table

| HTTP Method | API Path | Source Module | Auth Required | Authorized Roles | Request Body / Query | Response Model |
|:---|:---|:---|:---:|:---|:---|:---|
| `GET` | `/` | `main.py` | No | Public | None | `dict[str, Any]` |
| `GET` | `/api/v1/health` | `health.py` | No | Public | None | `HealthResponse` |
| `POST` | `/api/v1/auth/register` | `auth.py` | No | Public | `RegisterRequest` | `RegisterResponse` |
| `POST` | `/api/v1/auth/login` | `auth.py` | No | Public | `LoginRequest` | `TokenResponse` |
| `POST` | `/api/v1/auth/refresh` | `auth.py` | No | Public (Cookie/Body) | `RefreshRequest` | `TokenResponse` |
| `POST` | `/api/v1/auth/logout` | `auth.py` | Yes | Authenticated User | None | `MessageResponse` |
| `POST` | `/api/v1/auth/logout-all` | `auth.py` | Yes | Authenticated User | None | `MessageResponse` |
| `POST` | `/api/v1/auth/verify-email` | `auth.py` | No | Public | `VerifyEmailRequest` | `VerifyEmailResponse` |
| `POST` | `/api/v1/auth/password-reset/request` | `auth.py` | No | Public | `PasswordResetRequest` | `MessageResponse` |
| `POST` | `/api/v1/auth/password-reset/confirm` | `auth.py` | No | Public | `PasswordResetConfirmRequest` | `MessageResponse` |
| `GET` | `/api/v1/users/me` | `users.py` | Yes | Authenticated User | None | `UserMeResponse` |
| `GET` | `/api/v1/users/me/sessions` | `users.py` | Yes | Authenticated User | None | `list[SessionResponse]` |
| `DELETE` | `/api/v1/users/me/sessions/{session_id}` | `users.py` | Yes | Authenticated User | None | `MessageResponse` |
| `GET` | `/api/v1/volunteers/me` | `volunteers.py` | Yes | Authenticated User | None | `VolunteerProfileResponse` |
| `PATCH` | `/api/v1/volunteers/me` | `volunteers.py` | Yes | Authenticated User | `VolunteerProfileUpdate` | `VolunteerProfileResponse` |
| `GET` | `/api/v1/volunteers` | `volunteers.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `category`, `user_status`, `page`, `page_size` | `VolunteerListResponse` |
| `GET` | `/api/v1/volunteers/me/registrations` | `volunteers.py` | Yes | Authenticated User | `page`, `limit` | `RegistrationListResponse` |
| `GET` | `/api/v1/volunteers/{profile_id}` | `volunteers.py` | Yes | Self or Admin (BOLA) | None | `VolunteerProfileResponse` |
| `GET` | `/api/v1/applications/me` | `applications.py` | Yes | Authenticated User | None | `ApplicationResponse` |
| `GET` | `/api/v1/applications` | `applications.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `status`, `category`, `page`, `page_size` | `ApplicationListResponse` |
| `GET` | `/api/v1/applications/{application_id}` | `applications.py` | Yes | Self or Admin (BOLA) | None | `ApplicationDetailResponse` |
| `POST` | `/api/v1/applications/{application_id}/approve` | `applications.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `ApplicationApproveRequest` | `ApplicationResponse` |
| `POST` | `/api/v1/applications/{application_id}/reject` | `applications.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `ApplicationRejectRequest` | `ApplicationResponse` |
| `POST` | `/api/v1/applications/{application_id}/verify-parental-consent` | `applications.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `ParentalConsentVerifyRequest` | `VolunteerProfileResponse` |
| `GET` | `/api/v1/consent/me` | `consent.py` | Yes | Authenticated User | None | `ConsentResponse` |
| `PUT` | `/api/v1/consent/me` | `consent.py` | Yes | Authenticated User | `ConsentUpdate` | `ConsentResponse` |
| `GET` | `/api/v1/consent/me/history` | `consent.py` | Yes | Authenticated User | None | `ConsentHistoryResponse` |
| `GET` | `/api/v1/events` | `events.py` | Yes | Authenticated User | `status`, `category`, `page`, `limit` | `EventListResponse` |
| `POST` | `/api/v1/events` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `EventCreateRequest` | `EventResponse` |
| `GET` | `/api/v1/events/{event_id}` | `events.py` | Yes | Authenticated User | None | `EventResponse` |
| `PATCH` | `/api/v1/events/{event_id}` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `EventUpdateRequest` | `EventResponse` |
| `POST` | `/api/v1/events/{event_id}/publish` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `EventResponse` |
| `POST` | `/api/v1/events/{event_id}/close-registrations` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `EventResponse` |
| `POST` | `/api/v1/events/{event_id}/start` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `EventResponse` |
| `POST` | `/api/v1/events/{event_id}/cancel` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `EventStatusTransitionRequest` | `EventResponse` |
| `POST` | `/api/v1/events/{event_id}/duplicate` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `EventDuplicateRequest` | `EventResponse` |
| `POST` | `/api/v1/events/{event_id}/register` | `events.py` | Yes | Approved Volunteer | None | `RegistrationResponse` |
| `POST` | `/api/v1/events/{event_id}/withdraw` | `events.py` | Yes | Self or Admin (BOLA) | `WithdrawRequest` | `RegistrationResponse` |
| `GET` | `/api/v1/events/{event_id}/registrations` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `status`, `page`, `limit` | `RegistrationListResponse` |
| `POST` | `/api/v1/events/{event_id}/registrations/select-batch` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `BatchSelectionRequest` | `BatchSelectionResponse` |
| `POST` | `/api/v1/events/{event_id}/registrations/mark-not-selected` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `BatchSelectionRequest` | `BatchSelectionResponse` |
| `POST` | `/api/v1/events/{event_id}/registrations/{registration_id}/promote-waitlist` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `RegistrationResponse` |
| `GET` | `/api/v1/events/{event_id}/completion-preview` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `EventCompletionPreviewResponse` |
| `POST` | `/api/v1/events/{event_id}/complete` | `events.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `EventCompletionResponse` |
| `GET` | `/api/v1/events/{event_id}/attendance` | `attendance.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `status_filter`, `page`, `page_size` | `AttendanceListResponse` |
| `POST` | `/api/v1/events/{event_id}/attendance/check-in` | `attendance.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `CheckInRequest` | `list[AttendanceRecordResponse]` |
| `POST` | `/api/v1/events/{event_id}/attendance/check-out` | `attendance.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `CheckOutRequest` | `list[AttendanceRecordResponse]` |
| `POST` | `/api/v1/events/{event_id}/attendance/bulk` | `attendance.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `BulkAttendanceRequest` | `BulkAttendanceResponse` |
| `POST` | `/api/v1/attendance/{record_id}/correct` | `attendance.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `AttendanceCorrectionRequest` | `AttendanceRecordResponse` |
| `GET` | `/api/v1/attendance/me` | `attendance.py` | Yes | Authenticated User | `page`, `page_size` | `AttendanceListResponse` |
| `GET` | `/api/v1/volunteers/me/attendance` | `attendance.py` | Yes | Authenticated User | `page`, `page_size` | `AttendanceListResponse` |
| `GET` | `/api/v1/registrations/me` | `registrations.py` | Yes | Authenticated User | `page`, `limit` | `RegistrationListResponse` |
| `GET` | `/api/v1/registrations/{registration_id}` | `registrations.py` | Yes | Self or Admin (BOLA) | None | `RegistrationResponse` |
| `POST` | `/api/v1/registrations/{registration_id}/withdraw` | `registrations.py` | Yes | Self or Admin (BOLA) | `WithdrawRequest` | `RegistrationResponse` |
| `POST` | `/api/v1/registrations/{registration_id}/decline` | `registrations.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `DeclineRequest` | `RegistrationResponse` |
| `GET` | `/api/v1/gamification/summary/me` | `gamification.py` | Yes | Authenticated User | None | `GamificationSummaryResponse` |
| `GET` | `/api/v1/gamification/summary` | `gamification.py` | Yes | Authenticated User | None | `GamificationSummaryResponse` |
| `GET` | `/api/v1/gamification/ledger/me` | `gamification.py` | Yes | Authenticated User | `cycle_year`, `page`, `page_size` | `PointLedgerResponse` |
| `GET` | `/api/v1/gamification/ledger` | `gamification.py` | Yes | Authenticated User | `cycle_year`, `page`, `page_size` | `PointLedgerResponse` |
| `GET` | `/api/v1/leaderboards` | `gamification.py` | Yes | Authenticated User | `category`, `cycle_year`, `page`, `page_size` | `LeaderboardResponse` |
| `GET` | `/api/v1/gamification/leaderboard` | `gamification.py` | Yes | Authenticated User | `category`, `cycle_year`, `page`, `page_size` | `LeaderboardResponse` |
| `GET` | `/api/v1/gamification/leaderboard/overall` | `gamification.py` | Yes | Authenticated User | `cycle_year`, `page`, `page_size` | `LeaderboardResponse` |
| `GET` | `/api/v1/gamification/leaderboard/student` | `gamification.py` | Yes | Authenticated User | `cycle_year`, `page`, `page_size` | `LeaderboardResponse` |
| `GET` | `/api/v1/gamification/leaderboard/alumni` | `gamification.py` | Yes | Authenticated User | `cycle_year`, `page`, `page_size` | `LeaderboardResponse` |
| `GET` | `/api/v1/gamification/leaderboard/corporate` | `gamification.py` | Yes | Authenticated User | `cycle_year`, `page`, `page_size` | `LeaderboardResponse` |
| `GET` | `/api/v1/achievements` | `gamification.py` | Yes | Authenticated User | None | `VolunteerAchievementsListResponse` |
| `GET` | `/api/v1/gamification/achievements/me` | `gamification.py` | Yes | Authenticated User | None | `VolunteerAchievementsListResponse` |
| `POST` | `/api/v1/gamification/points/adjust` | `gamification.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `PointAdjustmentRequest` | `PointTransactionResponse` |
| `GET` | `/api/v1/notifications/me` | `notifications.py` | Yes | Authenticated User | `unread_only`, `page`, `limit` | `NotificationListResponse` |
| `GET` | `/api/v1/notifications` | `notifications.py` | Yes | Authenticated User | `unread_only`, `page`, `limit` | `NotificationListResponse` |
| `GET` | `/api/v1/notifications/unread-count` | `notifications.py` | Yes | Authenticated User | None | `UnreadCountResponse` |
| `PATCH` | `/api/v1/notifications/{notification_id}/read` | `notifications.py` | Yes | Self or Admin (BOLA) | None | `MarkReadResponse` |
| `POST` | `/api/v1/notifications/read-all` | `notifications.py` | Yes | Authenticated User | None | `MarkAllReadResponse` |
| `POST` | `/api/v1/notifications/device-token` | `notifications.py` | Yes | Authenticated User | `DeviceTokenCreate` | `DeviceTokenResponse` |
| `POST` | `/api/v1/notifications/devices` | `notifications.py` | Yes | Authenticated User | `DeviceTokenCreate` | `DeviceTokenResponse` |
| `DELETE` | `/api/v1/notifications/devices/{fcm_token}` | `notifications.py` | Yes | Self or Admin (BOLA) | None | None |
| `POST` | `/api/v1/media/signed-upload` | `media.py` | Yes | Authenticated User | `SignedUploadRequest` | `SignedUploadResponse` |
| `POST` | `/api/v1/media/sign-upload` | `media.py` | Yes | Authenticated User | `SignedUploadRequest` | `SignedUploadResponse` |
| `POST` | `/api/v1/media/assets` | `media.py` | Yes | Authenticated User | `MediaAssetRegisterRequest` | `MediaAssetResponse` |
| `POST` | `/api/v1/media/register` | `media.py` | Yes | Authenticated User | `MediaAssetRegisterRequest` | `MediaAssetResponse` |
| `DELETE` | `/api/v1/media/assets/{asset_id}` | `media.py` | Yes | Self or Admin (BOLA) | None | None |
| `GET` | `/api/v1/events/{event_id}/photos` | `media.py` | Yes | Authenticated User | None | `EventGalleryResponse` |
| `POST` | `/api/v1/events/{event_id}/photos` | `media.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `EventPhotoCreateRequest` | `EventPhotoResponse` |
| `GET` | `/api/v1/events/{event_id}/communications/linkedin-draft` | `media.py` | Yes | Authenticated User | None | `LinkedInDraftResponse` |
| `GET` | `/api/v1/admin/dashboard` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `AdminDashboardResponse` |
| `GET` | `/api/v1/admin/reports/student-contributions` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `page`, `limit`, `start_date`, `end_date` | `StudentContributionReportResponse` |
| `GET` | `/api/v1/admin/reports/alumni-contributions` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `page`, `limit`, `start_date`, `end_date` | `AlumniContributionReportResponse` |
| `GET` | `/api/v1/admin/reports/alumni-consistency` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `page`, `limit` | `AlumniConsistencyReportResponse` |
| `GET` | `/api/v1/admin/reports/inactive-volunteers` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `threshold_days`, `page`, `limit` | `InactiveVolunteerReportResponse` |
| `GET` | `/api/v1/admin/reports/interview-availability` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `page`, `limit` | `InterviewAvailabilityReportResponse` |
| `GET` | `/api/v1/admin/reports/organisation-contributions` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `page`, `limit`, `start_date`, `end_date` | `OrganisationContributionReportResponse` |
| `GET` | `/api/v1/admin/reports/{report_type}/export` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `StreamingResponse` (.xlsx) |
| `GET` | `/api/v1/admin/outbox/jobs` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `status`, `channel`, `page`, `limit` | `OutboxJobListResponse` |
| `GET` | `/api/v1/admin/outbox/dead-letter` | `admin.py` | Yes | `SUPER_ADMIN` | `page`, `limit` | `OutboxJobListResponse` |
| `POST` | `/api/v1/admin/outbox/jobs/{job_id}/retry` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `OutboxRetryResponse` |
| `POST` | `/api/v1/admin/outbox/{job_id}/requeue` | `admin.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `OutboxRetryResponse` |
| `GET` | `/api/v1/admin/audit-logs` | `admin.py` | Yes | `SUPER_ADMIN` | `actor_id`, `action`, `page`, `limit` | `AuditLogListResponse` |
| `GET` | `/api/v1/reports/volunteer-stats` | `reports.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `VolunteerStats` |
| `GET` | `/api/v1/reports/contribution-hours` | `reports.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `from_date`, `to_date` | `dict[str, Any]` |
| `GET` | `/api/v1/reports/inactive-volunteers` | `reports.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `threshold_days`, `page`, `limit` | `InactiveVolunteerReportResponse` |
| `POST` | `/api/v1/reports/export` | `reports.py` | Yes | `ADMIN`, `SUPER_ADMIN` | `ReportExportRequest` | `ReportExportResponse` |
| `GET` | `/api/v1/reports/exports/{export_id}` | `reports.py` | Yes | `ADMIN`, `SUPER_ADMIN` | None | `ReportExportResponse` |

---

## 3. Live Endpoint Verification

Direct HTTP probes against the running FastAPI daemon (`http://127.0.0.1:8000`) confirmed the baseline authentication guardrails and health diagnostics:

```powershell
# Probe 1: GET /api/v1/health (Public)
Response: 200 OK
{
    "status": "healthy",
    "version": "0.1.0",
    "environment": "development",
    "timestamp": "2026-11-05T14:45:37.448097Z",
    "database": {
        "connected": true,
        "dialect": "postgresql",
        "latency_ms": 6027.36,
        "error": null
    }
}

# Probe 2: POST /api/v1/auth/login (Invalid credentials)
Response: 401 Unauthorized
{
    "error_code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password.",
    "details": {},
    "timestamp": "2026-11-05T14:46:07.086305Z",
    "error": { "code": "INVALID_CREDENTIALS", "message": "Invalid email or password.", "details": {} }
}

# Probe 3: GET /api/v1/events (No auth header)
Response: 401 Unauthorized
{
    "error_code": "UNAUTHORIZED",
    "message": "Authentication credentials missing.",
    "details": {},
    "timestamp": "2026-11-05T14:46:07.485302Z",
    "error": { "code": "UNAUTHORIZED", "message": "Authentication credentials missing.", "details": {} }
}

# Probe 4: GET /api/v1/admin/dashboard (No auth header)
Response: 401 Unauthorized
{
    "error_code": "UNAUTHORIZED",
    "message": "Authentication credentials missing.",
    "details": {},
    "timestamp": "2026-11-05T14:46:08.227843Z",
    "error": { "code": "UNAUTHORIZED", "message": "Authentication credentials missing.", "details": {} }
}

# Probe 5: GET /api/v1/volunteers/me (No auth header)
Response: 401 Unauthorized
{
    "error_code": "UNAUTHORIZED",
    "message": "Authentication credentials missing.",
    "details": {},
    "timestamp": "2026-11-05T14:46:08.235614Z",
    "error": { "code": "UNAUTHORIZED", "message": "Authentication credentials missing.", "details": {} }
}
```

---

## 4. Detailed Audit Findings

### **ISSUE-API-001** [P2 — Medium]
- **Route/File**: `server/src/api/v1/` across multiple router modules
- **Description**: Inconsistent query parameter naming conventions for pagination (`page_size` vs `limit`).
- **Evidence**:
  - `admin.py`: `limit: int = Query(default=20, ge=1, le=100)`
  - `events.py`: `limit: int = Query(default=20, ge=1, le=100)`
  - `registrations.py`: `limit: int = Query(default=20, ge=1, le=100)`
  - `notifications.py`: `limit: int = Query(default=20, ge=1, le=100)`
  - `applications.py`: `page_size: int = Query(20, ge=1, le=100)`
  - `attendance.py`: `page_size: int = Query(default=20, ge=1, le=100)`
  - `gamification.py`: `page_size: int = Query(default=20, ge=1, le=100)`
  - `volunteers.py`: Line 79 uses `page_size`, while line 108 uses `limit`.
- **Impact**: Frontend clients and mobile SDKs must juggle two differing parameter aliases depending on which endpoint is invoked.
- **Recommendation**: Standardize on `page_size` across all paginated endpoints, adding `limit` as a deprecated fallback alias.

---

### **ISSUE-API-002** [P2 — Medium]
- **Route/File**:
  - `GET /api/v1/consent/me/history` (`server/src/api/v1/consent.py:46`)
  - `GET /api/v1/users/me/sessions` (`server/src/api/v1/users.py:44`)
  - `GET /api/v1/events/{event_id}/photos` (`server/src/api/v1/media.py:108`)
  - `GET /api/v1/achievements` (`server/src/api/v1/gamification.py:161`)
- **Description**: Missing pagination on collection/list endpoints.
- **Evidence**:
  - `GET /consent/me/history` returns `ConsentHistoryResponse` holding an unbounded list of historical consent changes.
  - `GET /users/me/sessions` returns `list[SessionResponse]` holding all un-revoked user sessions.
  - `GET /events/{event_id}/photos` returns `EventGalleryResponse` with all media assets tied to an event without paging limits.
- **Impact**: Response payload size scales linearly with user activity and community event size, creating memory spikes and response latency.
- **Recommendation**: Introduce `page` and `page_size` (default 20, max 100) pagination DTO wrappers on all collection endpoints.

---

### **ISSUE-API-003** [P1 — High]
- **Route/File**:
  - `server/src/services/attendance_service.py:130-196` (`check_in_volunteers`)
  - `server/src/services/attendance_service.py:465-515` (`bulk_process_attendance`)
  - `server/src/services/registration_service.py:307-362` (`select_volunteers_batch`)
- **Description**: N+1 database roundtrips executed within iterative loops during bulk/batch operations.
- **Evidence**:
  - In `attendance_service.py` (`check_in_volunteers`):
    ```python
    for vol_id in volunteer_profile_ids:
        # Query 1: Row lock check on registration
        res = await db.execute(stmt)
        # Query 2: Fetch existing attendance record with lock
        existing = await attendance_repository.get_by_registration_id_with_lock(db, registration.id)
        # Query 3: Create attendance record
        record = await attendance_repository.create_record(...)
        # Query 4: Reload record with eager relations
        reloaded = await attendance_repository.get_by_id(db, record.id)
    ```
    For a batch check-in of 50 volunteers, this generates 200 distinct SQL network roundtrips within a single transaction.
  - In `registration_service.py` (`select_volunteers_batch`):
    Iterates over `registration_ids` executing `get_by_id_with_lock`, `append_history`, and `get_by_id` reloading in three separate sequential loops ($3 \times N$ queries).
- **Impact**: Severe lock contention and transaction latency under high-concurrency event check-ins, leading to connection timeouts against Supabase pooler.
- **Recommendation**: Refactor batch operations to use `WHERE id = ANY(:ids)` with bulk inserts (`insert().values(...)`) and single-statement relation loading.

---

### **ISSUE-API-004** [P1 — High]
- **Route/File**: `web/src/types/index.ts:248-266` vs `server/src/schemas/event.py:235-260`
- **Description**: Schema field property drift between backend `EventResponse` and frontend `EventItem`.
- **Evidence**:
  - Backend schema defines:
    - `online_meeting_url: str | None`
    - `cover_media_id: uuid.UUID | None`
    - `volunteer_capacity: int` and `capacity_required: int`
    - `available_spots: int`
    - `waitlisted_count: int`
  - Frontend TypeScript `EventItem` defines:
    - `meeting_url?: string | null` (mismatched property name)
    - `banner_media_id?: string | null` (mismatched property name)
    - `capacity: number` (mismatched property name)
    - `withdrawal_deadline: string` (missing from backend response)
    - `attended_count: number` (missing from backend response)
- **Impact**: Frontend components attempting to read `event.meeting_url` or `event.capacity` receive `undefined` when reading live backend responses.
- **Recommendation**: Align `EventItem` in `web/src/types/index.ts` with canonical backend field names (`online_meeting_url`, `cover_media_id`, `capacity_required`, `volunteer_capacity`).

---

### **ISSUE-API-005** [P2 — Medium]
- **Route/File**: `server/src/main.py:56-58` and `server/src/core/exceptions.py`
- **Description**: Inconsistent error response structure for standard Starlette/FastAPI HTTP exceptions.
- **Evidence**:
  - Live probe against non-existent endpoint (`GET /api/v1/non_existent_route`):
    `404 Not Found` -> `{"detail": "Not Found"}`
  - Live probe against method mismatch (`DELETE /api/v1/health`):
    `405 Method Not Allowed` -> `{"detail": "Method Not Allowed"}`
  - Domain exceptions:
    `401 Unauthorized` -> `{"error_code": "UNAUTHORIZED", "message": "...", "details": {}, "timestamp": "...", "error": {...}}`
  - `server/src/main.py` registers handlers for `DomainException`, `RequestValidationError`, and `Exception`, but omits explicit handler for `starlette.exceptions.HTTPException`.
  - Frontend client (`web/src/lib/api-client.ts:238`) expects `errorData.message`. When encountering 404/405, it falls back to `"Request failed with status 404"` because `"detail"` is ignored.
- **Impact**: Frontend error banners fail to display informative server error reasons on standard HTTP errors.
- **Recommendation**: Add a specialized exception handler for `StarletteHTTPException` in `main.py` that formats the error into the canonical `{"error_code": "HTTP_STATUS", "message": exc.detail, ...}` envelope.

---

### **ISSUE-API-006** [P3 — Low]
- **Route/File**: `web/src/types/index.ts:185-231`
- **Description**: Flattened legacy profile attributes in TypeScript `VolunteerProfileResponse` that do not exist at root of backend model.
- **Evidence**:
  - TypeScript interface defines: `pincode?: string`, `address_line1?: string`, `city?: string`, `state?: string`, `emergency_contact_name?: string`, `emergency_contact_phone?: string`, `college_name?: string`, `department?: string`.
  - Backend `VolunteerProfileResponse` (`server/src/schemas/volunteer.py`) encapsulates category details within polymorphic sub-schemas (`student_profile`, `alumni_profile`, `corporate_profile`).
- **Impact**: Code smells and potential developer confusion when inspecting available profile properties in TypeScript.
- **Recommendation**: Deprecate and remove redundant flat category properties from `web/src/types/index.ts`.

---

## 5. Summary Table of API Findings

| Issue ID | Severity | Category | Affected Component | Impact Summary |
|:---|:---:|:---|:---|:---|
| **ISSUE-API-001** | **P2** | Consistency | Multiple Routers | Inconsistent pagination parameter names (`page_size` vs `limit`). |
| **ISSUE-API-002** | **P2** | Scalability | `consent`, `users`, `media` | Unbounded list endpoints without pagination limits. |
| **ISSUE-API-003** | **P1** | Performance | `attendance_service`, `registration_service` | N+1 roundtrips in bulk attendance and batch selection loops. |
| **ISSUE-API-004** | **P1** | Integration | `EventResponse` / `EventItem` | Property name mismatch (`online_meeting_url` vs `meeting_url`). |
| **ISSUE-API-005** | **P2** | Usability | `main.py`, `exceptions.py` | Native Starlette HTTP 404/405 bypass canonical envelope format. |
| **ISSUE-API-006** | **P3** | Maintenance | `web/src/types/index.ts` | Legacy flattened fields in TypeScript `VolunteerProfileResponse`. |
