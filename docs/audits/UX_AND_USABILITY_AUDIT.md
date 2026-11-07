# UX & Usability Audit
**Maatram Volunteering & Mentorship Portal — Web Client**
**Audit Date:** November 2026  
**Auditor:** Independent Production Readiness Audit Subagent  
**Evaluation Framework:** Nielsen Norman Group (NN/g) 10 Usability Heuristics & User Journey Assessment

---

## 1. Executive Summary

This usability audit evaluates the core user journeys of the Maatram Portal across both volunteer and administrative roles. The audit focuses on system status visibility, error prevention, heuristic alignment, and DPDP compliance.

### Overall Score: **68 / 100** (Needs Remediation Before Public Release)
- **Strengths:** Clean visual aesthetic, logical task flows, clear multi-step progression in registration, and comprehensive admin review controls.
- **Critical Vulnerabilities:**
  - **DPDP Consent Defaults (P0/Legal):** Consents default to `true` (opt-out) rather than `false` (opt-in) on initial load when null.
  - **Exception Masking as Success (P1):** Failed network/client requests in profile update report false positive "Profile changes saved successfully!"
  - **Broken Mock Navigation (P1):** Clicking fallback event cards navigates to invalid string-based IDs (`evt-school-visit-01`) triggering 422/404 API crashes.
  - **Fabricated Data & Gamification Transparency (P2):** Gamification formula is not displayed, leaderboard trends are fabricated by list index, and default year is hardcoded to 2025.

---

## 2. User Journey Deep-Dive Evaluations

### Journey A: New Visitor Landing & Discovery (`web/src/app/page.tsx`)
- **Mission Clarity:** Excellent. The hero banner clearly articulates Maatram's dual mission of educational mentorship and community transformation.
- **Category Differentiation:** Clear visual cards differentiating "General Volunteers" and "Student Volunteers" with eligibility requirements.
- **CTA Usability:** Dual CTAs ("Register as Volunteer" and "Sign In") are prominently placed.
- **Defects Identified:**
  - Line 188: A nested `<button>` is placed inside a Next.js `<Link>` component (`<Link href="/register"><Button>...</Button></Link>`), causing HTML invalid nesting warnings and accessibility tree confusion.
  - Color contrast on the hero badge violates WCAG AA standards (detailed in Accessibility Audit).

### Journey B: Volunteer Registration (`web/src/app/register/page.tsx`)
- **Form Progression:** Structured as a 3-step wizard:
  - Step 1: Category selection (General Volunteer vs Student Volunteer).
  - Step 2: Personal, educational, and institutional details (College, Degree, Year of Study, Student ID Proof).
  - Step 3: Password creation and initial DPDP data consent.
- **Validation & Recovery:**
  - Client-side validation triggers on step transitions.
  - **Usability Gap:** If a user navigates backward from Step 3 to Step 1, category-specific fields may clear or trigger stale validation errors.
  - **Error Linking:** Errors appear below inputs, but focus is not programmatically moved to the first invalid field upon submission failure.

### Journey C: Event Discovery & Registration (`web/src/app/volunteer/events/`)
- **Discovery Experience:** Volunteers can search by keyword, filter by category (`EDUCATION`, `ENVIRONMENT`, `HEALTH`, etc.), and toggle between upcoming and past drives.
- **Event Details:** `[id]/page.tsx` provides rich operational context (Venue address, time in IST, required skills badges, capacity status).
- **Critical Defect (P1):**
  - In `events/page.tsx` lines 38–87, fallback constant `DEFAULT_EVENTS` specifies string IDs such as `evt-school-visit-01`.
  - When backend returns empty or network fails, clicking a fallback card attempts to fetch `/api/v1/events/evt-school-visit-01`. The backend expects a UUID, immediately returning a 422 Unprocessable Entity or 404 Not Found error dialog.
  - In `recommended-events-section.tsx` lines 20–47, if fewer than 2 real events exist, the application completely discards real data and renders mock cards with non-existent IDs.

### Journey D: Admin Operational Workflows (`web/src/app/admin/`)
- **Application Review:** `applications/page.tsx` and `applications/[id]/page.tsx` provide complete operational controls: viewing student proof documents, inspecting volunteer profile details, and providing mandatory review notes for rejection or approval.
- **Attendance & Operations:**
  - Attendance check-in features both live QR scanning and manual search.
  - Operations dashboard provides full DLQ retry monitoring.
- **Usability Gap:**
  - In `web/src/app/admin/operations/page.tsx` line 69, manual DLQ retries trigger raw browser `alert()` popups instead of inline toast notifications.
  - `web/src/app/admin/reports/page.tsx` displays hardcoded volunteer hours and static distribution donuts (62%, 26%, 12%) regardless of actual database activity.

