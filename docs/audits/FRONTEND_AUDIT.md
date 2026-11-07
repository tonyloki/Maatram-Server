# Frontend Technical & Code Quality Audit
**Maatram Volunteering & Mentorship Portal — Web Client**
**Audit Date:** November 2026  
**Auditor:** Independent Production Readiness Audit Subagent  
**Scope:** TypeScript compilation, static code analysis (ESLint), state machine robustness, API client resilience, authentication context lifecycle, and type definitions.

---

## 1. Executive Summary

This technical audit examines the implementation quality of the Next.js frontend located in `web/`. The evaluation focuses on type safety, error boundaries, async state management, mock data pollution, API resilience, and memory/performance concerns.

### Scorecard Overview:
- **TypeScript Strict Compilation (`tsc --noEmit`):** **PASS** (0 compiler errors).
- **ESLint Analysis:** **0 Errors, 122 Warnings** (predominantly missing hook dependencies and cascading state updates in `useEffect`).
- **Data Integrity:** **FAIL** (Widespread hardcoded mock data in production event catalogs and admin analytics).
- **State Handling Resilience:** **PARTIAL** (Missing loading skeletons, unhandled network timeout limits, silent error suppression).
- **Type Definitions & Backend Alignment:** **GOOD** (Strong Pydantic-to-TypeScript mapping in `web/src/types/index.ts`).

---

## 2. Compilation, Static Analysis & Lint Findings

### 2.1 TypeScript Strictness Check
Command executed: `npx tsc --noEmit` in `web/`
- **Result:** Exited with code `0`.
- **Verdict:** Clean TypeScript compilation with strict mode enabled in `tsconfig.json`.

### 2.2 ESLint Diagnostic Categorization
Command executed: `npx eslint src/` in `web/`
- **Result:** `0 errors, 122 warnings` across 38 files.
- **Categorization of Warnings:**
  1. **React Hook Missing Dependencies (`react-hooks/exhaustive-deps`):** 46 warnings. Multiple `useEffect` blocks omit callback dependencies, risking stale closures during async state transitions.
  2. **Cascading State Updates in `useEffect`:** 28 warnings. State setters triggered directly in effects without conditional guards, risking re-render loops.
  3. **Unused Imports & Variables (`@typescript-eslint/no-unused-vars`):** 42 warnings. Unused icons (`lucide-react`), dead interfaces, and unused parameters.
  4. **Implicit Any Fallbacks (`@typescript-eslint/no-explicit-any`):** 6 instances in legacy utility functions.

---

## 3. Data Integrity & Mock Fallbacks

A critical standard of the Maatram platform is **"Database as Single Source of Truth"** (AGENTS.md §1.2). Production endpoints and interfaces must never present fabricated figures or mock objects. Several frontend views violate this mandate.

### 3.1 Production Catalog Mock Event Pollution
- **File:** `web/src/app/volunteer/events/page.tsx` (Lines 38–87)
- **Code Reference:**
  ```tsx
  const DEFAULT_EVENTS: VolunteerEvent[] = [
    {
      id: "evt-school-visit-01",
      title: "Government Higher Secondary School Visit",
      event_type: "EDUCATION",
      status: "PUBLISHED",
      points_value: 50,
      service_hours: 4,
      ...
    },
    ...
  ];
  ```
- **Finding:** If the backend API fails to respond or returns an empty array, the catalog falls back to `DEFAULT_EVENTS`. Because these IDs are dummy strings (`evt-school-visit-01`) rather than UUIDs, clicking any card immediately triggers a runtime HTTP 422 error on `GET /api/v1/events/evt-school-visit-01`.

### 3.2 Real Event Suppression in Dashboard Recommendations
- **File:** `web/src/components/volunteer/dashboard/recommended-events-section.tsx` (Lines 20–47, 55–58)
- **Code Reference:**
  ```tsx
  const drivesToRender = events.length >= 2 ? events.slice(0, 2) : fallbackDrives;
  ```
