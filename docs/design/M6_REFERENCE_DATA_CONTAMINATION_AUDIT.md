# M6 REFERENCE DATA CONTAMINATION AUDIT & REMEDIATION REPORT
**Maatram Volunteering & Gamification Portal**
**Document ID:** `M6_REFERENCE_DATA_CONTAMINATION_AUDIT`  
**Execution Date:** 2026-11-04  
**Status:** AUDIT COMPLETE & REMEDIATION IN PROGRESS  

---

## 1. Executive Summary & Directive Mandate

The design references (`ui-Reference/*.jpeg`) are purely visual layout and composition guides. The fictional individuals, profile portraits, names (e.g. Priya S., Arun K., Sneha R., Karthik V., Meena L.), and sample metrics depicted in them are **illustrative examples only**.

This audit identifies all locations across the frontend, backend, test suites, and asset directories where reference characters or hardcoded mock data were introduced. A zero-tolerance policy is enforced:
1. **No Fictional Personas as Real Users**: No reference character may be hardcoded into dashboards, profiles, leaderboards, or greetings.
2. **Dynamic Identity Binding**: All user information (names, emails, hours, points, roles) must be derived dynamically from the authenticated user session and canonical PostgreSQL database records.
3. **Empty State Fidelity**: If the backend returns empty or zero records, the UI must render an intentional, polished empty state rather than fabricating fictional records to fill the screen.
4. **Deterministic Initials Avatars**: Avatars must display the volunteer's actual uploaded profile photo (when permitted by affirmative consent). In the absence of an uploaded photo, the system must render a deterministic initials-based vector avatar. No synthetic or screenshot-cropped faces may ever be used.

---

## 2. Complete Contamination Inventory & Classification

| Component / File Path | Finding Description | Classification | Risk & Impact | Remediation Action |
| :--- | :--- | :--- | :--- | :--- |
| `web/src/app/volunteer/leaderboard/page.tsx` | `DEFAULT_ROWS` array with hardcoded Priya S. (580 pts), Arun K. (520 pts), Sneha R. (460 pts), Karthik V., Meena L. | **HARDCODED_FRONTEND_MOCK** | High: Displays fictional volunteers on podium when DB has 0 rows. | **PURGE.** Remove `DEFAULT_ROWS`. Render empty-state podium when 0 records exist. |
| `web/src/app/volunteer/leaderboard/page.tsx` | Hardcoded `item.volunteer_name.toLowerCase().includes("priya")` for `isYou` check. | **REFERENCE_DERIVED_SAMPLE** | High: Erroneously marks any user named Priya as the logged-in user. | **PURGE.** Replace with strict check: `currentVolunteer && item.volunteer_profile_id === currentVolunteer.id`. |
| `web/src/app/volunteer/leaderboard/page.tsx` | Hardcoded avatar paths `priya-leaderboard-avatar.jpg`, `arun-avatar.jpg`, `sneha-avatar.jpg`. | **REFERENCE_DERIVED_SAMPLE** | High: Displays synthetic faces instead of initials or permitted photos. | **PURGE.** Replace with deterministic initials-based `<Avatar />` component. |
| `web/src/app/volunteer/profile/page.tsx` | Initial state hooks hardcoded to `"Priya"`, `"S."`, `"+91 9876543210"`, `"Sathyabama..."`. | **HARDCODED_FRONTEND_MOCK** | High: Overwrites real user identity with reference mock if API fetch is pending. | **PURGE.** Initialize state hooks from authenticated user & profile response. |
| `web/src/app/volunteer/profile/page.tsx` | Hardcoded email `priya.s@maatram.org` and phone `+91 9876543210` in sidebar identity card. | **HARDCODED_FRONTEND_MOCK** | High: Exposes fictional email instead of real authenticated volunteer email. | **PURGE.** Replace with dynamic `user.email` and `profile.phone`. |
| `web/src/app/volunteer/profile/page.tsx` | Hardcoded `<Image src="/assets/maatram/photography/priya-avatar.jpg" />`. | **REFERENCE_DERIVED_SAMPLE** | High: Displays reference face instead of authenticated user's avatar. | **PURGE.** Render deterministic initials avatar or uploaded photo. |
| `web/src/app/register/page.tsx` | Form placeholders `placeholder="Priya"`, `placeholder="priya@example.com"`, `placeholder="Sathyabama..."`. | **REFERENCE_DERIVED_SAMPLE** | Low: Minor UX hint bias mimicking reference screenshot. | **REPLACE.** Use generic placeholders (`"First Name"`, `"volunteer@example.com"`, `"University Name"`). |
| `web/public/assets/maatram/photography/` | Avatar files: `priya-avatar.jpg`, `priya-leaderboard-avatar.jpg`, `arun-avatar.jpg`, `sneha-avatar.jpg`. | **REFERENCE_DERIVED_SAMPLE** | High: Synthetic character portraits imitating reference images. | **DELETE.** Permanently purge all 4 avatar files from the asset directory. |
| `server/tests/test_*.py` | Test cases registering test users named "Priya Rajan", "Arun", "Karthik". | **APPROVED_DEV_FIXTURE** | None: Isolated SQLite in-memory test fixtures executing during CI/Pytest runs. | **MAINTAIN.** Retain as valid test fixtures. Does not affect production DB. |
| `server/src/schemas/auth.py` | Error message example: `"Mobile number must be in valid international format (e.g. +919876543210)"`. | **APPROVED_DEV_FIXTURE** | None: Standard Pydantic regex documentation example. | **MAINTAIN.** Standard format documentation. |

---

## 3. Detailed Remediation Plan

### A. Leaderboard (`/volunteer/leaderboard`)
1. Delete `DEFAULT_ROWS` entirely.
2. If `leaderboardData?.items` is empty (`length === 0`):
   - Render a dedicated, polished empty state:
     - Golden trophy icon in warm amber circle
     - Title: **"No volunteers on this leaderboard yet"**
     - Subtitle: *"Service hours and points will appear here once volunteer activities are completed and verified for {year}."*
3. If `leaderboardData?.items` has records:
   - Render only actual eligible volunteers from the canonical PostgreSQL database.
   - For avatars: render deterministic initials `<Avatar fallback={item.volunteer_name} />` with unique pastel background hashing.
   - For `isYou`: check `currentVolunteer && item.volunteer_profile_id === currentVolunteer.id`.

### B. Volunteer Profile (`/volunteer/profile`)
1. Remove all hardcoded default state values (`"Priya"`, `"S."`, `"+91 9876543210"`, `"Sathyabama..."`, `"priya.s@maatram.org"`).
2. Bind state directly to the authenticated user from `useAuth()` and `/volunteers/me`.
3. Avatar display:
   - If `profile?.avatar_url` is present AND affirmative consent `consent?.share_profile_photo` is true, render their uploaded image.
   - Otherwise, render deterministic initials inside a golden ring.
4. Replace all contact and academic fields with actual backend data or `"Not specified"` when empty.

### C. Registration Form Placeholders (`/register`)
1. Replace `placeholder="Priya"` with `placeholder="First Name"`.
2. Replace `placeholder="priya@example.com"` with `placeholder="volunteer@example.com"`.
3. Replace `placeholder="Sathyabama Institute..."` with `placeholder="College / University Name"`.

### D. Asset Purge
1. Delete all synthetic avatar images:
   - `web/public/assets/maatram/photography/priya-avatar.jpg`
   - `web/public/assets/maatram/photography/priya-leaderboard-avatar.jpg`
   - `web/public/assets/maatram/photography/arun-avatar.jpg`
   - `web/public/assets/maatram/photography/sneha-avatar.jpg`

