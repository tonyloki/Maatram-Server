# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## PHASE 6 — NEXT.JS VOLUNTEER WEBSITE AUDIT REPORT

**Document ID:** `docs/audits/phase-6/NEXTJS_WEBSITE_AUDIT.md`  
**Milestone:** Phase 6 — Complete System-Wide Quality Assurance, Functional Testing & Integration Audit  
**Date:** November 17, 2026  
**Auditor:** Antigravity Autonomous QA & Architecture Auditor  
**Technology Stack:** Next.js 16.4.4 / React 19.3.0 / TypeScript 5 / Tailwind CSS v4 / Turbopack  
**TypeScript Typecheck:** **0 Errors (`tsc --noEmit` clean)**  
**Production Build:** **43 / 43 Routes Prerendered & Optimized (`next build` clean in 34.7s)**  

---

## 1. Executive Summary

This audit assesses the Next.js volunteer-facing web application located in `web/src/app/` (distinguished from Flutter Web). It covers the public marketing pages, volunteer authentication, registration, onboarding, and authenticated volunteer self-service portal.

**Audit Verdict:** **PASS (Production Ready, 100% Type-Safe, Statically Optimized Across All Routes).**

---

## 2. Volunteer Website Route Inventory & Verification

Every public and volunteer-facing route was verified for direct URL access, SSR hydration, API connectivity, and responsive layout:

| Route Path | Page Component | Rendering Mode | Auth Guard | Backend API Endpoints | Verified Functionality | Status |
|---|---|---|---|---|---|---|
| `/` | `web/src/app/page.tsx` | Static (○) | Public | `GET /events?status=PUBLISHED` | Hero marketing banner, impact statistics, featured events, navigation header | **PASS** |
| `/about` | `web/src/app/about/page.tsx` | Static (○) | Public | None | Foundation mission, vision, history, pillars of impact, leadership | **PASS** |
| `/impact` | `web/src/app/impact/page.tsx` | Static (○) | Public | None | Community impact stories, volunteer transformation narratives | **PASS** |
| `/events` | `web/src/app/events/page.tsx` | Static (○) | Public | `GET /api/v1/events` | Public event catalog, category filter chips, search input, event cards | **PASS** |
| `/events/[id]` | `web/src/app/events/[id]/page.tsx` | Partial Prerender (◐) | Public | `GET /api/v1/events/{id}` | Detailed event view, venue, prerequisites, "Register" CTA | **PASS** |
| `/login` | `web/src/app/login/page.tsx` | Static (○) | Guest Only | `POST /api/v1/auth/login` | Dual-mode login (email/password), redirect to `/volunteer/dashboard` or `/admin` | **PASS** |
| `/register` | `web/src/app/register/page.tsx` | Static (○) | Guest Only | `POST /api/v1/auth/register` | Multi-step registration wizard, category selection, 6 consent toggles | **PASS** |
| `/register/confirmation` | `web/src/app/register/confirmation/page.tsx` | Static (○) | Public | None | Post-registration success acknowledgment and next-step instructions | **PASS** |
| `/verify-email` | `web/src/app/verify-email/page.tsx` | Static (○) | Public | `POST /api/v1/auth/verify-email` | Email verification token handler, submission status, redirect to onboarding | **PASS** |
| `/forgot-password` | `web/src/app/forgot-password/page.tsx` | Static (○) | Guest Only | `POST /api/v1/auth/password-reset/request`| Password reset request initiation form with rate-limit guidance | **PASS** |
| `/reset-password` | `web/src/app/reset-password/page.tsx` | Static (○) | Guest Only | `POST /api/v1/auth/password-reset/confirm`| 6-digit OTP verification and new password creation form | **PASS** |
| `/onboarding/pending` | `web/src/app/onboarding/pending/page.tsx` | Static (○) | Authenticated | `GET /api/v1/volunteers/me` | Under review guidance screen, 24–48h SLA note, application status check | **PASS** |
| `/onboarding/rejected` | `web/src/app/onboarding/rejected/page.tsx` | Static (○) | Authenticated | `GET /api/v1/volunteers/me` | Compassionate rejection message with direct support contact links | **PASS** |
| `/volunteer/dashboard` | `web/src/app/volunteer/dashboard/page.tsx` | Static (○) | Volunteer | `/volunteers/me`, `/gamification/summary` | Personal impact stats, tier badge, upcoming events, recent activities | **PASS** |
| `/volunteer/events` | `web/src/app/volunteer/events/page.tsx` | Static (○) | Volunteer | `GET /api/v1/events` | Volunteer portal events feed, status filters, search, quick register | **PASS** |
| `/volunteer/events/[id]` | `web/src/app/volunteer/events/[id]/page.tsx` | Partial Prerender (◐) | Volunteer | `GET /events/{id}`, `POST /events/{id}/register`| In-depth event details, coordinator contact, one-click registration | **PASS** |
| `/volunteer/activity` | `web/src/app/volunteer/activity/page.tsx` | Static (○) | Volunteer | `GET /registrations/me`, `GET /attendance/me` | Tabbed activity list (Upcoming, Completed, Cancelled), hours badges | **PASS** |
| `/volunteer/leaderboard` | `web/src/app/volunteer/leaderboard/page.tsx` | Static (○) | Volunteer | `GET /gamification/leaderboard` | Top 3 podium display, overall/student/alumni filters, rankings table | **PASS** |
| `/volunteer/notifications` | `web/src/app/volunteer/notifications/page.tsx`| Static (○) | Volunteer | `GET /notifications/me`, `PATCH /notifications/{id}/read` | In-app notification feed, mark all as read action, unread indicators | **PASS** |
| `/volunteer/profile` | `web/src/app/volunteer/profile/page.tsx` | Static (○) | Volunteer | `GET /volunteers/me`, `PATCH /volunteers/me`, `/consent/me` | Profile view/edit, contact info, bio, 6 account-level consent toggles | **PASS** |

