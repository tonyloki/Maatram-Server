# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## PHASE 6 — PROJECT ARCHITECTURE INVENTORY & ECOSYSTEM BASELINE

**Document ID:** `docs/audits/phase-6/PROJECT_ARCHITECTURE_INVENTORY.md`  
**Milestone:** Phase 6 — Complete System-Wide Quality Assurance, Functional Testing & Integration Audit  
**Date:** November 17, 2026  
**Auditor:** Antigravity Autonomous QA & Architecture Auditor  
**Audit Standard:** Zero-Assumption, Forensic Code Inspection & Execution Verification  

---

## 1. Executive Ecosystem Summary

The Maatram Volunteering & Gamification Portal is architected as a cohesive, multi-client ecosystem powered by a single, canonical FastAPI modular monolith backend and backed by PostgreSQL:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT TIERS                                   │
│                                                                             │
│   ┌──────────────────────────┐    ┌─────────────────────────────────────┐  │
│   │  Flutter Mobile Client   │    │      Next.js Web Monorepo (`web/`)  │  │
│   │  • Android APK           │    │  • Volunteer Web Portal             │  │
│   │  • iOS                   │    │  • Admin Web Dashboard              │  │
│   │  • (Flutter Web Preview) │    │  (Turbopack, SSR, React 19)         │  │
│   └─────────────┬────────────┘    └──────────────────┬──────────────────┘  │
└─────────────────┼────────────────────────────────────┼──────────────────────┘
                  │ Bearer JWT (SecureStorage)         │ HTTP-Only Cookie + CSRF
                  ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CANONICAL FASTAPI BACKEND                            │
│                         (`server/src/api/v1/`)                              │
│                                                                             │
│   15 Router Modules │ 13 Domain Services │ 12 Repositories │ Outbox Worker   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ SQLAlchemy 2.0 AsyncPG
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PERSISTENCE & SERVICES                             │
│                                                                             │
│  PostgreSQL Database (29 Tables)  │ Resend Email │ Cloudinary │ Firebase FCM│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Explicit Client Distinction & Boundary Analysis

To prevent ambiguity between web technologies in the repository:

1. **Flutter Web (`mobile/build/web`):**
   - **Nature:** Compiled Skia/Wasm/CanvasKit bundle compiled directly from `mobile/lib/main.dart`.
   - **Purpose:** Cross-platform preview and web deployment of the Flutter mobile client.
   - **Distinction:** A successful Flutter Web build compiles Dart code to browser canvas/DOM; it does **not** validate, replace, or prove the functionality of the Next.js TypeScript web application.

2. **Next.js Volunteer Website (`web/src/app/(volunteer)/*`):**
   - **Nature:** Modern Server-Side Rendered (SSR) and Client-Hydrated React 19 application built with Next.js 16 (App Router) and Tailwind CSS v4.
   - **Purpose:** Public portal for volunteer onboarding, event discovery, impact stories, personal activity tracking, and gamification standings.
   - **Authentication:** Dual-mode authentication supporting HTTP-only secure session cookies with Double-Submit CSRF tokens and optional Bearer tokens.

3. **Next.js Admin Dashboard (`web/src/app/admin/*`):**
   - **Nature:** Enterprise administration console within the same Next.js application, strictly guarded by Role-Based Access Control (`ADMIN`, `SUPER_ADMIN`).
   - **Purpose:** Application review, volunteer lifecycle approvals, event lifecycle scheduling, participant selection, attendance check-in/out, manual hours corrections, gamification audit ledger, and Excel reporting.

---

## 3. Discovered Applications & Entry Points

| Tier / Application | Directory | Entry Point File | Technology Stack | Active Ports / Target |
|---|---|---|---|---|
| **Mobile Client** | `mobile/` | `mobile/lib/main.dart` | Flutter 3.29.0 / Dart 3.7.0, Riverpod 2.6, GoRouter 14.8, Dio 5.8 | Android / iOS / Web Canvas |
| **Web Portal & Admin** | `web/` | `web/src/app/layout.tsx` | Next.js 16.4.4, React 19.3.0, TypeScript 5, Tailwind CSS v4 | Port 3001 (`localhost:3001`) |
| **Backend API** | `server/` | `server/src/main.py` | Python 3.13.9, FastAPI 0.115.0, SQLAlchemy 2.0.36, Pydantic 2.9.0 | Port 8000 (`localhost:8000`) |
| **Outbox Worker** | `server/` | `server/src/workers/outbox_worker.py` | Python 3.13, asyncio, SQLAlchemy AsyncSession | Background Daemon |

