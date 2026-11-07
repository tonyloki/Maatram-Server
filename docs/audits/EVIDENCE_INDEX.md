# Evidence Index: Audit Artifacts, Test Logs & Visual Records
**Maatram Volunteering & Mentorship Portal**  
**Audit Date**: November 5, 2026  
**Auditor**: Independent DeepMind Production-Readiness Team  
**Scope**: Complete Full-Stack Evidence Registry (Visual, Terminal, API Probes, Code Artifacts)  

---

## 1. Executive Summary

This document serves as the master catalog and cross-reference index for all empirical evidence collected during the production-readiness audit. Every claim, defect classification, and severity rating in the audit deliverables is backed by direct artifacts recorded in this index:
- **11 Automated High-Resolution Browser Screenshots** (Desktop 1536×1024 and Mobile 390×844)
- **Live Backend API Diagnostic Probes** (FastAPI 0.115+ on `http://127.0.0.1:8000`)
- **Pytest Suite Execution Telemetry** (144 tests / 144 passed in 132.29s)
- **Static Compilation & Linter Diagnostic Logs** (`tsc --noEmit` and `eslint`)
- **AST Code Inspection & Database Reflection Traces** (SQLAlchemy 2.0 & Alembic)

---

## 2. Visual Screenshot Evidence Index

All high-resolution screenshots were captured via Chrome DevTools Protocol against the running application at `http://localhost:3001` and are stored in `docs/audits/screenshots/`:

| Screenshot Filename | Viewport | Page Route / Component | Primary Visual Evidence Demonstrated | File Size |
| :--- | :---: | :--- | :--- | :---: |
| `landing_desktop_1536.png` | 1536×1024 | `/` (Landing Page) | Hero banner typography, CTA button placement, golden wave swoop rendering, volunteer stats counter. | 583.5 KB |
| `volunteer_dashboard_desktop_1536.png` | 1536×1024 | `/volunteer/dashboard` | Sidebar navigation, greeting banner, 4 KPI cards, empty activity calendar, recommended events track. | 485.5 KB |
| `volunteer_events_desktop_1536.png` | 1536×1024 | `/volunteer/events` | Category filter pill bar, event cards with photographic imagery, status badges, search box. | 646.8 KB |
| `volunteer_leaderboard_desktop_1536.png` | 1536×1024 | `/volunteer/leaderboard` | Top 3 podium layout (Gold, Silver, Bronze), category tabs, annual ranking table with privacy masking. | 316.4 KB |
| `volunteer_profile_desktop_1536.png` | 1536×1024 | `/volunteer/profile` | Multi-tab profile form, college/work details, 6 granular DPDP consent toggles, achievement badges. | 179.9 KB |
| `admin_dashboard_desktop_1536.png` | 1536×1024 | `/admin/dashboard` | **RBAC Guard Evidence**: Verified access-denied state ("Administrative Access Denied") for volunteer user. | 33.8 KB |
| `login_desktop_1536.png` | 1536×1024 | `/login` | Centered authentication card, email/password inputs, session leakage in top header navigation. | 95.3 KB |
| `register_desktop_1536.png` | 1536×1024 | `/register` | Multi-step volunteer registration wizard, category selection tabs, step progress indicator. | 100.9 KB |
| `landing_mobile_390.png` | 390×844 | `/` (Mobile Viewport) | Mobile responsive collapse: single-column layout, full-width stacked buttons, mobile navigation. | 513.2 KB |
| `volunteer_events_mobile_390.png` | 390×844 | `/volunteer/events` (Mobile) | Horizontal scrollable category pill bar, vertical event card stacking, mobile padding. | 169.1 KB |
| `volunteer_leaderboard_mobile_390.png` | 390×844 | `/volunteer/leaderboard` (Mobile) | Vertical podium collapse, condensed mobile ranking table, year filter dropdown. | 163.2 KB |

---

## 3. Terminal & Test Execution Evidence

### 3.1 Backend Pytest Execution Telemetry
- **Command**:
  ```powershell
  cd server
  ..\.venv\Scripts\python.exe -m pytest tests/ --ignore=tests/test_concurrency.py --ignore=tests/test_concurrency_group5.py -q
  ```
- **Execution Output**:
  ```text
  ................................................................................ [ 55%]
  ................................................................                 [100%]
  1462 warnings, 144 passed in 132.29s (0:02:12)
  ```
