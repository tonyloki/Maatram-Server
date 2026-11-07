# UI & Visual Quality Audit Report
**Maatram Volunteering & Mentorship Portal**
**Audit Date**: November 5, 2026  
**Auditor**: Independent Production-Readiness Audit Team  
**Scope**: Frontend Web Application (`web/`), Design System Primitives, Static Assets, Viewport Visual Fidelity  
**Target Environment**: Next.js 16.4.4 / React 19 / Tailwind CSS v4 (`http://localhost:3001`)

---

## 1. Executive Summary

This independent UI and Visual Quality audit was conducted to verify that the **Maatram Volunteering & Mentorship Portal** complies with professional design standards, brand identity specifications, responsive layout requirements, and accessible component architectures. The audit evaluated static asset integrity, design token adoption, component consistency, and multi-device visual rendering using Chrome DevTools automated inspection.

### Key Audit Highlights
- **Asset Integrity**: 53 assets in `web/public/assets/maatram/`. All 44 SVG vector assets are 100% pure vectors without embedded base64 raster blobs. 52 out of 53 assets are actively referenced; 1 asset (`hero-volunteers-banner.png`, 157.5 KB) is orphaned. An asset directory redundancy was identified between `/assets/images/` and `/assets/maatram/photography/`.
- **Component Token Adoption**: `globals.css` defines a comprehensive `@theme` token palette (`--color-brand-primary: #F5B817`, `--color-canvas: #FAF8F5`, etc.). However, virtually all components and feature pages bypass these tokens in favor of hardcoded arbitrary hex classes (e.g. `bg-[#F5B817]`, `text-[#1F2421]`).
- **Design System Drift in Admin Workspace**: While Volunteer Portal routes utilize the brand gold palette (`#F5B817`), Admin routes (`/admin/events`) deviate to standard Tailwind amber (`bg-amber-500`, `text-charcoal-950`) and completely bypass reusable UI component primitives (`<Button>`, `<Input>`), introducing visual fragmentation.
- **Authentication State Leakage**: When an authenticated user visits `/login` or `/register`, the forms render in full beneath an active user session header, rather than redirecting to their role-appropriate dashboard.

---

## 2. Asset Integrity Audit

### 2.1 File Inventory & Format Breakdown

A complete inventory of `web/public/assets/maatram/` was conducted:

| Directory | File Count | Formats | Total Size | Vector Purity |
| :--- | :---: | :---: | :---: | :---: |
| `decorations/` | 7 | SVG | 3.2 KB | 100% Pure Vector (0 raster tags) |
| `gamification/` | 13 | SVG | 5.8 KB | 100% Pure Vector (0 raster tags) |
| `icons/` | 17 | SVG | 8.1 KB | 100% Pure Vector (0 raster tags) |
| `illustrations/` | 7 | SVG | 4.8 KB | 100% Pure Vector (0 raster tags) |
| `photography/` | 9 | JPG (8), PNG (1) | 5,160.0 KB | N/A (Raster Imagery) |
| **Total** | **53** | **SVG (44), JPG (8), PNG (1)** | **~5.18 MB** | **All 44 SVGs Pure Vector** |

### 2.2 SVG Raster Tag Audit
Every SVG file was scanned for `<image` tags and `data:image` base64 strings.
- **SVGs Scanned**: 44
- **SVGs with Embedded Raster Blobs**: 0 (Passed)
- **Result**: All icons, badges, crowns, and decorative swoop SVGs are cleanly authored paths and vectors that scale infinitely without pixelation.

### 2.3 Photographic Asset Specifications

Inspection of all raster photography via Python PIL:

