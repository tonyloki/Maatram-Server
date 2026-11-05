# M6_VISUAL_QA_STRATEGY.md — Visual Quality Assurance & Reference Verification Strategy
**Maatram Volunteering & Gamification Portal**  
**Milestone 6.0: Visual QA, Acceptance Gates & Regression Prevention**  
**Date:** November 2026 (Updated with Alignment Corrections)  
**Status:** **ALIGNED STRATEGY SPECIFICATION**

---

## 1. Executive Summary & Quality Objectives

The goal of the Visual QA Strategy is to establish an objective, repeatable methodology for verifying that future implementation phases (M6.1 through M6.9) achieve 100% aesthetic fidelity to the mentor's approved reference designs while maintaining zero functional regressions.

Every redesigned page will be systematically captured, overlaid, and evaluated against the mentor screenshots across four standard viewport tiers.

---

## 2. Benchmark Reference Dimensions & Test Matrix

### 2.1 Native Reference Target Dimensions & Sources
The mentor provided reference screenshots at exact desktop resolutions:
- **Reference 1 (Public Landing)**: Standard desktop `1440 × 900 px` & `1536 × 1024 px` (derived from M2 visual correction).
- **Reference 2 (Dashboard)**: `1536 × 1024 px` (`ui-Reference/Dashboard.jpeg`)
- **Reference 3 (Discover Events)**: `1536 × 1024 px` (`ui-Reference/Discover_Events.jpeg`)
- **Reference 4 (My Activity)**: `1536 × 1024 px` (`ui-Reference/MyActivities.jpeg`)
- **Reference 5 (Leaderboard)**: `1536 × 1024 px` (`ui-Reference/Leaderboard.jpeg`)
- **Reference 6 (My Profile)**: `1600 × 900 px` (`ui-Reference/Profile_page.jpeg`)

### 2.2 Standard Responsive Viewport Test Matrix
Every redesigned route must be verified across four standardized responsive breakpoints:

| Viewport Tier | Width × Height | Emulated Device / Display | Focus of Inspection |
| :--- | :--- | :--- | :--- |
| **Mobile** | `375 × 812 px` | iPhone 13 / Modern Smartphone | Single-column collapse, drawer navigation, touch target sizes (≥44px), zero horizontal overflow |
| **Tablet** | `768 × 1024 px` | iPad Mini / Portrait Tablet | Two-column grid reflow, compact header, touch accessibility |
| **Laptop** | `1366 × 768 px` | Standard HD Laptop | Sidebar layout, content container bounds, proportional scaling |
| **Desktop (Target)** | `1536 × 1024 px` & `1600 × 900 px` | Target Reference Benchmark | Exact side-by-side visual comparison against mentor screenshots |

---

## 3. Browser Capture & Visual Overlay Methodology

### 3.1 Automated & Headless Browser Capture
During implementation verification:
1. The production build of the Next.js frontend (`npm run build && npm run start`) runs locally against the live FastAPI test backend.
2. Captures are executed using Playwright or Chrome DevTools MCP at native device pixel ratios (`dpr: 1` and `dpr: 2`).
3. Viewport width, scroll offsets, and mock data state are normalized to match the reference records (e.g., Volunteer name *"Priya S."*, points `580`, hours `48`).

### 3.2 Visual Comparison Techniques
1. **Side-by-Side Dual Pane**: Render the reference screenshot and browser capture side-by-side in Markdown artifacts (`carousel` or grid) for qualitative review of typography, colors, and balance.
2. **Semi-Transparent Pixel Overlay**: Superimpose the rendered page over the mentor screenshot at 50% opacity to detect spatial drifting, font sizing discrepancies, and margin misalignments.
3. **Difference Image Generation (Diffing)**: Pixel-level diffing algorithms highlight color divergence or missing structural elements in bright magenta/red.

---

## 4. Nine-Point Visual Acceptance Checklist

A page is approved only when it passes all nine criteria:

| Category | Verification Criterion | Validation Method |
| :--- | :--- | :--- |
| **1. Layout Integrity** | Grid alignment, container bounds, sidebar width, and header placement match reference structure without clipping. | Viewport comparison at `1536×1024` & `1600×900` |
| **2. Typography Fidelity** | Font weights, line heights, letter-tracking, and heading-to-body scale match the design system hierarchy. | Computed CSS inspection & visual overlay |
| **3. Color Accuracy** | Exact hex token compliance: warm ivory canvas (`#FAF8F5`), pure white card surfaces (`#FFFFFF`), canonical brand gold (`#F5B817`), and deep charcoal text (`#1F2421`). | Color-picker sampling on rendered canvas |
| **4. Spacing Consistency** | Adherence to the 8pt spatial grid; internal card padding (`24px` desktop / `16px` mobile); consistent section gaps (`32px`). | Computed bounding rect inspection |
| **5. Imagery & Icons** | Authentic human-centered photography, 3D empty state artwork, laurel wreaths, and `lucide-react` icons render crisply with zero distortion. | Visual inspection at 100% zoom |
| **6. Component Reusability** | Shared UI components (`Button`, `Card`, `Badge`, `Switch`, `Input`) render identical variants across all routes without ad-hoc overrides. | Cross-page code audit |
| **7. Consent Preservation** | All six affirmative consent preferences (`leaderboard_visible`, `name_visible`, `thank_you_emails`, `linkedin_content`, `contact_available`, `media_usage`) are individually present and functional. | Verified against `ConsentRecord` API |
| **8. Achievement Governance**| Rendered achievements reflect live backend `VolunteerAchievement` records. Zero hardcoded achievement awards or synthetic criteria. | Database state verification |
| **9. Accessibility & Responsiveness** | Touch targets ≥ 44px; contrast ratios ≥ 4.5:1; zero horizontal scroll on mobile; reduced-motion compliance. | Chrome DevTools Lighthouse audit |

---

## 5. Regression Prevention & Performance Guardrails

1. **Preserve Request Deduplication**: Verify that page re-rendering does not bypass `inFlightGetRequests` or trigger redundant `/users/me` or `/notifications/unread-count` network calls.
2. **Preserve Next.js Static Optimization**: Ensure public pages pre-render statically and client-side chunks remain below 150 KB.
3. **Preserve API Contracts**: Never modify request schemas, response DTOs, or database models during visual refactoring.
