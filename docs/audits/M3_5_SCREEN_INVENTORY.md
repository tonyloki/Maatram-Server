# Maatram Volunteer App — M3.5 Screen Inventory & Master Specification
**Consolidated Phase 13 Milestone — 20 Screens Complete Specification**

---

## 1. Overview & Master Design Alignment

This document establishes the canonical screen inventory for the Maatram Volunteer mobile application, cross-referencing all 20 screens against the approved master design authority:
- **Master Reference**: `docs/audits/ui-ux/references/master_app_design.jpg` (19 Screens + My Activity = 20 Screens Total)
- **Detailed Mentor References**:
  - `ref_01_welcome_splash.jpg` (Screen 01: Welcome / Splash)
  - `ref_02_home_screen.jpg` (Screen 16: Home Screen)
  - `ref_03_my_activity.jpg` (Screen 20: My Activity Screen)

---

## 2. Complete Screen Inventory Table

| ID | Master Section | Screen Name | Flutter Implementation Widget | GoRouter Route | Auth State Requirement | Primary Design Assets / Key Features |
|---|---|---|---|---|---|---|
| **01** | 1. App Entry & Auth | Welcome / Splash Screen | `WelcomeSplashScreen` | `/welcome` | Public / Unauthenticated | Official Tamil/English logo, team hero photo, golden organic swoop, Georgia serif typography, Get Started & Sign In CTAs |
| **02** | 1. App Entry & Auth | Together, We Make a Difference (Sign In) | `LoginScreen` | `/login` | Public / Unauthenticated | Floating card, email & password inputs, password visibility toggle, Forgot Password link, Register link |
| **03** | 2. Password Reset Flow | Forgot Password | `ForgotPasswordScreen` | `/forgot-password` | Public / Unauthenticated | Envelope motif illustration, email input, Send Reset Link action, Back to Sign In |
| **04** | 2. Password Reset Flow | Reset Your Password | `ResetPasswordScreen` | `/reset-password` | Public / Unauthenticated | Padlock illustration, new password & confirm fields, live password requirements checklist, Reset Password CTA |
| **05** | 3. 6-Step Registration | Step 1 of 6: Basic Details | `Step1BasicDetails` | `/register` (Step 1) | Public / Unauthenticated | Full name, email address, mobile number validation, Next CTA |
| **06** | 3. 6-Step Registration | Step 2 of 6: Select Category | `Step2CategorySelection` | `/register` (Step 2) | Public / Unauthenticated | Student, Alumni, Corporate Panelist radio selection cards |
| **07** | 3. 6-Step Registration | Step 3 of 6: Category Details | `Step3CategoryDetails` | `/register` (Step 3) | Public / Unauthenticated | Dynamic fields per category: institution/college, course/degree, graduation/study year |
| **08** | 3. 6-Step Registration | Step 4 of 6: Skills & Availability | `Step4SkillsAvailability` | `/register` (Step 4) | Public / Unauthenticated | Multi-select skill chips (Mentoring, Communication, Content, Event Support), availability dropdown |
| **09** | 3. 6-Step Registration | Step 5 of 6: Privacy & Consent | `Step5PrivacyConsent` | `/register` (Step 5) | Public / Unauthenticated | Toggle switches for directory visibility, leaderboard ranking, impact notifications, media consent |
| **10** | 3. 6-Step Registration | Step 6 of 6: Review & Submit | `Step6ReviewSubmit` | `/register` (Step 6) | Public / Unauthenticated | Summary of entered details, category, skills, and consents; Submit Application CTA |
| **11** | 4. Email Verification & Status | Verify Your Email | `VerifyEmailScreen` | `/verify-email` | PENDING_VERIFICATION | 6-digit OTP code input boxes, resend countdown timer, Verify Email CTA |
| **12** | 4. Email Verification & Status | Email Verification Pending | `PendingVerificationScreen` | `/pending-verification` | PENDING_VERIFICATION | Hourglass motif, instruction list (check inbox/spam, 10 min expiry), Check Status CTA |
| **13** | 4. Email Verification & Status | Pending Under Review | `PendingApprovalScreen` | `/pending-approval` | PENDING_ADMIN_APPROVAL | Clipboard motif, explanation of volunteer application review process, Contact Support CTA |
| **14** | 4. Email Verification & Status | Application Update (Rejected) | `RejectedScreen` | `/rejected` | REJECTED | Rejection status card, dynamic rejection reason display, Contact Support action |
| **15** | 4. Email Verification & Status | Welcome to Maatram! | `WelcomeScreen` | `/welcome-approved` | APPROVED (First Launch) | Confetti popper illustration, warm congratulatory welcome message, Go to Home CTA |
| **16** | 5. Volunteer Portal | Home Screen | `HomeScreen` | `/home` (Tab 0) | APPROVED | Brand header, greeting, volunteer profile card with status chip & points, 4 metric cards (Hours, Events, This Year, Rank), Upcoming Events card, Your Progress ring, Together banner, 4-tab bottom navigation |
| **17** | 5. Volunteer Portal | Events Discovery | `EventsScreen` | `/events` (Tab 1) | APPROVED | Search bar, 4 category filter chips (All, Education, Mentoring, Career), event cards with badges, location & date chips, modal detail sheet with Register/Withdraw |
| **18** | 5. Volunteer Portal | Leaderboard | `LeaderboardScreen` | `/leaderboard` (Tab 2) | APPROVED | 3-way segmented filter (Overall, Students, Alumni), Top-3 podium (#2, #1 elevated with golden crown, #3), ranked volunteer list with point badges |
| **19** | 5. Volunteer Portal | More Menu | `MoreScreen` | `/more` (Tab 3) | APPROVED | Volunteer profile summary header card, menu items with icons (My Activities, My Profile, Notification Settings, Privacy & Consents, Help & Support, About Maatram, Sign Out) |
| **20** | 5. Volunteer Portal | My Activity Screen | `MyActivityScreen` | `/activity` | APPROVED | Brand header with notification bell & avatar, Cupped-Heart illustration with motivational text, 3 segmented tabs (Upcoming, Completed, Cancelled), Upcoming & Past event cards, Together banner |

---

## 3. Supplementary Feature Screens
In addition to the 20 canonical screens, the application provides supplementary routes accessible from the More Menu:
- **`ProfileScreen`** (`/profile`): Detailed volunteer profile view with academic/institution details, emergency contact, and verified status.
- **`PrivacyScreen`** (`/privacy`): Direct access to modify consent toggles and privacy settings post-onboarding.
- **`NotificationsScreen`** (`/notifications`): Notification feed with filter tabs and mark-all-as-read capability.
- **`DevShowcaseScreen`** (`/dev-showcase`): Complete interactive design system catalog showcasing typography, colors, radii, shadows, buttons, badges, feedback states, and animated counters.
