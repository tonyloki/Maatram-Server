# M6_PAGE_BY_PAGE_BLUEPRINT.md — Complete Page-by-Page Architectural Blueprint
**Maatram Volunteering & Gamification Portal**  
**Milestone 6.0: Detailed Page Specifications**  
**Date:** November 2026 (Updated with Alignment Corrections)  
**Status:** **ALIGNED ARCHITECTURAL BLUEPRINT**

---

## 1. Public Web Experience

### 1.1 Public Landing Page (`/`)
1. **Purpose**: Inspire prospective mentors, articulate Maatram's educational mission, present volunteering tracks, and drive registrations.
2. **Primary User**: Prospective volunteer (student, alumnus, corporate mentor) or supporter.
3. **Layout Composition**: 2-column editorial hero section, followed by a multi-section vertical flow on warm ivory canvas (`#FAF8F5`).
4. **Header/Sidebar Requirements**: `PublicHeader` (sticky, logo, links to About, Impact, Events, Login/Register CTAs). No sidebar. `PublicFooter`.
5. **Main Sections**:
   - Editorial Hero (Headline, mission hook, dual CTAs, trust badges, authentic classroom photography).
   - Signature Opportunities (Government School Visits, 1-on-1 Mock Interviews, BGV Support Drives).
   - How Volunteering Works (4-step progressive timeline).
   - Tailored Engagement Tracks (Students, Alumni, Corporates).
   - Mission Storytelling & Impact Quote.
   - Final Call-to-Action Banner & Public Trust Footer.
6. **Components**: `PublicHeader`, `Button`, `Card`, `Badge`, `PublicFooter`.
7. **Visual Hierarchy**: Display headline `#1F2421` -> Golden yellow primary CTA `#F5B817` -> Real photography -> Structured category cards.
8. **Photography / Illustration**: High-resolution authentic classroom photo (`/assets/images/hero-volunteering.jpg`), opportunity photos (`school-visit.jpg`, `mock-interview.jpg`, `bgv-support.jpg`).
9. **Interactions**: Primary CTA navigates to `/register`; secondary CTA to `/events`.
10. **Responsive Behavior**: Hero stacks vertically on `<1024px`; 3-card opportunity grid collapses to 1 column on `<640px`.
11. **Backend Data Required**: None (static public landing page with deep links).
12. **States**: Instant render, static pre-render with Next.js App Router.

---

### 1.2 About Page (`/about`)
1. **Purpose**: Document Maatram's founding story, mission, educational philosophy, and governance.
2. **Primary User**: Prospective volunteers, donors, academic partners.
3. **Layout Composition**: Single-column editorial layout with centered header and split storytelling blocks.
4. **Header/Sidebar Requirements**: `PublicHeader` + `PublicFooter`.
5. **Main Sections**: Hero statement, Founder's vision, Core values (Integrity, Empathy, Empowerment), Impact timeline, Advisory council.
6. **Components**: `PublicHeader`, `Card`, `Badge`, `PublicFooter`.
7. **Visual Hierarchy**: Inspiring mission quote -> Storytelling paragraphs -> Team cards.
8. **Photography / Illustration**: Authentic field work photography, founder portrait, leadership badges.
9. **Interactions**: CTAs to register or read impact report.
10. **Responsive Behavior**: Split storytelling blocks stack vertically on mobile.
11. **Backend Data Required**: None.
12. **States**: Static pre-render.

---

### 1.3 Impact Page (`/impact`)
1. **Purpose**: Showcase quantitative outcomes, student success stories, and verified scholarship enablement metrics.
2. **Primary User**: Prospective volunteers, corporate sponsors, public.
3. **Layout Composition**: Metric stat grid followed by student case studies and testimonials.
4. **Header/Sidebar Requirements**: `PublicHeader` + `PublicFooter`.
5. **Main Sections**: Cumulative impact numbers (Scholars supported, Volunteer hours, Colleges reached), Student success stories, Partner institutions.
6. **Components**: `Card`, `Badge`, `Button`, `PublicFooter`.
7. **Visual Hierarchy**: Large bold numbers with golden accents -> Human testimonial cards.
8. **Photography / Illustration**: Real student scholar portraits with graduation regalia.
9. **Interactions**: Interactive filter for graduation batches.
10. **Responsive Behavior**: 4-metric grid collapses to 2 columns on tablet and 1 column on mobile.
11. **Backend Data Required**: Aggregated metrics (or static milestones).
12. **States**: Instant load.