### Journey E: Profile & Consent Management (`web/src/app/volunteer/profile/page.tsx`)
- **Consent Hierarchy:** Presents all 6 granular DPDP consent toggles:
  1. Public leaderboard ranking visibility
  2. Public display of real full name on achievements
  3. Skill and professional background matching
  4. Marketing and event broadcast communications
  5. Cross-drive attendance analytics sharing
  6. Emergency institutional contact disclosures
- **Critical Defect (P0 / Legal Compliance):**
  - Lines 871, 921, 946, 971, 996 contain default fallbacks using nullish coalescing to `true`:
    ```tsx
    checked={consent?.leaderboard_visible ?? true}
    checked={consent?.show_full_name ?? true}
    checked={consent?.skills_matching ?? true}
    checked={consent?.marketing_emails ?? true}
    checked={consent?.analytics_sharing ?? true}
    ```
  - **DPDP Act 2023 Section 6(1)** strictly mandates that consent must be freely given, specific, informed, unconditional, and **unambiguous with affirmative action**. Defaulting consent to `true` violates the statutory opt-in principle.
- **Exception Masking (P1):**
  - In lines 212–215:
    ```tsx
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setInfoMessage({ type: "error", text: err.detail || "Failed to update profile." });
      } else {
        // BUG: Non-ApiError masks runtime failure as SUCCESS
        setInfoMessage({ type: "success", text: "Profile changes saved successfully!" });
      }
    }
    ```
    If a `TypeError`, JSON parsing error, or network drop occurs, the UI informs the volunteer that their changes were successfully saved when nothing was persisted!

### Journey F: Leaderboard & Gamification Transparency (`web/src/app/volunteer/leaderboard/page.tsx`)
- **Year Selection:**
  - Line 25 defaults the year filter to `2025`:
    ```tsx
    const [selectedYear, setSelectedYear] = useState<number>(2025);
    ```
    In production year 2026, opening the leaderboard defaults to historical archived data rather than active current year standings.
- **Gamification Formula Missing:**
  - Phase 08 specifies the canonical gamification formula:
    $$Points = (Events \times 10) + (Hours \times 2)$$
    This formula is nowhere to be found in the leaderboard or profile UI. Volunteers have no visibility into how their points or tier rankings are calculated.
- **Fabricated Visual Data:**
  - Line 93:
    ```tsx
    trend={idx === 0 || idx === 3 ? "up" : idx === 1 || idx === 4 ? "down" : "same"}
    ```
    The rank movement trend ("up", "down", "same") is completely fabricated using the modulo of the array index rather than computed from historical audit snapshots.

---

## 3. Detailed NN/g Heuristic Violations

