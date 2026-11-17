# Maatram Volunteer App — M3.5 Motion Choreography & Animation Audit Report
**Consolidated Phase 13 Milestone — Motion System Specification & Accessibility**

---

## 1. Overview & Motion System Architecture

The Maatram Volunteer mobile application incorporates an editorial, purposeful motion choreography system designed to reinforce the warm, community-focused brand identity while maintaining high visual performance (60/120fps).

Animations are not purely decorative; they serve three primary UX purposes:
1. **Spatial Continuity**: Visual transitions establish a clear hierarchy and spatial relationship between screens and modal states.
2. **Data Delight**: Points, volunteer hours, and event metrics celebrate volunteer impact using smooth counter easing.
3. **Accessibility First**: Full compliance with WCAG 2.1 Principle 2.3 (Seizures and Physical Reactions) via automated reduced-motion detection.

---

## 2. Core Motion Primitives Inventory

| Primitive / Widget | Source Location | Duration | Timing Curve | Purpose / Usage |
|---|---|---|---|---|
| **`FadeSlideIn`** | `core/animations/fade_slide_in.dart` | 350–500ms | `Curves.easeOutCubic` | Staggered entrance for cards, headers, list items, and section blocks |
| **`AnimatedCounter`** | `core/animations/animated_counter.dart` | 600–900ms | `Curves.easeOutExpo` | Smooth rolling integer animation for points (180), hours (24), and ranks (#1) |
| **`AnimatedProgress`** | `core/animations/animated_progress.dart` | 800ms | `Curves.easeInOutCubic` | Smooth arc sweep for the 75% circular progress ring on Home Screen |
| **`MaatramCard` Tap Motion**| `core/widgets/cards/maatram_card.dart` | 150ms | `Curves.easeInOut` | Micro-interaction scale down (0.98x) and shadow dampening upon press |
| **Podium Rise** | `features/leaderboard/presentation/` | 500ms | `Curves.elasticOut` | Dynamic staggered vertical expansion of leaderboard podium pillars |
| **Segmented Pill Slider**| `features/events/presentation/` | 250ms | `Curves.easeInOut` | Smooth horizontal translation of the active tab indicator |

---

## 3. Screen-by-Screen Motion Choreography

### 1. Welcome / Splash Screen (WP1)
- **Top Brand Logo**: Soft fade-in at 0ms.
- **Volunteer Hero Photo**: Smooth subtle scale-down from 1.05x to 1.00x over 700ms.
- **Golden Wave Swoop**: Dynamic curve slide-up from bottom boundary with subtle bezier interpolation.
- **Headline & CTAs**: Sequential fade-slide from bottom with 150ms stagger.

### 2. Home Screen (WP4)
- **Stagger 0 (0ms)**: Official logo and greeting text fade in.
- **Stagger 1 (100ms)**: Volunteer profile card with points badge glides in from bottom-left.
- **Stagger 2 (200ms)**: 2x2 metric cards (`Hours`, `Events`, `This Year`, `Rank`) animate with concurrent `AnimatedCounter` rollups.
- **Stagger 3 (300ms)**: Upcoming Events card glides in with hoverable chevron action.
- **Stagger 4 (400ms)**: "Your Progress" circular progress ring sweeps from 0% to 75%.
- **Stagger 5 (500ms)**: "Together for a Better Tomorrow" golden trophy banner glides into view.

### 3. My Activity Screen (WP2)
- **Cupped-Heart Motif**: Gentle floating animation with subtle golden glow.
- **Segmented Tabs**: Fluid pill indicator transition between `Upcoming`, `Completed`, and `Cancelled` without tab-switch flashing.
- **Activity Cards**: Staggered list fade-in with 60ms delay per card.

### 4. Leaderboard Screen (WP6)
- **Podium Entrance**: Staggered rise of the top 3 columns:
  - Rank #2 (Silver, left pillar): Rises at 100ms to 110dp.
  - Rank #3 (Bronze, right pillar): Rises at 180ms to 110dp.
  - Rank #1 (Gold, center pillar): Rises at 260ms to 140dp, followed by golden crown scale pop at 450ms.

---

## 4. Reduced Motion & Performance Compliance

- **Reduced Motion Support**:
  ```dart
  final reduceMotion = MediaQuery.of(context).disableAnimations;
  if (reduceMotion) {
    return child; // Instant render without translation or opacity transitions
  }
  ```
- **Frame Rate Stability**:
  - All motion primitives utilize GPU-composited layers (`Transform.translate`, `Opacity`, `CustomPainter`).
  - Zero layout reflow or widget rebuild triggered during animation ticks.
  - Verified 60fps performance on standard Android and iOS devices.
