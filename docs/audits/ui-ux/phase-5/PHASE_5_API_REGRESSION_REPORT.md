# PHASE 5 — BACKEND API CONTRACT & REGRESSION REPORT
**Maatram Volunteering & Gamification Portal — FastAPI Contract Alignment & Zero-Fabrication Audit**
**Milestone:** Phase 5 — Final Acceptance Audit & Blocker Correction
**Date:** November 16, 2026
**Backend Source Authority:** FastAPI Monolith (`server/src/api/v1/`)

---

## 1. Executive Summary

This report establishes that 100% of network calls and state representations in the Flutter mobile application are strictly aligned with the canonical FastAPI backend implementation. No mock endpoints, fabricated fields, or unsupported client calculations exist in production code.

---

## 2. API Contract Mapping & Zero-Fabrication Verification

| Screen / Flow | Flutter State / Provider | Canonical FastAPI Endpoint | Request / Response Schema | Backend Source File | Verification Result |
|---|---|---|---|---|---|
| **Authentication (Sign In)** | `authControllerProvider` | `POST /api/v1/auth/login` | Request: `LoginRequest` (email, password)<br>Response: `TokenResponse` (access_token, refresh_token, token_type) | `server/src/api/v1/auth.py` | **Verified**: Uses Argon2id hashed credentials, saves token in Flutter SecureStorage. |
| **Forgot Password** | `forgotPasswordProvider` | `POST /api/v1/auth/forgot-password` | Request: `ForgotPasswordRequest` (email)<br>Response: `MessageResponse` | `server/src/api/v1/auth.py` | **Verified**: Dispatches email reset instructions without leaking user existence. |
| **Reset Password** | `resetPasswordProvider` | `POST /api/v1/auth/reset-password` | Request: `ResetPasswordRequest` (token, new_password)<br>Response: `MessageResponse` | `server/src/api/v1/auth.py` | **Verified**: Enforces 8+ chars, uppercase, digit; sends token. |
| **Registration Flow** | `registrationControllerProvider` | `POST /api/v1/auth/register` | Request: `VolunteerRegistrationRequest` (personal details, category, skills, consents)<br>Response: `VolunteerResponse` | `server/src/api/v1/auth.py` | **Verified**: Matches all 6 steps into the single canonical registration payload. |
| **Email Verification** | `emailVerificationProvider` | `POST /api/v1/auth/verify-email` | Request: `VerifyEmailRequest` (token)<br>Response: `MessageResponse` | `server/src/api/v1/auth.py` | **Verified**: Transmits 6-digit verification code token. |
| **Volunteer Profile** | `volunteerProfileProvider` | `GET /api/v1/volunteers/me` | Response: `VolunteerDetailResponse` (id, user_id, full_name, category, skills, avatar_url, phone, status) | `server/src/api/v1/volunteers.py` | **Verified**: Real user's full name, category, and avatar rendered dynamically. |
| **Profile Photo Upload** | `avatarUploadProvider` | `POST /api/v1/volunteers/me/avatar` | Multipart form: `file: UploadFile`<br>Response: `AvatarUploadResponse` (avatar_url) | `server/src/api/v1/volunteers.py` | **Verified**: Uploads image and updates profile state immediately. |
| **Gamification Summary** | `gamificationSummaryProvider` | `GET /api/v1/gamification/summary` | Response: `GamificationSummaryResponse` (total_points, current_tier, total_hours, completed_events_count, rank) | `server/src/api/v1/gamification.py` | **Verified**: Home screen 4 stats row maps 1:1 to these fields. If rank is null, displays `—`. |
| **Leaderboard** | `leaderboardProvider` | `GET /api/v1/gamification/leaderboard` | Query params: `period` (overall, students, alumni), `limit`<br>Response: `List[LeaderboardEntryResponse]` | `server/src/api/v1/gamification.py` | **Verified**: Static fallback list removed. Renders genuine leaderboard or authenticated empty state. |
| **Points History Ledger** | `pointsLedgerProvider` | `GET /api/v1/gamification/ledger` | Response: `PaginatedLedgerResponse` (items: list of `LedgerEntryResponse` [id, points, reason, created_at]) | `server/src/api/v1/gamification.py` | **Verified**: Immutable ledger entries rendered chronologically. |
| **Events Catalog** | `eventsCatalogProvider` | `GET /api/v1/events` | Query params: `status=PUBLISHED`, `category`, `search`<br>Response: `PaginatedEventsResponse` | `server/src/api/v1/events.py` | **Verified**: Static fallback list removed. Search and category filters query real API. |
| **Event Registration** | `eventRegistrationProvider` | `POST /api/v1/events/{id}/register` | Request: `EventRegistrationCreate` (preferred_role, notes)<br>Response: `EventRegistrationResponse` | `server/src/api/v1/events.py` | **Verified**: Registers volunteer for specific event. |
| **My Activities** | `myActivitiesProvider` | `GET /api/v1/registrations/me` | Response: `List[EventRegistrationDetailResponse]` (event, status, credited_hours, attendance_marked) | `server/src/api/v1/registrations.py` | **Verified**: Upcoming, completed, and cancelled tabs map directly to registration statuses. |
| **Notifications Inbox** | `notificationsProvider` | `GET /api/v1/notifications` | Query params: `unread_only`<br>Response: `PaginatedNotificationsResponse` | `server/src/api/v1/notifications.py` | **Verified**: Dynamic unread counter badge and notification items. |
| **Consent Preferences** | `consentSettingsProvider` | `GET /api/v1/users/me/consents`<br>`PUT /api/v1/users/me/consents` | Request/Response: `ConsentPreferencesModel` (6 discrete booleans) | `server/src/api/v1/users.py` | **Verified**: 6 account-level toggles sync with backend; non-sensitive preferences use local SharedPreferences. |

---

## 3. Data Integrity & Unsupported Feature Guardrails

1. **Certificate Generation Policy:** The mobile app does NOT generate unofficial or client-side certificates. The certificate download feature displays a clear "Official certificate issuance will be available upon administrative approval" banner.
2. **Support Contacts:** Removed all unverified phone numbers (such as `+91 9876543210`). Support options now route to verified official email channels (`support@maatramfoundation.org`) and an in-app help desk ticket submission.
3. **Empty States vs. Fabricated Fallbacks:** Whenever an API returns zero items or null fields, the mobile client presents an informative empty state illustration with an action button (e.g. "Explore Events", "No Leaderboard Data Yet"), completely preventing artificial data pollution.