### ISSUE-UX-001 [P0 - Critical / Legal]
- **Route/File:** `web/src/app/volunteer/profile/page.tsx` (Lines 871, 921, 946, 971, 996)
- **Heuristic:** *Error Prevention (Heuristic #5)* & *User Control and Freedom (Heuristic #3)*
- **Description:** Consent preferences default to `true` (opt-out) when no consent record exists in database.
- **Evidence:**
  ```tsx
  <Switch
    checked={consent?.leaderboard_visible ?? true}
    onCheckedChange={(checked) => handleConsentToggle("leaderboard_visible", checked)}
  />
  ```
- **Impact:** Violates India's Digital Personal Data Protection (DPDP) Act 2023, exposing the organization to statutory non-compliance penalties.
- **Recommendation:** Change all default fallbacks from `?? true` to `?? false`. Ensure initial database migrations initialize consent records to `false`.

---

### ISSUE-UX-002 [P1 - High]
- **Route/File:** `web/src/app/volunteer/profile/page.tsx` (Lines 212–215)
- **Heuristic:** *Visibility of System Status (Heuristic #1)* & *Error Recovery (Heuristic #9)*
- **Description:** Non-ApiError exceptions (e.g., fetch failures, serialization bugs) in profile saving are trapped and displayed as successful saves.
- **Evidence:**
  ```tsx
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      setInfoMessage({ type: "error", text: err.detail || "Failed to update profile." });
    } else {
      setInfoMessage({ type: "success", text: "Profile changes saved successfully!" });
    }
  }
  ```
- **Impact:** Volunteers make critical changes (updating phone numbers, emergency contact, or college affiliation), encounter a network error, see a green success notification, and leave the page believing their data was saved.
- **Recommendation:** Replace the `else` block with an error state:
  ```tsx
  } else {
    setInfoMessage({ type: "error", text: "An unexpected error occurred. Please try again." });
  }
  ```

---

### ISSUE-UX-003 [P1 - High]
- **Route/File:** `web/src/app/volunteer/events/page.tsx` (Lines 38–87) and `web/src/components/volunteer/dashboard/recommended-events-section.tsx` (Lines 20–47)
- **Heuristic:** *Consistency and Standards (Heuristic #4)* & *Error Prevention (Heuristic #5)*
- **Description:** Mock event fallbacks use non-UUID dummy IDs that crash the application when clicked.
- **Evidence:**
  ```tsx
  const DEFAULT_EVENTS: VolunteerEvent[] = [
    {
      id: "evt-school-visit-01",
      title: "Government Higher Secondary School Visit",
      ...
    }
  ];
  ```
  Navigating to `/volunteer/events/evt-school-visit-01` invokes `GET /api/v1/events/evt-school-visit-01`. The FastAPI backend expects a UUID v7/v4 path parameter and returns HTTP 422 (`value is not a valid uuid`).
- **Impact:** Any user experiencing network latency or viewing the app when zero events exist is presented with unclickable, broken cards that lead to error screens.
- **Recommendation:** Remove mock fallback objects entirely. Display an authentic empty state ("No upcoming events scheduled at this time") with a refresh button.

---

### ISSUE-UX-004 [P2 - Medium]
- **Route/File:** `web/src/app/volunteer/leaderboard/page.tsx` (Lines 25, 93)
- **Heuristic:** *Recognition rather than Recall (Heuristic #6)* & *Visibility of System Status (Heuristic #1)*
- **Description:** Leaderboard defaults to year 2025, displays fabricated ranking trends, and fails to display the gamification scoring formula.
- **Evidence:**
  1. Year default: `const [selectedYear, setSelectedYear] = useState<number>(2025);`
  2. Trend computation: `trend={idx === 0 || idx === 3 ? "up" : idx === 1 || idx === 4 ? "down" : "same"}`
  3. Formula missing: Search for `formula`, `hours * 2`, or `events * 10` in `web/src/app/volunteer/leaderboard/` yields 0 results.
- **Impact:** Misleads volunteers with fabricated rank momentum and conceals how tier promotion criteria operate.
- **Recommendation:**
  1. Default `selectedYear` to `new Date().getFullYear()`.
  2. Either implement genuine trend tracking in backend `leaderboard_snapshots` or omit the trend indicator icon.
  3. Add an explanatory Gamification Info card in the leaderboard sidebar explaining the $P = 10E + 2H$ formula and tier cutoffs (Bronze: 0, Silver: 100, Gold: 300, Platinum: 600).

---

### ISSUE-UX-005 [P2 - Medium]
- **Route/File:** `web/src/app/admin/operations/page.tsx` (Line 69) and `web/src/app/volunteer/profile/page.tsx` (Line 174)
- **Heuristic:** *Aesthetic and Minimalist Design (Heuristic #8)* & *Flexibility and Efficiency of Use (Heuristic #7)*
- **Description:** Modal dialogs are bypassed in favor of native, blocking browser `alert()` dialogs.
- **Evidence:**
  `operations/page.tsx:69`:
  ```tsx
  alert(`Retry triggered: ${result.message || "Operation successful"}`);
  ```
  `profile/page.tsx:174`:
  ```tsx
  alert("File size must be under 5MB");
  ```
- **Impact:** Native alerts freeze the browser execution thread, look jarring, and degrade brand credibility.
- **Recommendation:** Integrate a modern, accessible toast notification provider (e.g., `sonner` or Radix UI Toast).

---

## 4. Usability Audit Summary Matrix

| Issue ID | Severity | Heuristic Violated | Affected File | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-UX-001** | **P0** | #5 Error Prevention / #3 Freedom | `web/src/app/volunteer/profile/page.tsx` | Open |
| **ISSUE-UX-002** | **P1** | #1 System Status / #9 Error Recovery | `web/src/app/volunteer/profile/page.tsx` | Open |
| **ISSUE-UX-003** | **P1** | #4 Consistency / #5 Error Prevention | `web/src/app/volunteer/events/page.tsx` | Open |
| **ISSUE-UX-004** | **P2** | #1 System Status / #6 Recognition | `web/src/app/volunteer/leaderboard/page.tsx` | Open |
| **ISSUE-UX-005** | **P2** | #8 Minimalist Design | `web/src/app/admin/operations/page.tsx` | Open |
| **ISSUE-UX-006** | **P3** | #4 Consistency & Standards | `web/src/app/page.tsx` (nested button in link) | Open |