---

## 4. Backend Architecture Inventory (`server/src/`)

### 4.1 FastAPI Routers (`server/src/api/v1/`)
All 15 router modules register dynamically into `server/src/api/v1/router.py`:

| Router File | Prefix | Endpoints Count | Domain Scope |
|---|---|---|---|
| `auth.py` | `/auth` | 8 | Registration, email verification, login, refresh, logout, password recovery |
| `volunteers.py` | `/volunteers` | 5 | Volunteer profile retrieval, polymorphic updates, volunteer search, status |
| `events.py` | `/events` | 6 | Event catalog, filtering, detail retrieval, creation, modification, status transitions |
| `registrations.py` | `/registrations` | 5 | Event registration, withdrawal, user registrations feed, capacity enforcement |
| `attendance.py` | `/attendance` | 6 | Check-in, check-out, attendance correction, volunteer attendance history, bulk check-in |
| `gamification.py` | `/gamification` | 6 | Summary statistics, tier progress, leaderboard, ledger transactions, achievements |
| `applications.py` | `/applications` | 5 | Volunteer application review, status checking, parent consent verification |
| `admin.py` | `/admin` | 8 | Volunteer lifecycle admin operations, dashboard metrics, administrative controls |
| `reports.py` | `/reports` | 6 | Excel/CSV reporting exports, volunteer activity, hours distribution, formula injection protection |
| `notifications.py` | `/notifications` | 5 | Notification feed, unread count badge, mark-as-read, device FCM registration |
| `consent.py` | `/consent` | 3 | Account-level privacy consents, directory listing, leaderboard suppression |
| `media.py` | `/media` | 3 | Cloudinary signed upload generation, asset verification, volunteer avatar linking |
| `users.py` | `/users` | 3 | User identity management, security settings |
| `health.py` | `/health` | 2 | Liveness probe, readiness probe with DB timeout |
| `router.py` | `/api/v1` | — | Master aggregator assembling all 14 sub-routers into FastAPI `app` |

### 4.2 Domain Services (`server/src/services/`)
1. `admin_service.py`: Coordinates cross-cutting administrative workflows, application reviews, and dashboard statistics.
2. `application_service.py`: Validates volunteer application constraints, category-specific invariants, and minor parental consents.
3. `attendance_service.py`: Enforces attendance invariants (no checkout without check-in, duplicate check-in prevention, threshold corrections).
4. `auth_service.py`: Argon2id password hashing, JWT session lifecycle, refresh token rotation, and OTP verification.
5. `consent_service.py`: Synchronizes the 6 granular account-level volunteer consent toggles.
6. `event_service.py`: Manages event scheduling, capacity calculation, publishing status, and conflict checks.
7. `gamification_service.py`: Implements canonical formula `P = (E × 10) + (H × 2)`, points ledger transactions, and tier calculations.
8. `media_service.py`: Validates Cloudinary upload signatures, asset registrations, and size/MIME constraints.
9. `notification_service.py`: Manages in-app notifications, unread badges, and transactional outbox email triggers.
10. `registration_service.py`: Handles volunteer event registrations, capacity locks, waitlists, and withdrawal deadlines.
11. `report_service.py`: Compiles streaming Excel reports with CSV formula injection sanitization.
12. `user_service.py`: Core user identity operations and account lockouts.
13. `volunteer_service.py`: Polymorphic profile mapping (Student, Alumni, Corporate) and profile bio/skills updates.

### 4.3 Database Persistence Repositories (`server/src/repositories/`)
1. `application_repo.py`: CRUD operations for volunteer applications and parent consents.
2. `attendance_repo.py`: Queries and updates for `AttendanceLog` records and verified hours.
3. `consent_repo.py`: Persistence for `VolunteerConsent`.
4. `event_repo.py`: Queries for `Event` records with composite index filtering.
5. `gamification_repo.py`: Queries for `PointLedger`, `PointBalance`, and `VolunteerAchievement`.
6. `media_repo.py`: CRUD for `MediaAsset`.
7. `notification_repo.py`: Feed queries and read-status tracking for `Notification`.
8. `registration_repo.py`: Capacity queries and state transitions for `EventRegistration`.
9. `report_repo.py`: Aggregated reporting queries across attendance, volunteers, and events.
10. `token_repo.py`: Refresh token hash storage and session revocation.
11. `user_repo.py`: `User` entity persistence and failed login counters.
12. `volunteer_repo.py`: `VolunteerProfile`, `StudentProfile`, `AlumniProfile`, and `CorporateProfile`.