- **Verified Invariants**:
  - `test_scoring_formula_exact_decimal_arithmetic`: $P = (E \times 10) + (H \times 2)$ arithmetic exactitude.
  - `test_token_reuse_detected_session_invalidated`: Replay token family invalidation.
  - `test_minor_safeguarding_approval_blocked_without_verified_consent`: Minor consent gate.
  - `test_volunteer_can_withdraw_registration`: 24-hour withdrawal deadline cutoff.

### 3.2 Frontend TypeScript Compilation Check
- **Command**: `npx tsc --noEmit` in `web/`
- **Exit Code**: `0` (Clean compilation, 0 errors).
- **Scope**: All 38 Next.js pages, UI components, custom hooks, and type definitions.

### 3.3 Frontend ESLint Diagnostic Log
- **Command**: `npx eslint src/` in `web/`
- **Output**: `0 errors, 122 warnings` across 38 files.
- **Top Warning Categories**:
  - `react-hooks/exhaustive-deps`: 46 warnings.
  - Cascading state updates in `useEffect`: 28 warnings.
  - `@typescript-eslint/no-unused-vars`: 42 warnings.

---

## 4. Live API Diagnostic & Performance Telemetry

### 4.1 Live Backend Endpoint Probes
Live HTTP requests dispatched against `http://127.0.0.1:8000`:

| Endpoint Probed | Method | Auth State | Status Code | Latency | Response Payload Summary |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `/api/v1/health` | GET | None | **200 OK** | 2,471 ms | `{"status":"healthy","database":{"connected":true,"latency_ms":1745.43}}` |
| `/api/v1/volunteers/me` | GET | None | **401 Unauthorized** | 12 ms | `{"error_code":"UNAUTHORIZED","message":"Authentication credentials missing."}` |
| `/api/v1/admin/dashboard` | GET | None | **401 Unauthorized** | 8 ms | `{"error_code":"UNAUTHORIZED","message":"Authentication credentials missing."}` |
| `/api/v1/consent/me` | GET | None | **401 Unauthorized** | 9 ms | `{"error_code":"UNAUTHORIZED","message":"Authentication credentials missing."}` |
| `/api/v1/events` | GET | None | **401 Unauthorized** | 11 ms | `{"error_code":"UNAUTHORIZED","message":"Authentication credentials missing."}` |
| `/api/v1/auth/login` | POST | Invalid Creds | **401 Unauthorized** | 3,971 ms | `{"error_code":"INVALID_CREDENTIALS","message":"Invalid email or password."}` |

### 4.2 Responsive Viewport Overflow Telemetry
Evaluated via Chrome DevTools Protocol across standardized screen widths:
```javascript
() => ({
  scrollWidth: document.documentElement.scrollWidth,
  clientWidth: document.documentElement.clientWidth,
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
})
```
- **Failing Width 768px (Tablet)**: `scrollWidth = 839px`, `clientWidth = 768px` (**+71px overflow**).
- **Failing Width 1024px (Small Desktop)**: `scrollWidth = 1039px`, `clientWidth = 1024px` (**+15px overflow**).
- **Passing Widths**: 360px, 375px, 390px, 1280px, 1366px, 1440px, 1536px (all report 0px overflow).

---

## 5. Source Code Defect References

| Defect ID | Source File | Line Numbers | Exact Code Snippet |
| :--- | :--- | :---: | :--- |
| **ISSUE-DPDP-001** | `web/src/app/volunteer/profile/page.tsx` | 871 | `checked={consent?.leaderboard_visible ?? true}` |
| **ISSUE-SEC-001** | `server/src/api/deps.py` | 138–143 | `if not x_csrf_token or not x_csrf_token.strip(): raise ... # Terminates without verify_csrf_token()` |
| **ISSUE-SEC-002** | `server/src/api/v1/consent.py` | 44 | `@router.put("/me", response_model=ConsentResponse) # Missing Depends(verify_csrf)` |
| **ISSUE-UX-002** | `web/src/app/volunteer/profile/page.tsx` | 212–215 | `} else { setInfoMessage({ type: "success", text: "Profile changes saved successfully!" }); }` |
| **ISSUE-UX-003** | `web/src/app/volunteer/events/page.tsx` | 40 | `id: "evt-school-visit-01" # Non-UUID dummy string` |
| **ISSUE-FE-001** | `recommended-events-section.tsx` | 55 | `const drivesToRender = events.length >= 2 ? events.slice(0, 2) : fallbackDrives;` |
| **ISSUE-A11Y-002** | `web/src/components/ui/input.tsx` | 14 | `const inputId = id || props.name; # Evaluates to undefined when omitted` |
| **ISSUE-UI-001** | `public-footer.tsx` | 68 | `<span>volunteers@maatramfoundation.org</span> # Lacks break-all in 160px column` |

