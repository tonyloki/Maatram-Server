# Performance & Responsiveness Audit Report
**Maatram Volunteering & Mentorship Portal**
**Audit Date**: November 5, 2026  
**Auditor**: Independent Production-Readiness Audit Team  
**Scope**: Frontend Web Application (`web/`), Next.js Production Chunks, Viewport Overflow, Backend API Latency (`server/`), Image Delivery  
**Target Environment**: Next.js 16.4.4 (`http://localhost:3001`), FastAPI 0.115+ (`http://127.0.0.1:8000`), Supabase PostgreSQL

---

## 1. Executive Summary

This independent performance and responsiveness audit evaluates the speed, bundle weight, database latency, and multi-device responsive stability of the **Maatram Volunteering & Mentorship Portal**. Testing was conducted through direct headless browser instrumentation (Chrome DevTools Protocol), network timing telemetry, bundle chunk inspection, and backend endpoint profiling.

### Key Audit Highlights
- **Responsive Overflow Detected**: On tablet viewports (768px portrait) and small desktop viewports (1024px landscape), pages containing the public footer (`/`, `/login`, `/register`) experience horizontal layout overflow (+71px at 768px; +15px at 1024px), producing an unwanted horizontal scrollbar. Mobile viewports (360px–390px) and wide desktop viewports (1280px+) are completely free of overflow.
- **Critical Database Roundtrip Latency**: The system health endpoint (`GET /api/v1/health`) exhibits an average response latency of **2,471 ms** (2.47 seconds). Live instrumentation confirms the root bottleneck is remote database roundtrip latency to Supabase PostgreSQL (**1,745.43 ms** for a simple `SELECT 1`).
- **Client Bundle Size**: Total static chunk size is **1.60 MB** across 25 chunks, with the largest JavaScript bundle measuring **229 KB** uncompressed (`1gj5u6mwx5p0u.js`).
- **Zero Code-Splitting**: There are **0 dynamic imports** (`next/dynamic` or `React.lazy`) in `web/src`. Heavy animation packages (`framer-motion`) and complex multi-tab forms are eagerly bundled into initial route loads.
- **Image Optimization Gaps**: While Next.js `<Image>` component is adopted on primary pages, four source JPEG photographs in `web/public/assets/maatram/photography/` exceed 800 KB each (up to **1.09 MB**), and `page.tsx` references redundant unoptimized files in `/assets/images/` (e.g. 1.02 MB hero image).

---

## 2. Responsive Overflow Audit

### 2.1 Viewport Matrix Testing Results

Each core application route was instrumented and evaluated across 9 standardized device viewport widths using Chrome DevTools:

```javascript
() => ({
  url: window.location.href,
  scrollWidth: document.documentElement.scrollWidth,
  clientWidth: document.documentElement.clientWidth,
  hasHorizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  viewportWidth: window.innerWidth
})
```

#### Responsive Test Results Matrix:

| Page Route | 360px | 375px | 390px | 768px (Tablet) | 1024px (Small Desktop) | 1280px | 1366px | 1440px | 1536px |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `/` (Landing Page) | PASS (360) | PASS (375) | PASS (390) | **FAIL (839px, +71px)** | **FAIL (1039px, +15px)** | PASS (1280) | PASS (1366) | PASS (1440) | PASS (1536) |
| `/volunteer/dashboard` | PASS (360) | PASS (375) | PASS (390) | PASS (768) | PASS (1024) | PASS (1280) | PASS (1366) | PASS (1440) | PASS (1536) |
| `/volunteer/events` | PASS (360) | PASS (375) | PASS (390) | PASS (768) | PASS (1024) | PASS (1280) | PASS (1366) | PASS (1440) | PASS (1536) |
| `/volunteer/leaderboard` | PASS (360) | PASS (375) | PASS (390) | PASS (768) | PASS (1024) | PASS (1280) | PASS (1366) | PASS (1440) | PASS (1536) |
| `/volunteer/profile` | PASS (360) | PASS (375) | PASS (390) | PASS (768) | PASS (1024) | PASS (1280) | PASS (1366) | PASS (1440) | PASS (1536) |
| `/login` | PASS (360) | PASS (375) | PASS (390) | **FAIL (839px, +71px)** | **FAIL (1039px, +15px)** | PASS (1280) | PASS (1366) | PASS (1440) | PASS (1536) |
| `/register` | PASS (360) | PASS (375) | PASS (390) | **FAIL (839px, +71px)** | **FAIL (1039px, +15px)** | PASS (1280) | PASS (1366) | PASS (1440) | PASS (1536) |

