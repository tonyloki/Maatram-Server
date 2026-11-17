# Mobile M2 Test & Verification Report
**Maatram Volunteering & Gamification Portal — Mobile (Volunteer App)**
**Milestone:** M2 — Authentication, Registration, Verification & Onboarding Acceptance Audit
**Date:** November 15, 2026

---

## 1. Executive Summary

Milestone M2 of the **Maatram Volunteer Mobile Application (`maatram_mobile`)** has undergone comprehensive stabilization, static analysis, unit/widget testing, multi-viewport responsive testing, and native Android debug build verification.

All tests pass cleanly without errors, all static analysis diagnostics affecting correctness have been resolved without suppressing checks, and the Android debug APK builds successfully.

| Verification Dimension | Target Criteria | Actual Result | Status |
| :--- | :--- | :--- | :--- |
| **Dart / Flutter Static Analysis** | 0 errors, 0 warnings (`dart analyze lib test`) | **0 errors, 0 warnings** (Exit code 0) | **PASS** |
| **Complete Flutter Test Suite** | 100% passing tests (`flutter test`) | **72 passed, 0 failed, 0 skipped** (Exit code 0) | **PASS** |
| **Authentication Flow Tests** | Exact copy, validation, error banner | **4 passed, 0 failed** | **PASS** |
| **Registration Flow Tests** | 6 steps forward/back, state preservation | **2 passed, 0 failed** | **PASS** |
| **Verification & Recovery Tests** | Token verification, neutral OTP reset | **3 passed, 0 failed** | **PASS** |
| **Application Status Tests** | 4 wait states, exact copy from `App answers.pdf` | **4 passed, 0 failed** | **PASS** |
| **Shell Navigation Tests** | Unauthenticated redirect, 4 tabs | **3 passed, 0 failed** | **PASS** |
| **Responsive Multi-Viewport Tests** | 320dp, 360dp, 390dp, 430dp, 800dp | **15 passed, 0 failed** | **PASS** |
| **Android Native Debug Build** | `flutter build apk --debug` | **Built `app-debug.apk`** (166.1s, Exit code 0) | **PASS** |

---

## 2. Test Execution Details by Group

### 2.1. Authentication Experience Tests
- **Test File**: `mobile/test/auth/auth_flow_test.dart`
- **Results**: 4 passed, 0 failed (Exit code 0)
- **Key Assertions Verified**:
  - Hero header with volunteering photography fallback and brand logo.
  - Exact headline: `"Together, We Make a Difference."`
  - Exact supporting text: `"Welcome to the Maatram volunteer community. Sign in and continue your journey of creating meaningful change."`
  - Exact validation copy: Empty email (`"Enter your email address."`), invalid email (`"Enter a valid email address."`), empty password (`"Enter your password."`).
  - Password visibility toggle (`obscureText` boolean inversion).
  - Failed login error banner with exact copy: `"The email address or password is incorrect."`

### 2.2. Six-Step Registration Wizard Tests
- **Test File**: `mobile/test/registration/registration_flow_test.dart`
- **Results**: 2 passed, 0 failed (Exit code 0)
- **Key Assertions Verified**:
  - Wizard steps forward cleanly through Step 1 (Basic Details), Step 2 (Category Selection), Step 3 (Category Specifics), Step 4 (Skills & Availability), Step 5 (Privacy & Consent), Step 6 (Review & Submit).
  - Mandatory field validation prevents advancing when required data is missing.
  - Back navigation (`notifier.previousStep()`) preserves all entered form data across all categories and custom fields without state loss.
  - Final payload serialization strictly maps to backend `RegisterRequest`.

### 2.3. Verification & Password Recovery Tests
- **Test File**: `mobile/test/auth/verification_and_recovery_test.dart`
- **Results**: 3 passed, 0 failed (Exit code 0)
- **Key Assertions Verified**:
  - `VerifyEmailScreen` masks email address (e.g. `v***r@maatram.org`) for volunteer privacy.
  - Delivery uncertainty notice copy verified: *"We couldn’t confirm email delivery yet. Please check your inbox and spam folder, then try again later."*
  - `ForgotPasswordScreen` displays neutral response on submission: *"If an account matches this email, password-reset instructions will be sent."*
  - `ResetPasswordScreen` validates 6-digit numeric OTP requirement and password confirmation matching.