---

### 1.4 Public Events Catalog (`/events` & `/events/[id]`)
1. **Purpose**: Allow prospective volunteers to browse published drives before creating an account.
2. **Primary User**: Unauthenticated visitor exploring opportunities.
3. **Layout Composition**: Top hero banner, search bar, category pills, and card grid matching Reference 3 styling.
4. **Header/Sidebar Requirements**: `PublicHeader` + `PublicFooter`.
5. **Main Sections**: Search & filter rail, opportunity card list, login prompt banner.
6. **Components**: `SearchInput`, `CategoryPill`, `EventCard`, `Button`.
7. **Visual Hierarchy**: Search bar -> Category filters -> Event cards with dates, badges, and "Login to Apply" CTAs.
8. **Photography / Illustration**: Event category photography thumbnails.
9. **Interactions**: Clicking "Apply" redirects to `/login?redirect=/events/{id}`.
10. **Responsive Behavior**: Responsive card grid collapses to single column on mobile.
11. **Backend Data Required**: `GET /events?status=PUBLISHED`.
12. **States**: Skeleton cards while fetching, empty state if no events match filter.

---

### 1.5 Authentication & Registration (`/login`, `/register`, `/register/confirmation`)
1. **Purpose**: Secure user sign-in, comprehensive multi-step onboarding, and affirmative consent collection across all 6 dimensions.
2. **Primary User**: Returning volunteer/admin, or applicant.
3. **Layout Composition**: Centered, floating white card (`rounded-3xl`, shadow-md) on warm ivory canvas.
4. **Header/Sidebar Requirements**: `PublicHeader` with minimal distraction.
5. **Main Sections**:
   - Login: Email input, password input, remember me toggle, submit button, register link.
   - Register: Step indicator (1: Personal, 2: Track & Skills, 3: Privacy & Consents), form fields, individual consent toggles for all 6 dimensions.
   - Confirmation: Celebration graphic, application reference code, next steps timeline.
6. **Components**: `Input`, `Button`, `ConsentSwitch`, `Card`, `Badge`.
7. **Visual Hierarchy**: Welcome message -> Form inputs -> Golden action button -> Support link.
8. **Photography / Illustration**: Maatram logo, subtle botanical wheat watermark, success checkmark.
9. **Interactions**: Instant validation, single-flight form submission, optimistic loading button.
10. **Responsive Behavior**: Card scales to 92vw on mobile with full-width touch-friendly inputs.
11. **Backend Data Required**: `POST /auth/login`, `POST /auth/register`.
12. **States**: Submitting spinner, inline validation errors, session-expired redirect alerts.

---

## 2. Authenticated Volunteer Portal

### 2.1 Volunteer Dashboard (`/volunteer/dashboard`) — *Reference 2*
1. **Purpose**: Primary home for active volunteers: summarize contributions, track upcoming drives, access volunteering guide, and monitor milestone progress.
2. **Primary User**: Authenticated volunteer (Student, Alumnus, or Corporate).
3. **Layout Composition**: 
   - Top Header Bar (Portal title, notification bell with unread badge, user profile pill).
   - Curved Golden Hero Welcome Banner (`Welcome back, Priya!`).
   - 4-metric KPI Row (`Your Contribution at a Glance`).
   - Asymmetric split lower grid: 2/3 left column (Upcoming Participation + Recommended Events), 1/3 right column (Volunteering Guide + Your Progress donut).
4. **Header/Sidebar Requirements**: `VolunteerShell` with floating white sidebar rail (`VolunteerSidebar`).
5. **Main Sections**:
   - Hero Banner with `[Student Volunteer]` and `[Approved]` badges, photo of volunteers in Maatram t-shirts.
   - Contribution KPI Row: Volunteering Points, Approved Hours, Events Attended, Current Rank.
   - Your Upcoming Participation: 3D desk calendar empty state or active registration cards.
   - Recently Viewed / Recommended Opportunities: Mini horizontal event cards.
   - Volunteering Guide: 3 numbered steps + hand-heart graphic (*"Together for a better tomorrow"*).
   - Your Progress: Donut progress ring populated from actual backend milestone data + milestone badge (*"1 more event to reach the next milestone 🎉"*).