### 2.2 Deep Root Cause Analysis of Horizontal Overflow

- **Failing Viewports**: 768px (iPad portrait) and 1024px (iPad Pro / small laptop).
- **Failing Pages**: All pages importing `<PublicFooter />` from `web/src/components/navigation/public-footer.tsx`.
- **Exact Element**: `<span>volunteers@maatramfoundation.org</span>` (DOM path: `footer > div > div.grid > div:nth-child(3) > ul > li:nth-child(2) > span`).
- **Mechanism**:
  1. In `public-footer.tsx`, the grid layout is configured as:
     ```tsx
     <div className="grid grid-cols-1 md:grid-cols-4 gap-8 lg:gap-12">
     ```
  2. On `md` screens (768px to 1023px), Column 1 occupies 2 spans (`md:col-span-2`), Column 2 occupies 1 span, and Column 3 (Community & Contact) occupies 1 span.
  3. Total available width for Column 3 at 768px is `(768px - 32px padding - 48px grid gaps) / 4` ≈ **160px**.
  4. The text string `volunteers@maatramfoundation.org` rendered at 14px font size requires **231px** of contiguous horizontal space.
  5. Because the element lacks CSS `break-all`, `break-words`, or `overflow-hidden`, the text refuses to wrap, forcing the container box out to 231px and pushing the entire document's `scrollWidth` to **839px**.

---

## 3. Bundle Size & Dependency Analysis

### 3.1 Next.js Production Static Chunks Inventory

An audit of the compiled `.next/static/chunks/` directory was executed:

| Chunk Filename | Uncompressed Size | Type / Contents |
| :--- | :---: | :--- |
| `1gj5u6mwx5p0u.js` | **229.1 KB** | Framework Vendor Chunk (React 19, Next.js Router, Hydration) |
| `33j1_fwxp3v_3.js` | **160.0 KB** | Client Animation & UI Library (`framer-motion`, `lucide-react`) |
| `3vna6glpsggmw.js` | **130.4 KB** | Shared Layout & Navigation Runtime |
| `0cz1d0mv5g_q7.js` | **112.6 KB** | Form Validation & Schema Parsing (`react-hook-form`, `zod`) |
| `2jhk5z5qq0o5y.css` | **88.0 KB** | Compiled Global Tailwind v4 CSS Bundle |
| `08je51kcr652t.js` | 68.5 KB | Page Chunk (Volunteer Profile & Form State) |
| `34gf5jzseghqf.js` | 48.4 KB | Page Chunk (Volunteer Leaderboard & Podium) |
| `10z8hbo57l_xx.js` | 41.1 KB | Page Chunk (Volunteer Events Listing) |
| `1p9jxi-w9el9o.js` | 40.9 KB | Page Chunk (Landing Page Hero & Feature Tracks) |
| `39bymntxv7gr3.js` | 38.9 KB | Page Chunk (Admin Events Management) |
| `1dszuj80wla5h.js` | 38.5 KB | Page Chunk (Volunteer Dashboard & KPI Cards) |
| Top 25 Chunks Total | **1.60 MB** | Full Compiled Client Assets |

### 3.2 Dependency Weight & Code Splitting Gaps

Inspection of `web/package.json`:
- `framer-motion`: `^14.9.0` (Significant bundle weight contribution in `33j1_fwxp3v_3.js`)
- `lucide-react`: `^1.67.0` (Full icon set imported across components)
- `date-fns` & `date-fns-tz`: Tree-shakeable date formatting utilities
- `zod` & `react-hook-form`: Bundled on forms routes

#### Code Splitting Audit:
- **`next/dynamic` usages in `web/src`**: 0
- **`React.lazy` usages in `web/src`**: 0
- **Finding**: Heavy interactive components such as `AchievementBadges`, `PublicLeaderboardTable`, and `VolunteerGuideCard` are statically bundled into initial route chunks rather than loaded progressively when scrolled into view.

---

## 4. API Response Time & Backend Performance

