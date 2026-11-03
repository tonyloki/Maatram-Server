# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## Web Application — Implementation Phasing & Milestones Roadmap

**Document Version:** 2.1.0 (Final Pre-Implementation Roadmap)  
**Status:** Canonical Implementation Plan (Awaiting User Sign-Off)  
**Target Monorepo Location:** `web/`  
**Prerequisite:** Full pass on all 144 backend tests in `server/` with zero regressions.

---

## Overview

The web implementation is organized into **five sequential milestones**. Each milestone has defined deliverables, test requirements, and acceptance criteria. Under no circumstances will mock data, simulated API delays, or placeholder responses be introduced into production builds.

---

## Milestone 1: Frontend Foundation, Core Client & Design Tokens

### Scope & Tasks
1. Initialize Next.js 15+ in `web/` using TypeScript, Tailwind CSS, and App Router.
2. Configure Tailwind CSS with the canonical design tokens (`#F5B817`, `#FAF8F3`, `#16171A`, `#DEF7EC`, `#FEF08A`, `#FDE8E8`).
3. Set up atomic typography and UI primitives: `Button`, `Card`, `Badge`, `Input`, `Switch`, `Modal`, `LoadingSkeleton`.
4. Implement the core API client (`src/lib/api-client.ts`):
   - Axios / Fetch wrapper targeting `NEXT_PUBLIC_API_URL` (defaulting to `http://localhost:8000/api/v1`).
   - Request interceptor attaching in-memory `Authorization: Bearer <access_token>` when available.
   - Response interceptor catching `401 Unauthorized` and executing silent refresh via `POST /api/v1/auth/refresh` with cookies.
   - Double-submit CSRF header (`X-CSRF-Token`) attachment on mutative operations when using cookie authentication.
5. Create TypeScript DTO interfaces mirrored strictly from `server/src/schemas/`.
6. Copy verified logo assets (`maatram_logo-removebg-preview.png`, `Maatramlogowithbg.jpeg`) into `web/public/`.

### Definition of Done (DoD)
- Next.js build runs cleanly (`npm run build` exits 0).
- TypeScript compiles with zero errors (`tsc --noEmit`).
- Storybook / component preview verifies UI primitives match design specifications.

---

## Milestone 2: Public Website, Authentication & Registration Flow

### Scope & Tasks
1. **Public Landing Page (Screen 1)**:
   - Header with official transparent logo, navigation links (`Home`, `About`, `Volunteer`, `Impact`), and `Login`/`Get Started` CTAs.
   - Hero section with inspiring headline *"Volunteer for a Better Tomorrow"* and warm wave graphic framing volunteer photography.
   - Three Opportunity Pillar cards: *School Visits*, *Mock Interviews*, *BGV Support*.
   - **Authentic Non-Numeric Impact Storytelling**: Communicates mission narratives without fabricated statistics or unverified numbers (prohibiting "1,200+ Volunteers" or "4,800+ Hours").
2. **Authentication System**:
   - `/login` with email, password, and client_type (`WEB`). Handles HttpOnly session cookies.
   - `/forgot-password` and `/reset-password` supporting 6-digit OTP confirmation.
   - `/verify-email` for post-registration activation tokens.
3. **Multi-Step Volunteer Registration (Screen P2)**:
   - 6-step wizard using `react-hook-form` + `zod` validation strictly matching `RegisterRequest`:
     - Step 1: Category Selection (`STUDENT`, `ALUMNI`, `CORPORATE`).
     - Step 2: Personal Details (Name, Mobile in E.164 format, Age, Gender).
       - **Strict Minor Safeguarding**: When `age < 18`, fields for `parent_guardian_name`, `relationship`, `contact`, and documentary consent upload are mandatory. The submitted claim sets `parental_consent_claimed = true` with `parental_consent_status = "PENDING"`. It is NOT marked verified.
     - Step 3: Polymorphic Category Details (College/Department/RegNo for Students; Org/Role/Exp/Skills for Alumni/Corporate).
     - Step 4: Volunteering Preferences & Skills.
     - Step 5: Affirmative Consent Settings across all 6 dimensions (all defaulting to `false`).
     - Step 6: Immutable Review & Submit calling `POST /api/v1/auth/register`.
