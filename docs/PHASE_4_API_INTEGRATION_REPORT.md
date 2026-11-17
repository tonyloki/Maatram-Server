# Phase 4 API Integration Report — Verified FastAPI Schemas & Client Bindings
**Maatram Volunteering & Gamification Portal**  
**Document ID**: `MTR-REP-P4-API-001`  
**Date**: November 16, 2026  
**Status**: VERIFIED & PRODUCTION READY

---

## 1. Overview & Backend Non-Negotiables

In strict adherence to the **Core Operating Principles**:
- **Zero backend modifications**: No FastAPI files, SQLAlchemy models, Alembic migrations, or database tables were modified during Phase 4.
- **Single Source of Truth**: All dynamic data is fetched from canonical PostgreSQL records via FastAPI v1 endpoints.
- **Zero Mock Endpoints**: The Flutter application interacts with actual backend routes using strongly-typed models deserialized from JSON responses.

---

## 2. Canonical FastAPI Endpoint Integration Matrix

### A. Authentication & Session Module
| Endpoint Path | HTTP Method | Request Body / Params | Response DTO / Model | Used In Flutter Screen |
|---|---|---|---|---|
| `/api/v1/auth/login` | `POST` | `LoginRequest` (`email`, `password`) | `TokenResponse` (`access_token`, `refresh_token`, `user`) | Screen 02: `LoginScreen` |
| `/api/v1/auth/register` | `POST` | `VolunteerRegisterRequest` | `VolunteerRegisterResponse` (`user_id`, `status`) | Screen 10: `RegisterStep6ReviewScreen` |
| `/api/v1/auth/verify-email` | `POST` | `VerifyEmailRequest` (`token`) | `MessageResponse` | Screen 11: `EmailVerificationScreen` |
| `/api/v1/auth/forgot-password` | `POST` | `ForgotPasswordRequest` (`email`) | `MessageResponse` | Screen 03: `ForgotPasswordScreen` |
| `/api/v1/auth/reset-password` | `POST` | `ResetPasswordRequest` (`token`, `new_password`) | `MessageResponse` | Screen 04: `ResetPasswordScreen` |
| `/api/v1/auth/refresh` | `POST` | `RefreshTokenRequest` (`refresh_token`) | `TokenResponse` | Global: `ApiClient` interceptor |
| `/api/v1/auth/logout` | `POST` | Header Bearer Token | `MessageResponse` | Screen 38: `LogoutConfirmationDialog` |

### B. User Profile & Account Module
| Endpoint Path | HTTP Method | Request Body / Params | Response DTO / Model | Used In Flutter Screen |
|---|---|---|---|---|
| `/api/v1/users/me/profile` | `GET` | Header Bearer Token | `VolunteerProfileResponse` | Screens 16, 23, 24, 25: Home, More, Profile |
| `/api/v1/users/me/profile` | `PUT` | `VolunteerProfileUpdateRequest` | `VolunteerProfileResponse` | Screen 25: `EditProfileScreen` |

### C. Events & Attendance Module
| Endpoint Path | HTTP Method | Request Body / Params | Response DTO / Model | Used In Flutter Screen |
|---|---|---|---|---|
| `/api/v1/events` | `GET` | `category`, `status`, `page`, `limit` | `PaginatedResponse[EventListItem]` | Screen 16, 17: Home, Events |
| `/api/v1/events/{id}` | `GET` | Path `id: UUID` | `EventDetailResponse` | Screen 18: `EventDetailsScreen` |
| `/api/v1/events/{id}/register` | `POST` | Path `id: UUID` | `RegistrationConfirmation` | Screen 19: `EventRegistrationScreen` |
| `/api/v1/attendance/my` | `GET` | `status`, `page`, `limit` | `PaginatedResponse[AttendanceRecord]` | Screen 20: `MyActivityScreen` |
| `/api/v1/attendance/{id}` | `GET` | Path `id: UUID` | `AttendanceDetailResponse` | Screen 21: `ActivityDetailsScreen` |

### D. Gamification & Leaderboard Module
| Endpoint Path | HTTP Method | Request Body / Params | Response DTO / Model | Used In Flutter Screen |
|---|---|---|---|---|
| `/api/v1/gamification/summary` | `GET` | Header Bearer Token | `GamificationSummaryResponse` | Screens 16, 20, 24, 27: Home, Activity, Profile, Points |
| `/api/v1/gamification/ledger` | `GET` | `page`, `limit` | `PaginatedResponse[LedgerTransaction]` | Screen 28: `PointsHistoryScreen` |
| `/api/v1/gamification/badges` | `GET` | Header Bearer Token | `List[BadgeItemResponse]` | Screens 29, 30: Achievements, Modal |
| `/api/v1/leaderboard` | `GET` | `cycle_year`, `category`, `limit` | `LeaderboardResponse` | Screen 22: `LeaderboardScreen` |

### E. Privacy, Consents & Notifications Module
| Endpoint Path | HTTP Method | Request Body / Params | Response DTO / Model | Used In Flutter Screen |
|---|---|---|---|---|
| `/api/v1/consent/me` | `GET` | Header Bearer Token | `ConsentResponse` (6 statutory flags) | Screen 09, 34: Reg Step 5, PrivacyScreen |
| `/api/v1/consent/me` | `PUT` | `ConsentUpdateRequest` | `ConsentResponse` | Screen 34: `PrivacyScreen` |
| `/api/v1/notifications` | `GET` | `unread_only`, `page`, `limit` | `PaginatedResponse[NotificationItem]` | Screens 16, 23, 31: Home, More, Notifications |
| `/api/v1/notifications/{id}/read`| `PUT` | Path `id: UUID` | `MessageResponse` | Screen 32: `NotificationDetailsScreen` |

---

## 3. Disambiguation: Device-Local Preferences vs. Account Privacy

A critical architectural distinction verified during Phase 4:
1. **Device-Local Preferences (`SharedPreferences`)**:
   - `pref_device_event_reminders`: Push alert 24h prior to event.
   - `pref_device_points_alerts`: Local badge and karma sound/banner alerts.
   - `pref_device_announcements`: Push alerts for coordinator updates.
   - `pref_device_quiet_hours`: Silence push triggers between 10 PM and 7 AM.
   - `pref_biometrics_enabled`: Device hardware biometric quick-unlock flag.
2. **Account-Level Privacy & Consents (`/api/v1/consent/me`)**:
   - `leaderboard_visible`: Statutory consent for public leaderboard ranking.
   - `name_visible`: Full name display vs. anonymized volunteer handle.
   - `thank_you_emails`: Beneficiary and organizer impact communication.
   - `linkedin_content`: Foundation marketing and story attribution.
   - `contact_available`: Intra-volunteer directory coordination availability.
   - `media_usage`: Event photo and video gallery publication consent.

---

## 4. Verification Summary

All client data models (`mobile/lib/core/models/`) match the FastAPI response shapes with 100% field type alignment. No undefined attributes, missing nullability checks, or type conversion anomalies exist.
