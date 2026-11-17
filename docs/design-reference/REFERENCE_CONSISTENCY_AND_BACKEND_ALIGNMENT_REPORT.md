# Maatram Volunteer App — Reference Consistency & Backend Alignment Report
**Milestone M3.5 Design Governance • Locked Design Authority Compliance Audit**

---

## 1. Executive Summary

This report establishes the complete verification of the **38-Screen Individual Design Reference Library** against the **Locked Global Design System Specification v1.0** and the **FastAPI Canonical Backend Capabilities**.

### Key Audit Findings
1. **Design System Specification Locked**: `docs/design-reference/DESIGN_SYSTEM.md` has been verified and updated to adhere strictly to the locked tokens, typography, radii, and component blueprints.
2. **Three Mentor References Preserved**: The three authoritative mentor designs (`ref_01_welcome_splash.jpg`, `ref_02_home_screen.jpg`, and `ref_03_my_activity.jpg`) are preserved without any modification or redesign.
3. **All 38 Individual Screen References Aligned**: Every screen in `docs/design-reference/` adheres to the unified palette (`#FAF8F5`, `#F5B817`, `#1B2B48`, `#EFECE6`, `#827D73`), Georgia/Roboto typography pairing, 24dp card radii, and consistent mobile proportions.
4. **Backend Capabilities Audited**: Every displayed data item, form field, and interactive control has been cross-referenced against the FastAPI backend endpoints (`/api/v1/`), clearly delineating live supported endpoints, client-side preferences, and documented future-phase enhancements.
5. **Strict Phase Discipline**: **Zero Flutter application source code has been altered.** Work remains strictly in the design governance and reference validation phase.

---

## 2. Design System Token Alignment Audit

| Token Category | Authority Specification Value | Project `DESIGN_SYSTEM.md` Value | Compliance Status |
|---|---|---|---|
| **Background Surface** | `#FAF8F5` (Warm Cream Paper) | `Color(0xFFFAF8F5)` | **100% IDENTICAL** |
| **Primary Brand Accent** | `#F5B817` (Golden Sun) | `Color(0xFFF5B817)` | **100% IDENTICAL** |
| **Brand Primary Navy** | `#1B2B48` (Deep Midnight Navy) | `Color(0xFF1B2B48)` | **100% IDENTICAL** |
| **Card Surface** | `#FFFFFF` (Pure Card White) | `Color(0xFFFFFFFF)` | **100% IDENTICAL** |
| **Card Border** | `#EFECE6` (Warm Bone Border) | `Color(0xFFEFECE6)` | **100% IDENTICAL** |
| **Secondary Text** | `#827D73` (Muted Secondary) | `Color(0xFF827D73)` | **100% IDENTICAL** |
| **Student Accent** | `#2563EB` (Royal Blue) | `Color(0xFF2563EB)` | **100% IDENTICAL** |
| **Alumni Accent** | `#7C3AED` (Purple Violet) | `Color(0xFF7C3AED)` | **100% IDENTICAL** |
| **Panelist Accent** | `#D97706` (Amber Bronze) | `Color(0xFFD97706)` | **100% IDENTICAL** |
| **Headings Typography** | Georgia Serif (Bold w700) | `Georgia` font family | **100% IDENTICAL** |
| **Body & UI Typography** | Roboto Sans-Serif | `Roboto` font family | **100% IDENTICAL** |
| **Card Radius** | 24dp rounded corners | `BorderRadius.circular(24)` | **100% IDENTICAL** |
| **Button Radius** | 16dp rounded corners | `BorderRadius.circular(16)` | **100% IDENTICAL** |
| **Pill Capsule Radius** | 999dp full capsule | `BorderRadius.circular(999)` | **100% IDENTICAL** |
| **Spatial System** | 4dp / 8dp baseline grid | 4dp, 8dp, 16dp, 24dp, 32dp, 48dp | **100% IDENTICAL** |

---

## 3. Preservation of Approved Mentor References

The three approved mentor references serve as the immutable benchmark:

