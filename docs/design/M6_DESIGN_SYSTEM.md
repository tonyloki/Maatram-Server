# M6_DESIGN_SYSTEM.md — Maatram Design System Specification
**Maatram Volunteering & Gamification Portal**  
**Milestone 6.0: Visual Foundations & Reusable Component Tokens**  
**Date:** November 2026 (Updated with Alignment Corrections)  
**Status:** **ALIGNED DESIGN SYSTEM SPECIFICATION**

---

## 1. Design System Philosophy & Principles

The Maatram Design System is built upon three core design pillars:
1. **Warm Human Welcoming**: Moving away from clinical cold greys to comforting warm ivory and cream backgrounds (`#FAF8F5`), organic botanical flourishes, and radiant golden-yellow accents.
2. **Tactile Elevation & Clarity**: Pure white floating cards (`#FFFFFF`) with generous border-radii (`rounded-2xl` to `rounded-3xl`), whisper-soft borders (`#EFECE6`), and delicate shadows that give interfaces a friendly, approachable touch.
3. **Purposeful Dignity**: Elevating the impact of volunteers and scholars through high-contrast typography, clear status communication, and uplifting milestone celebrations.

---

## 2. Color Palette & Token Architecture

### 2.1 Brand Primary Resolution: Canonical `#F5B817` (Maatram Radiant Gold)
*Source Analysis: Colorimetric sampling of the official Maatram logo (`web/public/Maatramlogowithbg.jpeg` — `#FFC20F`), mentor reference button fills (`ui-Reference/Dashboard.jpeg` — `#FEC216`), and existing code baseline (`web/src/app/globals.css`).*

**Resolution**: `#F5B817` is the **single canonical primary brand token**. The Tailwind default `amber-500` (`#F59E0B`) is discarded in favor of `#F5B817` to preserve exact brand identity across all media.

| Token Name | Hex Value | Usage / Description | Contrast & Accessibility Compliance |
| :--- | :--- | :--- | :--- |
| `--color-brand-primary` | `#F5B817` | Canonical primary brand color. Primary button fills, active tabs, progress arcs. | High contrast when paired with dark charcoal text (`#1F2421`, contrast > 11:1). |
| `--color-brand-hover` | `#E5A800` | Interactive hover state for primary buttons. | Accessible fill state. |
| `--color-brand-active` | `#C99200` | Pressed / active state for interactive elements. | Accessible fill state. |
| `--color-brand-subtle` | `#FFF8E7` | Soft warm surface fill, active sidebar item background. | Surface tint only; not for text. |
| `--color-brand-light` | `#FFFDF5` | Lightest canvas tint for subtle radial gradients. | Background tint. |
| `--color-brand-text` | `#946C00` | Supporting amber-brown text for links on light/cream backgrounds. | Contrast ratio ≥ 4.8:1 against `#FAF8F5` (WCAG AA compliant). |

> **Accessibility Rule**: Primary gold (`#F5B817`) must **never** be used as a raw text color against white or cream backgrounds. It is used strictly as a **surface fill** paired with deep charcoal text (`#1F2421`).

### 2.2 Warm Neutral Palette
*Source: Sampled directly from Mentor References 2–6.*

| Token Name | Hex Value | Usage / Description |
| :--- | :--- | :--- |
| `--color-canvas-bg` | `#FAF8F5` | Global body & main container canvas (warm ivory). |
| `--color-card-surface` | `#FFFFFF` | Floating card background. |
| `--color-card-border` | `#EFECE6` | Default card & container hairline border. |
| `--color-border-hover` | `#E5E0D8` | Interactive border hover state. |
| `--color-text-primary` | `#1F2421` | Headings, card titles, primary body copy (high contrast deep charcoal). |
| `--color-text-secondary`| `#4B5563` | Subtitles, descriptions, metadata (slate grey). |
| `--color-text-muted` | `#9CA3AF` | Inactive icons, placeholder text, character counts. |
| `--color-divider` | `#F3EFEA` | Horizontal dividers within cards. |

### 2.3 Semantic & Category Pill Palettes
*Source: Sampled from Mentor Reference 3 (Discover Events) & Reference 6 (Profile).*

