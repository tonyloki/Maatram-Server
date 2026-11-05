# M6_EXISTING_WEB_AUDIT.md — Comprehensive Codebase Audit of Existing Web Application
**Maatram Volunteering & Gamification Portal**  
**Milestone 6.0: Architecture & Codebase Inspection**  
**Component:** Next.js Web Application (`web/`)  
**Date:** November 2026 (Updated with Alignment Corrections)  
**Status:** **ALIGNED AUDIT COMPLETE — SOURCE CODE VERIFIED**

---

## 1. Executive Summary

This document presents a comprehensive, line-by-line inspection of the current Next.js 16 web application (`web/`). All 33 routes, layouts, navigation shells, shared UI primitives, utility libraries, and styling configurations were inspected to establish an exact baseline.

The application is functionally mature: all backend API endpoints are wired, authentication (HttpOnly cookies + single-flight refresh) is secure, RBAC guards are active, affirmative consent tracking across all six dimensions is established, and Milestone 5 performance optimizations (batching, eager loading, SWR in-flight deduplication) are working smoothly. 

Visually, there is a divergence between the current implementation and the mentor's approved reference designs:
1. The volunteer portal currently utilizes a dark charcoal / light yellow utilitarian layout rather than the soft warm ivory canvas (`#FAF8F5`), floating white cards, botanical flourishes, and signature curved golden hero banners showcased in the references.
2. Several pages lack tailored empty state illustrations (using generic text placeholders or raw spin loaders).
3. The Admin portal uses a dark slate theme (`#16171A`) that feels disconnected from the warm community visual identity of the volunteer and public portals. Any proposed admin restyling is treated strictly as a **design recommendation under review**, preserving operational data density and workflow efficiency.

---

## 2. Inventory of Routes, Pages & Layouts

The application implements exactly 33 `page.tsx` routes and 3 `layout.tsx` files across three distinct domains:

### 2.1 Public Web Experience (7 routes)
| Route Path | File Location | Primary Purpose | Current Layout / Shell |
| :--- | :--- | :--- | :--- |
| `/` | `web/src/app/page.tsx` | Main public landing page, mission, hero, opportunities, stats | PublicHeader + PublicFooter |
| `/about` | `web/src/app/about/page.tsx` | About Maatram, founder vision, leadership, philosophy | PublicHeader + PublicFooter |
| `/impact` | `web/src/app/impact/page.tsx` | Historical impact metrics, student testimonials, partner schools | PublicHeader + PublicFooter |
| `/events` | `web/src/app/events/page.tsx` | Public event catalog (read-only discovery without login) | PublicHeader + PublicFooter |
| `/events/[id]` | `web/src/app/events/[id]/page.tsx` | Public event details & CTA to login/register to participate | PublicHeader + PublicFooter |
| `/login` | `web/src/app/login/page.tsx` | Authentication portal (email/password, remember me, redirects) | PublicHeader + PublicFooter |
| `/register` | `web/src/app/register/page.tsx` | Multi-step volunteer registration & affirmative consent collection across all 6 dimensions | PublicHeader + PublicFooter |
| `/register/confirmation` | `web/src/app/register/confirmation/page.tsx` | Registration success & pending approval notice | PublicHeader + PublicFooter |

### 2.2 Volunteer Portal (9 routes)
All volunteer routes are wrapped within `web/src/app/volunteer/layout.tsx` which invokes `VolunteerShell`.
| Route Path | File Location | Primary Purpose | Backend API Integrations |
| :--- | :--- | :--- | :--- |
| `/volunteer` | `web/src/app/volunteer/page.tsx` | Redirects to `/volunteer/dashboard` | N/A |
| `/volunteer/dashboard` | `web/src/app/volunteer/dashboard/page.tsx` | Volunteer KPIs, upcoming drives, guide, progress | `GET /volunteers/me`, `GET /events`, `GET /registrations/me` |
| `/volunteer/events` | `web/src/app/volunteer/events/page.tsx` | Event discovery, category filtering, search, sorting | `GET /events`, `GET /registrations/me` |
| `/volunteer/events/[id]` | `web/src/app/volunteer/events/[id]/page.tsx` | Event details, register, withdraw, attendance status | `GET /events/{id}`, `POST /registrations`, `DELETE /registrations/{id}` |
| `/volunteer/activity` | `web/src/app/volunteer/activity/page.tsx` | Activity history tabs (Upcoming, Ongoing, Past, Ledger) | `GET /registrations/me`, `GET /gamification/me/ledger` |
| `/volunteer/leaderboard` | `web/src/app/volunteer/leaderboard/page.tsx` | Gamification rankings, category tabs, podium, user rank | `GET /gamification/leaderboard`, `GET /gamification/me/rank` |
| `/volunteer/profile` | `web/src/app/volunteer/profile/page.tsx` | Profile edit, academic info, skills, 6 affirmative consent controls | `GET /users/me`, `PUT /volunteers/me`, `GET /consents/me`, `PUT /consents/me` |
| `/volunteer/notifications` | `web/src/app/volunteer/notifications/page.tsx` | In-app notification center, unread filter, mark as read | `GET /notifications`, `POST /notifications/{id}/read` |