6. **Components**: `VolunteerShell`, `HeroBanner`, `MetricCard`, `EventMiniCard`, `DonutProgress`, `EmptyState`.
7. **Visual Hierarchy**: Hero welcome -> KPI numbers -> Actionable upcoming events -> Progress donut.
8. **Photography / Illustration**: Authentic photo of volunteers looking at tree, 3D desk calendar illustration, hand holding heart graphic, star and trophy icons.
9. **Interactions**: "Discover Opportunities ->" navigates to `/volunteer/events`; "All Activity History ->" to `/volunteer/activity`; "View Leaderboard ->" to `/volunteer/leaderboard`.
10. **Responsive Behavior**: Lower 2/3 + 1/3 split stacks on `<1024px`; KPI row wraps into 2x2 on tablet and 1x4 on mobile.
11. **Backend Data Required**: `GET /volunteers/me`, `GET /events`, `GET /registrations/me`.
12. **States**: Skeleton placeholders during load; friendly 3D calendar empty state when no upcoming registrations exist; error toast if API fails.

---

### 2.2 Discover Events (`/volunteer/events` & `/volunteer/events/[id]`) — *Reference 3*
1. **Purpose**: Comprehensive catalog for discovering, filtering, searching, and registering for volunteering drives.
2. **Primary User**: Active volunteer looking for upcoming commitments.
3. **Layout Composition**:
   - Curved Golden Hero Banner (`Discover Events`).
   - Full-width Search Input Card with yellow "Search" button.
   - Category Filter Pill Bar + Sort Dropdown.
   - Vertical stack of full-width horizontal opportunity cards.
4. **Header/Sidebar Requirements**: `VolunteerShell` with "Discover Events" active in sidebar.
5. **Main Sections**:
   - Search & Filter Controls: Pills for `All`, `School Visit`, `Mock Interview`, `BGV Support`, `Admissions`, `Panel Interview`.
   - Event Cards: Thumbnail image, event title, category tag, date, time, location/online pill, save bookmark, and `"View Details ->"` button.
6. **Components**: `SearchInput`, `CategoryPill`, `EventHorizontalCard`, `Badge`, `Button`.
7. **Visual Hierarchy**: Search & filters -> Event cards with high-contrast dates and category pills -> Golden action button.
8. **Photography / Illustration**: Photo of volunteers in banner; dedicated event category photographs for cards.
9. **Interactions**: Real-time client-side search; filter pill toggle; "View Details" opens event deep-dive.
10. **Responsive Behavior**: Horizontal card layout gracefully stacks thumbnail above details on mobile viewports (<640px).
11. **Backend Data Required**: `GET /events?status=PUBLISHED`, `GET /registrations/me`.
12. **States**: Skeleton loading cards; empty state with "No events found matching your search" and reset button.

---

### 2.3 Event Details Page (`/volunteer/events/[id]`)
1. **Purpose**: Full details of an event: schedule, venue map/link, coordinator contact, eligibility criteria, and register/withdraw action.
2. **Primary User**: Volunteer deciding whether to commit.
3. **Layout Composition**: Top breadcrumb, 2-column detail layout (2/3 event description, agenda, prerequisites; 1/3 sticky registration summary card).
4. **Header/Sidebar Requirements**: `VolunteerShell`.
5. **Main Sections**: Event title & category tag, schedule & venue block, agenda timeline, coordinator info, registration action card.
6. **Components**: `Badge`, `Card`, `Button`, `Dialog` (withdrawal confirmation modal).
7. **Visual Hierarchy**: Event title & status -> Action button -> Key logistical details -> Agenda.
8. **Photography / Illustration**: High-resolution event banner image.
9. **Interactions**: Register button triggers `POST /registrations` with instant toast feedback; Withdraw button triggers confirmation dialog.
10. **Responsive Behavior**: Sticky summary card moves below description on mobile.
11. **Backend Data Required**: `GET /events/{id}`, `GET /registrations/me`.
12. **States**: Loading skeleton; confirmed registered state with QR code check-in ticket; registration closed alert if capacity reached.

