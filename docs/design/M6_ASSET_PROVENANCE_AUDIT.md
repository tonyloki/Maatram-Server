# M6 ASSET PROVENANCE AUDIT & REMEDIATION PLAN
**Maatram Volunteering & Gamification Portal**
**Document ID:** `M6_ASSET_PROVENANCE_AUDIT`  
**Status:** In Progress / Active Remediation  
**Scope:** Complete frontend visual asset catalog across `web/public/assets/`

---

## 1. Executive Summary & Policy Directive

A zero-tolerance architectural policy is established against reusing screenshot fragments or cropped elements from design reference images (`ui-Reference/*.jpeg`):

> **Strict Prohibition**: The design reference screenshots define the visual direction and layout targets; they are **never** an asset source. No UI card, button, illustration, background, or hero banner may contain a cropped rectangular segment from a reference screenshot.

All visual elements must be:
1. **Clean Vector SVGs** for interface illustrations, empty states, badges, podiums, wreaths, crowns, charts, and decorative botanical watermarks.
2. **Authentic High-Resolution Photography** (minimum 800×500, up to 1376×768) for event thumbnails and storytelling.
3. **Programmatic CSS/SVG Compositions** for hero swoops, banners, cards, and interactive controls.

---

## 2. Comprehensive Asset Inventory & Provenance Classification