| Filename | Resolution (W×H) | Format | File Size | Aspect Ratio | Target Placement |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `community-engagement.jpg` | 1376 × 768 | JPEG | **1,096.2 KB** | 1.79:1 (16:9) | Fallback Event Banner |
| `admissions-guidance.jpg` | 1264 × 848 | JPEG | **1,012.6 KB** | 1.49:1 (3:2) | Admissions Track Card |
| `volunteers-team-hero.jpg` | 1376 × 768 | JPEG | **903.1 KB** | 1.79:1 (16:9) | Landing Page Hero |
| `panel-interview.jpg` | 1376 × 768 | JPEG | **808.4 KB** | 1.79:1 (16:9) | Panel Interview Track |
| `hero-volunteering.jpg` | 1200 × 800 | JPEG | 192.4 KB | 1.50:1 (3:2) | Volunteer Dashboard Hero |
| `hero-volunteers-banner.png`| 575 × 190 | PNG | 157.5 KB | 3.03:1 (Banner)| **Unused / Orphaned** |
| `mock-interview.jpg` | 800 × 533 | JPEG | 82.8 KB | 1.50:1 (3:2) | Mock Interview Card |
| `bgv-support.jpg` | 800 × 533 | JPEG | 77.4 KB | 1.50:1 (3:2) | BGV Support Card |
| `school-visit.jpg` | 800 × 498 | JPEG | 69.3 KB | 1.61:1 (~16:10) | School Visit Card |

> [!WARNING]
> Four photographic images exceed 800 KB each, totaling **3.82 MB** of unoptimized JPEG imagery. Serving uncompressed 1MB+ images on landing and event pages without WebP/AVIF generation degrades Core Web Vitals (LCP).

### 2.4 Asset Usage Cross-Reference & Redundancy

- **Total Assets in `web/public/assets/maatram/`**: 53
- **Active Codebase References in `web/src/`**: 52
- **Orphaned Assets**: 1
  - `web/public/assets/maatram/photography/hero-volunteers-banner.png` (157.5 KB) has 0 references in `web/src`.
- **Directory Bifurcation**:
  A second asset directory exists at `web/public/assets/images/` containing duplicate copies:
  - `web/public/assets/images/bgv-support.jpg` (256 KB)
  - `web/public/assets/images/hero-volunteering.jpg` (**1,023 KB** vs 192 KB in `maatram/photography/`!)
  - `web/public/assets/images/mock-interview.jpg` (746 KB vs 82.8 KB in `maatram/photography/`!)
  - `web/public/assets/images/school-visit.jpg` (980 KB vs 69.3 KB in `maatram/photography/`!)
  In `web/src/app/page.tsx`, lines 36, 44, and 52 explicitly reference `/assets/images/school-visit.jpg` instead of the canonical `/assets/maatram/photography/` path, inadvertently forcing users to download the 980 KB file rather than the 69 KB file!

---

## 3. Component Consistency Audit

### 3.1 Design System Primitives Analysis

The core UI component primitives in `web/src/components/ui/` were audited:

#### 1. Button (`button.tsx`)
- **Strengths**: Fully typed with forwardRef, supports loading spinners (`<Loader2>`), custom icon slots (`leftIcon`, `rightIcon`), micro-animations (`hover:-translate-y-0.5`, `active:scale-[0.98]`).
- **Deficiencies**:
  - Hardcoded hex values throughout (`bg-[#F5B817]`, `hover:bg-[#E5A800]`, `bg-[#FFF8E7]`, `border-[#EFECE6]`) instead of referencing `@theme` tokens.
  - Variant Redundancy: `variant="gold"` and `variant="primary"` have completely identical CSS string definitions (lines 42–45).

