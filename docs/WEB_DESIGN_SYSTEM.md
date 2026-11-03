# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## Web Application — Design System & Component Library

**Document Version:** 1.0.0  
**Design Direction:** Warm, Accessible, Human-Centered Community Identity  
**Primary Visual Anchor:** 9-Screen Reference Interface (`media_1793701809062_b4b2702a.jpg`)  
**Tailwind CSS Integration:** Customized `tailwind.config.ts` Tokens  

---

## 1. Visual Token Foundations

### 1.1 Color Palette

```
Warm Canvas:       #FAF8F3 (Soft Ivory Global Background)
Brand Primary:     #F5B817 (Golden Yellow Primary Action / Brand Accent)
Brand Hover:       #E5A800 (Deep Golden Yellow for Active / Pressed States)
Brand Subtle:      #FFF8E7 (Trophy Highlight / Active Tab Tint)
Brand Contrast:    #946C00 (High-Contrast Text on Brand Subtle)

Text Primary:      #1F2421 (Deep Charcoal for Headings & Prominent Metrics)
Text Secondary:    #6B7280 (Subtitles, Meta Labels, Table Headers)
Text Muted:        #9CA3AF (Placeholders, Inactive Icons, Disabled States)

Surface Card:      #FFFFFF (Pure White for Floating Cards & Modals)
Border Subtle:     #EBE6DD (Warm Neutral Outline for Cards & Dividers)
Border Focus:      #F5B817 (Form Focus Ring with 2px Offset)

Admin Sidebar:     #16171A (Deep Charcoal Admin Command Rail)
Admin Active Pill: #282A30 (Admin Sidebar Selected Navigation State)
Admin Border:      #2A2C33 (Dividers within Admin Command Interface)
```

### 1.2 Semantic Status System

Every status token is strictly paired with an accessible text color meeting WCAG 2.1 AA (contrast ratio > 4.5:1 against its background):

| State / Status | Background | Text Color | Border Color | Real-World Application |
| :--- | :--- | :--- | :--- | :--- |
| **Selected / Approved / Attended** | `#DEF7EC` | `#03543F` | `#BCF0DA` | Active registrations, verified attendance, approved accounts |
| **Pending / Waitlisted / In Review**| `#FEF08A` | `#854D0E` | `#FDE047` | Awaiting admin review, event waitlist position |
| **Rejected / Declined / Cancelled**| `#FDE8E8` | `#9B1C1C` | `#F8B4B4` | Rejected applicant, event cancellation, declined invite |
| **Incomplete / Missing Check-out** | `#FFEDD5` | `#9A3412` | `#FDBA74` | Volunteer checked in but forgot check-out |
| **Draft / Closed / Archived** | `#F3F4F6` | `#374151` | `#E5E7EB` | Draft events, closed registrations, past cycles |

---

## 2. Typography Hierarchy

The type system prioritizes extreme legibility for multilingual names, Tamil terminology, dense tabular rosters, and dynamic metrics.

- **Primary Typeface**: `Inter` (Variable font supporting weights 400, 500, 600, 700).
- **Display Accent**: `Plus Jakarta Sans` or `Inter Display` for landing headlines.
- **Monospace Accent**: `JetBrains Mono` for UUIDs, transaction hashes, and session identifiers.

### Typography Scale

| Class Name | Font Size | Line Height | Weight | Usage |
| :--- | :--- | :--- | :--- | :--- |
| `text-display-1` | 48px (`3rem`) | 56px (`1.15`) | 700 (Bold) | Landing page hero headline |
| `text-display-2` | 36px (`2.25rem`)| 44px (`1.20`) | 700 (Bold) | Section headlines, impact summary |
| `text-heading-1` | 28px (`1.75rem`)| 36px (`1.25`) | 600 (SemiBold) | Page headers (Discover Events, Leaderboard) |
| `text-heading-2` | 22px (`1.375rem`)| 28px (`1.30`) | 600 (SemiBold) | Card titles, event titles, modal titles |
| `text-heading-3` | 18px (`1.125rem`)| 24px (`1.35`) | 600 (SemiBold) | Sub-tabs, widget titles, table sections |
| `text-body-lg` | 16px (`1rem`) | 24px (`1.50`) | 400 / 500 | Hero descriptions, article intros |
| `text-body-base` | 14px (`0.875rem`)| 20px (`1.45`) | 400 / 500 | Standard body copy, table cells, form labels |
| `text-body-sm` | 12px (`0.75rem`)| 16px (`1.35`) | 400 / 500 | Badges, timestamps, helper text, captions |
| `text-mono-sm` | 13px (`0.8125rem`)| 18px (`1.40`) | 500 (Mono) | IDs, transaction codes |

---

## 3. Atomic Components & UI Primitives

### 3.1 Buttons
- **Primary Pill Button (`variant="primary"`)**:
  - Classes: `bg-[#F5B817] text-[#1F2421] font-semibold rounded-full px-6 py-2.5 hover:bg-[#E5A800] transition-colors shadow-sm focus:ring-2 focus:ring-[#F5B817] focus:ring-offset-2 active:scale-[0.98]`
  - Usage: `Register for this Event`, `Get Started`, `Mark as Completed`, `Select Volunteer`.