| Category / Status | Background | Text Color | Border Color | Example Tag |
| :--- | :--- | :--- | :--- | :--- |
| **Onsite / Approved** | `#DCFCE7` | `#166534` | `#BBF7D0` | `[Onsite]`, `[Approved]` |
| **Online / Info** | `#E0F2FE` | `#0369A1` | `#BAE6FD` | `[Online]` |
| **School Visit** | `#FEF3C7` | `#92400E` | `#FDE68A` | `[School Visit]` |
| **Mock Interview** | `#E0F2FE` | `#0369A1` | `#BAE6FD` | `[Mock Interview]` |
| **BGV Support** | `#EDE9FE` | `#6D28D9` | `#DDD6FE` | `[BGV Support]` |
| **Admissions Guidance** | `#FFEDD5` | `#C2410C` | `#FED7AA` | `[Admissions]` |
| **Panel Interview** | `#CCFBF1` | `#0F766E` | `#99F6E4` | `[Panel Interview]` |
| **Warning / Review** | `#FEF9C3` | `#854D0E` | `#FEF08A` | `[Pending Review]` |
| **Error / Suspended** | `#FEE2E2` | `#991B1B` | `#FECACA` | `[Suspended]` |

---

## 3. Typography Scale & Hierarchy

The design system pairs high-legibility display headings with warm, rhythmic body typography.

| Level | Size (Desktop) | Size (Mobile) | Weight | Line Height | Tracking | Token Class |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Display Title (Hero)** | 32px (2rem) | 26px (1.625rem) | 700 (Bold) | 1.15 | `-0.02em` | `text-2xl md:text-3xl font-bold tracking-tight` |
| **Section Header (H2)** | 22px (1.375rem)| 19px (1.1875rem)| 700 (Bold) | 1.25 | `-0.01em` | `text-lg md:text-xl font-bold tracking-tight` |
| **Card Header (H3)** | 18px (1.125rem)| 16px (1.0rem) | 600 (Semibold)| 1.3 | `normal` | `text-base md:text-lg font-semibold` |
| **Body (Default)** | 15px (0.9375rem)| 14px (0.875rem) | 400 (Regular) | 1.5 | `normal` | `text-sm md:text-base text-stone-700` |
| **Body (Medium / Link)** | 14px (0.875rem) | 13px (0.8125rem)| 500 (Medium) | 1.4 | `normal` | `text-sm font-medium` |
| **Caption / Subtext** | 12px (0.75rem) | 11px (0.6875rem)| 400 (Regular) | 1.4 | `normal` | `text-xs text-stone-500` |
| **Badge / Pill Tag** | 12px (0.75rem) | 11px (0.6875rem)| 600 (Semibold)| 1.0 | `+0.01em` | `text-xs font-semibold px-2.5 py-1 rounded-full` |
| **Portal Header Tag** | 11px (0.6875rem)| 10px (0.625rem) | 600 (Semibold)| 1.0 | `+0.05em` | `text-[11px] uppercase tracking-wider font-semibold text-stone-500` |

---

## 4. Spacing, Grids & Container Radii

### 4.1 Spacing Scale (8pt Grid)
- `space-1`: 4px
- `space-2`: 8px
- `space-3`: 12px
- `space-4`: 16px (standard card interior padding on mobile)
- `space-6`: 24px (standard card interior padding on desktop)
- `space-8`: 32px (section gap)
- `space-10`: 40px (major container separation)

### 4.2 Border Radii System
- **Pills & Buttons**: `rounded-full` (9999px) for search pills, category tags, and primary action buttons.
- **Form Controls & Inputs**: `rounded-xl` (12px).
- **Standard Cards**: `rounded-2xl` (16px) for KPI metrics, upcoming participation, and horizontal event cards.
- **Hero Banners & Major Containers**: `rounded-3xl` (24px) for the large curved golden hero banners and identity overview card.

### 4.3 Elevation & Shadows
- **Card Ambient Shadow**: `box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02), 0 4px 12px rgba(0, 0, 0, 0.03)` (`shadow-xs` / `shadow-sm`).
- **Interactive Card Hover**: `box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 10px 20px -3px rgba(0, 0, 0, 0.05)` (`shadow-md`).
- **Modal / Drawer Shadow**: `box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)` (`shadow-xl`).

---

## 5. Component Specifications

### 5.1 Primary Pill Button (`Button variant="primary"`)
- **Visuals**: Solid golden yellow (`#F5B817`), dark charcoal text (`#1F2421`), `font-semibold text-sm`, `rounded-full` (or `rounded-xl`), `px-5 py-2.5`.
- **Interaction**:
  - Hover: Background `#E5A800`, subtle lift (`-translate-y-0.5`).
  - Active: Scale feedback (`scale-95`).
  - Right Icon: Includes subtle right arrow `ArrowRight` with transition (`group-hover:translate-x-0.5`).