| Asset Path | Format & Dimensions | Size | Classification | Current Usage | Verdict & Remediation Action |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `assets/maatram/illustrations/activity-calendar-clock.png` | PNG (380×180) | 63.5 KB | **SCREENSHOT_CROP** | `volunteer/activity` | **REJECTED.** Cropped from `MyActivities.jpeg`. Recreating as pure SVG `activity-calendar-clock.svg`. |
| `assets/maatram/illustrations/empty-calendar-activity.png` | PNG (380×180) | 63.5 KB | **SCREENSHOT_CROP** | Duplicate alias | **DEPRECATED.** Remove immediately. |
| `assets/maatram/photography/volunteers-group-hero.png` | PNG (575×190) | 157.5 KB | **SCREENSHOT_CROP** | `volunteer/activity`, `events` | **REJECTED.** Cropped from `MyActivities.jpeg`. Replace with authentic high-res photography + SVG mask. |
| `assets/maatram/photography/volunteers-banner-exact.png` | PNG (516×208) | 165.4 KB | **SCREENSHOT_CROP** | `volunteer/activity`, `events` | **REJECTED.** Cropped from `MyActivities.jpeg`. Replace with clean SVG composition + authentic photo. |
| `assets/maatram/photography/landing-hero-volunteers.png` | PNG (690×564) | 395.4 KB | **SCREENSHOT_CROP** | Landing page (`/`) | **REJECTED.** Cropped from reference upload. Replace with authentic high-res photo + SVG swoop. |
| `assets/maatram/gamification/leaderboard-hero-art.png` | PNG (636×155) | 113.8 KB | **SCREENSHOT_CROP** | `volunteer/leaderboard` | **REJECTED.** Cropped from `Leaderboard.jpeg`. Replace with SVG crowd silhouettes + vector trophy. |
| `assets/maatram/photography/school-visit.jpg` | JPEG (140×85) | 6.6 KB | **SCREENSHOT_CROP** | `volunteer/events` | **REJECTED.** 6.6 KB crop. Replace with high-res `assets/images/school-visit.jpg` (800×498). |
| `assets/maatram/photography/mock-interview.jpg` | JPEG (140×85) | 5.1 KB | **SCREENSHOT_CROP** | `volunteer/events` | **REJECTED.** 5.1 KB crop. Replace with high-res `assets/images/mock-interview.jpg` (800×533). |
| `assets/maatram/photography/bgv-support.jpg` | JPEG (140×85) | 5.6 KB | **SCREENSHOT_CROP** | `volunteer/events` | **REJECTED.** 5.6 KB crop. Replace with high-res `assets/images/bgv-support.jpg` (800×533). |
| `assets/maatram/photography/admissions-guidance.jpg` | JPEG (140×85) | 4.8 KB | **SCREENSHOT_CROP** | `volunteer/events` | **REJECTED.** 4.8 KB crop. Replace with high-res authentic admissions photography. |
| `assets/maatram/photography/arun-avatar.jpg` | JPEG (90×90) | 2.5 KB | **AVATAR_PORTRAIT** | `volunteer/leaderboard` | **REPLACE.** Replace with crisp 256×256 portrait. |
| `assets/maatram/photography/priya-avatar.jpg` | JPEG (110×110) | 2.9 KB | **AVATAR_PORTRAIT** | `volunteer/profile` | **REPLACE.** Replace with crisp 256×256 portrait. |
| `assets/maatram/photography/sneha-avatar.jpg` | JPEG (90×90) | 2.7 KB | **AVATAR_PORTRAIT** | `volunteer/leaderboard` | **REPLACE.** Replace with crisp 256×256 portrait. |
| `assets/images/hero-volunteering.jpg` | JPEG (1200×800) | 192.4 KB | **ORIGINAL_HIGH_RES_PHOTO** | Landing page | **APPROVED.** Authentic high-res photo. |
| `assets/images/school-visit.jpg` | JPEG (800×498) | 69.3 KB | **ORIGINAL_HIGH_RES_PHOTO** | Landing page | **APPROVED.** Authentic high-res photo. |
| `assets/images/mock-interview.jpg` | JPEG (800×533) | 82.8 KB | **ORIGINAL_HIGH_RES_PHOTO** | Landing page | **APPROVED.** Authentic high-res photo. |
| `assets/images/bgv-support.jpg` | JPEG (800×533) | 77.4 KB | **ORIGINAL_HIGH_RES_PHOTO** | Landing page | **APPROVED.** Authentic high-res photo. |
| `assets/maatram/photography/community-engagement.jpg` | JPEG (1376×768) | 1096.2 KB | **ORIGINAL_HIGH_RES_PHOTO** | Event details | **APPROVED.** Authentic high-res photo. |
| `assets/maatram/photography/panel-interview.jpg` | JPEG (1376×768) | 808.4 KB | **ORIGINAL_HIGH_RES_PHOTO** | Event details | **APPROVED.** Authentic high-res photo. |
| `assets/maatram/illustrations/together-heart.svg` | SVG (Vector) | 3.3 KB | **ORIGINAL_SVG_VECTOR** | Sidebar, Dashboard | **APPROVED.** Independent vector SVG. |
| `assets/maatram/illustrations/empty-calendar-event.svg` | SVG (Vector) | 3.8 KB | **ORIGINAL_SVG_VECTOR** | Dashboard | **APPROVED.** Independent vector SVG. |
| `assets/maatram/illustrations/community-mentorship.svg` | SVG (Vector) | 4.6 KB | **ORIGINAL_SVG_VECTOR** | Showcase | **APPROVED.** Independent vector SVG. |
| `assets/maatram/decorations/birds-flock.svg` | SVG (Vector) | 1.1 KB | **ORIGINAL_SVG_VECTOR** | Dashboard hero | **APPROVED.** Independent vector SVG. |
| `assets/maatram/decorations/tree-silhouette.svg` | SVG (Vector) | 1.2 KB | **ORIGINAL_SVG_VECTOR** | Dashboard hero | **APPROVED.** Independent vector SVG. |
| `assets/maatram/decorations/wheat-stalks.svg` | SVG (Vector) | 1.2 KB | **ORIGINAL_SVG_VECTOR** | Sidebar, Profile | **APPROVED.** Independent vector SVG. |
| `assets/maatram/decorations/golden-sunburst.svg` | SVG (Vector) | 1.6 KB | **ORIGINAL_SVG_VECTOR** | Profile, Landing | **APPROVED.** Independent vector SVG. |
| `assets/maatram/decorations/celebratory-confetti.svg` | SVG (Vector) | 2.7 KB | **ORIGINAL_SVG_VECTOR** | Showcase | **APPROVED.** Independent vector SVG. |
| `assets/maatram/decorations/warm-wave-accent.svg` | SVG (Vector) | 1.1 KB | **ORIGINAL_SVG_VECTOR** | Showcase | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/trophy-grand.svg` | SVG (Vector) | 5.0 KB | **ORIGINAL_SVG_VECTOR** | Gamification | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/laurel-wreath.svg` | SVG (Vector) | 2.5 KB | **ORIGINAL_SVG_VECTOR** | Gamification | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/crown-gold.svg` | SVG (Vector) | 1.1 KB | **ORIGINAL_SVG_VECTOR** | Gamification | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/crown-silver.svg` | SVG (Vector) | 1.1 KB | **ORIGINAL_SVG_VECTOR** | Gamification | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/crown-bronze.svg` | SVG (Vector) | 1.1 KB | **ORIGINAL_SVG_VECTOR** | Gamification | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/podium-rank-1-gold.svg` | SVG (Vector) | 3.4 KB | **ORIGINAL_SVG_VECTOR** | Gamification | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/podium-rank-2-silver.svg` | SVG (Vector) | 2.4 KB | **ORIGINAL_SVG_VECTOR** | Gamification | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/podium-rank-3-bronze.svg` | SVG (Vector) | 2.4 KB | **ORIGINAL_SVG_VECTOR** | Gamification | **APPROVED.** Independent vector SVG. |
| `assets/maatram/gamification/badge-*.svg` (4 files) | SVG (Vector) | ~1.6 KB ea | **ORIGINAL_SVG_VECTOR** | Gamification, Profile | **APPROVED.** Independent vector SVGs. |
| `assets/maatram/icons/nav-*.svg` (6 files) | SVG (Vector) | ~0.4 KB ea | **ORIGINAL_SVG_VECTOR** | Sidebar | **APPROVED.** Independent vector SVGs. |
| `assets/maatram/icons/cat-*.svg` (5 files) | SVG (Vector) | ~0.5 KB ea | **ORIGINAL_SVG_VECTOR** | Category filters | **APPROVED.** Independent vector SVGs. |
| `assets/maatram/icons/metric-*.svg` (4 files) | SVG (Vector) | ~0.5 KB ea | **ORIGINAL_SVG_VECTOR** | Dashboard metrics | **APPROVED.** Independent vector SVGs. |