- **Finding:** If the backend has only 1 active event published (`events.length === 1`), `events.length >= 2` evaluates to `false`. As a result, the legitimate backend event is **discarded**, and two fake fallback drives (`school-visit-curated` and `mock-interview-curated`) are displayed to the volunteer!

### 3.3 Fabricated Analytics in Admin Reports
- **File:** `web/src/app/admin/reports/page.tsx` (Lines 125–138, 261, 273, 285, 297, 371–410)
- **Code Reference:**
  ```tsx
  // Hardcoded volunteer hours chart values
  const monthlyHours = [250, 320, 410, 500, 480, 520, 610, 590, 680, 720, 810, 890];

  // Hardcoded distribution donut percentages
  <div style={{ width: "62%" }} className="bg-brand-yellow" />
  <div style={{ width: "26%" }} className="bg-blue-500" />
  <div style={{ width: "12%" }} className="bg-emerald-500" />
  ```
- **Finding:** The executive reports dashboard displays hardcoded hours and hardcoded tier distributions (62% Bronze, 26% Silver, 12% Gold). Real database metrics are ignored, rendering the reports dashboard misleading for administrative planning.

---

## 4. API Client & Auth Lifecycle Review

### 4.1 API Client Analysis (`web/src/lib/api-client.ts`)
- **Token Refresh Queue:** `api-client.ts` implements a mutex queue for concurrent 401 responses. When multiple parallel requests receive 401 Unauthorized, only a single `/api/v1/auth/refresh` request is dispatched. Pending requests are held in memory and retried upon successful token rotation.
- **Request Timeout Vulnerability (P2):**
  - The `fetch` calls in `api-client.ts` do not configure an `AbortSignal.timeout()` or `AbortController` timeout handler.
  - If the backend or intermediate network proxy hangs or stalls, client requests wait indefinitely without failing gracefully, freezing button spinners and user interfaces.
- **Error Deserialization:** Robust. Maps backend RFC-7807/FastAPI error structures into an `ApiError` class with HTTP status code, `detail`, and field-specific validation lists.

### 4.2 Authentication Context (`web/src/lib/auth-context.tsx`)
- **Session Lifecycle:** Tracks `accessToken`, `user`, and `isLoading`. State is synchronized with `localStorage` and server cookies.
- **Logout Cleanup:** Accurately wipes cookies, clears local tokens, resets in-memory user objects, and triggers Next.js router redirection to `/login`.
- **RBAC Role Gate:** Correctly exposes `hasRole(["VOLUNTEER", "ADMIN", "SUPERADMIN"])` helper functions used across layouts.

### 4.3 Schema Alignment (`web/src/types/index.ts`)
- **Pydantic Correspondence:**
  - `User`, `VolunteerProfile`, `VolunteerEvent`, `EventRegistration`, `AttendanceLog`, `GamificationScore`, and `ConsentPreferences` match backend database models.
  - Enums (`UserRole`, `VolunteerCategory`, `EventStatus`, `AttendanceStatus`, `GamificationTier`) mirror backend SQLAlchemy enumeration values.
- **Gap:** Missing schema typing for backend `AuditLog` response DTOs (relevant to Phase 12).

---

## 5. State Handling: Loading, Error & Empty States

| Component / Page | Loading State | Error State | Empty State | Findings |
| :--- | :--- | :--- | :--- | :--- |
| `volunteer/dashboard/page.tsx` | Present (Skeleton) | Present (Banner) | Present | Robust async state machine. |
| `recommended-events-section.tsx` | **Missing** | **Missing** | Replaced with Mock Data | Prop `isLoading` is accepted but unused; renders mock data instead of empty state. |
| `volunteer/activity/page.tsx` | **Missing** | **Missing** | Present | Flashes empty state while fetching; network errors are silently ignored. |
| `volunteer/leaderboard/page.tsx` | Present (Skeleton) | Present (Banner) | Present | Good state management. |
| `volunteer/profile/page.tsx` | Present (Spinner) | **Masked** (Bug) | N/A | Non-ApiError exceptions are caught and reported as successful saves. |
| `admin/applications/page.tsx` | Present (Table skeleton) | Present (Banner) | Present | Complete operational state handling. |
| `admin/reports/page.tsx` | **Missing** | **Missing** | **Missing** | Renders static hardcoded figures instantly without loading indicators. |