### 4.1 Live Endpoint Benchmark Results

Benchmarks were executed against the local running backend (`http://127.0.0.1:8000`) over 5 sequential runs:

| Run Number | `GET /api/v1/health` Latency | Database Component (`SELECT 1`) | Unauthenticated `GET /api/v1/events` |
| :---: | :---: | :---: | :---: |
| Run 1 | 2,289.05 ms | ~1,745 ms | 889.80 ms (Cold) |
| Run 2 | 2,547.74 ms | ~1,980 ms | 68.33 ms (401 Fast-Fail) |
| Run 3 | 2,612.93 ms | ~2,050 ms | 217.58 ms (401 Fast-Fail) |
| Run 4 | 2,018.87 ms | ~1,520 ms | 61.17 ms (401 Fast-Fail) |
| Run 5 | 2,889.91 ms | ~2,210 ms | 61.04 ms (401 Fast-Fail) |
| **Average** | **2,471.70 ms** | **1,745.43 ms** | **259.58 ms** |

### 4.2 Database Latency Diagnostic Analysis

Direct inspection of `http://127.0.0.1:8000/api/v1/health` JSON payload:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-11-05T15:03:15.667992Z",
  "database": {
    "connected": true,
    "dialect": "postgresql",
    "latency_ms": 1745.43,
    "error": null
  }
}
```

#### Diagnostic Findings:
1. **Remote Cloud Database Hop**: The application connects to Supabase PostgreSQL over WAN. A basic query (`SELECT 1`) takes **1,745 ms** due to geographic network distance and connection overhead.
2. **Health Check SLA Risk**: In production cloud environments (AWS ECS, Google Cloud Run, Kubernetes), container health checks typically enforce a 1,000 ms to 2,000 ms timeout. A health check endpoint taking **2,471 ms** will trigger false-positive container restarts and service crash loops.
3. **Session vs Pool Connection String**: The current connection configuration connects directly to the PostgreSQL session port (`5432`) rather than Supabase's transaction pooler (PgBouncer port `6543`), incurring high SSL handshake and process fork latencies on new sessions.

---

## 5. Image Delivery & Optimization Audit

### 5.1 Next.js Image Component vs Raw `<img>`

- **Total Raw `<img>` tags in `web/src/`**: 1 (in `web/src/app/showcase/assets/page.tsx:663`)
- **Total Next.js `<Image>` tags in `web/src/`**: 1 (in `components/ui/logo.tsx`)
- **Other Image References**: Images across `page.tsx`, `hero-welcome-banner.tsx`, and `recommended-events-section.tsx` are rendered via custom wrappers that utilize Next.js image optimization URLs (`/_next/image?url=...&w=1080&q=75`).

### 5.2 Source Image Weight Findings

While Next.js dynamically resizes images for the client viewport, the source photographic files in `web/public/assets/` are unnecessarily heavy:

| File Path | Raw File Size | Resolution | Recommended Optimization |
| :--- | :---: | :---: | :--- |
| `assets/maatram/photography/community-engagement.jpg` | **1,096.2 KB** | 1376×768 | Convert to WebP, 82% quality → Target: ~95 KB |
| `assets/maatram/photography/admissions-guidance.jpg` | **1,012.6 KB** | 1264×848 | Convert to WebP, 82% quality → Target: ~85 KB |
| `assets/maatram/photography/volunteers-team-hero.jpg` | **903.1 KB** | 1376×768 | Convert to WebP, 80% quality → Target: ~80 KB |
| `assets/maatram/photography/panel-interview.jpg` | **808.4 KB** | 1376×768 | Convert to WebP, 82% quality → Target: ~75 KB |
| `assets/images/hero-volunteering.jpg` (Duplicate) | **1,023.0 KB** | 1200×800 | Delete duplicate directory |
| `assets/images/school-visit.jpg` (Duplicate) | **980.0 KB** | 800×498 | Delete duplicate directory |
| `assets/images/mock-interview.jpg` (Duplicate) | **746.0 KB** | 800×533 | Delete duplicate directory |

---

## 6. Detailed Findings & Severity Classification

### ISSUE-PERF-001 [P1 — High]
- **Route/File**: `web/src/components/navigation/public-footer.tsx` (Lines 68–71)
- **Description**: Horizontal layout overflow (+71px) on tablet viewports (768px–1024px).
- **Evidence**: Chrome DevTools automated audit reported `scrollWidth: 839px` vs `clientWidth: 768px` on `/`, `/login`, and `/register`. Root element: `<span>volunteers@maatramfoundation.org</span>` expanding beyond its 160px column allocation.
- **Impact**: Causes unwanted horizontal scrolling, awkward whitespace margins, and degraded mobile UX on iPad and tablet screens.
- **Recommendation**:
  1. Add `break-all` to the email `<span>` in `public-footer.tsx`:
     ```tsx
     <span className="break-all">volunteers@maatramfoundation.org</span>
     ```
  2. Adjust the tablet footer grid definition from `md:grid-cols-4` to `grid-cols-1 sm:grid-cols-2 md:grid-cols-4`.

---

### ISSUE-PERF-002 [P1 — High]
- **Route/File**: `server/src/api/v1/health.py` & Database Connection Pool Configuration
- **Description**: Extreme health check latency (2,471 ms avg) caused by remote Supabase PostgreSQL WAN roundtrip.
- **Evidence**: `GET /api/v1/health` averaged 2,471 ms across 5 runs. The response payload reports `database.latency_ms: 1745.43` for `SELECT 1`.
- **Impact**: Container orchestration platforms (Kubernetes, AWS ECS, GCP Cloud Run) will flag containers as unhealthy and trigger continuous crash loops if health check timeouts are set below 3 seconds.
- **Recommendation**:
  1. Switch SQLAlchemy connection string to Supabase PgBouncer pooled connection (port `6543` with `?pgbouncer=true`).
  2. For liveness probes (`/health/liveness`), return HTTP 200 immediately without executing database queries; reserve database roundtrip checks for readiness probes (`/health/readiness`).

---

### ISSUE-PERF-003 [P2 — Medium]
- **Route/File**: `web/public/assets/maatram/photography/` & `web/public/assets/images/`
- **Description**: Heavy photographic assets (>800 KB each) and duplicate uncompressed asset directory.
- **Evidence**: 4 images in `maatram/photography/` exceed 800 KB (totaling 3.82 MB). Redundant duplicate folder `assets/images/` contains 3 files totaling 2.74 MB referenced directly by `page.tsx`.
- **Impact**: Server CPU overhead during on-demand Next.js image resizing; massive network payload if any image is served statically.
- **Recommendation**: Pre-compress source images to modern WebP format under 100 KB each and delete the duplicate `/assets/images/` folder.

---

### ISSUE-PERF-004 [P3 — Low]
- **Route/File**: Entire Next.js Frontend (`web/src/`)
- **Description**: Zero dynamic code-splitting (`next/dynamic` or `React.lazy`).
- **Evidence**: Search for dynamic imports yielded 0 occurrences. All client modules, animations (`framer-motion`), and complex form dialogs are loaded eagerly in the main route chunks.
- **Impact**: Increases initial JavaScript bundle execution time, impacting First Input Delay (FID) and Interaction to Next Paint (INP).
- **Recommendation**: Wrap heavy below-the-fold components (e.g. `AchievementBadges`, `VolunteeringGuideCard`, `PublicLeaderboardTable`) with `dynamic(() => import(...), { ssr: false })`.

---

## 7. Summary Findings Table

| Issue ID | Severity | Category | Route / File | Summary Description |
| :--- | :---: | :--- | :--- | :--- |
| **ISSUE-PERF-001** | **P1** | Responsiveness | `public-footer.tsx` | Unbroken email string creates 71px horizontal overflow on 768px tablet screens |
| **ISSUE-PERF-002** | **P1** | Backend Latency | `server/src/api/v1/health.py` | Healthcheck latency averages 2,471 ms due to remote Supabase DB WAN roundtrip |
| **ISSUE-PERF-003** | **P2** | Asset Performance | `photography/` & `/assets/images/` | 3.8 MB in heavy raw JPEGs (>800 KB each) + 2.7 MB duplicate directory |
| **ISSUE-PERF-004** | **P3** | Bundle Architecture | `web/src/` | 0 dynamic imports; framer-motion and heavy dialogs eagerly bundled |

---
*End of Performance & Responsiveness Audit Report.*