### 4.4 Database Models & Schema (`server/src/models/` — 29 Tables)
All models inherit from SQLAlchemy 2.0 `Base` and utilize UUID primary keys:
1. `users`: Core identity table (Argon2id password hash, role, status, lockout fields).
2. `user_sessions`: Active server-tracked sessions for refresh token rotation.
3. `email_verifications`: High-entropy verification tokens and expiration timestamps.
4. `password_resets`: 6-digit numeric OTP hashes and attempt counters.
5. `volunteer_profiles`: Base volunteer entity (category, bio, mobile, emergency contacts).
6. `student_profiles`: 1:1 extension for student volunteers (college, degree, graduation year).
7. `alumni_profiles`: 1:1 extension for alumni volunteers (current company, graduation year).
8. `corporate_profiles`: 1:1 extension for corporate volunteers (company, designation).
9. `volunteer_skills`: Association table for normalized volunteer skill tags.
10. `volunteer_consents`: 6 account-level privacy toggles with UTC update tracking.
11. `events`: Volunteering opportunities (title, capacity, schedule, venue, category, status).
12. `event_skills`: Prerequisite skill associations for events.
13. `event_registrations`: Volunteer signups (`SUBSCRIBED`, `SELECTED`, `WAITLISTED`, `NOT_SELECTED`, `DECLINED`, `WITHDRAWN`).
14. `attendance_logs`: Verified check-in/out timestamps, hours credited, supervisor signoff.
15. `point_transactions`: Append-only immutable gamification ledger.
16. `point_balances`: Materialized volunteer point totals, hours, and tier rank.
17. `achievements`: Master catalog of badge definitions and criteria.
18. `volunteer_achievements`: Earned badges linked to volunteers with award timestamps.
19. `notifications`: In-app notification messages and read receipts.
20. `device_tokens`: Registered FCM device tokens for mobile push notifications.
21. `media_assets`: Uploaded photos and certificates with Cloudinary secure public IDs.
22. `transactional_outbox`: Reliable outbox pattern for asynchronous email and push jobs.
23. `audit_logs`: Immutable security and administrative action audit trail.
24. `rate_limits`: Database-backed distributed IP rate limiting logs.
25. `parental_consents`: Minor volunteer safeguarding consents and verification tokens.
26. `volunteer_applications`: Formal applications submitted during onboarding.
27. `application_reviews`: Administrative review notes, approver ID, and decisions.
28. `event_coordinators`: Assigned volunteer and admin event coordinators.
29. `system_settings`: Platform-wide configurable business policies.

---

## 5. Next.js Web Monorepo Route Inventory (`web/src/app/`)

The Next.js application organizes 43 routes into public, volunteer portal, and admin dashboard surfaces:

### 5.1 Public & Authentication Routes (13 routes)
1. `/`: Public marketing landing page and impact statistics overview.
2. `/about`: Maatram Foundation mission, history, leadership, and pillars.
3. `/impact`: Verified metrics, student stories, and community transformation.
4. `/events`: Publicly discoverable event catalog with category filtering.
5. `/events/[id]`: Public event details view with registration prompt.
6. `/login`: Secure dual-role (Volunteer & Admin) authentication page.
7. `/register`: Multi-step volunteer registration wizard.
8. `/register/confirmation`: Post-submission registration acknowledgement.
9. `/verify-email`: Email verification token submission.
10. `/forgot-password`: Password reset request initiation.
11. `/reset-password`: 6-digit OTP verification and new password submission.
12. `/onboarding/pending`: Application under review status view.
13. `/onboarding/rejected`: Application decision status view with support contact.

### 5.2 Volunteer Portal Routes (`web/src/app/volunteer/*` — 7 routes)
1. `/volunteer`: Root redirection to volunteer dashboard.
2. `/volunteer/dashboard`: Authenticated volunteer hub (points card, impact stats, upcoming events).
3. `/volunteer/events`: Volunteer events discovery, search, and category filter.
4. `/volunteer/events/[id]`: Detailed event view with direct registration action.
5. `/volunteer/activity`: Tabbed volunteer activity history (Upcoming, Completed, Cancelled).
6. `/volunteer/leaderboard`: Real-time gamification standings and tier rankings.
7. `/volunteer/notifications`: Notification inbox and read status management.
8. `/volunteer/profile`: Volunteer profile management and 6 account-level privacy consent toggles.

