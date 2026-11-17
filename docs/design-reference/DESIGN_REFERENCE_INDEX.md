# Maatram Volunteer Mobile Application — Complete Design Reference Index
**Master Screen Inventory, Implementation Classification & Architectural Registry (38 Screens Across 6 Groups)**

---

## 1. Classification Methodology

Every screen in the inventory is strictly classified under one of four development lifecycle statuses:
1. **Existing Implemented Route**: Screen route is already wired in GoRouter with functional controller and validated UI.
2. **Existing Route Requiring UI Refinement**: Route and data binding exist, but layout/styling requires fine-tuning against Locked Design System v1.0.
3. **New Screen Requiring Implementation**: Route and feature are approved in product scope, but require full UI implementation and controller wiring.
4. **Proposed Screen Requiring Product Approval**: Screen represents an auxiliary capability (e.g., granular setting, FAQ accordion, certificate export) requiring product confirmation.

---

## 2. Definitive Screen Classification Matrix

| # | Group | Screen Name | Route Path | Implementation Classification | Backend Dependency (FastAPI) | Reference File Path |
|---|---|---|---|---|---|---|
| **01** | `01-authentication` | **Welcome / Splash** | `/welcome` | **Existing Implemented Route** | None (Client-side routing) | `01-authentication/welcome_splash.png` *(Mentor Ref 01)* |
| **02** | `01-authentication` | **Login** | `/login` | **Existing Implemented Route** | `POST /api/v1/auth/login` | `01-authentication/login.png` |
| **03** | `01-authentication` | **Forgot Password** | `/forgot-password` | **Existing Route Requiring UI Refinement** | `POST /api/v1/auth/password-reset/request` | `01-authentication/forgot_password.png` |
| **04** | `01-authentication` | **Reset Password** | `/reset-password` | **Existing Route Requiring UI Refinement** | `POST /api/v1/auth/password-reset/confirm` | `01-authentication/reset_password.png` |
| **05** | `02-registration` | **Registration — Step 1: Basic Details** | `/register` (Step 1) | **Existing Implemented Route** | Form state accumulation | `02-registration/registration_basic_details.png` |
| **06** | `02-registration` | **Registration — Step 2: Category Select** | `/register` (Step 2) | **Existing Implemented Route** | Form state accumulation | `02-registration/registration_category.png` |
| **07** | `02-registration` | **Registration — Step 3: Category Details** | `/register` (Step 3) | **Existing Implemented Route** | Form state accumulation | `02-registration/registration_category_details.png` |
| **08** | `02-registration` | **Registration — Step 4: Skills & Availability** | `/register` (Step 4) | **Existing Implemented Route** | Form state accumulation | `02-registration/registration_skills_availability.png` |
| **09** | `02-registration` | **Registration — Step 5: Privacy & Consent** | `/register` (Step 5) | **Existing Implemented Route** | Form state accumulation | `02-registration/registration_privacy_consent.png` |
| **10** | `02-registration` | **Registration — Step 6: Review & Submit** | `/register` (Step 6) | **Existing Implemented Route** | `POST /api/v1/auth/register` | `02-registration/registration_review_submit.png` |
| **11** | `03-verification` | **Email Verification** | `/verify-email` | **Existing Route Requiring UI Refinement** | `POST /api/v1/auth/verify-email` | `03-verification/email_verification.png` |
| **12** | `03-verification` | **Pending Verification** | `/onboarding/pending-verification` | **Existing Implemented Route** | `POST /api/v1/auth/resend-verification` | `03-verification/pending_verification.png` |
| **13** | `03-verification` | **Pending Approval** | `/onboarding/pending-approval` | **Existing Implemented Route** | `GET /api/v1/applications/me` | `03-verification/pending_approval.png` |
| **14** | `03-verification` | **Application Rejected** | `/onboarding/rejected` | **Existing Implemented Route** | `GET /api/v1/applications/me` | `03-verification/application_rejected.png` |
| **15** | `03-verification` | **Post-Approval Welcome** | `/onboarding/welcome` | **Existing Implemented Route** | `GET /api/v1/applications/me` & `/volunteers/me` | `03-verification/post_approval_welcome.png` |
| **16** | `04-main-application` | **Volunteer Home** | `/home` | **Existing Implemented Route** | `/volunteers/me`, `/gamification/summary`, `/events` | `04-main-application/home.png` *(Mentor Ref 02)* |
| **17** | `04-main-application` | **Events Discovery** | `/events` | **Existing Route Requiring UI Refinement** | `GET /api/v1/events` | `04-main-application/events.png` |
| **18** | `04-main-application` | **Event Details** | `/events/:id` | **New Screen Requiring Implementation** | `GET /api/v1/events/{event_id}` | `04-main-application/event_details.png` |
| **19** | `04-main-application` | **Event Registration Confirmation** | `/events/:id/register` | **New Screen Requiring Implementation** | `POST /api/v1/events/{event_id}/register` | `04-main-application/event_registration.png` |
| **20** | `04-main-application` | **My Activity** | `/activity` | **Existing Implemented Route** | `GET /registrations/me`, `GET /attendance/me` | `04-main-application/my_activity.png` *(Mentor Ref 03)* |
| **21** | `04-main-application` | **Activity Record Details** | `/activity/:id` | **New Screen Requiring Implementation** | `GET /api/v1/attendance/me` (Certificate: Preview/Unavailable) | `04-main-application/activity_details.png` |
| **22** | `04-main-application` | **Leaderboard** | `/leaderboard` | **Existing Route Requiring UI Refinement** | `GET /api/v1/gamification/leaderboard` | `04-main-application/leaderboard.png` |
| **23** | `04-main-application` | **More Hub** | `/more` | **Existing Route Requiring UI Refinement** | `GET /api/v1/volunteers/me` | `04-main-application/more.png` |
| **24** | `05-volunteer-account` | **Volunteer Profile** | `/profile` | **Existing Route Requiring UI Refinement** | `GET /api/v1/volunteers/me` | `05-volunteer-account/profile.png` |
| **25** | `05-volunteer-account` | **Edit Profile** | `/profile/edit` | **New Screen Requiring Implementation** | `PATCH /api/v1/volunteers/me` | `05-volunteer-account/edit_profile.png` |
| **26** | `05-volunteer-account` | **Profile Photo Management** | `/profile/photo` | **New Screen Requiring Implementation** | `POST /api/v1/media/signed-upload` + `POST /api/v1/media/assets` | `05-volunteer-account/profile_photo.png` |
| **27** | `05-volunteer-account` | **My Points Overview** | `/points` | **New Screen Requiring Implementation** | `GET /api/v1/gamification/summary` | `05-volunteer-account/points.png` |
| **28** | `05-volunteer-account` | **Points History (Audit Ledger)** | `/points/history` | **New Screen Requiring Implementation** | `GET /api/v1/gamification/ledger` | `05-volunteer-account/points_history.png` |
| **29** | `05-volunteer-account` | **Achievements Gallery** | `/achievements` | **New Screen Requiring Implementation** | `GET /api/v1/gamification/achievements/me` | `05-volunteer-account/achievements.png` |
| **30** | `05-volunteer-account` | **Achievement Details Modal** | `/achievements/:id` | **Proposed Screen Requiring Product Approval** | `GET /api/v1/gamification/achievements/me` | `05-volunteer-account/achievement_details.png` |
| **31** | `06-notifications-settings` | **Notifications Feed** | `/notifications` | **Existing Route Requiring UI Refinement** | `GET /api/v1/notifications/me` | `06-notifications-settings/notifications.png` |
| **32** | `06-notifications-settings` | **Notification Details** | `/notifications/:id` | **Proposed Screen Requiring Product Approval** | `PATCH /api/v1/notifications/{notification_id}/read` | `06-notifications-settings/notification_details.png` |
| **33** | `06-notifications-settings` | **Notification Settings** | `/settings/notifications` | **Proposed Screen Requiring Product Approval** | `POST /api/v1/notifications/device-token` + SharedPreferences | `06-notifications-settings/notification_settings.png` |
| **34** | `06-notifications-settings` | **Privacy & Consent Manager** | `/privacy` | **Existing Route Requiring UI Refinement** | `GET /api/v1/consent/me`, `PUT /api/v1/consent/me` | `06-notifications-settings/privacy_consent.png` |
| **35** | `06-notifications-settings` | **App Settings** | `/settings` | **Proposed Screen Requiring Product Approval** | Device local storage (`SharedPreferences`) | `06-notifications-settings/settings.png` |
| **36** | `06-notifications-settings` | **Help & Support** | `/help` | **Proposed Screen Requiring Product Approval** | Configurable Intent (Email / Support URL) | `06-notifications-settings/help_support.png` |
| **37** | `06-notifications-settings` | **About Maatram** | `/about` | **Proposed Screen Requiring Product Approval** | Static foundation asset | `06-notifications-settings/about_maatram.png` |
| **38** | `06-notifications-settings` | **Logout Confirmation Dialog** | Modal Bottom Sheet | **Existing Route Requiring UI Refinement** | `POST /api/v1/auth/logout` | `06-notifications-settings/logout_confirmation.png` |

---

## 3. Classification Summary

- **Existing Implemented Routes**: 13 Screens (34.2%)
- **Existing Routes Requiring UI Refinement**: 9 Screens (23.7%)
- **New Screens Requiring Implementation**: 8 Screens (21.1%)
- **Proposed Screens Requiring Product Approval**: 8 Screens (21.1%)
- **Total Cataloged Screens**: **38 Screens (100%)**
