# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## Web Application — Comprehensive API Integration Matrix

**Document Version:** 2.0.0 (Post-Audit Canonical Specification)  
**Verification Date:** 2026-11-03  
**Backend Runtime:** FastAPI with SQLAlchemy 2.0 (PostgreSQL)  
**Total Verified Endpoints in Master Router:** 94 Registered Endpoints  

---

## 1. Classification & Status Legend

Every endpoint in this matrix is classified into one of three unambiguous categories:
1. **ACTUAL ENDPOINT**: Fully implemented, verified against backend source code, tested, and ready for production web consumption.
2. **ENDPOINT ALIAS**: Secondary registered endpoint path resolving to the same underlying service handler (for pluralization or backwards compatibility).
3. **PROPOSED FUTURE ENDPOINT**: Endpoint not currently implemented in the backend, documented for future roadmap consideration. **Never to be called or mocked by frontend code**.

---

## 2. Master Feature-to-API Integration Matrix

### 2.1 Authentication & Session Management (`server/src/api/v1/auth.py` & `users.py`)

| Frontend Screen & Feature | Exact Registered Endpoint | HTTP Method | Request Schema | Response Schema | Auth Required? | Role Authorization | Backend Source File Reference | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P2: Volunteer Registration** | `/api/v1/auth/register` | POST | `RegisterRequest` | `RegisterResponse` | No (Public) | None | `server/src/api/v1/auth.py#L37` | ACTUAL ENDPOINT |
| **P1, P2: User Login** | `/api/v1/auth/login` | POST | `LoginRequest` | `TokenResponse` | No (Public) | None | `server/src/api/v1/auth.py#L82` | ACTUAL ENDPOINT |
| **All: Silent Token Refresh** | `/api/v1/auth/refresh` | POST | `RefreshRequest` (or cookie) | `TokenResponse` | No / Cookie | None | `server/src/api/v1/auth.py#L148`| ACTUAL ENDPOINT |
| **Auth: Email Verification** | `/api/v1/auth/verify-email` | POST | `VerifyEmailRequest` | `VerifyEmailResponse` | No (Public) | None | `server/src/api/v1/auth.py#L190`| ACTUAL ENDPOINT |
| **Auth: Request Password Reset**| `/api/v1/auth/password-reset/request` | POST | `PasswordResetRequest` | `MessageResponse` | No (Public) | None | `server/src/api/v1/auth.py#L225`| ACTUAL ENDPOINT |
| **Auth: Confirm Password Reset**| `/api/v1/auth/password-reset/confirm` | POST | `PasswordResetConfirmRequest` | `MessageResponse` | No (Public) | None | `server/src/api/v1/auth.py#L262`| ACTUAL ENDPOINT |
| **All: User Logout (Current)** | `/api/v1/auth/logout` | POST | None | `MessageResponse` | Yes (Bearer/Cookie) | Any Authenticated | `server/src/api/v1/auth.py#L295`| ACTUAL ENDPOINT |
| **V5, A1: User Logout (All)** | `/api/v1/auth/logout-all` | POST | None | `MessageResponse` | Yes (Bearer/Cookie) | Any Authenticated | `server/src/api/v1/auth.py#L305`| ACTUAL ENDPOINT |
| **All: Get Current User Identity**| `/api/v1/users/me` | GET | None | `UserMeResponse` | Yes (Bearer/Cookie) | Any Authenticated | `server/src/api/v1/users.py#L23` | ACTUAL ENDPOINT |
| **V5, A1: List Active Sessions** | `/api/v1/users/me/sessions` | GET | None | `list[SessionResponse]` | Yes (Bearer/Cookie) | Any Authenticated | `server/src/api/v1/users.py#L36` | ACTUAL ENDPOINT |
| **V5, A1: Revoke Session** | `/api/v1/users/me/sessions/{session_id}` | DELETE | None | `MessageResponse` | Yes (Bearer/Cookie) | Session Owner | `server/src/api/v1/users.py#L58` | ACTUAL ENDPOINT |

---

### 2.2 Volunteer Portal Features (`volunteers.py`, `consent.py`, `events.py`, `registrations.py`, `gamification.py`, `notifications.py`, `media.py`)

