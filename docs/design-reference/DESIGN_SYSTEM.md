# Maatram Volunteer Mobile Application — Global Design System Specification
**Version 1.0 (LOCKED GLOBAL DESIGN AUTHORITY)**
*Approved Source of Truth for Visual Fidelity, Interaction Architecture & Technical Implementation*

---

## 1. Design Philosophy & Core Principles

The Maatram Volunteer Mobile Application is the dedicated digital platform for student volunteers, alumni mentors, and corporate panelists serving with the Maatram Foundation. 

The design system establishes a unified visual and interaction language based on three non-negotiable principles:
1. **Warm Human-Centered Purpose**: A visual tone that honors the service of volunteers through warm cream paper backgrounds (`#FAF8F5`), radiant golden sun accents (`#F5B817`), and authentic photography capturing volunteer collaboration.
2. **Editorial Gravitas**: Georgia serif headlines that lend dignity and distinction to educational volunteering, paired with pristine, highly readable Roboto sans-serif for forms, metadata, and controls.
3. **Structured Simplicity**: A disciplined 4dp/8dp spatial grid, generous touch targets (minimum 48dp), consistent 24dp card curvature, 16dp button curvature, 999dp pill capsules, and smooth, purposeful motion.

---

## 2. Global Token Registry (Authoritative & Locked)

### 2.1 Brand Identity & Surface Palette

| Design Token | Hex Code | Flutter Color Value | Semantic Purpose |
|---|---|---|---|
| **Background (Cream Paper)** | `#FAF8F5` | `Color(0xFFFAF8F5)` | Global canvas background; warm, approachable, non-fatiguing paper tone. |
| **Primary Brand Gold** | `#F5B817` | `Color(0xFFF5B817)` | Golden sun motif, primary CTA buttons, active state indicators, trophy laurels. |
| **Deep Midnight Navy** | `#1B2B48` | `Color(0xFF1B2B48)` | Editorial headings, prominent branding, high-contrast labels, primary icon strokes. |
| **Surface Pure White** | `#FFFFFF` | `Color(0xFFFFFFFF)` | Card bodies, input fields, modal bottom sheets, elevated container surfaces. |
| **Warm Border / Divider** | `#EFECE6` | `Color(0xFFEFECE6)` | Subtle card outlines, segmented pill containers, list separators. |
| **Secondary / Muted Text** | `#827D73` | `Color(0xFF827D73)` | Subtitles, helper text, timestamps, secondary metadata, inactive tabs. |

### 2.2 Volunteer Category Accents

| Volunteer Category | Hex Code | Flutter Color Value | Usage |
|---|---|---|---|
| **Student Volunteer** | `#2563EB` | `Color(0xFF2563EB)` | Category pill, profile badges, student leaderboard filters. |
| **Alumni Volunteer** | `#7C3AED` | `Color(0xFF7C3AED)` | Category pill, mentorship tags, alumni leaderboard filters. |
| **Corporate Panelist** | `#D97706` | `Color(0xFFD97706)` | Interviewer badge, panelist verification chips, corporate filters. |

### 2.3 Semantic & Functional States

| Semantic State | Hex Code | Flutter Color Value | Light Tint Hex / Value | Application |
|---|---|---|---|---|
| **Success / Verified** | `#16A34A` | `Color(0xFF16A34A)` | `#DCFCE7` / `Color(0xFFDCFCE7)` | "Approved" chip, "Completed" attendance badge, form success. |
| **Warning / Pending** | `#D97706` | `Color(0xFFD97706)` | `#FEF3C7` / `Color(0xFFFEF3C7)` | "Under Review", upcoming deadlines, attendance warnings. |
| **Critical / Error** | `#DC2626` | `Color(0xFFDC2626)` | `#FEE2E2` / `Color(0xFFFEE2E2)` | Form validation errors, application rejection, destructive actions. |
| **Info / Scheduled** | `#2563EB` | `Color(0xFF2563EB)` | `#DBEAFE` / `Color(0xFFDBEAFE)` | Event information chips, system notices, link affordances. |

---

## 3. Typography Architecture

### 3.1 Typeface Pairing
- **Editorial Headings**: **Georgia** (Classical serif with warmth and literary prestige).
- **Body, UI, Forms & Controls**: **Roboto** (Clean, neutral, highly legible sans-serif).

### 3.2 Type Scale Specification

| Role | Typeface | Size | Weight | Line Height | Color |
|---|---|---|---|---|---|
| **Headline 1 (Editorial Display)** | Georgia | 28pt | Bold (w700) | 34pt | Deep Navy (`#1B2B48`) |
| **Headline 2 (Section Title)** | Georgia | 20pt | Bold (w700) | 26pt | Deep Navy (`#1B2B48`) |
| **Headline 3 (Card / Group Title)** | Georgia | 17pt | Bold (w700) | 22pt | Deep Navy (`#1B2B48`) |
| **Subtitle / Subheading** | Roboto | 15pt | Regular (w400) | 22pt | Secondary Text (`#827D73`) |
| **Body Large** | Roboto | 15pt | Regular (w400) | 22pt | Deep Navy (`#1B2B48`) |
| **Body Medium (Default)** | Roboto | 14pt | Regular (w400) | 20pt | Deep Navy (`#1B2B48`) |
| **Body Medium Muted** | Roboto | 14pt | Regular (w400) | 20pt | Secondary Text (`#827D73`) |
| **Body Medium Bold** | Roboto | 14pt | SemiBold (w600) | 20pt | Deep Navy (`#1B2B48`) |
| **Form Label** | Roboto | 13pt | SemiBold (w600) | 18pt | Deep Navy (`#1B2B48`) |
| **Button Text** | Roboto | 15pt | SemiBold (w600) | 20pt | Deep Navy / White |
| **Metadata / Timestamp** | Roboto | 12pt | Medium (w500) | 16pt | Secondary Text (`#827D73`) |
| **Caption / Badge / Tag** | Roboto | 11pt | SemiBold (w600) | 14pt | Categorical |
| **Micro Caption** | Roboto | 10pt | Medium (w500) | 14pt | Secondary Text (`#827D73`) |

