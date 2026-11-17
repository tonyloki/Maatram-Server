# Mobile M2 Milestone Implementation Report
**Maatram Volunteering & Gamification Portal — Mobile (Volunteer App)**
**Milestone:** M2 — Authentication, Registration, Verification, Onboarding & Session Management
**Authoritative Reference:** `docs/App answers.pdf`
**Date:** November 2026

---

## 1. Executive Summary

Milestone M2 of the **Maatram Volunteer Mobile Application (`maatram_mobile`)** has been completed in one continuous implementation. M2 delivers the complete volunteer lifecycle foundation: from brand-authentic login, through a six-step guided registration wizard with 3 category tracks and 6 independent consent preferences, token-based verification, secure OTP password recovery, calm application status wait states, and an approved celebration welcome experience.

All screen text, headline copy, error messages, and neutral security statements are directly synchronized with the official product requirements in `docs/App answers.pdf`.

---

## 2. Work Package Details & Deliverables

### M2.1 — Complete Login Experience & Ergonomics
- **Visual Structure**:
  - Hero image with authentic volunteering photography (`assets/images/hero-volunteering.jpg`) and brand logo container.
  - Floating card layout elevated above the warm ivory organic background (`#FAF8F5`).
- **Brand Copy**:
  - **Headline**: `"Together, We Make a Difference."`
  - **Supporting Text**: `"Welcome to the Maatram volunteer community. Sign in and continue your journey of creating meaningful change."`
- **Field Ergonomics**:
  - Email field with `AutofillHints.email` and format validation.
  - Password field with `AutofillHints.password`, visibility toggle (eye icon), and `KeyboardLockMode.capsLock` warning indicator (*"Caps Lock is ON"*).
- **Exact Error Copy**:
  - Empty email: `Enter your email address.`
  - Invalid email: `Enter a valid email address.`
  - Empty password: `Enter your password.`
  - Credential mismatch: `The email address or password is incorrect.`
  - Unverified email: `Please verify your email address to continue.`
  - Offline / disconnect: `You’re offline. Check your internet connection and try again.`
  - Server failure: `We couldn’t complete your request right now. Please try again.`
- **Post-Login 4-State Routing**:
  - `PENDING_VERIFICATION` -> `/onboarding/pending-verification`
  - `PENDING_ADMIN_APPROVAL` -> `/onboarding/pending-approval`
  - `REJECTED` -> `/onboarding/rejected`
  - `APPROVED` -> `/onboarding/welcome` (first launch) or `/home` (returning volunteer)

---

### M2.2 — Six-Step Guided Registration Wizard
- **Progress Header**: Dynamic step title and linear progress indicator (1 to 6).
- **Step 1: Basic Details**:
  - First Name, Last Name, Email, Mobile Number (pre-filled with `+91`), Age selector, Gender dropdown (`MALE`, `FEMALE`, `OTHER`, `PREFER_NOT_TO_SAY`).
- **Step 2: Volunteer Category Selection**:
  - Interactive selection cards with Maatram gold active state:
    1. **Student Volunteer** (`STUDENT`): For currently enrolled college/university students.
    2. **Alumni Mentor** (`ALUMNI`): For graduated alumni guiding students.
    3. **Corporate Panelist** (`CORPORATE`): For industry professionals participating in interviews and mentorship.
- **Step 3: Category-Specific Details**:
  - *Student*: College name, degree, department, batch year, current year of study, optional Maatram reg number.
  - *Alumni*: Alma mater college, degree, department, batch year, graduation year, current company, job role, years of experience, city.
  - *Corporate*: Employer organization, designation, total years of experience, city.
- **Step 4: Skills & Availability**:
  - Multi-select interactive filter chips for volunteering skills (Mentoring, School Visits, Mock Interviews, Event Coordination, etc.).
  - Radio selection for weekly availability (Weekends, Weekdays & Weekends, Flexible/On-call, Evenings).
- **Step 5: Privacy & Consent (6 Independent Preferences)**:
  1. `leaderboard_visible`: Show profile on public volunteer leaderboards.
  2. `name_visible`: Display real name on public impact recognition pages.
  3. `thank_you_emails`: Receive quarterly appreciation & thank-you email updates.
  4. `linkedin_content`: Allow mentioning participation in Maatram LinkedIn impact stories.
  5. `contact_available`: Allow coordinators to contact directly for urgent on-ground support.
  6. `media_usage`: Consent to photos and videos taken during events being used for foundation reporting.
  - *Mandatory*: Terms of Service & Privacy Policy agreement checkbox.
- **Step 6: Account Review & Credentials**:
  - Password creation (min 8 chars) with confirm password check and visibility toggles.
  - Comprehensive summary review card displaying all entered personal, academic/professional, and availability data.
  - Direct submission via `POST /api/v1/auth/register`.

---