---

## 3. Remediation Execution Plan

1. **Empty-State Illustration (`activity-calendar-clock.svg`)**:
   - Create an independent vector SVG featuring a 3D isometric desk calendar binder with golden header, rounded date grid, overlapping analog clock with dark hands, radiant sun sparks, and surrounding botanical leaves.
   - 100% transparent background, vector scalable at any resolution, zero rectangular border clipping.

2. **Hero Banner Visuals & Photography**:
   - Deprecate screenshot crops `volunteers-banner-exact.png` and `volunteers-group-hero.png`.
   - Implement programmatic SVG / CSS banners with organic golden branch watermarks.
   - Use high-resolution authentic photography (`assets/images/hero-volunteering.jpg` or `community-engagement.jpg`) with smooth gradient masks rather than raw screenshot fragments.

3. **Discover Events Photography**:
   - Replace low-res crops with high-resolution authentic photographs (minimum 800×500) for School Visit, Mock Interview, BGV Support, and Admissions Guidance.

4. **Landing Page Hero & Swoop Wave**:
   - Recreate the dynamic golden wave swoop as a clean mathematical SVG path (`landing-wave-swoop.svg`).
   - Use high-resolution photography integrated seamlessly above the vector swoop.

5. **Leaderboard Hero Crowd Artwork**:
   - Replace `leaderboard-hero-art.png` with an independent SVG composition combining celebratory crowd silhouettes with `trophy-grand.svg`.

6. **Sidebar "Together for a Better Tomorrow" Card**:
   - Verify `together-heart.svg` is rendered as an independent scalable SVG with clean typography and proper padding.