---

### 2.4 My Activity (`/volunteer/activity`) — *Reference 4*
1. **Purpose**: Track participation history, view confirmed registrations, and review points ledger.
2. **Primary User**: Active volunteer reviewing past and upcoming commitments.
3. **Layout Composition**:
   - Curved Golden Hero Banner (`My Activity`).
   - Segmented Tab Pill Bar: `Upcoming (0)`, `Ongoing (0)`, `Past (0)`, `Points Ledger`.
   - Dynamic tab content card (empty state illustration or activity list).
4. **Header/Sidebar Requirements**: `VolunteerShell` with "My Activity" active.
5. **Main Sections**:
   - Tab 1 (Upcoming): List of upcoming events with check-in instructions.
   - Tab 2 (Ongoing): Currently active event with check-in button / QR code.
   - Tab 3 (Past): Completed drives with awarded hours and points.
   - Tab 4 (Points Ledger): Immutable ledger table showing credits, event references, and dates.
6. **Components**: `SegmentedTabs`, `ActivityCard`, `PointsLedgerTable`, `EmptyState`.
7. **Visual Hierarchy**: Tab bar -> Status badges -> Event/transaction details.
8. **Photography / Illustration**: Banner volunteer photo; 3D desk calendar and clock with leaves empty state illustration.
9. **Interactions**: Tab switching with smooth indicator animation; link to view event details.
10. **Responsive Behavior**: Tables become card lists on mobile; tab pills horizontally scrollable.
11. **Backend Data Required**: `GET /registrations/me`, `GET /gamification/me/ledger`.
12. **States**: Friendly empty state with "Discover Events ->" button when no records exist.

---

### 2.5 Leaderboard (`/volunteer/leaderboard`) — *Reference 5*
1. **Purpose**: Gamified community rankings celebrating top contributors across student, alumni, and corporate tiers.
2. **Primary User**: Volunteers motivated by peer recognition.
3. **Layout Composition**:
   - Curved Golden Hero Banner (`Leaderboard`) with crown icon and cheering crowd illustration.
   - Category Filter Pills (`Overall`, `Students`, `Alumni`, `Corporate`) + Year Selector (`Year: 2025 v`).
   - 3-Step Physical Podium Pedestal (1st Gold in center, 2nd Silver on left, 3rd Bronze on right).
   - Ranking Data Table with highlighted current user row.
4. **Header/Sidebar Requirements**: `VolunteerShell` with "Leaderboard" active.
5. **Main Sections**:
   - Top-3 Podium: Avatars, crowns, wreaths, names, points.
   - Ranking Table: Rank number badges, avatar/icon, volunteer name (or *Anonymous Volunteer* depending on affirmative consent), category, points, hours, trend indicator.
6. **Components**: `Podium`, `CategoryPills`, `DataTable`, `TrendIndicator`, `Badge`.
7. **Visual Hierarchy**: 1st place gold pedestal -> 2nd/3rd pedestals -> User's personal rank row in table.
8. **Photography / Illustration**: Cheering crowd silhouette in golden banner; portrait avatars; gold, silver, bronze crown icons.
9. **Interactions**: Switching category filter instantly recalculates rankings; year dropdown filters historical cycles.
10. **Responsive Behavior**: Podium pedestals stack cleanly or scale proportionally on mobile; table scrolls horizontally.
11. **Backend Data Required**: `GET /gamification/leaderboard?period=YEARLY`, `GET /gamification/me/rank`.
12. **States**: Skeletons for podium and table rows during fetch; empty state if cycle has no recorded points.

---

### 2.6 My Profile & Consents (`/volunteer/profile`) — *Reference 6*
1. **Purpose**: Manage personal details, academic background, volunteering interests, and privacy & consent preferences.
2. **Primary User**: Volunteer managing their profile and privacy choices.
3. **Layout Composition**:
   - Top Header (`My Profile` with golden vertical accent bar).
   - 2-Column Asymmetric Layout:
     - Left Column (~320px): Identity overview card (photo, name, approved badge, contact, mini KPIs, edit button).
     - Right Column (~960px): Tabbed form panels + bottom dual sub-cards (Privacy toggles + Achievements).