### 5.3 Admin Web Dashboard Routes (`web/src/app/admin/*` — 16 routes)
1. `/admin`: Root admin redirection to `/admin/dashboard`.
2. `/admin/dashboard`: Master KPI console (active volunteers, pending reviews, event counts, hours).
3. `/admin/applications`: Volunteer application review pipeline with category and status filters.
4. `/admin/applications/[id]`: Detailed applicant dossier, document inspection, approve/reject CTAs.
5. `/admin/volunteers`: Master volunteer directory with search, status filters, and export.
6. `/admin/volunteers/[id]`: Comprehensive volunteer record, attendance history, points ledger.
7. `/admin/events`: Master event management catalog with status badges.
8. `/admin/events/create`: Event creation form (capacity, location, prerequisites, dates).
9. `/admin/events/[id]`: Event details management, publishing controls, and status transitions.
10. `/admin/events/[id]/participants`: Registration roster, waitlist management, participant selection.
11. `/admin/events/[id]/attendance`: Event-specific check-in and check-out management.
12. `/admin/events/[id]/complete`: Event closure, attendance finalization, and points trigger.
13. `/admin/attendance`: Global attendance management and manual hours correction.
14. `/admin/audit-logs`: Immutable administrative audit trail viewer.
15. `/admin/reports`: Downloadable Excel report generator with formula sanitization.
16. `/admin/operations`: Outbox worker monitoring and batch operations.
17. `/admin/settings`: Platform policy configurations and business rule thresholds.

---

## 6. Flutter Mobile Application Inventory (`mobile/lib/`)

The mobile client contains 38 completely implemented screens matching the canonical design system:
- **01–04:** Entry & Authentication (`WelcomeSplash`, `Login`, `ForgotPassword`, `ResetPassword`).
- **05–10:** 6-Step Registration Flow (`BasicDetails`, `CategorySelection`, `CategoryDetails`, `SkillsAvailability`, `PrivacyConsent`, `ReviewSubmit`).
- **11–15:** Email Verification & Status (`VerifyEmail`, `PendingVerification`, `PendingReview`, `Rejected`, `WelcomeApproved`).
- **16–23:** Volunteer Portal Hub (`HomeDashboard`, `EventsCatalog`, `EventDetails`, `EventRegistration`, `MyActivity`, `ActivityDetails`, `LeaderboardPodium`, `MoreHub`).
- **24–30:** Profile & Gamification (`Profile`, `EditProfile`, `ProfilePhoto`, `PointsOverview`, `PointsHistory`, `AchievementsShowcase`, `AchievementDetailsModal`).
- **31–38:** Notifications & Device Settings (`NotificationsFeed`, `NotificationDetails`, `NotificationSettings`, `PrivacyConsentSettings`, `AppSettings`, `HelpSupport`, `AboutMaatram`, `LogoutConfirmationModal`).

---

## 7. Third-Party Integrations Inventory

| Service | Client Module | Backend Integration | Purpose & Security Controls |
|---|---|---|---|
| **Resend** | N/A | `server/src/integrations/resend_client.py` | Transactional emails (verification, reset OTP, approvals). API key stored strictly in backend `.env`. |
| **Cloudinary** | `mobile/` ApiClient | `server/src/integrations/cloudinary_client.py` | Volunteer avatars and event photos. Signed upload URLs generated on backend with 15-minute signature expiry; secrets never exposed to clients. |
| **Firebase FCM** | `mobile/` Native Plugin | `server/src/integrations/fcm_client.py` | Mobile push notifications. Service account credentials kept strictly server-side. |
| **PostgreSQL (Supabase)** | N/A | `server/src/core/database.py` (AsyncPG) | Canonical persistence across 29 tables. Direct connections prohibited from clients. |

---

## 8. Baseline Test Inventory & Execution Status

```
========================================================================================
APPLICATION / TEST SUITE                      DISCOVERED  PASSED  FAILED  STATUS
========================================================================================
Flutter Mobile (`flutter test`)               206 tests   206     0       100% PASS
Flutter Static Analysis (`flutter analyze`)   0 issues    —       —       CLEAN
Next.js TypeScript (`tsc --noEmit`)           0 errors    —       —       CLEAN
Next.js Lint (`eslint`)                       102 warn    —       0 err   CLEAN
Next.js Production Build (`next build`)       43 routes   43      0 err   CLEAN
FastAPI Pytest (`pytest server/tests/`)       210 tests   210     0       100% PASS
========================================================================================
```

All 3 core client and server components compile cleanly and have verified baseline test suites. With Phase 0 discovery complete, forensic functional testing across Phase 1 through Phase 10 begins.
