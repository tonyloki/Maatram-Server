# M6_ASSET_PLAN.md — Asset Inventory, Provenance & Production Specifications
**Maatram Volunteering & Gamification Portal**  
**Milestone 6.0: Asset Planning & Visual Resource Roadmap**  
**Date:** November 2026 (Updated with Alignment Corrections)  
**Status:** **ALIGNED ASSET PLAN — NO ASSETS DOWNLOADED OR GENERATED IN M6.0**

---

## 1. Executive Summary & Verified Existing Asset Inventory

Every asset currently residing in `web/public/` was verified through direct binary and filesystem inspection. Dimensions, file sizes, and color profiles have been empirically validated.

### 1.1 Verified Existing Workspace Assets
| Asset Path | Format | Measured Dimensions | File Size | Usage & Provenance | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `web/public/maatram_logo-removebg-preview.png` | PNG | `709 × 352 px` | 96.1 KB | Official Maatram Foundation logo (transparent background). | **VERIFIED EXISTING** |
| `web/public/Maatramlogowithbg.jpeg` | JPEG | `709 × 352 px` | 33.2 KB | Official Maatram Foundation logo (white background). Sampled gold `#FFC20F`. | **VERIFIED EXISTING** |
| `web/public/assets/images/hero-volunteering.jpg` | JPEG | `1200 × 800 px` | 192.4 KB | Authentic education classroom mentoring photography on public landing page. | **VERIFIED EXISTING** |
| `web/public/assets/images/school-visit.jpg` | JPEG | `800 × 498 px` | 69.3 KB | Authentic Government High School classroom visit photography. | **VERIFIED EXISTING** |
| `web/public/assets/images/mock-interview.jpg` | JPEG | `800 × 533 px` | 82.8 KB | Authentic 1-on-1 mock interview mentoring session photography. | **VERIFIED EXISTING** |
| `web/public/assets/images/bgv-support.jpg` | JPEG | `800 × 533 px` | 77.4 KB | Authentic background verification field documentation photography. | **VERIFIED EXISTING** |
| `web/public/favicon.ico` | ICO | `32 × 32 px` | 15.1 KB | Browser tab favicon. | **VERIFIED EXISTING** |

---

## 2. Inventory of All Six Mentor Reference Sources

The mentor provided five native reference screenshots and one approved reference specification:
1. **Reference 1: Public Landing Page** — Derived from `docs/execution-groups/MILESTONE_2_VISUAL_CORRECTION_REPORT.md` and `web/src/app/page.tsx`.
2. **Reference 2: Volunteer Dashboard** — Source file: `ui-Reference/Dashboard.jpeg` (`1536 × 1024 px`, 302.5 KB).
3. **Reference 3: Discover Events** — Source file: `ui-Reference/Discover_Events.jpeg` (`1536 × 1024 px`, 305.7 KB).
4. **Reference 4: My Activity** — Source file: `ui-Reference/MyActivities.jpeg` (`1536 × 1024 px`, 201.8 KB).
5. **Reference 5: Leaderboard** — Source file: `ui-Reference/Leaderboard.jpeg` (`1536 × 1024 px`, 218.4 KB).
6. **Reference 6: My Profile** — Source file: `ui-Reference/Profile_page.jpeg` (`1600 × 900 px`, 226.6 KB).

---

## 3. Proposed Assets & Provenance Requirements (For Implementation in M6.1+)

The following assets are required for full visual parity with the mentor reference designs. **None of these assets are downloaded or generated in Milestone 6.0.**

### 3.1 Panoramic Hero Photography & Illustrations
| Proposed Asset Name | Proposed Destination | Target Page(s) | Target Dimensions | Subject & Style Description | Licensing & Sourcing Requirements |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Volunteers Panoramic Banner** | `/assets/images/banner-volunteers.png` | Volunteer Dashboard, Events, Activity | `960 × 300 px` (`16:5`) | Panoramic photo of 4–5 volunteers wearing black Maatram t-shirts looking towards a tree across a green field. Warm gold color grade. | Must be authentic Maatram Foundation volunteer photography or licensed photography depicting South Asian education volunteers under commercial-use license. |
| **Leaderboard Trophy & Crowd** | `/assets/images/leaderboard-trophy-banner.png` | Volunteer Leaderboard | `960 × 300 px` (`16:5`) | Gleaming golden trophy with star, framed by silhouetted cheering crowd in monochrome amber on golden gradient background. | Custom SVG / vector artwork created specifically for Maatram or licensed vector graphic. |