4. **Onboarding Status Views**:
   - `/onboarding/pending` waiting room with status queried from `GET /api/v1/applications/me`.
   - `/onboarding/rejected` notice displaying administrative feedback.

### Definition of Done (DoD)
- End-to-end registration creates a real record in `users`, `volunteer_profiles`, and `volunteer_applications` in PostgreSQL.
- Minor safeguarding correctly marks applications `parental_consent_status = "PENDING"` and prevents unverified account activation.
- Rate limiting errors (HTTP 429) from backend are gracefully communicated to the user.

---

## Milestone 3: Volunteer Portal (Screens 2, 3, 4, 5, 6)

### Scope & Tasks
1. **Volunteer Layout & Sidebar**:
   - Light ivory layout with left navigation rail (`Home`, `Discover Events`, `My Activity`, `Leaderboard`, `Profile`).
   - Top header with notifications bell and user identity chip (`GET /api/v1/users/me`).
2. **Discover Events (Screen 2)**:
   - Keyword search across event title, description, and location.
   - Category filter pills (`All`, `School Visit`, `Mock Interview`, `BGV Support`) and mode dropdown (`ONLINE`, `OFFLINE`).
   - Paginated grid of event cards with live capacity indicators.
3. **Event Details & Registration (Screen 4)**:
   - Two-column view: Left (Banner photo, sub-tabs: *About*, *Requirements*, *Location*, *Organizer*); Right (Sticky info card with date, time, venue, deadline).
   - Action CTA: `Register for this Event` calling `POST /api/v1/events/{id}/register`.
   - Registration withdrawal modal calling `POST /api/v1/events/{id}/withdraw` with mandatory reason.
4. **My Activity (Screen 3)**:
   - Sub-tabs: `Upcoming`, `Ongoing`, `Past` binding to `GET /api/v1/registrations/me`.
   - Badges: `SELECTED`, `WAITLISTED`, `ATTENDED`, `DECLINED`.
