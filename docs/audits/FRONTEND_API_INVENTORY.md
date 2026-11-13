# Frontend API Inventory & Verification Matrix
**Maatram Volunteering & Gamification Portal**
**Audit Date:** November 2026  
**Status:** Canonical & Audited  

---

## 1. Overview & Architectural Scope

This document provides a comprehensive, production-grade audit of every HTTP API endpoint consumed by the Next.js App Router frontend application (`web/src/`). All frontend interactions route through the unified FastAPI modular monolith backend (`server/src/api/v1/`) with strict session enforcement, CSRF double-submit protection, and database-backed transactional integrity.

### Authentication Modes
- **Public**: Unauthenticated endpoints (e.g. registration, login, deterministic health check).
- **Volunteer**: Authenticated volunteer sessions via HttpOnly `access_token` and `refresh_token` cookies with optional in-memory Bearer token fallback.
- **Admin**: Authenticated administrative accounts (`ADMIN` or `SUPER_ADMIN` role).

---

## 2. Comprehensive API Endpoint Inventory

| Module / Feature | HTTP Method | Frontend Endpoint | Auth Mode | Request Payload / Query Params | Response Type | Status | Automated Test Evidence |
| :--- | :---: | :--- | :---: | :--- | :--- | :---: | :--- |
| **Auth** — Register | `POST` | `/auth/register` | Public | `RegisterRequest` (email, password, category, details, consent) | `RegisterResponse` | Verified | `test_auth_workflows.py::test_register_student_volunteer_success` |
| **Auth** — Login | `POST` | `/auth/login` | Public | `LoginRequest` (email, password) | `TokenResponse` | Verified | `test_auth_workflows.py::test_login_web_client_cookies_and_csrf` |
| **Auth** — Refresh | `POST` | `/auth/refresh` | Public / Cookie | Cookie `refresh_token` | `TokenResponse` | Verified | `test_auth_workflows.py::test_refresh_token_rotation_success` |
| **Auth** — Logout | `POST` | `/auth/logout` | Volunteer / Admin | None (clears auth cookies) | `MessageResponse` | Verified | `test_auth_workflows.py::test_logout_and_logout_all` |
| **Auth** — Verify Email | `POST` | `/auth/verify-email` | Public | `VerifyEmailRequest` (token, email) | `VerifyEmailResponse` | Verified | `test_auth_workflows.py::test_email_verification_workflow` |
| **Auth** — Forgot Password | `POST` | `/auth/password-reset/request` | Public | `PasswordResetRequest` (email) | `MessageResponse` | Verified | `test_password_reset_rate_limit.py` |
| **Auth** — Confirm Reset | `POST` | `/auth/password-reset/confirm` | Public | `PasswordResetConfirmRequest` (email, otp, new_password) | `MessageResponse` | Verified | `test_auth_workflows.py::test_password_reset_otp_workflow` |
| **User** — Profile Me | `GET` | `/users/me` | Volunteer / Admin | None | `UserMeResponse` | Verified | `test_auth_workflows.py::test_get_current_user_me_success` |
| **Volunteer** — Profile Me | `GET` | `/volunteers/me` | Volunteer | None | `VolunteerProfileResponse` | Verified | `test_volunteers.py::test_get_my_volunteer_profile_student` |
| **Volunteer** — Update Me | `PATCH` | `/volunteers/me` | Volunteer | `VolunteerProfileUpdate` | `VolunteerProfileResponse` | Verified | `test_volunteers.py::test_update_my_volunteer_profile_success` |
| **Volunteer** — Get by ID | `GET` | `/volunteers/{id}` | Admin / Self | Path `id` (UUID) | `VolunteerProfileResponse` | Verified | `test_volunteers.py::test_volunteer_profile_ownership_bola` |
| **Volunteer** — List Directory | `GET` | `/volunteers` | Admin | `category`, `status`, `search`, `page`, `page_size` | `VolunteerListResponse` | Verified | `test_volunteers.py::test_admin_directory_listing_and_filtering` |
| **Application** — My App | `GET` | `/applications/me` | Volunteer | None | `ApplicationResponse` | Verified | `test_applications.py::test_get_my_application` |
| **Application** — List All | `GET` | `/applications` | Admin | `status`, `category`, `search`, `page`, `page_size` | `ApplicationListResponse` | Verified | `test_applications.py::test_registration_creates_pending_application` |
| **Application** — Detail | `GET` | `/applications/{id}` | Admin / Self | Path `id` (UUID) | `ApplicationDetailResponse` | Verified | `test_applications.py::test_get_application_by_id_bola` |
| **Application** — Approve | `POST` | `/applications/{id}/approve` | Admin | `ApplicationApproveRequest` (notes) | `ApplicationResponse` | Verified | `test_applications.py::test_minor_safeguarding_parental_consent_verification_and_approval` |
| **Application** — Reject | `POST` | `/applications/{id}/reject` | Admin | `ApplicationRejectRequest` (reason) | `ApplicationResponse` | Verified | `test_applications.py::test_admin_rejection_workflow` |
| **Application** — Verify Consent | `POST` | `/applications/{id}/verify-parental-consent` | Admin | `ParentalConsentVerifyRequest` (status, notes) | `VolunteerProfileResponse` | Verified | `test_applications.py::test_minor_safeguarding_parental_consent_verification_and_approval` |
| **Consent** — Get Consents | `GET` | `/consent/me` | Volunteer | None | `ConsentResponse` | Verified | `test_consent.py` |
| **Consent** — Update Consents | `PUT` | `/consent/me` | Volunteer | `ConsentUpdate` (6 statutory dimensions) | `ConsentResponse` | Verified | `test_sprint0_security.py::test_consent_put_updates_only_specified_fields_without_overwriting` |
| **Events** — List Events | `GET` | `/events` | Volunteer / Admin | `status`, `category`, `mode`, `search`, `limit`, `page` | `EventListResponse` | Verified | `test_events.py` |
| **Events** — Create Event | `POST` | `/events` | Admin | `EventCreateRequest` | `EventResponse` | Verified | `test_events.py` |
| **Events** — Get Event | `GET` | `/events/{id}` | Volunteer / Admin | Path `id` (UUID) | `EventResponse` | Verified | `test_events.py` |
| **Events** — Publish | `POST` | `/events/{id}/publish` | Admin | Path `id` (UUID) | `EventResponse` | Verified | `test_events.py` |
| **Events** — Close Reg | `POST` | `/events/{id}/close-registration` | Admin | Path `id` (UUID) | `EventResponse` | Verified | `test_events.py` |
| **Events** — Register | `POST` | `/events/{id}/register` | Volunteer | Path `id` (UUID) | `RegistrationResponse` | Verified | `test_registrations.py` |
| **Events** — Batch Select | `POST` | `/events/{id}/select` | Admin | `SelectionRequest` (registration_ids) | `BatchSelectionResponse` | Verified | `test_registrations.py::test_admin_can_select_volunteers` |
| **Events** — Select Single | `POST` | `/events/{id}/registrations/{reg_id}/select` | Admin | Path `id`, `reg_id` | `RegistrationResponse` | Verified | `test_registrations.py::test_admin_can_select_volunteers` |
| **Events** — Waitlist Promote | `POST` | `/events/{id}/waitlist/{reg_id}/promote` | Admin | Path `id`, `reg_id` | `RegistrationResponse` | Verified | `test_registrations.py::test_admin_can_promote_from_waitlist` |
| **Events** — Not Selected | `POST` | `/events/{id}/registrations/{reg_id}/not-selected` | Admin | Path `id`, `reg_id` | `RegistrationResponse` | Verified | `test_registrations.py::test_admin_can_mark_not_selected` |
| **Registrations** — My Regs | `GET` | `/registrations/me` | Volunteer | `page`, `limit` | `RegistrationListResponse` | Verified | `test_registrations.py::test_volunteer_view_own_registrations` |
| **Registrations** — Event Regs | `GET` | `/events/{id}/registrations` | Admin | Path `id` (UUID), `status`, `page`, `limit` | `RegistrationListResponse` | Verified | `test_registrations.py::test_admin_view_event_registrations` |
| **Registrations** — Withdraw | `POST` | `/registrations/{id}/withdraw` | Volunteer | `WithdrawRequest` (reason) | `RegistrationResponse` | Verified | `test_registrations.py::test_volunteer_can_withdraw_registration` |
| **Attendance** — Check In | `POST` | `/events/{id}/attendance/check-in` | Admin | `CheckInRequest` (volunteer_profile_ids) | `BulkAttendanceResponse` | Verified | `test_attendance.py::test_admin_can_check_in_selected_volunteer` |
| **Attendance** — Check Out | `POST` | `/events/{id}/attendance/check-out` | Admin | `CheckOutRequest` (volunteer_profile_ids) | `BulkAttendanceResponse` | Verified | `test_attendance.py::test_check_out_calculates_duration_and_hours` |
| **Attendance** — Event List | `GET` | `/events/{id}/attendance` | Admin | Path `id` (UUID), `page`, `limit` | `AttendanceListResponse` | Verified | `test_attendance.py` |
| **Attendance** — My History | `GET` | `/attendance/me` | Volunteer | `page`, `page_size` | `AttendanceListResponse` | Verified | `test_attendance.py::test_volunteer_can_view_own_attendance_history` |
| **Attendance** — Correct Hours | `POST` | `/attendance/{id}/correct` | Admin | `AttendanceCorrectionRequest` (hours, status, reason) | `AttendanceRecordResponse` | Verified | `test_attendance.py::test_attendance_correction_under_threshold_by_admin` |
| **Gamification** — Preview | `GET` | `/events/{id}/completion-preview` | Admin | Path `id` (UUID) | `EventCompletionPreviewResponse` | Verified | `test_event_completion.py` |
| **Gamification** — Complete | `POST` | `/events/{id}/complete-and-award` | Admin | Path `id` (UUID) | `EventCompletionResponse` | Verified | `test_event_completion.py` |
| **Gamification** — Summary | `GET` | `/gamification/summary` | Volunteer | `cycle_year` | `GamificationSummaryResponse` | Verified | `test_gamification.py` |
| **Gamification** — Ledger | `GET` | `/gamification/ledger` | Volunteer | `page`, `page_size`, `cycle_year` | `PointLedgerResponse` | Verified | `test_gamification.py` |
| **Gamification** — Leaderboard | `GET` | `/gamification/leaderboard` | Volunteer | `category`, `cycle_year`, `page`, `page_size` | `LeaderboardResponse` | Verified | `test_gamification.py` |
| **Gamification** — Badges | `GET` | `/achievements` | Volunteer | None | `VolunteerAchievementsListResponse` | Verified | `test_gamification.py` |
| **Notifications** — List | `GET` | `/notifications/me` | Volunteer | `page`, `limit` | `NotificationListResponse` | Verified | `test_notifications.py` |
| **Notifications** — Unread | `GET` | `/notifications/unread-count` | Volunteer | None | `UnreadCountResponse` | Verified | `test_notifications.py` |
| **Notifications** — Mark Read | `PATCH` | `/notifications/{id}/read` | Volunteer | Path `id` (UUID) | `NotificationResponse` | Verified | `test_notifications.py` |
| **Notifications** — Read All | `POST` | `/notifications/read-all` | Volunteer | None | `MessageResponse` | Verified | `test_notifications.py` |
| **Admin** — Dashboard | `GET` | `/admin/dashboard` | Admin | None | `AdminDashboardResponse` | Verified | `test_admin_reporting.py::test_admin_dashboard_summary_metrics` |
| **Admin** — Audit Logs | `GET` | `/admin/audit-logs` | Admin | `action`, `resource_type`, `search`, `page`, `limit` | `AuditLogListResponse` | Verified | `test_admin_reporting.py::test_audit_logs_super_admin_restriction` |

---

## 3. Reliability Findings & Resolutions

1. **Resolution of Volunteer Status Drift Bug**:
   - *Issue*: Previously, new volunteer registrations appeared directly in the active volunteer roster rather than under pending applications review.
   - *Root Cause*: `volunteer_profiles` was queried without enforcing `User.status == "APPROVED"`. Concurrently, two orphaned accounts created prior to Phase 5 lacked corresponding rows in `volunteer_applications`.
   - *Fix*: Backfilled orphaned rows in PostgreSQL; unified the admin volunteer interface under `/admin/volunteers` querying `/applications` by tab (`ALL`, `PENDING`, `APPROVED`, `REJECTED`).
2. **Consolidation of Redundant Admin Routes**:
   - Removed standalone `/admin/attendance`, `/admin/reports`, `/admin/operations`, and `/admin/applications` pages.
   - Replaced with instantaneous server-side `redirect()` calls ensuring backwards-compatible bookmark and link traversal.
3. **Password Visibility Toggle**:
   - Added interactive `Eye` / `EyeOff` accessible button to `/login` input field, enabling credential inspection without form submission interference.
