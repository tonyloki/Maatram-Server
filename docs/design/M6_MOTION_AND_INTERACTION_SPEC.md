# M6_MOTION_AND_INTERACTION_SPEC.md — Motion & Interaction Design Specification
**Maatram Volunteering & Gamification Portal**  
**Milestone 6.0: Motion Principles, Choreography & Accessibility**  
**Date:** November 2026 (Updated with Alignment Corrections)  
**Status:** **APPROVED SPECIFICATION**

---

## 1. Motion Philosophy & Core Principles

Motion in the Maatram Volunteering & Gamification Portal is **purposeful, warm, and restrained**. It reinforces user orientation, provides immediate feedback, and celebrates volunteer impact without delaying content access or triggering vestibular discomfort.

### Core Motion Principles:
1. **Never Block Content**: Animations must never delay user interaction. Critical information (headings, stats, buttons) must remain immediately accessible and indexable.
2. **Organic Physics**: Transitions employ gentle spring or natural cubic-bezier curves (`cubic-bezier(0.16, 1, 0.3, 1)`) reflecting real-world physical inertia rather than mechanical linear motion.
3. **Restraint & Dignity**: Avoid bouncy, exaggerated cartoon movements. Community service is dignified; animations should feel warm, polished, and calm.
4. **Absolute Accessibility**: Complete respect for the `prefers-reduced-motion` media query. Users with vestibular sensitivities receive zero motion or instant opacity fades.

---

## 2. Motion Tokens & Timing Scale

| Token Name | Duration | Easing Function | Intended Usage |
| :--- | :--- | :--- | :--- |
| `motion-fast` | 150ms | `cubic-bezier(0.4, 0, 0.2, 1)` | Micro-interactions: Button hover, switch toggle, icon rotation |
| `motion-medium` | 250ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Element transitions: Tab switching, dropdown menus, card hover lift |
| `motion-slow` | 350ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Major UI shifts: Modal dialog entry, mobile drawer slide, notification toasts |
| `motion-shimmer`| 1500ms | `linear` (Infinite) | Skeleton loader background shimmer gradient |

---

## 3. Choreography & Interaction Rules

### 3.1 Page & Route Transitions
- **Behavior**: When navigating between volunteer sub-pages (e.g., from Dashboard to Discover Events), the incoming container performs a gentle fade-in (`opacity: 0` to `opacity: 1`) combined with a 4px upward drift (`y: 4` to `y: 0`) over 200ms.
- **Implementation**:
  ```typescript
  export const pageTransitionVariants = {
    initial: { opacity: 0, y: 4 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] } },
    exit: { opacity: 0, transition: { duration: 0.15 } },
  };
  ```

### 3.2 Navigation Rail Active Indicator (Framer Motion `layoutId`)
- **Behavior**: As the volunteer clicks between sidebar links (Dashboard -> Discover Events -> Leaderboard), the golden pill background (`#FFF8E7`) slides smoothly behind the active item using Framer Motion's shared `layoutId="activeNavPill"`.
- **Timing**: 250ms spring (`stiffness: 400`, `damping: 30`).
- **Benefit**: Creates a seamless, high-end native application feel.

### 3.3 Card Hover & Interaction Lift
- **Behavior**: Interactive opportunity cards and metric cards exhibit a subtle upward elevation:
  - `transform: translateY(-2px)`
  - `box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 10px 20px -3px rgba(0, 0, 0, 0.05)`
  - `border-color: #E5E0D8`
- **Timing**: 200ms ease-out.
- **Rule**: Never translate more than 2px to maintain visual stability.

### 3.4 Button Feedback & Press States
- **Hover**: Background shifts to hover token (`#E5A800`), right arrow icon drifts 2px to the right (`translate-x-0.5`).
- **Active / Press**: Tactile scale depression (`scale: 0.97`) over 100ms.
- **Focus Visible**: Accessible double ring: `focus-visible:ring-2 focus-visible:ring-[#F5B817] focus-visible:ring-offset-2`.
- **Loading**: Spinner replaces arrow icon while button text dims slightly (`opacity: 0.8`), maintaining exact button width to prevent layout jump.

### 3.5 Segmented Tab Switching
- **Behavior**: On `/volunteer/activity` and `/volunteer/leaderboard`, switching tabs moves the active pill indicator smoothly to the newly selected tab.
- **Timing**: 200ms spring transition.

### 3.6 Modal Dialog & Overlay Transitions
- **Backdrop**: Fades from `opacity: 0` to `opacity: 0.4` (`bg-stone-950/40 backdrop-blur-xs`) over 200ms.
- **Modal Card**: Scales gently from `scale: 0.96` to `scale: 1.0` with fade-in over 250ms ease-out.
- **Exit**: Direct fade-out over 150ms.

### 3.7 Form Feedback & Affirmative Consent Switches
- **Consent Switch**: Thumb glides across the track with a crisp spring motion (180ms), with immediate color transition on the track (`#D1D5DB` -> `#F5B817`).
- **Inline Validation**: Error alerts slide down smoothly (`height: auto`, `opacity: 1`) over 150ms, accompanied by a subtle 2px lateral shake if invalid input is submitted.

### 3.8 Skeleton Loading Shimmer
- **Visuals**: Skeletons use warm neutral grey (`#F3EFEA`) with a subtle lighter highlight (`#FAF8F5`) sweeping horizontally every 1.5 seconds.
- **Timing**: Infinite linear sweep.

### 3.9 Leaderboard Podium Entry Choreography
- When the Leaderboard page loads, the top-3 pedestals stage their entrance sequentially:
  1. 2nd Place (Silver) rises from `y: 20` over 300ms.
  2. 1st Place (Gold) rises from `y: 25` over 350ms (delayed by 80ms for triumphant emphasis).
  3. 3rd Place (Bronze) rises from `y: 15` over 300ms (delayed by 160ms).
  4. Subtle golden sunburst rays gently fade into full brilliance behind the podium.

---

## 4. Strict Accessibility & Reduced Motion Support

In full compliance with [WCAG 2.2 Guideline 2.3 (Seizures and Physical Reactions)](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html):

```css
@media (prefers-reduced-motion: reduce) {
  *,
  ::before,
  ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

- When `prefers-reduced-motion` is detected:
  - All positional shifts (`transform: translateY`, `y: 20`) are disabled.
  - Skeletons use static pulsing opacity rather than continuous moving gradients.
  - Modals and drawers appear via instant opacity toggle (`opacity: 1`).
  - No animation is permitted to delay page accessibility or hide content behind unresolved variant keys.
