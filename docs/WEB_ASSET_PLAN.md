# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## Web Application — Visual Asset Strategy & Production Plan

**Document Version:** 1.0.0  
**Status:** Asset Procurement & Optimization Plan  
**Governing Principle:** Authentic branding, preserved typography, and strict prohibition of cropped reference images or artificial volunteer depictions.

---

## 1. Official Maatram Brand Assets

Two canonical logo files are present in the repository root and verified:

| File Name | Physical Dimensions | Aspect Ratio | Color / Format | Designated Production Placement |
| :--- | :--- | :--- | :--- | :--- |
| `maatram_logo-removebg-preview.png` | 709 × 352 px | 2.014 : 1 (~2:1) | Transparent PNG (RGBA) | Public Header, Volunteer Sidebar, Admin Sidebar (with contrast guard), Favicon / Web App Manifest |
| `Maatramlogowithbg.jpeg` | 709 × 352 px | 2.014 : 1 (~2:1) | Opaque JPEG (White BG) | OpenGraph social preview cards (`og:image`), Email notification headers via Resend |

### 1.1 Brand Usage Rules
- **Preserved Aspect Ratio**: The logo must always render at its natural ~2:1 proportion (e.g. `w-[140px] h-[70px]` or `w-[110px] h-[55px]` on mobile).
- **Prohibited Alterations**: Under no circumstances may the official Tamil typography (**மாற்றம்**) or English tagline (*"Educational Aid Foundation"*) be retyped, distorted, horizontally condensed, or recolored.
- **Admin Dark Sidebar Contrast**: When placed on the dark charcoal admin rail (`#16171A`), the logo is rendered within a high-contrast container with an elegant light backdrop chip or inverted brand lockup to guarantee WCAG compliance.

---

## 2. Visual Asset Inventory & Sourcing Strategy

The design reference illustrates 9 screens with rich imagery. Below is the strict sourcing plan for every category:

### 2.1 Landing Page Hero Imagery (Screen 1)
- **Concept**: A photograph of actual Maatram volunteers collaborating or wearing official Foundation shirts, framed by organic warm golden wave curves.
- **Sourcing Rule**: 
  - Sourced from official Maatram Foundation media archives or authentic community photography.
  - **Strictly Prohibited**: Do NOT crop the low-resolution volunteer photograph from the reference collage (`media_1793701809062_b4b2702a.jpg`).
  - **Strictly Prohibited**: Do NOT generate fictional, hyper-realistic AI people posing as Maatram volunteers.
  - **Fallback / Placeholder**: An elegant vector illustration showcasing students and mentors with Maatram's brand colors until production photos are uploaded.

### 2.2 Three Opportunity Pillar Icons & Graphics (Screen 1)
1. **School Visits**:
   - Icon: Graduation cap / Government school illustration.
   - Vector Asset: `public/assets/pillars/school-visits.svg`
   - Purpose: Represents volunteer mentorship in government schools.
2. **Mock Interviews**:
   - Icon: Video conference / 1-on-1 career interview desk illustration.
   - Vector Asset: `public/assets/pillars/mock-interviews.svg`
   - Purpose: Represents career readiness and communication practice.
3. **BGV Support (Background Verification)**:
   - Icon: Document verification with verification seal / shield.
   - Vector Asset: `public/assets/pillars/bgv-support.svg`
   - Purpose: Represents verifying eligibility for scholarship distribution.

### 2.3 Event Banner Photos & Placeholders (Screens 2, 3, 4)
- **Concept**: High-quality 16:9 venue and activity banner images (e.g. Government school facade, interview room, verification center).
- **Cloudinary Dynamic Assets**:
  - Event banners are uploaded and served via Cloudinary with dynamic transformation URLs (`c_fill,w_800,h_450,q_auto,f_auto`).
- **Default Category Fallbacks**:
  - `public/assets/events/default-school-visit.jpg`
  - `public/assets/events/default-mock-interview.jpg`
  - `public/assets/events/default-bgv-support.jpg`

### 2.4 Gamification Badges & Podium Crowns (Screen 5)
- **Canonical Database Achievements (Phase 9)**:
  1. **First Step** (`FIRST_STEP`): Single event completed. Laurel leaf badge with bronze center.
  2. **Dedicated Volunteer** (`DEDICATED_VOLUNTEER`): 10 verified hours. Starburst badge with silver center.
  3. **Pillar of Maatram** (`PILLAR_OF_MAATRAM`): 10 events completed. Shield emblem with gold center.
  4. **Centurion** (`CENTURION`): 100 verified hours. Centurion laurel wreath with platinum center.
- **Podium Accents**:
  - Gold Crown SVG (`public/assets/gamification/crown-gold.svg`) for Rank #1.
  - Silver Laurel Wreath SVG for Rank #2.
  - Bronze Laurel Wreath SVG for Rank #3.

### 2.5 User Avatars & Privacy Masking (Screens 2, 5, 6, 7, 8)
- **User Uploads**: Stored in Cloudinary under `avatars/` with circular thumbnail transformations (`w_120,h_120,c_thumb,g_face`).
- **Default Avatar**: Clean geometric initials avatar with category color ring (Student: Teal, Alumni: Purple, Corporate: Blue).
- **Anonymous Masking (Screen 5)**: When a volunteer's affirmative consent has `name_visible: false` or `leaderboard_visible: false`, the interface renders a neutral silhouette avatar (`public/assets/avatars/anonymous-volunteer.svg`) with label *"Anonymous Volunteer"*.

### 2.6 Empty State & System Illustrations
- **Zero Events Found**: Warm line art illustration of a notebook and magnifying glass (`public/assets/empty/no-events.svg`).
- **No Registrations Yet**: Welcoming illustration encouraging discovery (`public/assets/empty/no-activity.svg`).
- **No Notifications**: Inbox clean illustration (`public/assets/empty/inbox-zero.svg`).
- **Pending Review**: Animated hourglass / verification document (`public/assets/onboarding/pending-review.svg`).

