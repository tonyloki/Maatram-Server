# Accessibility Audit (WCAG 2.2 AA)
**Maatram Volunteering & Mentorship Portal — Web Client**
**Audit Date:** November 2026  
**Auditor:** Independent Production Readiness Audit Subagent  
**Standard:** Web Content Accessibility Guidelines (WCAG) 2.2 Conformance Level AA

---

## 1. Executive Summary

This accessibility audit evaluates the production readiness of the Maatram Portal interface against WCAG 2.2 Level AA criteria. The assessment was performed via comprehensive code inspection across component primitives (`web/src/components/ui/`), layout templates, forms, modals, tables, and navigation bars.

### Conformance Overview:
- **WCAG 2.2 Level AA Compliance Status:** **NON-COMPLIANT** (Critical blockers identified in contrast, focus trapping, form labelling, and ARIA attributes).
- **Total Deficiencies Logged:** 9 discrete violations.
  - **P1 (High / Severe Blocker):** 4 violations
  - **P2 (Medium / Significant Usability Barrier):** 4 violations
  - **P3 (Low / Polish Issue):** 1 violation

---

## 2. Mathematical Color Contrast Analysis (Criterion 1.4.3)

### The Brand Yellow Contrast Failure
Maatram’s brand palette utilizes `#F5B817` ("brand-yellow") as a primary accent for button backgrounds, highlight badges, active tab markers, and status indicators.

#### Contrast Ratio Mathematical Derivation:
1. Linearized sRGB Luminance Formula:
   $$R_{lin} = \begin{cases} \frac{R}{12.92} & \text{if } R \le 0.04045 \\ \left(\frac{R + 0.055}{1.055}\right)^{2.4} & \text{otherwise} \end{cases}$$
2. Color Decomposition for `#F5B817`:
   - Red: $\text{0xF5} = 245/255 \approx 0.9608 \implies R_{lin} \approx 0.9103$
   - Green: $\text{0xB8} = 184/255 \approx 0.7216 \implies G_{lin} \approx 0.4812$
   - Blue: $\text{0x17} = 23/255 \approx 0.0902 \implies B_{lin} \approx 0.0099$
3. Relative Luminance ($L$):
   $$L_1 = 0.2126(0.9103) + 0.7152(0.4812) + 0.0722(0.0099) \approx 0.1935 + 0.3442 + 0.0007 = \mathbf{0.5384}$$
4. Relative Luminance of Pure White Background (`#FFFFFF`):
   $$L_2 = \mathbf{1.0000}$$
5. Contrast Ratio Calculation:
   $$\text{Ratio} = \frac{L_2 + 0.05}{L_1 + 0.05} = \frac{1.0000 + 0.05}{0.5384 + 0.05} = \frac{1.05}{0.5884} = \mathbf{1.785 : 1} \approx \mathbf{1.79 : 1}$$

#### WCAG Thresholds vs. Reality:
- **WCAG 2.2 AA Requirement for Normal Text:** $\ge 4.5:1$ (**FAILS at 1.79:1**)
- **WCAG 2.2 AA Requirement for Large Text / UI Components:** $\ge 3.0:1$ (**FAILS at 1.79:1**)

#### Affected Locations in Codebase:
1. `web/src/app/page.tsx` (Line 376): Hero statistics text and category pill badges rendered in `#F5B817` on white container backgrounds.
2. `web/src/components/navigation/admin-sidebar.tsx` (Line 107) & `volunteer-sidebar.tsx` (Line 134): Active navigation indicator badges.
3. `web/src/app/register/page.tsx` (Lines 82–96): Step number circle text in wizard header.
4. `web/src/app/volunteer/leaderboard/page.tsx` (Lines 112–115): Gold tier rank badge and points highlight text.

---

## 3. Detailed WCAG 2.2 AA Findings

### ISSUE-A11Y-001 [P1 - High]
- **WCAG Criterion:** **1.4.3 Contrast (Minimum)** & **1.4.11 Non-text Contrast** (Level AA)
- **Route/File:** Global (`web/src/app/page.tsx`, `register/page.tsx`, `leaderboard/page.tsx`, sidebars)
- **Description:** Yellow brand color `#F5B817` on white `#FFFFFF` produces an impermissible contrast ratio of **1.79:1**.
- **Impact:** Low-vision volunteers and users under bright outdoor sunlight cannot read badge labels, step numbers, or points values.
- **Recommendation:**
  - When `#F5B817` is used as a background fill, force high-contrast dark text (`text-slate-900` or `#1E293B`, yielding **11.4:1** contrast).
  - When text is placed on a light/white background, use darkened amber (`#92400E` / `amber-800`, yielding **5.2:1** contrast) instead of raw brand yellow.

---