### 3.2 Illustrations & Empty States
| Proposed Asset Name | Proposed Destination | Target Page(s) | Target Dimensions | Subject & Style Description | Licensing & Sourcing Requirements |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Together Hand-Heart Graphic** | `/assets/illustrations/together-heart.png` | Dashboard (Guide), Sidebar card | `300 × 300 px` (`1:1`) | Two hands cupping a radiant golden heart with rays and slogan *"Together for a better tomorrow"*. | Custom vector artwork in SVG/PNG format. |
| **Calendar Empty State (Upcoming)** | `/assets/illustrations/empty-calendar.png` | Volunteer Dashboard | `400 × 300 px` (`4:3`) | 3D desk flip-calendar showing Maatram logo on front leaf, set on soft yellow radial glow. | Custom 3D render or vector graphic adhering to Maatram branding. |
| **Activity Empty State (Clock & Calendar)** | `/assets/illustrations/empty-activity.png` | Volunteer Activity | `450 × 320 px` (`4:3`) | 3D desk calendar alongside a floating analogue clock and golden leaves. | Custom 3D render or vector graphic. |
| **Botanical Leaf Watermarks** | `/assets/decorations/wheat-leaves.svg` | Volunteer Sidebar, Card Corners | `120 × 200 px` (Vector) | Delicate wheat stalks and botanical leaves in soft amber (`#F5B817` at 15% opacity). | Custom SVG path (zero external dependencies). |

### 3.3 Gamification & Achievement Badges
| Proposed Asset Name | Proposed Destination | Target Page(s) | Target Dimensions | Subject & Style Description | Governance & Sourcing Rule |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rank 1 Crown & Laurel** | `/assets/icons/podium-crown-gold.svg` | Leaderboard (Podium) | Vector SVG | 5-point golden crown flanked by circular laurel branches. | Custom vector SVG. |
| **Rank 2 Crown (Silver)** | `/assets/icons/podium-crown-silver.svg` | Leaderboard (Podium) | Vector SVG | Polished silver crown with number `2`. | Custom vector SVG. |
| **Rank 3 Crown (Bronze)** | `/assets/icons/podium-crown-bronze.svg` | Leaderboard (Podium) | Vector SVG | Warm bronze crown with number `3`. | Custom vector SVG. |
| **Visual Example Medals** | `/assets/badges/badge-*.png` | Volunteer Profile | `120 × 120 px` each | Medals illustrated in Reference 6 are visual examples only. | Dynamically bound to `AchievementDefinition` records in database. No hardcoded achievements. |

### 3.4 Additional Event Category Photography
| Proposed Asset Name | Proposed Destination | Target Page(s) | Target Dimensions | Subject & Style Description | Licensing & Sourcing Requirements |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Admissions Guidance Thumbnail** | `/assets/images/admissions-guidance.jpg` | Discover Events | `800 × 450 px` (`16:9`) | Students or graduates in celebration under open sky. | High-resolution photography with verified commercial license. |
| **Panel Interview Thumbnail** | `/assets/images/panel-interview.jpg` | Discover Events | `800 × 450 px` (`16:9`) | Volunteer mentors conducting interactive interview panel with student. | High-resolution photography with verified commercial license. |

---

## 4. Strict Asset Governance Rules

1. **NO CODE OR ASSET GENERATION IN M6.0**: No image files, SVG exports, or binary assets are created or placed in `web/` during this planning milestone.
2. **NO SCREENSHOT BACKGROUND SHORTCUTS**: Entire reference screenshots must **never** be used as page backgrounds or structural shortcuts. Every card, hero, and rail must be composed of semantic HTML, Tailwind utility tokens, and discrete asset components.
3. **IMAGE OPTIMIZATION STANDARDS**: In subsequent implementation milestones, all photographic assets must be transcoded to WebP/AVIF via `next/image` with explicit `width`, `height`, and `sizes` attributes to prevent Cumulative Layout Shift (CLS).