#### 2. Card & KpiCard (`card.tsx`)
- **Strengths**: Clean separation of `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, and `CardFooter`. Dedicated `KpiCard` component with semantic trend indicators.
- **Deficiencies**:
  - Hardcoded hex borders (`border-[#EFECE6]`) and text colors (`text-[#1F2421]`, `text-[#4B5563]`).
  - Inconsistent radius options: default is `"2xl"`, but some pages manually override with `"rounded-xl"`.

#### 3. Badge (`badge.tsx`)
- **Strengths**: Rich variant coverage (status variants: `success`, `warning`, `error`, `attention`, `neutral`, `brand`; event category variants: `school-visit`, `mock-interview`, `bgv`, `admissions`, `panel`). Built-in accessible dot indicators.
- **Deficiencies**:
  - Hardcoded color maps instead of linking to `--color-status-*` or `--color-tag-*` CSS variables.

#### 4. Input & Textarea (`input.tsx`)
- **Strengths**: ForwardRef support, built-in validation error styling (`border-[#F8B4B4]`), accessible label binding, character counters.
- **Deficiencies**:
  - Uses `border-[#E5E7EB]` whereas `card.tsx` uses `border-[#EFECE6]`, creating subtle 1px border contrast mismatch between form containers and input boxes.

#### 5. Switch & ConsentSwitch (`switch.tsx`)
- **Strengths**: Excellent compliance with DPDP affirmative consent standards. Clear plain-language consent descriptions. Focus-visible accessibility rings.

### 3.2 Page-Level Component Adoption Audit

An audit of button and input usage across major application routes revealed severe component adoption gaps:

| Page Route | Raw `<button>` | `<Button>` Primitives | Arbitrary Hex Classes | Primary Color Inconsistency |
| :--- | :---: | :---: | :---: | :--- |
| `web/src/app/page.tsx` (Landing) | 2 | 4 | 95 | Uses `#F5B817` |
| `web/src/app/volunteer/events/page.tsx` | **5** | **0** | 57 | Uses `#F5B817` |
| `web/src/app/volunteer/leaderboard/page.tsx` | **1** | **0** | 87 | Uses `#F5B817` |
| `web/src/app/admin/events/page.tsx` | **4** | **0** | 0 | **Uses `amber-500` / `charcoal-950`** |

#### Key Component Consistency Findings:
1. **Total Component Bypass in Feature Pages**:
   Neither `/volunteer/events` nor `/volunteer/leaderboard` nor `/admin/events` uses the shared `<Button>` component. They re-implement `<button>` from scratch with custom class strings.
2. **Palette Divergence in Admin Workspace**:
   `admin/events/page.tsx` does not use the canonical Radiant Gold `#F5B817`. Instead, it uses Tailwind's default `bg-amber-500` (`#F59E0B`), creating an uncoordinated shade difference between administrative tools and volunteer facing portals.
3. **Input Component Bypass**:
   `admin/events/page.tsx` uses raw `<input className="w-full text-xs pl-9 pr-3 py-2 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-amber-500" />` instead of the accessible, validated `<Input>` component from `@/components/ui/input`.

---

## 4. Visual Screenshots & Viewport Inspection

Full visual audits were executed using Chrome DevTools MCP against `http://localhost:3001` across Desktop (1536×1024) and Mobile (390×844) viewports.

### 4.1 Screenshot Evidence Index

All captured screenshots are stored in `docs/audits/screenshots/`:

| Viewport | Route | Filename | Key Observations |
| :--- | :--- | :--- | :--- |
| 1536×1024 | `/` (Landing Page) | `landing_desktop_1536.png` | Hero banner clean; golden wave swoop renders properly; public footer present. |
| 1536×1024 | `/volunteer/dashboard` | `volunteer_dashboard_desktop_1536.png` | Sidebar navigation, welcome banner, 4 KPI cards, empty activity card, recommendation cards. |
| 1536×1024 | `/volunteer/events` | `volunteer_events_desktop_1536.png` | Category pill filter bar, event grid cards with photography, status badges. |
| 1536×1024 | `/volunteer/leaderboard` | `volunteer_leaderboard_desktop_1536.png` | Podium ranking cards (Gold, Silver, Bronze), filter tabs, full volunteer ranking table. |
| 1536×1024 | `/volunteer/profile` | `volunteer_profile_desktop_1536.png` | Multi-tab profile form, DPDP consent switches, achievement badges. |
| 1536×1024 | `/admin/dashboard` | `admin_dashboard_desktop_1536.png` | RBAC guard active: Displays centered "Administrative Access Denied" card for volunteer account. |
| 1536×1024 | `/login` | `login_desktop_1536.png` | Centered authentication card with email/password inputs. Top header leaks active user session. |
| 1536×1024 | `/register` | `register_desktop_1536.png` | Volunteer onboarding registration form with role selection tabs. |
| 390×844 | `/` (Mobile) | `landing_mobile_390.png` | Single column vertical collapse; CTA buttons stack full-width cleanly. |
| 390×844 | `/volunteer/events` (Mobile) | `volunteer_events_mobile_390.png` | Category pills scroll horizontally; event cards stack vertically. |
| 390×844 | `/volunteer/leaderboard` (Mobile) | `volunteer_leaderboard_mobile_390.png` | Podium cards stack vertically; leaderboard table responsive. |

---

## 5. Detailed Findings & Severity Classification

### ISSUE-UI-001 [P1 — High]
- **Route/File**: `web/src/components/navigation/public-footer.tsx` (Lines 68–71)
- **Description**: Unbroken email text string creates tablet-viewport horizontal layout overflow.
- **Evidence**: Testing at 768px tablet width produces `scrollWidth: 839px` vs `clientWidth: 768px` (+71px overflow). The right edge of `<span>volunteers@maatramfoundation.org</span>` extends to 839px because the 4-column `md:grid-cols-4` grid allocates ~160px width to column 4, which is narrower than the 230px rendered email text.
- **Impact**: Causes horizontal page jitter and horizontal scrollbars on iPad and tablet viewports.
- **Recommendation**: Add `break-all` or `truncate` CSS classes to the contact email link, or revise tablet grid to `md:grid-cols-2 lg:grid-cols-4`.

---

### ISSUE-UI-002 [P2 — Medium]
- **Route/File**: `web/src/app/page.tsx` (Lines 36, 44, 52) & `web/public/assets/images/`
- **Description**: Asset directory bifurcation causing massive image payload downloads.
- **Evidence**: `web/src/app/page.tsx` references `/assets/images/school-visit.jpg` (980 KB) and `/assets/images/mock-interview.jpg` (746 KB). Identical images exist in `web/public/assets/maatram/photography/` optimized at 69.3 KB and 82.8 KB respectively.
- **Impact**: Landing page downloads over 2.7 MB of duplicate uncompressed images instead of 300 KB, degrading First Contentful Paint.
- **Recommendation**: Update all image references in `page.tsx` to `/assets/maatram/photography/...` and delete the redundant `web/public/assets/images/` folder.

---

### ISSUE-UI-003 [P2 — Medium]
- **Route/File**: `web/src/app/login/page.tsx` & `web/src/app/register/page.tsx`
- **Description**: Authenticated user session leakage on login/register views without redirection.
- **Evidence**: Navigating to `http://localhost:3001/login` while logged in displays the authenticated user email (`consent_verify_9a211f@example.com`) and "Logout" button in the navigation header, while the main body renders the "Welcome Back" login credential form.
- **Impact**: Confusing and broken UX; authenticated volunteers might re-enter credentials or wonder if they are signed in.
- **Recommendation**: Add an auth guard redirect in `/login` and `/register` client components:
  ```typescript
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      router.replace(redirectUrl || "/volunteer/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);
  ```

---

### ISSUE-UI-004 [P2 — Medium]
- **Route/File**: `web/src/components/ui/button.tsx`, `card.tsx`, `badge.tsx`, and all pages
- **Description**: Tailwind v4 design tokens in `globals.css` completely bypassed in favor of hardcoded arbitrary hex classes.
- **Evidence**: `globals.css` defines `--color-brand-primary: #F5B817`, `--color-canvas: #FAF8F5`, `--color-text-primary: #1F2421`. Over 239 instances of `bg-[#F5B817]`, `text-[#1F2421]`, `bg-[#FFF8E7]`, and `border-[#EFECE6]` are hardcoded across `web/src/app/`.
- **Impact**: Breaks central theming and dark-mode readiness; design system maintenance requires search-and-replacing hundreds of arbitrary strings.
- **Recommendation**: Replace arbitrary hex classes with Tailwind v4 `@theme` utilities (`bg-brand-primary`, `text-text-primary`, `border-border-subtle`).

---

### ISSUE-UI-005 [P2 — Medium]
- **Route/File**: `web/src/app/admin/events/page.tsx`
- **Description**: Brand palette divergence and shared component bypass in Admin Workspace.
- **Evidence**: `admin/events/page.tsx` uses raw `<button>` with `bg-amber-500` (hex `#F59E0B`) and `text-charcoal-950` rather than the official Radiant Gold `#F5B817` brand palette. It also uses raw `<input>` with custom ring styles instead of the accessible `@/components/ui/input` component.
- **Impact**: Inconsistent look and feel across administrative and volunteer portal interfaces.
- **Recommendation**: Migrate `admin/events/page.tsx` to use `<Button variant="...">`, `<Input>`, and the canonical brand design tokens.

---

### ISSUE-UI-006 [P3 — Low]
- **Route/File**: `web/src/components/ui/button.tsx` (Lines 42–45)
- **Description**: Redundant duplicate variant declaration in Button component.
- **Evidence**:
  ```typescript
  primary: "bg-[#F5B817] text-[#1F2421] hover:bg-[#E5A800] active:bg-[#C99200] hover:-translate-y-0.5 active:translate-y-0 focus-visible:ring-[#F5B817] shadow-xs hover:shadow-sm",
  gold:    "bg-[#F5B817] text-[#1F2421] hover:bg-[#E5A800] active:bg-[#C99200] hover:-translate-y-0.5 active:translate-y-0 focus-visible:ring-[#F5B817] shadow-xs hover:shadow-sm",
  ```
- **Impact**: Dead code / confusion for developers wondering whether `primary` or `gold` is canonical.
- **Recommendation**: Remove `gold` or alias it cleanly to `primary` in TypeScript types.

---

### ISSUE-UI-007 [P3 — Low]
- **Route/File**: `web/src/app/admin/events/page.tsx` (Line 143)
- **Description**: Non-standard Tailwind CSS class `focus:outline-hidden`.
- **Evidence**: `className="... focus:outline-hidden focus:ring-2 focus:ring-amber-500"`
- **Impact**: `outline-hidden` is non-standard in standard Tailwind configurations and may fail to suppress default browser outlines on older WebKit engines.
- **Recommendation**: Replace with standard `focus:outline-none` or `focus-visible:outline-none`.

---

### ISSUE-UI-008 [P4 — Enhancement]
- **Route/File**: `web/public/assets/maatram/photography/hero-volunteers-banner.png`
- **Description**: Orphaned asset file present in public directory.
- **Evidence**: 157.5 KB file has zero references across all `.ts`, `.tsx`, and `.css` files.
- **Impact**: Minor disk and deployment artifact bloat.
- **Recommendation**: Delete `hero-volunteers-banner.png` from version control.

---

## 6. Summary Findings Table

| Issue ID | Severity | Category | Route / File | Summary Description |
| :--- | :---: | :--- | :--- | :--- |
| **ISSUE-UI-001** | **P1** | Responsive Layout | `public-footer.tsx` | Unbroken email string creates 71px horizontal overflow on tablet viewports |
| **ISSUE-UI-002** | **P2** | Asset Management | `page.tsx` & `/assets/images/` | Directory bifurcation causes 2.7 MB duplicate high-res image download |
| **ISSUE-UI-003** | **P2** | Authentication UX | `/login`, `/register` | Authenticated session shown simultaneously with login form; no auto-redirect |
| **ISSUE-UI-004** | **P2** | Design Tokens | Global UI Primitives & Pages | Comprehensive `@theme` tokens bypassed for arbitrary hex strings |
| **ISSUE-UI-005** | **P2** | Component System | `admin/events/page.tsx` | Admin events bypasses UI components and uses divergent `amber-500` palette |
| **ISSUE-UI-006** | **P3** | Code Quality | `button.tsx` | Identical duplicate definition for `primary` and `gold` button variants |
| **ISSUE-UI-007** | **P3** | Accessibility CSS | `admin/events/page.tsx` | Non-standard `focus:outline-hidden` class on search input |
| **ISSUE-UI-008** | **P4** | Asset Cleanup | `hero-volunteers-banner.png` | Orphaned 157.5 KB PNG asset with zero codebase usage |

---
*End of UI & Visual Quality Audit Report.*
