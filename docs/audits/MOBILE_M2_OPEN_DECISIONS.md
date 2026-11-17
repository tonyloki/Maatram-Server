# Mobile M2 Open Decisions & Architectural Gaps
**Maatram Volunteering & Gamification Portal — Mobile (Volunteer App)**
**Milestone:** M2 — Authentication, Registration, Verification & Onboarding
**Date:** November 2026

---

## 1. Context & Purpose

During the M2 implementation of the Maatram Volunteer Mobile Application, all UI flows, validation rules, screen copies, and error states were strictly aligned with the authoritative requirements in `docs/App answers.pdf` and the operational guidelines in `AGENTS.md`.

This document records architectural decisions made to bridge minor specification gaps and prevent regressions to the FastAPI backend API contract.

---

## 2. Open Decisions & Recommendations

### Decision 1: Email Verification Protocol (Token vs. 6-Digit OTP)

- **Product Requirement / UI Prompt**:
  - The UI specification requested a 6-digit OTP entry screen for email verification.
- **Canonical Backend Reality (`server/src/api/v1/auth.py` & `server/src/schemas/auth.py`)**:
  - `POST /api/v1/auth/verify-email` strictly requires:
    ```json
    {
      "token": "string (min_length=1)",
      "email": "user@example.com"
    }
    ```
  - The backend generates a 32-byte cryptographic URL-safe token (`secrets.token_urlsafe(32)`), sent via Resend transactional email as an activation link or token code.
  - In contrast, the password reset endpoint (`POST /api/v1/auth/password-reset/confirm`) explicitly accepts a 6-digit numeric string:
    ```json
    {
      "otp": "123456",
      "email": "user@example.com",
      "new_password": "..."
    }
    ```
- **Mobile M2 Resolution**:
  - In accordance with Phase Discipline and the rule forbidding arbitrary backend modifications, `VerifyEmailScreen` supports token input (allowing volunteers to paste or type the verification token dispatched to their inbox).
  - Deep linking support is wired to extract both `token` and `email` from query parameters (`/verify-email?token=...&email=...`).
- **Recommendation for Future Phase (M3 / Backend)**:
  - If a 6-digit numeric OTP is preferred for email verification, introduce an alternate endpoint `POST /api/v1/auth/verify-email-otp` that stores a hashed 6-digit numeric code with a 15-minute expiration window, maintaining backward compatibility.

---

### Decision 2: Neutral Password Reset Request Response

- **Product Requirement**:
  - The UI must display the exact message:
    > *"If an account matches this email, password-reset instructions will be sent."*
- **Backend Behavior**:
  - `POST /api/v1/auth/password-reset/request` returns `200 OK` regardless of whether the email address exists in the database.
- **Resolution**:
  - `ForgotPasswordScreen` immediately presents the neutral confirmation banner, eliminating email enumeration vulnerabilities while giving the volunteer clear next steps to enter their OTP.

---

### Decision 3: Biometric Authentication Security Model

- **Product Requirement**:
  - Optional biometric unlock (fingerprint / face recognition) for returning volunteers.
- **Security Constraint**:
  - Biometric authentication must never bypass server-side token validation or allow revoked sessions to access data.
- **Resolution**:
  - Biometric preferences are stored in hardware-encrypted secure storage (`flutter_secure_storage`).
  - Successfully completing biometric prompt releases the encrypted refresh and access tokens to the in-memory Dio client.
  - On the first network request, `AuthInterceptor` verifies token validity against the backend. If the session was revoked or expired on the server, the client immediately drops the session and redirects to `/login`.

---

### Decision 4: Post-Login 4-State Routing Logic

- **Requirements Alignment**:
  - Post-login navigation inspects `session.status`:
    1. `PENDING_VERIFICATION`: Volunteer must verify email before proceeding.
    2. `PENDING_ADMIN_APPROVAL`: Email verified, application under administrative review.
    3. `REJECTED`: Application declined; respectful guidance with support contact.
    4. `APPROVED`: Full volunteer access to initiatives, tracking, and leaderboards.
- **Resolution**:
  - Dedicated screens are implemented for all 4 states in `mobile/lib/features/onboarding/presentation/`.
  - GoRouter's declarative `redirect` guard enforces these states globally, preventing direct URL or deep-link navigation into `/home` before admin approval.

---

### Decision 5: Volunteer Lifecycle Integrity & Administrative Email Verification Bypass Policy

- **Canonical Approved Lifecycle**:
  $$\text{PENDING\_VERIFICATION} \xrightarrow{\text{Email Verification}} \text{PENDING\_APPROVAL} \xrightarrow{\text{Admin Decision}} \text{APPROVED / REJECTED}$$
- **Separation of Operational Responsibilities**:
  1. **Email Verification**: A cryptographic proof-of-possession mechanism confirming that the registrant actually owns the specified mailbox.
  2. **Administrator Approval**: A governance review evaluating applicant background, eligibility, safeguarding clearances, and organizational fit.
- **Current Backend Assessment (`server/src/services/application_service.py`)**:
  - In response to an administrative UI blockage where an admin attempted to approve an applicant who had not yet verified their email, a backend shortcut was introduced:
    ```python
    if user.status == "PENDING_VERIFICATION":
        user.status = "PENDING_APPROVAL"
    enforce_status_transition(user.status, "APPROVED")
    ```
  - **Security & Integrity Impact**:
    - Treating administrative approval as an implicit proof of email ownership circumvents the email ownership verification loop.
    - If a user entered a typo or malicious email address during registration, admin approval activates the account without verifying recipient reachability, potentially sending notifications and sensitive volunteer communications to an unconfirmed address.
- **Proposed Safe Policy & Engineering Correction**:
  1. **Option A (Strict Lifecycle Adherence — Recommended)**:
     - Disallow administrative approval when `user.status == "PENDING_VERIFICATION"`.
     - In the admin portal modal, disable the "Confirm Approval" button or display a validation block:
       > *"Applicant email has not been verified yet. The applicant must complete email verification before administrative approval can be granted."*
     - Provide an administrative action to **"Resend Verification Email"** on behalf of the applicant if their token expired.
  2. **Option B (Explicit Super-Admin Bypass with Audit Trail)**:
     - If Maatram leadership explicitly requires administrators to override email verification (e.g., during on-ground in-person registration camps), it must require:
       - Explicit `bypass_email_verification: true` flag in the approve request.
       - Restricted to `SUPER_ADMIN` role only.
       - A mandatory reason logged in the immutable audit log (`admin_audit_logs`).
  - **Immediate Status**: No production data or live database records have been altered. The policy choice remains documented here pending explicit leadership directive.