### 2.3 Admin Portal (15 routes)
All admin routes are wrapped within `web/src/app/admin/layout.tsx` which invokes `AdminShell`.
| Route Path | File Location | Primary Purpose | Backend API Integrations |
| :--- | :--- | :--- | :--- |
| `/admin` | `web/src/app/admin/page.tsx` | Redirects to `/admin/dashboard` | N/A |
| `/admin/dashboard` | `web/src/app/admin/dashboard/page.tsx` | Strategic KPIs, pending queue counters, upcoming drives | `GET /admin/dashboard` (Milestone 5 CTE query) |
| `/admin/applications` | `web/src/app/admin/applications/page.tsx` | Volunteer applications review queue, bulk actions | `GET /admin/applications` |
| `/admin/applications/[id]` | `web/src/app/admin/applications/[id]/page.tsx` | Application deep-dive, approve, reject, revision request | `GET /admin/applications/{id}`, `POST .../approve`, `POST .../reject` |
| `/admin/volunteers` | `web/src/app/admin/volunteers/page.tsx` | Volunteer roster, status filters, search, points audit | `GET /admin/volunteers` |
| `/admin/volunteers/[id]` | `web/src/app/admin/volunteers/[id]/page.tsx` | Volunteer detail, activity history, manual point adjust | `GET /admin/volunteers/{id}`, `POST .../adjust-points` |
| `/admin/events` | `web/src/app/admin/events/page.tsx` | Event lifecycle list (Draft, Published, Completed) | `GET /admin/events` |
| `/admin/events/create` | `web/src/app/admin/events/create/page.tsx` | Create event form with category, date, venue, capacity | `POST /admin/events` |
| `/admin/events/[id]` | `web/src/app/admin/events/[id]/page.tsx` | Event overview, roster, edit event metadata | `GET /admin/events/{id}`, `PUT /admin/events/{id}` |
| `/admin/events/[id]/participants` | `web/src/app/admin/events/[id]/participants/page.tsx` | Manage registered volunteers, approve/reject signups | `GET /admin/events/{id}/participants`, `PUT ...` |
| `/admin/events/[id]/attendance` | `web/src/app/admin/events/[id]/attendance/page.tsx` | Mark attendance, verify check-in/check-out timestamps | `GET /admin/events/{id}/attendance`, `POST .../verify` |
| `/admin/events/[id]/complete` | `web/src/app/admin/events/[id]/complete/page.tsx` | Finalize event drive, calculate & award points/hours | `POST /admin/events/{id}/complete` |
| `/admin/attendance` | `web/src/app/admin/attendance/page.tsx` | Cross-event attendance monitoring & manual corrections | `GET /admin/attendance/records` |
| `/admin/reports` | `web/src/app/admin/reports/page.tsx` | Analytics charts, metrics, async Excel exports | `GET /admin/reports/summary`, `POST .../export-excel` |
| `/admin/operations` | `web/src/app/admin/operations/page.tsx` | Transactional outbox status, dead-letter jobs, retry | `GET /admin/operations/outbox`, `POST .../retry` |
| `/admin/settings` | `web/src/app/admin/settings/page.tsx` | Portal configuration, email templates, system params | `GET /admin/settings` |

---

## 3. Affirmative Consent Architecture (All Six Dimensions)

The backend database (`consent_records` table) enforces affirmative consent across **six independent privacy dimensions**:
1. `leaderboard_visible`: Opt-in to appear on the public leaderboard.
2. `name_visible`: Opt-in to show real name (if false, shown as Anonymous Volunteer).
3. `thank_you_emails`: Opt-in to receive milestone and event thank-you communications.
4. `linkedin_content`: Opt-in to have volunteer contributions featured in LinkedIn draft posts.
5. `contact_available`: Opt-in to share email and mobile numbers with event coordinators.
6. `media_usage`: Opt-in to appear in Maatram promotional and annual media photography.

