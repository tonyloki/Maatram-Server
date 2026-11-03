# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## Web Application — Motion, Interaction & Dynamic Behavior Specification

**Document Version:** 1.0.0  
**Framework:** Motion for React (`framer-motion`) + CSS Micro-Transitions  
**Philosophy:** Purposeful, fluid, respectful of accessibility, and free of gratuitous ornamentation  

---

## 1. Core Motion Principles & Token Variables

Motion in the Maatram Portal serves functional communication: conveying hierarchy, confirming user intent, smoothing state transitions, and celebrating community milestones.

### 1.1 Timing & Easing Curves

```typescript
export const MOTION_TOKENS = {
  // Durations
  durationFast: 0.15,    // Hover, active, focus rings (150ms)
  durationNormal: 0.25,  // Button state changes, dropdowns, tooltips (250ms)
  durationPage: 0.35,    // Modals, card entrances, tab content (350ms)
  durationPodium: 0.55,  // Leaderboard podium elevation, counter roll-up (550ms)

  // Easing Curves
  easeOutExpo: [0.16, 1, 0.3, 1],   // Natural decelerating entrance
  easeInOutQuart: [0.77, 0, 0.175, 1], // Modal scaling & tab indicators
  springSnappy: { type: "spring", stiffness: 400, damping: 30 }, // Buttons & switches
  springGentle: { type: "spring", stiffness: 200, damping: 25 }, // Podiums & cards
};
```

### 1.2 Accessibility & Reduced Motion Directive
Every animated component must inspect `prefers-reduced-motion` via the `useReducedMotion()` hook or CSS `@media (prefers-reduced-motion: reduce)`. 
- **When Reduced Motion is Requested**: Disable all spatial movement (translate-x/y, zoom, parallax). Replace with subtle cross-fades (`opacity` 0 → 1 in 150ms) or instantaneous state updates.

---

## 2. Interaction Specifications by Component

### 2.1 Page Transitions & View Routing
- **Trigger**: Next.js route change across portals.
- **Animation**: Content container fades in with a gentle vertical lift.
- **Variants**:
  ```typescript
  export const pageTransitionVariants = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] } },
    exit: { opacity: 0, y: -4, transition: { duration: 0.15 } }
  };
  ```

### 2.2 Staggered Content Entrances (Grid & Rosters)
- **Trigger**: Initial fetch of event cards, volunteer rows, or metric cards.
- **Behavior**: Parent container staggers children by 40ms. Prevents jarring simultaneous pop-ins.
- **Variants**:
  ```typescript
  export const staggerContainer = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.04 }
    }
  };
  export const staggerItem = {
    hidden: { opacity: 0, y: 12 },
    show: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" } }
  };
  ```

### 2.3 Event Card Hover & Focus States
- **Resting**: Clean `#FFFFFF` surface with subtle border `#EBE6DD` and soft shadow.
- **Hover**: 
  - Elevation: Card translates `translateY(-2px)` with shadow expanding to `0 8px 24px -4px rgba(0,0,0,0.08)`.
  - Image: Subtle zoom `scale(1.02)` within overflow-hidden boundary in 300ms.
  - Border: Soft brand border tint `border-[#F5B817]/40`.
- **Keyboard Focus**: Visible 2px outline offset with `outline-[#F5B817]`.

### 2.4 Button Press & Loading Micro-Interactions
- **Active State**: Pill button scales slightly down `scale(0.98)` on mouse-down/touch.
- **Loading State**:
  - Button text fades out while width remains stable.
  - A circular spinner (`w-4 h-4 border-2 border-current border-t-transparent animate-spin`) fades into center.
  - Button disabled attribute is applied immediately to prevent double-click submissions.

### 2.5 Animated Dashboard Stat Counters
- **Trigger**: Admin Dashboard or Volunteer Profile initial load.
- **Behavior**: Integer values count up smoothly from 0 to the target count over 600ms using an exponential easing curve (e.g. `1,248` total volunteers).
- **Reduced Motion**: Directly renders the final integer without ticker animation.

### 2.6 Leaderboard Top 3 Podium Entrance (Screen 5)
- **Sequence**:
  1. Base table fades in (`opacity: 1`).
  2. Podium pedestals elevate in staggered order: Rank 3 (Bronze, 200ms delay), Rank 2 (Silver, 100ms delay), Rank 1 (Gold, 0ms delay).
  3. Pedestal spring animation: `scaleY: [0.4, 1]` with transform-origin at bottom.
  4. Golden Crown above Rank 1 drops into position with a playful spring bounce (`y: [-12, 0]`, damping 15).
  5. Current user sticky banner at bottom slides up from bottom of viewport (`translateY: [40, 0]`).

### 2.7 Multi-Step Registration Step Transitions (Screen P2)
- **Forward Progression**: Current step slides left (`x: -30, opacity: 0`), new step slides in from right (`x: 30 -> 0, opacity: 1`).
- **Backward Progression**: Current step slides right (`x: 30, opacity: 0`), previous step slides in from left (`x: -30 -> 0, opacity: 1`).
- **Duration**: 280ms easeOutExpo.

### 2.8 Granular Affirmative Consent Switch Interactions (Screen 6)
- **Toggle Action**:
  - Clicking toggle track smoothly shifts knob `translateX(0px)` → `translateX(20px)`.
  - Track color morphs from `#E5E7EB` to `#F5B817` in 180ms.
  - A brief subtle pulse ring expands and fades out (`ring-4 ring-[#F5B817]/30`) confirming state change.
  - Immediate optimistic UI update with debounced background synchronization to `PUT /api/v1/consent/me`.

### 2.9 Real-Time Notification Toast & Bell Badges
- **Arrival**: Toast drops down from top-right viewport: `y: [-20, 0], opacity: [0, 1]` in 250ms.
- **Unread Badge Pulse**: When unread count increments via SSE or polling, the notification bell badge gently scales `scale: [1, 1.25, 1]` once to catch the peripheral eye without persistent strobe.

### 2.10 Skeleton Loading & Empty States
- **Skeleton Shimmer**:
  - Warm neutral background `#F3F0EB` with an animated diagonal gradient shimmer passing horizontally (`background-position: -200%` to `200%` in 1.5s).
- **Empty States**:
  - Illustrated graphic with warm text and clear action button ("No upcoming events found. Check back soon or broaden filters.").
  - Container fades in smoothly once query finishes with 0 records.