4. **Header/Sidebar Requirements**: `VolunteerShell` with "My Profile" active.
5. **Main Sections**:
   - Identity Card: Portrait photo with camera upload overlay, name, status pill, contact details, mini stats (Hours, Points, Events).
   - Tabbed Forms: Personal Information, Volunteer Preferences, Consents & Privacy, Achievements.
   - **Privacy & Consent Governance Section** (Accounting for **all six affirmative consent preferences**):
     1. `leaderboard_visible`: *"Show my participation on the public leaderboard"*.
     2. `name_visible`: *"Display my real name on public leaderboard"* (if disabled, displays as Anonymous Volunteer).
     3. `thank_you_emails`: *"Receive milestone and event thank-you email updates"*.
     4. `linkedin_content`: *"Allow my achievements to be featured in LinkedIn celebration drafts"*.
     5. `contact_available`: *"Share my contact details (email/mobile) with event coordinators"*.
     6. `media_usage`: *"Allow photos and videos featuring me in Maatram communications"*.
     - Transparency Note: Explains that administrators always see real volunteer identity for verification.
   - **My Achievements Section**:
     - Dynamically rendered list of badges awarded to the volunteer from `VolunteerAchievement` records.
     - *Governance*: Badges displayed in Reference 6 are visual examples only. No new thresholds or hardcoded achievement awards are introduced.
6. **Components**: `AvatarCard`, `TabRail`, `Input`, `Select`, `Textarea`, `ConsentSwitch`, `AchievementBadgeContainer`, `Button`.
7. **Visual Hierarchy**: Volunteer portrait & status -> Active form tab -> Save Changes button -> Privacy & consent toggles.
8. **Photography / Illustration**: User portrait photo; dynamically populated badge icons.
9. **Interactions**: Tab switching, photo upload trigger, switch toggles with individual server persistence (`PUT /consents/me`), form validation, Save button with loading feedback.
10. **Responsive Behavior**: 2 columns stack vertically on mobile; tab rail scrolls horizontally.
11. **Backend Data Required**: `GET /users/me`, `GET /volunteers/me`, `GET /consents/me`, `PUT /volunteers/me`, `GET /gamification/me`.
12. **States**: Saving spinner; success toast; validation alerts.

---

### 2.7 Notifications Center (`/volunteer/notifications`)
1. **Purpose**: Centralized inbox for application updates, event confirmations, reminder alerts, and milestone badges.
2. **Primary User**: Volunteer checking messages.
3. **Layout Composition**: Top title and filter tabs (`All`, `Unread`), vertical notification card list.
4. **Header/Sidebar Requirements**: `VolunteerShell` with "Notifications" active.
5. **Main Sections**: Filter tabs, mark-all-as-read button, list of notification items with timestamp, icon, message, and deep-link button.
6. **Components**: `Badge`, `Card`, `Button`, `EmptyState`.
7. **Visual Hierarchy**: Unread items highlighted with soft yellow surface -> Action link.
8. **Photography / Illustration**: Friendly bell illustration for empty state.
9. **Interactions**: Clicking notification marks it as read and navigates to the relevant event/profile.
10. **Responsive Behavior**: Single-column vertical list on all viewports.
11. **Backend Data Required**: `GET /notifications`, `POST /notifications/{id}/read`.
12. **States**: Empty state (*"All caught up! No notifications to show"*).

---

## 3. Administrative Operations Portal

> **DESIGN DIRECTION STATUS: RECOMMENDATION UNDER REVIEW**  
> All administrative styling updates described below represent a **design recommendation under review**, NOT an approved change. Existing admin functionality, table density, operational workflows, and information hierarchy must remain 100% preserved.

### 3.1 Admin Dashboard (`/admin/dashboard`)
1. **Purpose**: Executive oversight of volunteering drives, applicant triage pipelines, and operational health.
2. **Primary User**: Maatram Administrator.
3. **Layout Composition**: KPI summary cards row, quick-action triage buttons, split view of pending applications and upcoming drives.
4. **Header/Sidebar Requirements**: `AdminShell` with `AdminSidebar` (Theme comparison prepared in Section 4).
5. **Main Sections**:
   - Executive KPIs: Total Volunteers, Pending Applications, Active Drives, Verified Service Hours.
   - Pending Approvals Queue: Quick view of applicants needing review.
   - Operational Drives: Calendar view of upcoming weekend drives.