| Frontend Screen & Feature | Exact Registered Endpoint | HTTP Method | Request Schema | Response Schema | Auth Required? | Role Authorization | Backend Source File Reference | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **V5: Get Volunteer Profile** | `/api/v1/volunteers/me` | GET | None | `VolunteerProfileResponse` | Yes | Any Authenticated | `server/src/api/v1/volunteers.py#L23` | ACTUAL ENDPOINT |
| **V5: Update Volunteer Profile** | `/api/v1/volunteers/me` | PATCH | `VolunteerProfileUpdate` | `VolunteerProfileResponse` | Yes | Profile Owner | `server/src/api/v1/volunteers.py#L38` | ACTUAL ENDPOINT |
| **Onboarding: My Application** | `/api/v1/applications/me` | GET | None | `ApplicationResponse` | Yes | Any Authenticated | `server/src/api/v1/applications.py#L26`| ACTUAL ENDPOINT |
| **V5: Get Affirmative Consent** | `/api/v1/consent/me` | GET | None | `ConsentResponse` | Yes | Any Authenticated | `server/src/api/v1/consent.py#L20` | ACTUAL ENDPOINT |
| **V5: Update Affirmative Consent**| `/api/v1/consent/me` | PUT | `ConsentUpdate` | `ConsentResponse` | Yes | Profile Owner | `server/src/api/v1/consent.py#L35` | ACTUAL ENDPOINT |
| **V5: Consent Audit Trail** | `/api/v1/consent/me/history` | GET | None | `ConsentHistoryResponse` | Yes | Profile Owner | `server/src/api/v1/consent.py#L61` | ACTUAL ENDPOINT |
| **V1: Discover Published Events**| `/api/v1/events` | GET | Query params: `category`, `mode`, `from_date`, `to_date`, `search`, `page`, `limit` | `EventListResponse` | Yes | Any Authenticated | `server/src/api/v1/events.py#L56` | ACTUAL ENDPOINT |
| **V3: Get Event Details** | `/api/v1/events/{event_id}` | GET | None | `EventResponse` | Yes | Any Authenticated | `server/src/api/v1/events.py#L90` | ACTUAL ENDPOINT |
| **V3: Register for Event** | `/api/v1/events/{event_id}/register` | POST | `RegistrationCreateRequest` (`notes`) | `RegistrationResponse` | Yes | Approved Volunteer | `server/src/api/v1/events.py#L241`| ACTUAL ENDPOINT |
| **V3, V2: Withdraw Registration**| `/api/v1/events/{event_id}/withdraw` | POST | `WithdrawRequest` (`reason`) | `RegistrationResponse` | Yes | Registration Owner | `server/src/api/v1/events.py#L265`| ACTUAL ENDPOINT |
| **V2: List My Registrations** | `/api/v1/registrations/me` | GET | Query params: `page`, `limit` | `RegistrationListResponse` | Yes | Authenticated Volunteer | `server/src/api/v1/registrations.py#L22`| ACTUAL ENDPOINT |
| **V2: My Registrations (Alias)** | `/api/v1/volunteers/me/registrations` | GET | Query params: `page`, `limit` | `RegistrationListResponse` | Yes | Authenticated Volunteer | `server/src/api/v1/volunteers.py#L99` | ENDPOINT ALIAS |
| **V2: Registration Details** | `/api/v1/registrations/{registration_id}` | GET | None | `RegistrationResponse` | Yes | Registration Owner / Admin | `server/src/api/v1/registrations.py#L43`| ACTUAL ENDPOINT |
| **V2: Withdraw by Reg ID** | `/api/v1/registrations/{registration_id}/withdraw` | POST | `WithdrawRequest` (`reason`) | `RegistrationResponse` | Yes | Registration Owner | `server/src/api/v1/registrations.py#L62`| ACTUAL ENDPOINT |
| **V2: My Attendance History** | `/api/v1/attendance/me` | GET | Query params: `page`, `page_size` | `AttendanceListResponse` | Yes | Authenticated Volunteer | `server/src/api/v1/attendance.py#L136` | ACTUAL ENDPOINT |
| **V2: Attendance (Alias)** | `/api/v1/volunteers/me/attendance` | GET | Query params: `page`, `page_size` | `AttendanceListResponse` | Yes | Authenticated Volunteer | `server/src/api/v1/attendance.py#L140` | ENDPOINT ALIAS |
| **V1, V5: Gamification Summary** | `/api/v1/gamification/summary` | GET | Query params: `cycle_year` | `GamificationSummaryResponse` | Yes | Authenticated Volunteer | `server/src/api/v1/gamification.py#L79`| ACTUAL ENDPOINT |
| **V1, V5: Summary (Alias)** | `/api/v1/gamification/summary/me` | GET | Query params: `cycle_year` | `GamificationSummaryResponse` | Yes | Authenticated Volunteer | `server/src/api/v1/gamification.py#L84`| ENDPOINT ALIAS |
| **V5: Point Ledger History** | `/api/v1/gamification/ledger` | GET | Query params: `cycle_year`, `page`, `page_size` | `PointLedgerResponse` | Yes | Authenticated Volunteer | `server/src/api/v1/gamification.py#L102`| ACTUAL ENDPOINT |
| **V5: Ledger History (Alias)** | `/api/v1/gamification/ledger/me` | GET | Query params: `cycle_year`, `page`, `page_size` | `PointLedgerResponse` | Yes | Authenticated Volunteer | `server/src/api/v1/gamification.py#L107`| ENDPOINT ALIAS |
| **V4: Master Leaderboard** | `/api/v1/gamification/leaderboard` | GET | Query params: `category`, `cycle_year`, `page`, `page_size` | `LeaderboardResponse` | Yes | Any Authenticated | `server/src/api/v1/gamification.py#L158`| ACTUAL ENDPOINT |
| **V4: Leaderboards (Alias)** | `/api/v1/leaderboards` | GET | Query params: `category`, `cycle_year`, `page`, `page_size` | `LeaderboardResponse` | Yes | Any Authenticated | `server/src/api/v1/gamification.py#L153`| ENDPOINT ALIAS |
| **V4: Overall Leaderboard** | `/api/v1/gamification/leaderboard/overall` | GET | Query params: `cycle_year`, `page`, `page_size` | `LeaderboardResponse` | Yes | Any Authenticated | `server/src/api/v1/gamification.py#L181`| ACTUAL ENDPOINT |
| **V4: Student Tier Leaderboard**| `/api/v1/gamification/leaderboard/student` | GET | Query params: `cycle_year`, `page`, `page_size` | `LeaderboardResponse` | Yes | Any Authenticated | `server/src/api/v1/gamification.py#L200`| ACTUAL ENDPOINT |
| **V4: Alumni Tier Leaderboard** | `/api/v1/gamification/leaderboard/alumni` | GET | Query params: `cycle_year`, `page`, `page_size` | `LeaderboardResponse` | Yes | Any Authenticated | `server/src/api/v1/gamification.py#L217`| ACTUAL ENDPOINT |
| **V4: Corporate Tier Board** | `/api/v1/gamification/leaderboard/corporate` | GET | Query params: `cycle_year`, `page`, `page_size` | `LeaderboardResponse` | Yes | Any Authenticated | `server/src/api/v1/gamification.py#L235`| ACTUAL ENDPOINT |
| **V5: Available & Earned Badges**| `/api/v1/achievements` | GET | None | `VolunteerAchievementsListResponse` | Yes | Any Authenticated | `server/src/api/v1/gamification.py#L258`| ACTUAL ENDPOINT |
| **V5: Badges (Alias)** | `/api/v1/gamification/achievements/me` | GET | None | `VolunteerAchievementsListResponse` | Yes | Any Authenticated | `server/src/api/v1/gamification.py#L263`| ENDPOINT ALIAS |
| **V1, A1: Notifications Inbox** | `/api/v1/notifications/me` | GET | Query params: `unread_only`, `page`, `limit` | `NotificationListResponse` | Yes | Any Authenticated | `server/src/api/v1/notifications.py#L24`| ACTUAL ENDPOINT |
| **V1, A1: Unread Counter** | `/api/v1/notifications/unread-count` | GET | None | `UnreadCountResponse` | Yes | Any Authenticated | `server/src/api/v1/notifications.py#L51`| ACTUAL ENDPOINT |
| **V1, A1: Mark Read** | `/api/v1/notifications/{notification_id}/read` | PATCH | None | `MarkReadResponse` | Yes | Notification Owner | `server/src/api/v1/notifications.py#L64`| ACTUAL ENDPOINT |
| **V1, A1: Mark All Read** | `/api/v1/notifications/read-all` | POST | None | `MarkAllReadResponse` | Yes | Any Authenticated | `server/src/api/v1/notifications.py#L82`| ACTUAL ENDPOINT |
| **All: Register FCM Device** | `/api/v1/notifications/device-token` | POST | `DeviceTokenRegister` | `DeviceTokenResponse` | Yes | Any Authenticated | `server/src/api/v1/notifications.py#L96`| ACTUAL ENDPOINT |
| **V5: Signed Upload Params** | `/api/v1/media/signed-upload` | POST | `SignUploadRequest` | `SignedUploadResponse` | Yes | Any Authenticated | `server/src/api/v1/media.py#L26` | ACTUAL ENDPOINT |
| **V5: Register Uploaded Asset** | `/api/v1/media/assets` | POST | `MediaAssetCreate` | `MediaAssetResponse` | Yes | Any Authenticated | `server/src/api/v1/media.py#L49` | ACTUAL ENDPOINT |
| **V3: Get Event Photo Gallery** | `/api/v1/events/{event_id}/photos` | GET | None | `EventGalleryResponse` | Yes | Any Authenticated | `server/src/api/v1/media.py#L93` | ACTUAL ENDPOINT |