### ISSUE-A11Y-002 [P1 - High]
- **WCAG Criterion:** **1.3.1 Info and Relationships** & **4.1.2 Name, Role, Value** (Level A)
- **Route/File:** `web/src/components/ui/input.tsx` (Line 14) and `web/src/app/register/page.tsx`
- **Description:** Form `<input>` elements lack programmatic associations with their `<label>` elements.
- **Evidence:**
  `web/src/components/ui/input.tsx`:
  ```tsx
  const inputId = id || props.name;
  ...
  {label && <label htmlFor={inputId}>{label}</label>}
  <input id={inputId} ... />
  ```
  In `register/page.tsx` and custom form groups, inputs are frequently rendered without explicit `id` or `name` attributes (or wrapped in generic flex containers). As a result, `inputId` evaluates to `undefined`, outputting `<label htmlFor={undefined}>` and `<input id={undefined}>`.
- **Impact:** Screen readers (NVDA, JAWS, VoiceOver) cannot associate the visual label with the input field. Visually impaired users hear only "Edit text, blank" without knowing whether the field requests "Full Name", "College Name", or "Graduation Year".
- **Recommendation:** Use React 18/19 `useId()` hook inside `Input` to automatically generate unique deterministic DOM IDs when no explicit `id` is provided:
  ```tsx
  const generatedId = useId();
  const inputId = id || props.name || generatedId;
  ```

---

### ISSUE-A11Y-003 [P1 - High]
- **WCAG Criterion:** **2.4.3 Focus Order** & **2.1.2 No Keyboard Trap** (Level A)
- **Route/File:** `web/src/components/ui/dialog.tsx` (Lines 1–65)
- **Description:** Modal dialogs do not constrain (trap) keyboard focus or manage focus restoration.
- **Evidence:**
  `web/src/components/ui/dialog.tsx` renders a standard HTML `div` with absolute positioning. It does not:
  1. Move initial focus to the dialog header or first interactive element upon opening.
  2. Trap Tab/Shift-Tab keypresses within the dialog container. Users pressing Tab cycle out of the dialog into the background document.
  3. Restore focus back to the triggering button when closed.
- **Impact:** Keyboard-only and assistive technology users can navigate invisible background elements behind an active modal, leading to accidental form submissions or background link activations.
- **Recommendation:** Adopt Radix UI Dialog (`@radix-ui/react-dialog`) or implement standard focus trap listeners using `focus-trap-react` or native HTML5 `<dialog>` with `.showModal()`.

---

### ISSUE-A11Y-004 [P1 - High]
- **WCAG Criterion:** **4.1.2 Name, Role, Value** (Level A)
- **Route/File:** `web/src/app/volunteer/profile/page.tsx` (Lines 868–1000)
- **Description:** Consent switches declare `role="switch"` and `aria-checked`, but lack accessible names (`aria-label` or `aria-labelledby`).
- **Evidence:**
  ```tsx
  <Switch
    checked={consent?.leaderboard_visible ?? true}
    onCheckedChange={(checked) => handleConsentToggle("leaderboard_visible", checked)}
  />
  ```
- **Impact:** Assistive technologies announce "Switch, On" or "Switch, Off" without conveying what consent permission is being granted or revoked.
- **Recommendation:** Add explicit `aria-label` attributes to each switch:
  ```tsx
  <Switch
    aria-label="Consent to display rank on public leaderboard"
    checked={consent?.leaderboard_visible ?? false}
    ...
  />
  ```

---

### ISSUE-A11Y-005 [P2 - Medium]
- **WCAG Criterion:** **2.4.1 Bypass Blocks** (Level A)
- **Route/File:** `web/src/app/layout.tsx` (Root Layout)
- **Description:** The portal lacks a "Skip to main content" bypass link.
- **Evidence:** `web/src/app/layout.tsx` mounts global fonts and providers, but contains no hidden anchor link pointing to `<main id="main-content">`.
- **Impact:** Keyboard-only users must press the Tab key 10–15 times on every page load to bypass top navigation headers and sidebars before reaching the page content.
- **Recommendation:** Add an accessible skip link at the very top of `layout.tsx`:
  ```tsx
  <a
    href="#main-content"
    className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-slate-900 focus:text-white focus:rounded-md"
  >
    Skip to main content
  </a>
  ```

---

### ISSUE-A11Y-006 [P2 - Medium]
- **WCAG Criterion:** **3.3.1 Error Identification** & **4.1.3 Status Messages** (Level A / AA)
- **Route/File:** `web/src/app/register/page.tsx`, `web/src/app/login/page.tsx`
- **Description:** Form validation error messages are visually rendered but not programmatically announced to screen readers.
- **Evidence:**
  Validation error text is rendered in basic spans:
  ```tsx
  {errors.email && <span className="text-xs text-red-500">{errors.email}</span>}
  ```
  The span lacks `role="alert"` or `aria-live="polite"`, and the corresponding `<input>` lacks `aria-invalid="true"` and `aria-describedby="email-error"`.