---

## 4. Spacing, Geometry & Radii

### 4.1 4dp/8dp Spatial Rhythm
- **`2xs` (2dp)**: Icon-to-text sub-pixel nudge.
- **`xs` (4dp)**: Micro-gaps inside badges, tight chip horizontal margins.
- **`sm` (8dp)**: Form field gaps, list item vertical margins, chip horizontal padding.
- **`md` (16dp)**: Standard screen margin, card interior padding, button horizontal padding.
- **`lg` (24dp)**: Section-to-section vertical rhythm, modal interior padding.
- **`xl` (32dp)**: Major layout separation, hero banner clearance.
- **`2xl` (48dp)**: Major page cluster division, minimum touch target height.

### 4.2 Corner Radii Specification
- **Card Surfaces**: **24dp** (`BorderRadius.circular(24)`).
- **Interactive Action Buttons**: **16dp** (`BorderRadius.circular(16)`).
- **Form Text Fields**: **14dp - 16dp** (`BorderRadius.circular(14)`).
- **Pills, Badges & Chips**: **999dp** (Fully rounded capsule: `BorderRadius.circular(999)`).
- **Metric Cards (Compact 2x2)**: **16dp** (`BorderRadius.circular(16)`).
- **Bottom Sheet Dialogs**: **24dp** top corners (`BorderRadius.vertical(top: Radius.circular(24))`).

### 4.3 Elevations & Shadows
- **Card Surface Subtle**: `BoxShadow(color: Color(0x0A000000), blurRadius: 10, offset: Offset(0, 4))`
- **Card Highlight / Floating**: `BoxShadow(color: Color(0x14000000), blurRadius: 16, offset: Offset(0, 6))`
- **Bottom Navigation Bar**: `BoxShadow(color: Color(0x0F000000), blurRadius: 20, offset: Offset(0, -4))`

---

## 5. Component Architectural Blueprints

### 5.1 Official Brand Header Bar
- **Logo Position**: Left-aligned official bilingual Maatram Tamil/English logo with golden sun motif (height: 38dp–44dp).
- **Notification Bell**: Circular button (40dp) with red notification badge containing unread count (e.g. `3`).
- **Profile Avatar**: Circular avatar (40dp) with 2dp Primary Gold ring (`#F5B817`).

### 5.2 4-Destination Persistent Navigation Bar
- **Bar Height**: 64dp + bottom safe area.
- **Destinations**:
  1. `Home` (`Icons.home_rounded`)
  2. `Events` (`Icons.calendar_month_rounded`)
  3. `Leaderboard` (`Icons.emoji_events_rounded`)
  4. `More` (`Icons.grid_view_rounded`)
- **Active State Indicator**: Gold capsule pill (`#F5B817`, height 32dp, radius 16dp) enclosing active icon in Deep Navy (`#1B2B48`), with bold label below.
- **Inactive State**: Muted secondary text and icon (`#827D73`).

### 5.3 Segmented Tab Capsule Selector
- **Container**: Full-width white container with 1dp `#EFECE6` border, 2dp padding, and 999dp pill radius.
- **Tabs**: Equal-width segments. Selected tab displays brand gold pill (`#F5B817`) with Deep Navy text/icon; unselected tabs display muted secondary text (`#827D73`).
- **Transition**: Smooth animated translation and color cross-fade (300ms `Curves.easeInOutCubic`).

### 5.4 Metric & Stat Cards (2x2 Grid)
- **Container**: White surface with 1dp `#EFECE6` border and 16dp radius.
- **Top Row**: Centered golden icon in circular background.
- **Center**: Prominent numerical metric in Deep Navy or Gold (20pt Georgia Bold).
- **Bottom**: Descriptive label in Secondary Text (11pt Roboto Medium).

---

## 6. Motion, Transitions & Micro-Interactions

- **Page Entrance**: Staggered fade and slide-up (300ms–450ms, `Curves.fastOutSlowIn`, 16dp translation).
- **Tab Switching**: Cross-fade and subtle slide (250ms, `Curves.easeInOutCubic`).
- **Button Feedback**: Tactile scale-down (scale: 0.97, 120ms duration) on press.
- **Numbers / Metrics**: Smooth numerical counter tween (`AnimatedCounter`, 800ms duration).
- **Reduced Motion Support**: Instantaneous state shifts when `prefers-reduced-motion` is active.

---

## 7. Strict Prohibitions (Design System Guardrails)

- ❌ **NO Generic Dashboards**: Avoid sterile corporate blue/gray dashboards.
- ❌ **NO Purple/Blue Gradients**: Do not use heavy tech-startup neon gradients.
- ❌ **NO Random Fonts**: Only Georgia (headings) and Roboto (body/UI) are permitted.
- ❌ **NO Unstyled Containers**: Every card must feature `#FFFFFF` fill, 24dp radius, and `#EFECE6` border.
- ❌ **NO Unreadable Text**: Never use placeholder gibberish or unscaled labels.
- ❌ **NO Hardcoded Mock Production Data**: All displayed numbers and metrics in runtime code must come from real API endpoints.