### 2.4. Dedicated Application Status Tests
- **Test File**: `mobile/test/onboarding/application_status_test.dart`
- **Results**: 4 passed, 0 failed (Exit code 0)
- **Key Assertions Verified**:
  - `PendingVerificationScreen`: Exact copy from `App answers.pdf`: *"Your email address hasn’t been verified yet. Please complete email verification to continue with your Maatram volunteer application. Check your inbox for the verification code, or request a new code if available."*
  - `PendingApprovalScreen`: Exact copy from `App answers.pdf`: *"Your email is verified and your volunteer application has been submitted successfully. The Maatram team is reviewing your application. You’ll be able to access volunteer activities once your application is approved. Thank you for your patience and your interest in making a difference."*
  - `WelcomeScreen`: Exact approved welcome copy: *"Welcome to the Maatram volunteer community. We’re glad to have you with us!"* and onboarding feature primer cards.
  - `RejectedScreen`: Respectful decline copy: *"Thank you for your interest in volunteering with Maatram. We’re unable to approve your application at this time."* with foundation support email link.

### 2.5. Shell Navigation & Route Guard Tests
- **Test File**: `mobile/test/router/navigation_test.dart`
- **Results**: 3 passed, 0 failed (Exit code 0)
- **Key Assertions Verified**:
  - Unauthenticated access automatically redirects to `/login`.
  - Authenticated session with `status == APPROVED` loads the 4-destination navigation shell (`/home`, `/events`, `/leaderboard`, `/more`).
  - Bottom navigation bar taps correctly switch branches without shell re-instantiation.

### 2.6. Multi-Viewport Responsive Tests
- **Test File**: `mobile/test/responsive/m2_viewports_test.dart`
- **Results**: 15 passed, 0 failed (Exit code 0)
- **Viewports Tested**:
  - `Compact 320dp` (320 x 640)
  - `Android 360dp` (360 x 800)
  - `Standard 390dp` (390 x 844)
  - `Large 430dp` (430 x 932)
  - `Tablet 800dp` (800 x 1280)
- **Screens Verified Across All Viewports**:
  - `LoginScreen`: 5/5 viewports passed
  - `RegistrationFlowScreen`: 5/5 viewports passed
  - `WelcomeScreen`: 5/5 viewports passed

---

## 3. Investigated Failures & Root Cause Resolution

During the audit, the initial test and analyzer run encountered several issues. All were systematically diagnosed and resolved at the architectural root cause:

| Issue | Offending File(s) | Root Cause | Engineering Solution |
| :--- | :--- | :--- | :--- |
| **Analyzer: Undefined getter `user`** | `app_router.dart`, `login_screen.dart`, status screens | `AuthState` had `session` property but was missing ergonomic `user => session` alias expected by consuming widgets. | Added `UserSession? get user => session;` to `AuthState`. |
| **Analyzer: Undefined `registrationNotifierProvider`** | `step2_category_selection.dart` | Step 2 consumed `registrationNotifierProvider` while `registration_state.dart` defined `registrationProvider`. | Standardized provider usage and exported `registrationNotifierProvider` alias in `registration_state.dart`. |
| **Analyzer: Argument type `BorderRadius` not assignable to `double`** | `category_card.dart`, `consent_checkbox_row.dart` | `MaatramRadii.cardRadius` is already a `BorderRadius`; passing it to `BorderRadius.circular()` caused a type conflict. | Replaced `BorderRadius.circular(MaatramRadii.cardRadius)` with `MaatramRadii.cardRadius`. |
| **Viewport RenderFlex 79px overflow** | `login_screen.dart` | The bottom registration link row (`Row(children: [Text, GestureDetector])`) overflowed on narrow 320dp/360dp screens under fixed font metrics. | Replaced rigid `Row` with `Wrap(alignment: WrapAlignment.center, ...)` to wrap gracefully across lines. |
| **Viewport RenderFlex 169px overflow** | `step1_basic_details.dart`, `step3_category_details.dart` | `DropdownButtonFormField` for gender and college study year defaulted to `isExpanded: false`, causing inner row to expand past available space on narrow viewports. | Added `isExpanded: true` and `TextOverflow.ellipsis` to dropdowns. |
| **Viewport RenderFlex 187px overflow** | `welcome_screen.dart` | `WelcomeScreen` used an unconstrained `Column` inside `SafeArea` without a scroll container, overflowing on short 640px height viewports. | Wrapped layout in `Center(child: SingleChildScrollView(physics: BouncingScrollPhysics(), ...))` to enable smooth scrolling on compact devices. |

---

## 4. Android Build Verification

- **Command**: `flutter build apk --debug`
- **Execution Time**: 166.1 seconds
- **Exit Code**: `0`
- **Output Artifact**: `build\app\outputs\flutter-apk\app-debug.apk`
- **Validation**: Gradle compilation, resource merging, Java 21 compilation, and DEX packaging succeeded with zero fatal errors.

---

## 5. Verification Conclusion

Milestone M2 has met all definition-of-done criteria:
- **Analysis**: Clean (0 errors, 0 warnings).
- **Tests**: 100% passing (72/72 tests).
- **Responsiveness**: Zero layout overflows across 320dp through 800dp viewports.
- **Build**: Android debug APK built successfully.
- **Copy Fidelity**: Exact match to `docs/App answers.pdf`.