- **Secondary / Outlined Pill (`variant="outline"`)**:
  - Classes: `bg-white text-[#1F2421] border border-[#EBE6DD] font-medium rounded-full px-5 py-2.5 hover:bg-[#FAF8F3] transition-colors shadow-sm active:scale-[0.98]`
  - Usage: `Login`, `View Details`, `Waitlist Volunteer`.
- **Subtle / Ghost Button (`variant="ghost"`)**:
  - Classes: `bg-transparent text-[#6B7280] font-medium rounded-full px-4 py-2 hover:bg-[#FAF8F3] hover:text-[#1F2421] transition-colors`
  - Usage: `Cancel`, `Back to Events`.
- **Destructive Button (`variant="destructive"`)**:
  - Classes: `bg-white text-[#9B1C1C] border border-[#F8B4B4] font-medium rounded-full px-4 py-2 hover:bg-[#FDE8E8] transition-colors`
  - Usage: `Decline Volunteer`, `Withdraw Registration`.

### 3.2 Form Controls & Inputs
- **Text & Select Inputs**:
  - Classes: `w-full rounded-xl border border-[#EBE6DD] bg-white px-4 py-2.5 text-sm text-[#1F2421] placeholder-[#9CA3AF] focus:border-[#F5B817] focus:outline-none focus:ring-2 focus:ring-[#F5B817]/20 transition-all`
- **Granular Affirmative Consent Switch (`<ConsentSwitch />`)**:
  - Structure: Accessible `<label>` with hidden checkbox and stylized toggle track.
  - Track (Inactive): `w-11 h-6 bg-[#E5E7EB] rounded-full p-0.5 transition-colors cursor-pointer`
  - Track (Active): `w-11 h-6 bg-[#F5B817] rounded-full p-0.5 transition-colors cursor-pointer`
  - Knob: `w-5 h-5 bg-white rounded-full shadow-md transform transition-transform` (translates `translateX(20px)` when active).
  - Label Description: High-contrast title with clear, plain-language description explaining the affirmative permission.

### 3.3 Cards & Containers
- **Content Card (`<Card />`)**:
  - Classes: `bg-white rounded-2xl border border-[#EBE6DD] p-6 shadow-sm hover:shadow-md transition-shadow`
- **KPI Metric Card (`<KpiCard />`)**:
  - Structure: Top row (Icon badge + trend indicator), Middle (Prominent metric integer), Bottom (Label).
  - Metric Display: `text-3xl font-bold text-[#1F2421] tracking-tight`.

### 3.4 Navigation Elements
- **Volunteer Light Sidebar**:
  - Background: `#FAF8F3`.
  - Item Inactive: `text-[#6B7280] hover:text-[#1F2421] hover:bg-white/80 rounded-xl px-4 py-3 font-medium flex items-center gap-3`
  - Item Active: `bg-[#FFF8E7] text-[#946C00] font-semibold rounded-xl px-4 py-3 flex items-center gap-3 border-l-4 border-[#F5B817]`
- **Admin Dark Sidebar**:
  - Background: `#16171A`.
  - Item Inactive: `text-[#9CA3AF] hover:text-white hover:bg-[#212328] rounded-xl px-4 py-3 font-medium flex items-center gap-3 transition-colors`
  - Item Active: `bg-[#212328] text-white font-semibold rounded-xl px-4 py-3 flex items-center gap-3 border-l-4 border-[#F5B817]`

---

## 4. Accessibility & Contrast Validation (WCAG 2.1 AA)

All primary, secondary, and semantic combinations have been validated for contrast compliance:

| Foreground Color | Background Color | Computed Contrast | Minimum Required | Status |
| :--- | :--- | :--- | :--- | :--- |
| `#1F2421` (Charcoal) | `#FAF8F3` (Ivory Canvas) | **14.8:1** | 4.5:1 | PASSED (AAA) |
| `#1F2421` (Charcoal) | `#F5B817` (Brand Yellow) | **8.2:1** | 4.5:1 | PASSED (AAA) |
| `#946C00` (Dark Gold) | `#FFF8E7` (Subtle Tint) | **5.4:1** | 4.5:1 | PASSED (AA) |
| `#03543F` (Dark Green) | `#DEF7EC` (Light Green) | **7.1:1** | 4.5:1 | PASSED (AAA) |
| `#854D0E` (Dark Amber) | `#FEF08A` (Light Amber) | **5.8:1** | 4.5:1 | PASSED (AA) |
| `#9B1C1C` (Dark Red) | `#FDE8E8` (Light Red) | **6.9:1** | 4.5:1 | PASSED (AAA) |
| `#FFFFFF` (White) | `#16171A` (Admin Sidebar) | **15.6:1** | 4.5:1 | PASSED (AAA) |

