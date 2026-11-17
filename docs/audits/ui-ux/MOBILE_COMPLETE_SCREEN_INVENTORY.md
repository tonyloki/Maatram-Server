# MAATRAM VOLUNTEER APP — COMPLETE SCREEN INVENTORY
**Comprehensive Census of Routes, Implemented Screens, Visual References & Verification Status**

---

## 1. Executive Summary

This inventory documents every screen, destination, and nested flow discovered across the Maatram Flutter volunteer codebase (`mobile/`).

- **Total Screens / Routes Discovered**: 19 screens/views across 5 functional domains.
- **Screens with Official Approved Design References (Mentor Designs)**: 3 screens.
  1. *Welcome / Splash Screen* (`ref_01_welcome_splash.jpg`)
  2. *Volunteer Home Screen* (`ref_02_home_screen.jpg`)
  3. *My Activity Screen* (`ref_03_my_activity.jpg`)
- **Screens Fully Implemented**: 15 screens.
- **Screens in Placeholder / Shell Status**: 3 screens (`EventsPlaceholderScreen`, `LeaderboardPlaceholderScreen`, `MorePlaceholderScreen`).
- **Screens with Missing Visual Implementation**: 2 mentor references are not yet integrated into the live route hierarchy:
  - *Reference 1 (Welcome / Splash Screen)* is missing from the initial app entrance.
  - *Reference 3 (My Activity Screen)* is not yet implemented as a destination or nested route.

---

## 2. Complete Screen Inventory Table

| # | Route Path | Screen Class Name | Source File | Design Reference Status | Implementation Status | Visual Verification |
|---|---|---|---|---|---|---|
| 1 | `/` (Implicit) | *N/A (Redirects to `/home` or `/login`)* | `mobile/lib/app/router/app_router.dart` | **Approved Ref 1** (`ref_01_welcome_splash.jpg`) | ❌ **Missing Initial Splash Route** | **Gapped** (Redirects straight to login) |
| 2 | `/login` | `LoginScreen` | `mobile/lib/features/auth/presentation/login_screen.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** (`01_login_screen.png`) |
| 3 | `/register` (Step 1) | `Step1BasicDetails` | `mobile/lib/features/registration/presentation/steps/step1_basic_details.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** (`04_registration_step1.png`) |
| 4 | `/register` (Step 2) | `Step2CategorySelection` | `mobile/lib/features/registration/presentation/steps/step2_category_selection.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** |
| 5 | `/register` (Step 3) | `Step3CategoryDetails` | `mobile/lib/features/registration/presentation/steps/step3_category_details.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** |
| 6 | `/register` (Step 4) | `Step4SkillsAvailability` | `mobile/lib/features/registration/presentation/steps/step4_skills_availability.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** |
| 7 | `/register` (Step 5) | `Step5PrivacyConsent` | `mobile/lib/features/registration/presentation/steps/step5_privacy_consent.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** |
| 8 | `/register` (Step 6) | `Step6AccountReview` | `mobile/lib/features/registration/presentation/steps/step6_account_review.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** |
| 9 | `/verify-email` | `VerifyEmailScreen` | `mobile/lib/features/auth/presentation/verify_email_screen.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** (`05_verify_email.png`) |
| 10 | `/forgot-password` | `ForgotPasswordScreen` | `mobile/lib/features/auth/presentation/forgot_password_screen.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** (`06_forgot_password.png`) |
| 11 | `/reset-password` | `ResetPasswordScreen` | `mobile/lib/features/auth/presentation/reset_password_screen.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** (`07_reset_password.png`) |
| 12 | `/onboarding/pending-verification` | `PendingVerificationScreen` | `mobile/lib/features/onboarding/presentation/pending_verification_screen.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** (`08_pending_verification.png`) |
| 13 | `/onboarding/pending-approval` | `PendingApprovalScreen` | `mobile/lib/features/onboarding/presentation/pending_approval_screen.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** (`09_pending_approval.png`) |
| 14 | `/onboarding/rejected` | `RejectedScreen` | `mobile/lib/features/onboarding/presentation/rejected_screen.dart` | Design-System-Reviewed (App Answers M2) | ✅ **Fully Implemented** | **Verified** (`10_rejected.png`) |
| 15 | `/onboarding/welcome` | `WelcomeScreen` | `mobile/lib/features/onboarding/presentation/welcome_screen.dart` | Design-System-Reviewed (Post-Approval Onboarding) | ✅ **Fully Implemented** | **Verified** (`02_post_approval_welcome.png`) |
| 16 | `/home` | `HomeScreen` | `mobile/lib/features/home/presentation/home_screen.dart` | **Approved Ref 2** (`ref_02_home_screen.jpg`) | ✅ **Fully Implemented** | **Verified** (`03_home_screen_390dp.png`) |
| 17 | `/events` | `EventsPlaceholderScreen` | `mobile/lib/features/events/presentation/events_placeholder_screen.dart` | Design-System-Reviewed (M1 Foundation) | ⚠️ **Shell / Mockup Placeholder** | **Verified** (`11_events_tab.png`) |
| 18 | `/leaderboard` | `LeaderboardPlaceholderScreen` | `mobile/lib/features/leaderboard/presentation/leaderboard_placeholder_screen.dart` | Design-System-Reviewed (M1 Foundation) | ⚠️ **Shell / Mockup Placeholder** | **Verified** (`12_leaderboard_tab.png`) |
| 19 | `/more` | `MorePlaceholderScreen` | `mobile/lib/features/more/presentation/more_placeholder_screen.dart` | Design-System-Reviewed (M1 Foundation) | ⚠️ **Shell / Mockup Placeholder** | **Verified** (`13_more_tab.png`) |
| 20 | `/more/activity` *(Missing Route)* | *Not implemented* | *None* | **Approved Ref 3** (`ref_03_my_activity.jpg`) | ❌ **Missing Implementation** | **Gapped** (Tile in `/more` is unlinked) |
| 21 | `/dev/showcase` | `DevShowcaseScreen` | `mobile/lib/features/dev_showcase/presentation/dev_showcase_screen.dart` | Design-System-Reviewed (Engineering Showcase) | ✅ **Fully Implemented** | **Verified** (`14_dev_showcase.png`) |