5. **Leaderboard & Recognition (Screen 5)**:
   - Category segmented control (`Overall`, `Students`, `Alumni`, `Corporate`) and year selector calling `GET /api/v1/gamification/leaderboard`.
   - **Top 3 Visual Podium** (Gold Crown #1, Silver Laurel #2, Bronze Laurel #3).
   - Ranked roster table with anonymous masking for users with `name_visible: false`.
   - Pinned sticky bottom row displaying current volunteer's personal ranking.
6. **Profile & Affirmative Consent Management (Screen 6)**:
   - Left card: Volunteer identity, category badge, verified hours, and points (`GET /api/v1/volunteers/me`).
   - Right tabbed panel:
     - `My Information`: Editable profile fields (`PATCH /api/v1/volunteers/me`).
     - `Consents`: 6 explicit affirmative switches with live sync to `PUT /api/v1/consent/me` and change audit history (`GET /api/v1/consent/me/history`).
     - `Achievements`: The 4 canonical achievement badges (`FIRST_STEP`, `DEDICATED_VOLUNTEER`, `PILLAR_OF_MAATRAM`, `CENTURION`) queried from `GET /api/v1/gamification/achievements/me`.
7. **In-App Notifications**:
   - Notifications center with unread count badge, mark-as-read, and mark-all-read.

### Definition of Done (DoD)
- All volunteer screens pull live records from PostgreSQL.
- Consent toggles persist immediately with differential audit records created in `consent_history`.
- Leaderboard honors affirmative privacy preferences without leaking names.

---

## Milestone 4: Admin Command Portal (Screens 7, 8, 9)

### Scope & Tasks
1. **Admin Layout & Dark Sidebar**:
   - Dark charcoal rail (`#16171A`) with navigation items and admin profile chip.
   - RBAC gate: Middleware and route guards strictly restrict access to `ADMIN` and `SUPER_ADMIN`.
2. **Admin Dashboard (Screen 7)**:
   - 4 Top KPI Cards (`Total Volunteers`, `Pending Approvals`, `Total Events`, `Verified Hours`) queried from `GET /api/v1/admin/dashboard`.
   - Volunteer Participation Donut Chart (Students, Alumni, Corporate breakdown).
   - "Action Required" task list linking to pending review items.
   - Recent Activity feed displaying real-time audit logs.
3. **Onboarding Applications Review & Minor Safeguarding Verification**:
   - Tabular queue of pending volunteer applications with category and search filters.
   - Detailed review modal with explicit parental consent verification workflow for minor applicants:
     - Inspection of uploaded consent documentation.
     - Action calling `POST /api/v1/applications/{id}/verify-parental-consent` (`status="VERIFIED"` or `"REJECTED"`, with required notes).
     - Account approval (`POST /api/v1/applications/{id}/approve`) enabled only after consent verification succeeds.
   - Rejection action with mandatory justification (`POST /api/v1/applications/{id}/reject`).
4. **Volunteer Directory & Profile Inspection**:
   - Multi-field search across name, college, and employer (`GET /api/v1/volunteers`).
   - Detailed volunteer history view.
5. **Event Management & Participant Roster (Screen 8)**:
   - Event creation wizard with category, dates, capacity, venue, and mode.
   - Status actions: `Publish Event`, `Close Registrations`, `Cancel Event`, `Duplicate Event`.
   - Participant Roster tabs: `Subscribed`, `Selected`, `Attendance`, `Completion`.
   - Actions: Single volunteer selection, batch selection (`POST /api/v1/events/{id}/select`), promote from waitlist (`POST /api/v1/events/{id}/waitlist/{reg_id}/promote`), decline volunteer.
6. **Attendance Tracking & Hours Verification**:
   - Administrative check-in and check-out actions calling `POST /api/v1/events/{id}/attendance/check-in` and `/check-out`.
   - Attendance correction dialog with mandatory reason (`POST /api/v1/attendance/{id}/correct`).
7. **Event Completion & Gamification Awarding**:
   - Dry-run preview (`GET /api/v1/events/{id}/completion-preview`) showing points, hours, and draft LinkedIn copy.
   - Atomic completion action (`POST /api/v1/events/{id}/complete-and-award`) creating point transactions and outbox jobs.
8. **Reports & Analytics (Screen 9)**:
   - Sub-tabs: `Student Contributions`, `Alumni Contributions`, `Alumni Consistency`, `Employer Reports`, `Interview Availability`, `Inactive Volunteers`.
   - Monthly Verified Hours Bar Chart and Category Donut Chart.
   - Streaming Excel export button calling `GET /api/v1/admin/reports/{report_type}/export`.
9. **Outbox DLQ & Audit Logs**:
   - Outbox Dead-Letter Queue inspection and manual requeue/retry.
   - Security audit logs viewer (Super Admin only).

### Definition of Done (DoD)
- Admin actions update PostgreSQL records and produce immutable audit logs.
- Attendance check-in/out and correction compute correct durations.
- Streaming Excel export downloads valid `.xlsx` files without corruption.

---

## Milestone 5: Verification, Accessibility & Performance Sign-Off

### Scope & Tasks
1. **End-to-End User Journeys**:
   - Journey A: Guest registers as Student -> Admin reviews and approves -> Volunteer logs in -> Discovers event -> Registers -> Admin selects volunteer -> Admin checks in and checks out -> Event completed -> Points awarded -> Leaderboard updated -> Volunteer views rank on podium.
   - Journey B: Minor applicant registers -> Parental consent flagged as `PENDING` -> Admin inspects documentary evidence and verifies parental consent (`VERIFIED`) -> Account approved.
   - Journey C: Volunteer updates consent switches -> Leaderboard masks name in real time.
2. **Cross-Viewport & Device Verification**:
   - Desktop (1440px): Full multi-column dashboard and tabular rosters.
   - Tablet (768px): Responsive card stacking, collapsible sidebar.
   - Mobile (375px): Full-width cards, slide-out drawer navigation, touch targets ≥ 44px.
3. **Accessibility (WCAG 2.1 AA) Audit**:
   - Lighthouse accessibility score ≥ 95.
   - Color contrast verified on all text and badges.
   - Full keyboard navigation (Tab, Enter, Space, Escape) on all modals, forms, and tables.
4. **Zero Mock Data Certification**:
   - Verify that 100% of dashboard counters, tables, charts, and rosters originate from the canonical PostgreSQL backend.

---

## Milestone Execution Governance

> [!IMPORTANT]
> Milestone 1 will not be initialized until explicit user approval is granted on this specification package.