6. **Components**: `AdminShell`, `KPICard`, `DataTable`, `Badge`, `Button`.
7. **Visual Hierarchy**: Pending action counters -> Event schedules -> Detailed metrics.
8. **Photography / Illustration**: Clean admin icons (`lucide-react`).
9. **Interactions**: Quick triage button deep-links to application detail.
10. **Responsive Behavior**: KPI row wraps from 4 to 2 to 1 columns.
11. **Backend Data Required**: `GET /admin/dashboard` (Milestone 5 CTE consolidated query).
12. **States**: Skeletons during fetch; zero-queue empty state.

---

### 3.2 Applications Review & Details (`/admin/applications` & `/admin/applications/[id]`)
1. **Purpose**: Screen and approve prospective volunteers with complete audit trail.
2. **Primary User**: Volunteer Coordinator / Administrator.
3. **Layout Composition**: Filterable high-density data table on list page; structured 2-column dossier on detail page.
4. **Header/Sidebar Requirements**: `AdminShell`.
5. **Main Sections**: Applicant info, academic/career verification, motivation statement, track assignment, decision action buttons (`Approve`, `Reject`, `Request Info`).
6. **Components**: `DataTable`, `Badge`, `Button`, `Dialog` (decision confirmation with mandatory reason input).
7. **Visual Hierarchy**: Applicant identity & category -> Qualifications -> Action decision bar.
8. **Photography / Illustration**: Applicant uploaded photo (if available).
9. **Interactions**: Modal dialog for approval/rejection captures mandatory reason and creates immutable audit log.
10. **Responsive Behavior**: Dossier stacks vertically on smaller screens.
11. **Backend Data Required**: `GET /admin/applications`, `POST .../approve`, `POST .../reject`.
12. **States**: Submitting loader; success notification; audit log history.

---

### 3.3 Events Management (`/admin/events`, `create`, `[id]`, `participants`, `attendance`, `complete`)
1. **Purpose**: Full lifecycle management of volunteering drives from creation to attendance check-in and points awarding.
2. **Primary User**: Event Coordinator.
3. **Layout Composition**:
   - List Page: Event cards with lifecycle badges (Draft, Published, Completed).
   - Create/Edit Page: Multi-section form (Logistics, Venue, Capacity, Track).
   - Detail Command Center: Tabs for Overview, Participants, Attendance QR Verification, Wrap-up Completion.
4. **Header/Sidebar Requirements**: `AdminShell`.
5. **Main Sections**: Logistics editor, volunteer roster table, QR verification interface, completion calculation preview.
6. **Components**: `Form`, `Input`, `Select`, `DataTable`, `QRScannerPlaceholder`, `Badge`, `Button`.
7. **Visual Hierarchy**: Event status badge -> Capacity counter -> Attendance verification -> Completion button.
8. **Photography / Illustration**: Event photo uploader with preview.
9. **Interactions**: Real-time attendance check-in toggle; event completion triggers gamification point awards.
10. **Responsive Behavior**: Attendance scanner and roster adapt to mobile view for on-field coordinators.
11. **Backend Data Required**: `GET /admin/events`, `POST /admin/events`, `POST .../attendance`, `POST .../complete`.
12. **States**: Validation alerts; confirmation dialogs; completion certificate preview.

---

### 3.4 Volunteer Directory & Profiles (`/admin/volunteers` & `/admin/volunteers/[id]`)
1. **Purpose**: Master directory of all volunteers, participation history, status management, and manual point adjustments.
2. **Primary User**: Administrator.
3. **Layout Composition**: Data table with search and filters on list; comprehensive volunteer dossier on detail.
4. **Header/Sidebar Requirements**: `AdminShell`.
5. **Main Sections**: Search bar, status filters (`Active`, `Suspended`), volunteer profile view, participation logs, manual point adjustment tool.
6. **Components**: `DataTable`, `Badge`, `Button`, `PointAdjustmentModal`.
7. **Visual Hierarchy**: Volunteer name & status -> Cumulative hours/points -> Historical drives.
8. **Photography / Illustration**: Volunteer avatar.
9. **Interactions**: Point adjustment modal requires explicit audit reason.
10. **Responsive Behavior**: Responsive table with mobile card fallback.
11. **Backend Data Required**: `GET /admin/volunteers`, `GET /admin/volunteers/{id}`, `POST .../adjust-points`.
12. **States**: Audit confirmation toast.