### M2.3 — Email Verification Architecture
- **Screen**: `VerifyEmailScreen`.
- **Masked Email Display**: Privacy-conscious email display (e.g. `n***y@gmail.com`).
- **Token Input**: Text field supporting token paste or deep-link parsing.
- **Delivery Uncertainty Notice**:
  > *"We couldn’t confirm email delivery yet. Please check your inbox and spam folder, then try again later."*
- **Action**: Direct submission to `POST /api/v1/auth/verify-email`. Upon verification, status transitions to `PENDING_ADMIN_APPROVAL`.

---

### M2.4 — Password Recovery & Reset Flow
- **Request Step (`ForgotPasswordScreen`)**:
  - Volunteer inputs registered email.
  - Submits to `POST /api/v1/auth/password-reset/request`.
  - Neutral security response preventing email enumeration:
    > *"If an account matches this email, password-reset instructions will be sent."*
- **Confirm Step (`ResetPasswordScreen`)**:
  - Volunteer inputs 6-digit numeric OTP, new password, and confirmed password.
  - Submits to `POST /api/v1/auth/password-reset/confirm`.
  - On success, redirects to `/login` with success feedback.

---

### M2.5 — Dedicated Application Status Screens
- **Pending Verification (`PendingVerificationScreen`)**:
  - Calm gold envelope icon.
  - Exact copy: *"Your email address hasn’t been verified yet. Please complete email verification to continue with your Maatram volunteer application. Check your inbox for the verification code, or request a new code if available."*
  - CTAs: "Enter Verification Token", "Sign Out".
- **Pending Admin Approval (`PendingApprovalScreen`)**:
  - Dignified green hourglass icon.
  - Exact copy: *"Your email is verified and your volunteer application has been submitted successfully. The Maatram team is reviewing your application. You’ll be able to access volunteer activities once your application is approved. Thank you for your patience and your interest in making a difference."*
  - Interactive "Check Approval Status" button calling `/users/me` session refresh.
- **Rejected Screen (`RejectedScreen`)**:
  - Respectful tone with foundation contact details.
  - Exact copy: *"Thank you for your interest in volunteering with Maatram. We’re unable to approve your application at this time."*
  - Support contact: `support@maatramfoundation.org`.

---

### M2.6 — Auth Session & API Integration
- **State Management**: Centralized `AuthController` (Riverpod `StateNotifier<AuthState>`).
- **Security & Persistence**:
  - JWT access & refresh tokens stored in platform KeyStore / Keychain via `flutter_secure_storage`.
  - Session restoration on app cold start.
  - Automatic 401 refresh interceptor with token rotation.
  - Immediate local session drop on 401 refresh failure.
- **Network Boundaries**:
  - Strict timeout settings: 10s connection, 30s receive/send.
  - Zero retry on non-idempotent `POST /auth/register`.

---

### M2.7 — First-Time Welcome Experience
- **Screen**: `WelcomeScreen`.
- **Approved Celebration Header**: Gold celebratory badge with personalized volunteer name greeting (*"Vanakkam, [Name]!"*).
- **Exact Welcome Copy**:
  > *"Welcome to the Maatram volunteer community. We’re glad to have you with us!"*
- **Portal Primer**: Educational feature cards highlighting event discovery, hour tracking & impact points, and the multi-category community network.
- **CTA**: "Get Started" stores first-launch completion in secure storage and navigates to `/home`.

---

## 3. Responsive & Multi-Viewport Verification

All screens were verified against 5 viewport profiles:
1. **Compact Mobile (320 x 640)** — Zero overflow, scrollable content cards.
2. **Android Standard (360 x 800)** — Native layout fidelity.
3. **iPhone Standard (390 x 844)** — Clean typography and touch targets.
4. **Large Flagship (430 x 932)** — Editorial whitespace balance.
5. **Tablet (800 x 1280)** — Centered reading widths with organic backdrop.

---

## 4. Verification Evidence & Quality Metrics

- **Dart Analysis (`dart analyze lib test`)**: Clean exit code 0; 0 errors, 0 warnings.
- **Flutter Test Suite (`flutter test`)**: 72/72 tests passed (100% pass rate; exit code 0).
  - Auth Experience: 4/4 passed.
  - 6-Step Registration Wizard: 2/2 passed.
  - Verification & Password Recovery: 3/3 passed.
  - Dedicated Application Status: 4/4 passed.
  - 4-Destination Shell Navigation: 3/3 passed.
  - Multi-Viewport Responsive Tests: 15/15 passed.
  - Foundation & Component Library: 41/41 passed.
- **Android Native Debug Build (`flutter build apk --debug`)**: Success (`build\app\outputs\flutter-apk\app-debug.apk`, 166.1s build time).
- **Comprehensive Test Audit**: Detailed breakdown, failure investigations, and resolutions documented in [MOBILE_M2_TEST_REPORT.md](file:///c:/Users/Logesh/Documents/Maatram_Gamification/docs/audits/MOBILE_M2_TEST_REPORT.md).