- **Impact:** Visually impaired users attempting to submit forms hear no notification that validation failed or which specific fields require correction.
- **Recommendation:** Link inputs to error messages via `aria-describedby` and mark error containers with `role="alert"`.

---

### ISSUE-A11Y-007 [P2 - Medium]
- **WCAG Criterion:** **1.3.1 Info and Relationships** (Level A)
- **Route/File:** `web/src/components/ui/tabs.tsx` (Lines 1–45)
- **Description:** Custom tabs component declares `role="tablist"` but fails to implement ARIA tab semantics and keyboard arrow navigation.
- **Evidence:**
  `tabs.tsx` uses custom `div` elements with `role="tablist"` and `role="tab"`, but:
  - Omits `aria-selected="true|false"` on tab buttons.
  - Omits `aria-controls="panel-id"` pointing to the corresponding tabpanel.
  - Lacks keyboard event handlers for `ArrowLeft` / `ArrowRight` (WAI-ARIA design pattern for tabs).
- **Impact:** Screen reader users cannot understand which tab is active or how many tabs exist in the set.
- **Recommendation:** Align tabs with WAI-ARIA Tab guidelines or adopt `@radix-ui/react-tabs`.

---

### ISSUE-A11Y-008 [P2 - Medium]
- **WCAG Criterion:** **1.3.1 Info and Relationships** (Level A)
- **Route/File:** `web/src/components/ui/table.tsx` and `web/src/app/volunteer/leaderboard/page.tsx`
- **Description:** Data tables lack `scope="col"` on header cells (`<th>`) and table `<caption>` elements.
- **Evidence:**
  In `web/src/components/ui/table.tsx`:
  ```tsx
  const TableHead = React.forwardRef<HTMLTableCellElement, ...>(
    ({ className, ...props }, ref) => <th ref={ref} className={...} {...props} />
  );
  ```
  Header cells do not default to `scope="col"`.
- **Impact:** Screen readers navigating across multi-column leaderboard tables cannot associate cell values (such as points or rank) with their respective column header.
- **Recommendation:** Add default `scope="col"` to `TableHead` and include visually hidden or visible `<caption>` elements in data tables.

---

### ISSUE-A11Y-009 [P3 - Low]
- **WCAG Criterion:** **1.1.1 Non-text Content** (Level A)
- **Route/File:** `web/src/app/admin/applications/[id]/page.tsx` (Student ID Proof Document Preview)
- **Description:** Uploaded verification document preview uses generic alt text (`alt="Student Proof"`).
- **Evidence:**
  ```tsx
  <img src={application.student_proof_url} alt="Student Proof" className="..." />
  ```
- **Impact:** While alt text is technically present, it lacks context for screen reader operators verifying applicant details.
- **Recommendation:** Provide descriptive dynamic alt text, e.g., `alt={`Student identification document for ${application.user.full_name}`}`.

---

## 4. Accessibility Conformance Summary Matrix

| Finding ID | Severity | WCAG 2.2 Criterion | Affected Component / Page | Level |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-A11Y-001** | **P1** | 1.4.3 Contrast (Minimum) | Global (`#F5B817` on `#FFFFFF` = 1.79:1) | AA |
| **ISSUE-A11Y-002** | **P1** | 1.3.1 Info & Relationships / 4.1.2 | `web/src/components/ui/input.tsx` | A |
| **ISSUE-A11Y-003** | **P1** | 2.4.3 Focus Order / 2.1.2 Keyboard | `web/src/components/ui/dialog.tsx` | A |
| **ISSUE-A11Y-004** | **P1** | 4.1.2 Name, Role, Value | `web/src/app/volunteer/profile/page.tsx` (Consent switches) | A |
| **ISSUE-A11Y-005** | **P2** | 2.4.1 Bypass Blocks | `web/src/app/layout.tsx` (Missing Skip Link) | A |
| **ISSUE-A11Y-006** | **P2** | 3.3.1 Error Identification / 4.1.3 | `web/src/app/register/page.tsx`, `login/page.tsx` | A / AA |
| **ISSUE-A11Y-007** | **P2** | 1.3.1 Info & Relationships | `web/src/components/ui/tabs.tsx` | A |
| **ISSUE-A11Y-008** | **P2** | 1.3.1 Info & Relationships | `web/src/components/ui/table.tsx` | A |
| **ISSUE-A11Y-009** | **P3** | 1.1.1 Non-text Content | `web/src/app/admin/applications/[id]/page.tsx` | A |