---

### 2.3 Admin Command Portal Features (`admin.py`, `applications.py`, `events.py`, `attendance.py`, `reports.py`)

| Frontend Screen & Feature | Exact Registered Endpoint | HTTP Method | Request Schema | Response Schema | Auth Required? | Role Authorization | Backend Source File Reference | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A1: Admin Dashboard Aggregates**| `/api/v1/admin/dashboard` | GET | None | `AdminDashboardResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L32` | ACTUAL ENDPOINT |
| **A1, Onboarding: Applications**| `/api/v1/applications` | GET | Query params: `status`, `category`, `date_from`, `date_to`, `search`, `page`, `page_size` | `ApplicationListResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/applications.py#L40`| ACTUAL ENDPOINT |
| **Onboarding: Application Details**| `/api/v1/applications/{application_id}` | GET | None | `ApplicationDetailResponse` | Yes | `ADMIN`, `SUPER_ADMIN` (or applicant) | `server/src/api/v1/applications.py#L78`| ACTUAL ENDPOINT |
| **Onboarding: Approve Application**| `/api/v1/applications/{application_id}/approve` | POST | `ApplicationApproveRequest` (`notes`) | `ApplicationResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/applications.py#L97`| ACTUAL ENDPOINT |
| **Onboarding: Reject Application** | `/api/v1/applications/{application_id}/reject` | POST | `ApplicationRejectRequest` (`reason`) | `ApplicationResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/applications.py#L126`| ACTUAL ENDPOINT |
| **Onboarding: Verify Minor Consent**| `/api/v1/applications/{application_id}/verify-parental-consent` | POST | `ParentalConsentVerifyRequest` (`status`, `notes`) | `VolunteerProfileResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/applications.py#L154`| ACTUAL ENDPOINT |
| **Volunteers: Directory Listing** | `/api/v1/volunteers` | GET | Query params: `category`, `status`, `college`, `employer`, `search`, `page`, `page_size` | `VolunteerListResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/volunteers.py#L64` | ACTUAL ENDPOINT |
| **Volunteers: Inspect Profile** | `/api/v1/volunteers/{profile_id}` | GET | None | `VolunteerProfileResponse` | Yes | `ADMIN`, `SUPER_ADMIN` (or self) | `server/src/api/v1/volunteers.py#L119`| ACTUAL ENDPOINT |
| **Events: Create Event** | `/api/v1/events` | POST | `EventCreateRequest` | `EventResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L39` | ACTUAL ENDPOINT |
| **Events: Update Event Details**| `/api/v1/events/{event_id}` | PATCH | `EventUpdateRequest` | `EventResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L105` | ACTUAL ENDPOINT |
| **Events: Publish Event** | `/api/v1/events/{event_id}/publish` | POST | None | `EventResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L124` | ACTUAL ENDPOINT |
| **Events: Close Registrations** | `/api/v1/events/{event_id}/close-registrations` | POST | None | `EventResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L159` | ACTUAL ENDPOINT |
| **Events: Close Reg (Singular Alias)**| `/api/v1/events/{event_id}/close-registration` | POST | None | `EventResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L140` | ENDPOINT ALIAS |
| **Events: Cancel Event** | `/api/v1/events/{event_id}/cancel` | POST | `EventStatusTransitionRequest` (`reason`) | `EventResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L176` | ACTUAL ENDPOINT |
| **Events: Duplicate Event** | `/api/v1/events/{event_id}/duplicate` | POST | `EventDuplicateRequest` | `EventResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L214` | ACTUAL ENDPOINT |
| **A2: List Event Registrations**| `/api/v1/events/{event_id}/registrations` | GET | Query params: `status`, `page`, `limit` | `RegistrationListResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L288` | ACTUAL ENDPOINT |
| **A2: Select Single Volunteer** | `/api/v1/events/{event_id}/registrations/{registration_id}/select` | POST | None | `RegistrationResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L335` | ACTUAL ENDPOINT |
| **A2: Batch Select Volunteers** | `/api/v1/events/{event_id}/select` | POST | `SelectionRequest` (`registration_ids`) | `BatchSelectionResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L313` | ACTUAL ENDPOINT |
| **A2: Promote from Waitlist** | `/api/v1/events/{event_id}/waitlist/{registration_id}/promote` | POST | None | `RegistrationResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L357` | ACTUAL ENDPOINT |
| **A2: Mark Not Selected (Decline)**| `/api/v1/events/{event_id}/registrations/{registration_id}/not-selected` | POST | `WithdrawRequest` (`reason`) | `RegistrationResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/events.py#L379` | ACTUAL ENDPOINT |
| **A2: Check-in Volunteers** | `/api/v1/events/{event_id}/attendance/check-in` | POST | `CheckInRequest` (`volunteer_profile_ids`) | `list[AttendanceRecordResponse]` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/attendance.py#L25` | ACTUAL ENDPOINT |
| **A2: Check-out Volunteers** | `/api/v1/events/{event_id}/attendance/check-out` | POST | `CheckOutRequest` (`volunteer_profile_ids`) | `list[AttendanceRecordResponse]` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/attendance.py#L47` | ACTUAL ENDPOINT |
| **A2: Bulk Attendance Action** | `/api/v1/events/{event_id}/attendance/bulk` | POST | `BulkAttendanceRequest` | `BulkAttendanceResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/attendance.py#L114` | ACTUAL ENDPOINT |
| **A2: List Event Attendance** | `/api/v1/events/{event_id}/attendance` | GET | Query params: `status`, `page`, `page_size` | `AttendanceListResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/attendance.py#L69` | ACTUAL ENDPOINT |
| **A2: Correct Attendance Time** | `/api/v1/attendance/{record_id}/correct` | POST | `AttendanceCorrectionRequest` (`new_check_in_time`, `new_check_out_time`, `reason`) | `AttendanceRecordResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/attendance.py#L93` | ACTUAL ENDPOINT |
| **A2: Event Completion Preview**| `/api/v1/events/{event_id}/completion-preview` | GET | None | `EventCompletionPreviewResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/gamification.py#L31`| ACTUAL ENDPOINT |
| **A2: Complete & Award Points** | `/api/v1/events/{event_id}/complete-and-award` | POST | None | `EventCompletionResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/gamification.py#L49`| ACTUAL ENDPOINT |
| **A2: Complete (Alias)** | `/api/v1/events/{event_id}/complete` | POST | None | `EventCompletionResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/gamification.py#L55`| ENDPOINT ALIAS |
| **A2: Upload Gallery Photo** | `/api/v1/events/{event_id}/photos` | POST | `EventPhotoCreate` | `EventPhotoResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/media.py#L107` | ACTUAL ENDPOINT |
| **A2: Generate LinkedIn Copy** | `/api/v1/events/{event_id}/communications/linkedin-draft` | GET | None | `LinkedInDraftResponse` | Yes | Any Authenticated | `server/src/api/v1/media.py#L128` | ACTUAL ENDPOINT |
| **A1: Super Admin Point Adjust**| `/api/v1/gamification/adjust` | POST | `PointAdjustmentRequest` | `PointTransactionResponse` | Yes | `SUPER_ADMIN` only | `server/src/api/v1/gamification.py#L129`| ACTUAL ENDPOINT |
| **A3: Student Contribution Report**| `/api/v1/admin/reports/student-contributions` | GET | Query params: `start_date`, `end_date`, `page`, `limit` | `StudentContributionReportResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L46` | ACTUAL ENDPOINT |
| **A3: Alumni Contribution Report** | `/api/v1/admin/reports/alumni-contributions` | GET | Query params: `start_date`, `end_date`, `page`, `limit` | `AlumniContributionReportResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L69` | ACTUAL ENDPOINT |
| **A3: Alumni Consistency Report** | `/api/v1/admin/reports/alumni-consistency` | GET | Query params: `page`, `limit` | `AlumniConsistencyReportResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L92` | ACTUAL ENDPOINT |
| **A3: Inactive Volunteers Report** | `/api/v1/admin/reports/inactive-volunteers` | GET | Query params: `threshold_days`, `page`, `limit` | `InactiveVolunteerReportResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L111`| ACTUAL ENDPOINT |
| **A3: Interview Availability Report**| `/api/v1/admin/reports/interview-availability` | GET | Query params: `page`, `limit` | `InterviewAvailabilityReportResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L132`| ACTUAL ENDPOINT |
| **A3: Organisation Contributions**| `/api/v1/admin/reports/organisation-contributions` | GET | Query params: `start_date`, `end_date`, `page`, `limit` | `OrganisationContributionReportResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L151`| ACTUAL ENDPOINT |
| **A3: Streaming Excel Export** | `/api/v1/admin/reports/{report_type}/export` | GET | Path: `report_type` (`student-contributions`, `alumni-contributions`, etc.) | Streaming binary (`.xlsx`) | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L174`| ACTUAL ENDPOINT |
| **A1: Dead-Letter Outbox Queue**| `/api/v1/admin/outbox/dead-letter` | GET | Query params: `page`, `limit` | `OutboxJobListResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L201`| ACTUAL ENDPOINT |
| **A1: Retry Outbox Job** | `/api/v1/admin/outbox/jobs/{job_id}/retry` | POST | None | `OutboxRetryResponse` | Yes | `ADMIN`, `SUPER_ADMIN` | `server/src/api/v1/admin.py#L245`| ACTUAL ENDPOINT |
| **A1: System Audit Logs** | `/api/v1/admin/audit-logs` | GET | Query params: `actor_id`, `action`, `resource_type`, `from_date`, `to_date`, `page`, `limit` | `AuditLogListResponse` | Yes | `SUPER_ADMIN` only | `server/src/api/v1/admin.py#L270`| ACTUAL ENDPOINT |

---

## 3. Proposed Future Endpoints (Not in Canonical Backend)

| Proposed Feature | Proposed Endpoint | Proposed Method | Intended Schema | Status & Frontend Handling Directive |
| :--- | :--- | :--- | :--- | :--- |
| **P1: Public Impact Counters** | `/api/v1/public/stats` | GET | `{ total_volunteers: int, total_events: int, total_hours: Decimal }` | **PROPOSED FUTURE ENHANCEMENT**. Do NOT call or mock. The Public Landing Page must render non-numeric impact storytelling until this endpoint is implemented in PostgreSQL. |