---

### 3.5 Reports, Analytics & Exports (`/admin/reports`)
1. **Purpose**: Executive impact reporting, volunteering hours summaries, and Excel workbook downloads.
2. **Primary User**: Foundation Director / Trustee.
3. **Layout Composition**: Date range picker, metric cards, breakdown charts, and export actions.
4. **Header/Sidebar Requirements**: `AdminShell`.
5. **Main Sections**: Date filter, Total Impact summary, Category breakdown (School visits vs Mock interviews), Asynchronous Excel download trigger.
6. **Components**: `DateRangePicker`, `KPICard`, `ChartPlaceholder`, `Button`.
7. **Visual Hierarchy**: Date selector -> Macro impact numbers -> Visual distribution charts -> Export button.
8. **Photography / Illustration**: Chart graphics and spreadsheet export icons.
9. **Interactions**: "Download Excel" triggers threadpool-offloaded workbook generation via `POST /admin/reports/export-excel`.
10. **Responsive Behavior**: Charts scale responsively to container width.
11. **Backend Data Required**: `GET /admin/reports/summary`, `POST .../export-excel`.
12. **States**: Excel generation spinner; download prompt.

---

### 3.6 System Operations & Settings (`/admin/operations`, `/admin/settings`)
1. **Purpose**: Monitor outbox worker background jobs, dead-letter retries, portal parameters, and email templates.
2. **Primary User**: System Administrator / Technical Coordinator.
3. **Layout Composition**: System health status indicators, outbox queue table with retry buttons, settings forms.
4. **Header/Sidebar Requirements**: `AdminShell`.
5. **Main Sections**: Outbox queue health (Pending, Processed, Failed), Dead-letter retry triggers, System parameter controls.
6. **Components**: `DataTable`, `Badge`, `Button`, `Form`.
7. **Visual Hierarchy**: Failed job counter (red badge) -> Queue table -> Parameter inputs.
8. **Photography / Illustration**: Server health status icons.
9. **Interactions**: Manual retry button for failed outbox notifications.
10. **Responsive Behavior**: Full table view on desktop.
11. **Backend Data Required**: `GET /admin/operations/outbox`, `POST .../retry`, `GET /admin/settings`.
12. **States**: Action confirmation alerts.

---

## 4. Admin Portal Theme Comparison Matrix (Recommendation vs Current)

| Theme Dimension | Current Baseline Implementation | Proposed Design Recommendation | Recommendation Rationale |
| :--- | :--- | :--- | :--- |
| **Sidebar Background** | Deep Charcoal / Black (`#16171A`) | Warm Slate / Charcoal (`#1C1D21` or `#23252B`) | Softens extreme black while preserving clear administrative separation from volunteer portal. |
| **Active Nav Link** | Solid Dark Grey (`#212328`) with white text | Charcoal with Maatram Gold accent border (`#F5B817`) | Visually connects the administrative portal to the Maatram brand identity. |
| **Main Content Canvas** | Cool Grey (`#F9FAFB`) | Warm Off-White / Ivory (`#FAF8F5`) | Creates seamless page transitions between public, volunteer, and admin domains. |
| **Table Data Density** | Compact (36px row height, border `#E5E7EB`) | **PRESERVED UNCHANGED** (Compact 36px row height) | Maintains high operational efficiency for triage of hundreds of applications. |
| **Status Badges** | Standard Tailwind pills | Soft pastel semantic pills with dark text | Improves at-a-glance legibility without sacrificing table space. |
| **Final Decision Gate** | Current baseline remains active. | Requires explicit user sign-off prior to Phase 6.8. | Zero unapproved visual changes to admin portal. |