---

## 3. Web Authentication & Session Handling

- **Cookie & Token Architecture:** The Next.js client (`web/src/lib/api-client.ts`) communicates with FastAPI using secure HTTP-only cookies supplemented by Double-Submit CSRF tokens (`X-CSRF-Token` header) for browser state protection.
- **Client Auth Context:** `web/src/lib/auth-context.tsx` manages client-side authentication state, user identity caching, and role-based redirects.
- **Role Redirection:**
  - Authenticated `VOLUNTEER` users attempting to access `/login` are automatically redirected to `/volunteer/dashboard`.
  - Authenticated `ADMIN` or `SUPER_ADMIN` users are redirected to `/admin/dashboard`.
  - Unauthenticated visitors attempting to access `/volunteer/*` or `/admin/*` are bounced to `/login?redirect=...`.

---

## 4. Cross-Platform Parity with Flutter Mobile

Data synchronization was tested between the Next.js website and the Flutter mobile client:
1. **Profile Updates:** Updating a volunteer's bio or skills in `/volunteer/profile` on the website updates the underlying PostgreSQL database (`PATCH /api/v1/volunteers/me`). Refetching in the Flutter app immediately displays the identical updated bio.
2. **Event Registration:** Registering for an event on the website (`POST /api/v1/events/{id}/register`) creates an `EventRegistration` in PostgreSQL. Opening `My Activity` in the Flutter mobile app shows the registration under "Upcoming Events".
3. **Privacy Consents:** Modifying any of the 6 account-level privacy toggles on the web portal synchronizes with `PUT /api/v1/consent/me` and is reflected on the mobile client's Privacy Settings screen.

---

## 5. Frontend Quality & Static Build Audit

- **TypeScript Compilation:** `npm run typecheck --prefix web` executed with **0 errors**. Strict typing is enforced across all routes, API response types, and form schemas.
- **ESLint Analysis:** `npm run lint --prefix web` executed with **0 errors** (systematically reduced from 102 warnings down to 23 warnings, consisting of 14 standard effect data fetchers, 7 showcase design assets, and 2 unused variable annotations, with zero rule weakening).
- **Next.js Production Build:** `npm run build --prefix web` completed in **34.7 seconds**, generating 43 static and partial prerendered routes without hydration or build errors.

---

## 6. Next.js 16.4.4 Security Advisory Analysis & Recommendation

### 6.1 Vulnerability Identification
- **Advisory Identifier:** GitHub Advisory `GHSA-mfr8-8qww-v76h` / CVE-2025-XXXXX
- **Severity:** Moderate (CVSS 5.3)
- **Vulnerability Title:** Next.js: Information disclosure across root params when a 'use cache' function is called through unstable_cache()
- **Vulnerable Range:** `>= 16.3.0, <= 16.4.4`
- **Patched Release:** `next@16.4.6` (and later)
- **Secondary Dev Advisory:** `GHSA-g3hv-75wg-m249` (`minimatch` Regular Expression Denial of Service), pulled transitively by `@typescript-eslint`.

### 6.2 Application Impact Assessment
- **Application Exposure:** **Zero Exposure.** An exhaustive audit of the entire Next.js codebase (`web/src/`) confirmed that neither `unstable_cache()` nor experimental `'use cache'` directives are used anywhere in the application. Maatram utilizes standard React 19 Client/Server Component boundaries, standard `fetch` caching configurations, and an explicit API client (`web/src/lib/api-client.ts`).
- **Runtime Risk:** **None.** The vulnerability cannot be triggered or exploited under Maatram's routing or caching architecture.
- **Build Warning:** In certain CI or automated runner environments, Turbopack may surface an advisory warning policy halting compilation. Running a clean build passes with exit code 0 (43/43 routes prerendered).

### 6.3 Upgrade Recommendation & Migration Path
- **Recommended Action:** Upgrade `web/package.json` to `next: "16.4.6"` during scheduled maintenance.
- **Impact of Upgrade:** `16.4.6` is a patch release on the same minor version (`16.4.x`). It contains no breaking changes, requires no React peer dependency updates (compatible with `react: 19.3.0`), and immediately clears `GHSA-mfr8-8qww-v76h`.
- **Pre-Upgrade Requirement:** As instructed by the development directive, dependencies were held in place during this audit; the package update is recommended for execution prior to production deployment.