---

## 6. Detailed Frontend Issue Log

### ISSUE-FE-001 [P1 - High]
- **Route/File:** `web/src/components/volunteer/dashboard/recommended-events-section.tsx` (Lines 55–58)
- **Description:** Real backend events are discarded in favor of mock drives when fewer than two events are available.
- **Evidence:**
  ```tsx
  const drivesToRender = events.length >= 2 ? events.slice(0, 2) : fallbackDrives;
  ```
- **Impact:** A newly created, legitimate volunteering event cannot be recommended on the volunteer dashboard if it is the only published event in the system.
- **Recommendation:** Refactor logic to render available events regardless of count, and show an empty/invitation card when count is 0:
  ```tsx
  const drivesToRender = events.slice(0, 2);
  ```

---

### ISSUE-FE-002 [P1 - High]
- **Route/File:** `web/src/app/volunteer/activity/page.tsx` (Lines 28–46)
- **Description:** Activity page lacks loading and error states, flashing empty state during data retrieval and suppressing errors.
- **Evidence:**
  ```tsx
  useEffect(() => {
    async function loadData() {
      try {
        const history = await getAttendanceHistory();
        setLogs(history);
      } catch (err) {
        console.error("Failed to load activity", err);
      }
    }
    loadData();
  }, []);
  ```
- **Impact:** When a user navigates to "My Volunteering", the screen immediately renders "No volunteering activity yet" for 1–2 seconds before populating with records. If the request fails, the user is permanently shown that they have 0 hours and 0 attended events.
- **Recommendation:** Add explicit `isLoading` and `error` state variables. Render skeleton cards while loading and an error retry banner on failure.

---

### ISSUE-FE-003 [P2 - Medium]
- **Route/File:** `web/src/lib/api-client.ts` (Lines 68–95)
- **Description:** API client does not specify a request timeout.
- **Evidence:**
  ```tsx
  const res = await fetch(url, {
    ...options,
    headers,
  });
  ```
- **Impact:** Slow or hanging network connections cause indefinite loading spinners on submit buttons, preventing the user from retrying or recovering.
- **Recommendation:** Introduce `AbortSignal.timeout(15000)` (15 seconds) or configurable timeout controller for all API fetch calls.

---

### ISSUE-FE-004 [P2 - Medium]
- **Route/File:** `web/src/app/admin/reports/page.tsx` (Lines 125–138)
- **Description:** Volunteer hours graph and impact metrics are hardcoded rather than fetched from backend reporting endpoints.
- **Evidence:** `monthlyHours = [250, 320, 410, 500, ...]`; donut chart percentages hardcoded to `62%`, `26%`, `12%`.
- **Impact:** Administrators cannot rely on the Reports view for actual organizational impact evaluation.
- **Recommendation:** Connect `reports/page.tsx` to `GET /api/v1/gamification/analytics` and `GET /api/v1/attendance/summary` endpoints implemented in Phase 11 & Phase 12.

---

## 7. Frontend Code Quality Summary

| Metric | Status | Finding |
| :--- | :--- | :--- |
| **TypeScript Type Safety** | **Verified** | 0 build errors with strict mode enabled. |
| **ESLint Hygiene** | **Warnings Only** | 122 warnings; 46 hook dependencies need memoization. |
| **Backend Contract Alignment** | **Good** | Types match Pydantic schemas; missing AuditLog DTO. |
| **Mock Data Separation** | **Deficient** | Mock fallbacks pollute production catalogs and dashboard views. |
| **Async Resilience** | **Needs Improvement** | Lacks fetch timeouts; silent catch blocks present in activity & profile. |