**Audit Rule**: All 6 dimensions must be individually controllable in the UI. No dimension may be combined, removed, or silently defaulted without volunteer opt-in.

---

## 4. Design Tokens & Styling Architecture

### 4.1 CSS Configuration
- **Framework**: Tailwind CSS v4 using `@theme` directive in `web/src/app/globals.css`.
- **Resolved Canonical Brand Primary**: `--color-brand-primary: #F5B817` (sample-validated against original logo `#FFC20F` and mentor references `#FEC216`).
- **Supporting Palette**:
  - `--color-brand-hover`: `#E5A800`
  - `--color-brand-active`: `#C99200`
  - `--color-brand-subtle`: `#FFF8E7`
  - `--color-brand-text`: `#946C00`
  - `--color-canvas-bg`: `#FAF8F5`
  - `--color-card-surface`: `#FFFFFF`
  - `--color-card-border`: `#EFECE6`
  - `--color-text-primary`: `#1F2421`
  - `--color-text-secondary`: `#4B5563`
  - `--color-text-muted`: `#9CA3AF`

---

## 5. Performance Optimizations to Strictly Preserve

The following Milestone 5 performance optimizations **must remain untouched** during visual redesign:
1. **Frontend Request Deduplication (`web/src/lib/api-client.ts`)**:
   - `inFlightGetRequests` map prevents duplicate simultaneous requests for `/users/me` and `/notifications/unread-count`.
   - `responseMemoryCache` short-lived SWR cache for idempotent GET requests.
   - Automatic cache invalidation on any POST/PUT/DELETE mutation.
   - Instant cache purge (`clearApiCache`) on logout or auth state transitions.
2. **Backend Batching & Eager Loading**:
   - `get_batch_registration_counts` in event queries.
   - Dashboard CTE aggregation.
   - `joinedload` on Many-to-One event registration relations.
   - Argon2id password hashing offloaded to dedicated worker thread pool.

---

## 6. Component Categorization Matrix

| Component / File | Recommendation | Primary Action Required |
| :--- | :--- | :--- |
| `web/src/lib/api-client.ts` | **PRESERVE UNTOUCHED** | Zero functional or behavioral modifications. |
| `web/src/lib/auth-context.tsx` | **PRESERVE UNTOUCHED** | Zero authentication modifications. |
| `web/src/lib/utils.ts` | **REUSE AS-IS** | Utility helpers (`cn`) are optimal. |
| `web/src/components/ui/button.tsx` | **ENHANCE & RESTYLE** | Apply canonical gold `#F5B817`, rounded-full/rounded-xl, arrow feedback. |
| `web/src/components/ui/card.tsx` | **RESTYLE** | Apply `#FFFFFF`, `rounded-2xl`/`rounded-3xl`, soft warm border `#EFECE6`. |
| `web/src/components/ui/badge.tsx` | **RESTYLE** | Align pastel fills with mentor references. |
| `web/src/components/ui/input.tsx` | **POLISH** | Generous padding, soft borders, warm focus rings. |
| `web/src/components/ui/switch.tsx` | **RESTYLE** | Golden yellow active track (`#F5B817`) to match references. |
| `web/src/components/navigation/volunteer-sidebar.tsx` | **MAJOR REDESIGN** | Floating white card, golden pill active links, leaf watermark, Together card. |
| `web/src/components/navigation/volunteer-shell.tsx` | **RESTYLE & POLISH** | Align top header with references; keep responsive drawer logic. |
| `web/src/app/volunteer/dashboard/page.tsx` | **MAJOR REDESIGN** | Reconstruct hero banner, metric cards, guide, progress donut. |
| `web/src/app/volunteer/events/page.tsx` | **MAJOR REDESIGN** | Reconstruct hero banner, search bar, category pills, opportunity cards. |
| `web/src/app/volunteer/activity/page.tsx` | **MAJOR REDESIGN** | Reconstruct hero banner, segmented tab pills, empty state illustration. |
| `web/src/app/volunteer/leaderboard/page.tsx` | **MAJOR REDESIGN** | Reconstruct hero banner, top-3 podium pedestals, ranking table. |
| `web/src/app/volunteer/profile/page.tsx` | **MAJOR REDESIGN** | Reconstruct avatar card, tabbed forms, all 6 affirmative consent switches. |
| `web/src/app/admin/*` (All 15 routes) | **RECOMMENDATION UNDER REVIEW** | Theme comparison prepared; preserve operational table density. |