---

## 3. Reference vs Screen Alignment Summary

### Approved Reference 1: Welcome / Splash Screen
- **Reference Asset**: `docs/audits/ui-ux/references/ref_01_welcome_splash.jpg`
- **Reference Concept**: Full-height brand visual with Maatram logo, volunteer sunrise photograph, gold swoop, and "Volunteer for a Better Tomorrow" headline.
- **Codebase Mapping**: No standalone splash/welcome entry route currently exists. Unauthenticated launches currently bypass this entirely and display `/login`.
- **Finding**: **High-priority gap**. This screen must be introduced as the top-of-funnel entry before `/login`.

### Approved Reference 2: Volunteer Home Screen
- **Reference Asset**: `docs/audits/ui-ux/references/ref_02_home_screen.jpg`
- **Reference Concept**: 8-section volunteer portal with header, welcome greeting, profile & points card, impact statistics, upcoming events carousel, progress journey, and community banner.
- **Codebase Mapping**: `mobile/lib/features/home/presentation/home_screen.dart`.
- **Finding**: **Implemented & dynamically integrated**. Matches reference closely with specific polish refinements identified in Section 4.

### Approved Reference 3: My Activity Screen
- **Reference Asset**: `docs/audits/ui-ux/references/ref_03_my_activity.jpg`
- **Reference Concept**: Segmented tabs (`Upcoming`, `Completed`, `Cancelled`), vertical accent bar headers, event cards with status badges and chvrons, motivational bottom banner.
- **Codebase Mapping**: Currently represented only as an inactive navigation tile inside `MorePlaceholderScreen`.
- **Finding**: **High-priority missing screen**. Must be implemented under `/more/activity` or as a primary sub-flow.