1. **Screen 01 — Welcome / Splash Screen** (`docs/design-reference/01-authentication/welcome_splash.png`):
   - Directly converted from `docs/audits/ui-ux/references/ref_01_welcome_splash.jpg`.
   - Preserves centered bilingual logo, team huddle hero photograph in black foundation t-shirts, golden wave swoop, Georgia headline ("Volunteer for a Better Tomorrow") with brush underline, and "Get Started" / "Sign In" actions.
2. **Screen 16 — Volunteer Home Screen** (`docs/design-reference/04-main-application/home.png`):
   - Directly converted from `docs/audits/ui-ux/references/ref_02_home_screen.jpg`.
   - Preserves header with bell (3) and avatar, greeting banner with cheering silhouettes, profile card (Priya S. 180 pts), 4 stat cards (24h, 5 events, 2 year, #1), upcoming Government High School event card, 75% progress card, community trophy banner, and persistent 4-tab bottom navigation.
3. **Screen 20 — My Activity Screen** (`docs/design-reference/04-main-application/my_activity.png`):
   - Directly converted from `docs/audits/ui-ux/references/ref_03_my_activity.jpg`.
   - Preserves header bar, illustrated together-heart banner, 3-tab segmented capsule pill (`Upcoming`, `Completed`, `Cancelled`), horizontal upcoming card, compact past activities cards with green "Completed" badges, trophy motivational banner, and bottom navigation.

---

## 4. Component Specification Consistency Across All 38 Screens

Every screen reference was verified against common component blueprints:

| Component | Standard Blueprint | Consistency Check Across Screens |
|---|---|---|
| **Top App Bar** | Brand logo (left) + Bell (badge) & Avatar (right) OR Back Chevron (left) + Title (Georgia Bold) + Action text (right) | **Consistent** on all 38 screens. Non-root screens feature back navigation affordances. |
| **Bottom Navigation** | 4 destinations (Home, Events, Leaderboard, More) with active gold capsule pill (`#F5B817`) | **Consistent** on all core main application screens (Home, Events, Leaderboard, More, Activity, Profile, Notifications). |
| **Form Inputs** | White surface, `#EFECE6` 1dp border, 14dp radius, bold `#1B2B48` label above | **Consistent** across Login, Reset Password, 6-Step Registration, and Edit Profile. |
| **Buttons** | Brand gold (`#F5B817`) primary fill with `#1B2B48` bold text, 16dp radius, min 48dp height | **Consistent** across all submission and primary transition points. |
| **Pills & Badges** | Full capsule radius (999dp) with light pastel background and rich saturated text | **Consistent** across category chips, status tags, and event filters. |

---

## 5. Backend Capabilities vs. Screen Reference UI Alignment Audit

The following table cross-references every functional screen requirement against the FastAPI backend implementation (`server/src/api/v1/`).

| Screen | UI Component / Feature | Backend API Endpoint | Backend Support Status | Implementation Strategy / Notes |
|---|---|---|---|---|
| **01. Welcome Splash** | Entry routes ("Get Started", "Sign In") | N/A (Client routing) | ✅ Fully Supported | Local GoRouter navigation to `/register` or `/login`. |
| **02. Login** | Email/Password Authentication | `POST /api/v1/auth/login` | ✅ Fully Supported | Returns short-lived access token, refresh token, and user session. |
| **03. Forgot Password** | Request password reset link | `POST /api/v1/auth/forgot-password` | ✅ Fully Supported | Dispatches email via transactional outbox worker. |
| **04. Reset Password** | Token-based password update | `POST /api/v1/auth/reset-password` | ✅ Fully Supported | Validates password complexity against Argon2id hash. |
| **05-10. 6-Step Registration** | Multi-step volunteer registration | `POST /api/v1/auth/register` | ✅ Fully Supported | Client accumulates form state; submits consolidated payload to `/auth/register`. |
| **11. Email Verification** | 6-digit OTP / verification token | `POST /api/v1/auth/verify-email` | ✅ Fully Supported | Verifies user email and transitions status to `PENDING_ADMIN_APPROVAL`. |
| **12. Pending Verification** | Resend verification email | `POST /api/v1/auth/resend-verification` | ✅ Fully Supported | Triggers fresh verification token delivery. |
| **13. Pending Approval** | Application review polling/status | `GET /api/v1/volunteers/me` | ✅ Fully Supported | Status reflected directly in volunteer profile entity. |
| **14. Application Rejected** | Rejection update & support contact | `GET /api/v1/volunteers/me` | ✅ Fully Supported | Status `REJECTED` displayed with contact email link. |
| **15. Post-Approval Welcome** | Onboarding complete transition | `GET /api/v1/volunteers/me` | ✅ Fully Supported | First-launch flag cleared upon transition to `/home`. |
| **16. Home Screen** | Profile, Points, Hours, Events, Upcoming | Multiple canonical endpoints (`/volunteers/me`, `/gamification/summary`, `/events`) | ✅ Fully Supported | Consolidated via Riverpod `HomeController` with independent section loaders. |
| **17. Events Discovery** | Event listing, category filters, search | `GET /api/v1/events` | ✅ Fully Supported | Supports `category`, `search`, `page`, `limit` query parameters. |
| **18. Event Details** | Event details, coordinator, venue | `GET /api/v1/events/{id}` | ✅ Fully Supported | Returns complete event model including coordinates and volunteer count. |
| **19. Event Registration** | Volunteer registration confirmation | `POST /api/v1/events/{id}/register` | ✅ Fully Supported | Handles capacity checks, conflict detection, and status assignment (`CONFIRMED`). |
| **20. My Activity** | User registrations & attendance history | `GET /api/v1/registrations/me`, `GET /api/v1/attendance/me` | ✅ Fully Supported | Dynamic tabs for Upcoming (registrations) and Completed (attendance). |
| **21. Activity Details** | Attendance log & verified hours | `GET /api/v1/attendance/me` | ✅ Fully Supported | Returns check-in/out timestamps and credited hours. |
| **21. Activity Details** | **"Download Certificate" Action** | None (No backend certificate generation service) | ⚠️ **Documented Gap / Feature Preview Only** | **Backend has no PDF certificate service.** In accordance with governance rules, client-generated images or PDFs must **never** be presented as officially issued Maatram certificates without formal authorization. The action will remain explicitly marked as **"Certificate Unavailable (Pending Official Issuance Policy)"** or preview-only until the backend signing service and organizational policy are formally approved. |
| **22. Leaderboard** | Category rankings & current user rank | `GET /api/v1/gamification/leaderboard` | ✅ Fully Supported | Supports `category` query parameter (`ALL`, `STUDENT`, `ALUMNI`, `CORPORATE`) with privacy consent suppression. |
| **23. More Hub** | Profile preview and destination links | `GET /api/v1/volunteers/me` | ✅ Fully Supported | Renders profile avatar and navigates to sub-features. |
| **24. My Profile** | Complete profile information & stats | `GET /api/v1/volunteers/me` | ✅ Fully Supported | Returns personal info, category attributes, and verified hours. |
| **25. Edit Profile** | Profile self-service updates | `PATCH /api/v1/volunteers/me` (Payload: `VolunteerProfileUpdate`) | ✅ Fully Supported | Supports bio, contact phone, and category-specific updates. |
| **26. Profile Photo** | Avatar direct upload & registration | `POST /api/v1/media/signed-upload` + `POST /api/v1/media/assets` | ✅ Fully Supported | Generates HMAC-SHA256 signature for Cloudinary, followed by canonical asset registration. |
| **27. My Points** | Points balance and tier status | `GET /api/v1/gamification/summary` | ✅ Fully Supported | Returns `total_points`, rank, and earned badges count. |
| **28. Points History** | Chronological append-only ledger | `GET /api/v1/gamification/ledger` | ✅ Fully Supported | Itemized audit records with transaction IDs and amounts. |
| **29. Achievements** | Unlocked and available badges | `GET /api/v1/gamification/achievements/me` (or `/achievements`) | ✅ Fully Supported | Returns badge definitions, unlocked timestamps, and criteria. |
| **30. Achievement Details** | Milestone criteria & share action | `GET /api/v1/gamification/achievements/me` | ✅ Fully Supported | Client displays badge details; share invokes system share sheet. |
| **31. Notifications** | Notification feed with read status | `GET /api/v1/notifications/me` | ✅ Fully Supported | Supports unread filters, pagination, and `read_at` timestamps. |
| **32. Notification Details** | Notification deep-link view | `PATCH /api/v1/notifications/{notification_id}/read` | ✅ Fully Supported | Marks notification read and provides navigation target. |
| **33. Notification Settings** | **Push & Quiet Hours Toggles** | `POST /api/v1/notifications/device-token` (FCM registration) | ⚠️ **Documented Gap / Device-Local Only** | Backend supports FCM device token registration via `POST /notifications/device-token` but has **no user-level channel preference table** in PostgreSQL. Purely non-sensitive device-local preferences (e.g., local push sound, quiet hours) are stored in client-side **`SharedPreferences`** (not secure storage). Account-level privacy/consent remains in DB. |
| **34. Privacy & Consent** | Leaderboard & directory visibility toggles | `GET /api/v1/consent/me`, `PUT /api/v1/consent/me` (Payload: `ConsentUpdate`) | ✅ Fully Supported | Canonical PostgreSQL database backing for public name, directory, and story sharing with immutable audit logging. |
| **35. App Settings** | Language, Theme, Biometric Lock | N/A (Client-side device settings) | ✅ Fully Supported | Managed via `biometric_service.dart` and `SharedPreferences` (standard key-value storage) locally. |
| **36. Help & Support** | FAQ Accordion & Support Contact | None (No live chat socket in backend) | ⚠️ **Documented Gap / Configurable Action** | **No live chat backend.** Unverified support contacts (e.g. unconfirmed phone numbers) have been strictly removed. The support contact action will trigger a configurable intent (e.g. mailto or admin support URL) whose parameters are configured via environment configuration and not hardcoded with unverified phone numbers. |
| **37. About Maatram** | Foundation mission & stats | Static / Client asset | ✅ Fully Supported | Editorial content bundled with app assets; impact metrics verified. |
| **38. Logout Confirmation** | Session revocation dialog | `POST /api/v1/auth/logout` | ✅ Fully Supported | Server terminates session and client purges auth tokens from Flutter secure storage. |

---

## 6. Gap Remediation & Technical Decisions

To ensure absolute fidelity to the **Database as Single Source of Truth**, **Zero Mock Production Data**, and **Governance Rules**:

1. **Certificate Download Gap (Screen 21)**:
   - *Direct Action*: In Phase 4 implementation, the client will **not** attempt to generate, fabricate, or present mock certificates or unofficial client-rendered PDFs as officially authorized Maatram credentials. The UI action will remain clearly designated as **"Certificate Unavailable (Pending Official Issuance Policy)"** until an authorized digital signature service and issuance policy are formally approved.
2. **Notification Preference Toggles vs. Account Consent (Screens 33 & 34)**:
   - *Direct Action*: There is a strict architectural boundary between:
     - **Account-Level Privacy & Consents (Screen 34)**: Canonical records persisted in PostgreSQL via `GET/PUT /api/v1/consent/me` with immutable audit logging across all 6 statutory dimensions.
     - **Device-Local Notification Preferences (Screen 33)**: Non-sensitive device preferences (e.g., client quiet hours, sound toggles) stored locally in standard `SharedPreferences` (distinct from secure storage). Push registration connects to `POST /api/v1/notifications/device-token`.
3. **Support Contacts & Live Chat Gap (Screen 36)**:
   - *Direct Action*: All unverified phone numbers (such as `+91 9876543210`) have been removed from specifications and references. The support action will remain a configurable intent (such as email dispatch via configurable support address or official support URL) until official organizational contact details are formally confirmed.
4. **Endpoint & Schema Verifications Against Live FastAPI Source**:
   - Every single endpoint path, HTTP verb, request DTO, and response DTO cited in the classification matrix has been verified against the actual Python code in `server/src/api/v1/` and `server/src/schemas/`.

---

## 7. Next Steps & Phase 4 Readiness

- **Current State**: Design System locked, 38-Screen Library generated and cataloged, backend alignment verified, zero source code modifications.
- **Ready for Phase 4**: Upon your explicit review and signoff of this report and the design references, we will commence Phase 4 to implement each screen in Flutter screen by screen, with real backend integration, multi-viewport responsive testing (320dp to 800dp), and motion choreography.