### 5.2 Floating White Card (`Card`)
- **Structure**:
  ```tsx
  <div className="bg-white rounded-2xl md:rounded-3xl border border-[#EFECE6] p-5 md:p-6 shadow-xs hover:shadow-sm transition-all">
    {children}
  </div>
  ```

### 5.3 Curved Golden Hero Banner (`HeroBanner`)
- **Structure**:
  - Warm golden gradient background (`from-[#FFF8E1] via-[#FEE48A] to-[#F5B817]`).
  - Organic curved SVG bottom boundary or rounded-3xl clipping.
  - Left content cluster (tags, headline, subhead, action button or tabs).
  - Right visual container (authentic volunteering photo with curved mask, or celebratory trophy illustration).
  - Background vector motifs (silhouetted flying birds, delicate sunburst rays, leafy silhouettes).

### 5.4 Segmented Tab Pill Bar (`SegmentedTabs`)
- **Structure**:
  - Horizontal container with light grey border or soft transparent backing.
  - Active Tab: Solid yellow pill (`bg-[#F5B817] text-[#1F2421] font-semibold shadow-xs`).
  - Inactive Tab: Clean white pill (`bg-white text-stone-600 border border-stone-200 hover:text-stone-900`).

### 5.5 Form Controls (`Input`, `Select`, `Textarea`)
- **Styling**: `bg-white border border-[#E5E7EB] rounded-xl px-4 py-2.5 text-sm text-[#1F2421] placeholder:text-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:border-transparent transition-all`.
- **Read-Only State**: Soft stone background (`bg-stone-50`), lock icon, and `Read Only` tag.

### 5.6 Privacy & Consent Switch Controls (`ConsentSwitch`)
To strictly preserve the backend affirmative consent architecture, the UI must account for **all six independent consent preferences** defined in `ConsentRecord`:
1. `leaderboard_visible`: Show profile on the public leaderboard.
2. `name_visible`: Show real volunteer name on public leaderboard (if false, appears as Anonymous Volunteer).
3. `thank_you_emails`: Receive milestone and event thank-you email communications.
4. `linkedin_content`: Allow profile and achievements to be featured in LinkedIn celebration drafts.
5. `contact_available`: Share contact details (email/mobile) with event coordinators.
6. `media_usage`: Allow photos and videos featuring the volunteer in Maatram communications.

- **Switch Visuals**:
  - Off: Stone grey track (`bg-stone-300`), white thumb.
  - On: Radiant golden track (`bg-[#F5B817]`), white thumb with soft shadow.
  - Transition: Smooth 200ms spring transition.
- **Governance**: Individual opt-in controls with instant server persistence via `PUT /consents/me`. Visual controls provide clear consent management, without making unverified legal compliance claims.

### 5.7 Dynamic Achievement Container (`AchievementBadgeContainer`)
- **Visual Example Standard**: The medals illustrated in Reference 6 (*First Contribution*, *Community Mentor*, *Consistent Volunteer*) are **visual design examples only**.
- **Backend Single Source of Truth**: The UI dynamically renders only achievements returned by the backend (`GET /gamification/me` -> `VolunteerAchievement`), which are mapped to canonical `AchievementDefinition` records.
- **Strict Rule**: No hardcoded achievement progress, awards, or synthetic eligibility thresholds are introduced.

### 5.8 Empty State Container (`EmptyState`)
- **Components**:
  - Friendly illustration (e.g., desk calendar with Maatram logo, floating clock).
  - Headline in bold display sans-serif (`#1F2421`).
  - Empathetic explanatory copy (`#4B5563`).
  - Primary golden pill action button (`[Browse Opportunities ->]`).

---

## 6. Iconography System

- **Library**: `lucide-react` (consistent with existing codebase and mentor references).
- **Stroke Width**: `1.75px` to `2.0px`.
- **Sizes**:
  - Micro / Inline: `14px` (`w-3.5 h-3.5`).
  - Default / Button: `16px` – `18px` (`w-4 h-4` or `w-4.5 h-4.5`).
  - Nav Rail & Headers: `20px` (`w-5 h-5`).
  - KPI Stat Circle: `24px` (`w-6 h-6`).
