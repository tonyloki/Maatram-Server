# M6_REFERENCE_ANALYSIS.md — In-Depth Analysis of Mentor UI Reference Images
**Maatram Volunteering & Gamification Portal**  
**Milestone 6.0: Design Discovery & Visual Decomposition**  
**Date:** November 2026 (Updated with Alignment Corrections)  
**Status:** **ALIGNED REFERENCE ANALYSIS**

---

## 1. Executive Summary & Inventory of All Six Mentor References

The mentor provided five high-resolution reference screenshots in `ui-Reference/` capturing the authenticated volunteer experience, alongside the visual language for the public website established in the approved Milestone 2 visual correction report.

Every reference was inspected directly at native resolution to extract colors, typography, spatial rhythms, card constructions, decorative treatments, and interaction patterns.

### Complete Inventory of All Six References & Source Files:
1. **Reference 1: Public Landing Page** — Derived from the mentor design system and approved Milestone 2 visual correction. (Source specification: `docs/execution-groups/MILESTONE_2_VISUAL_CORRECTION_REPORT.md` and `web/src/app/page.tsx`).
2. **Reference 2: Volunteer Dashboard** — Source file: `ui-Reference/Dashboard.jpeg` (Dimensions: `1536 × 1024 px`, File size: 302.5 KB).
3. **Reference 3: Discover Events** — Source file: `ui-Reference/Discover_Events.jpeg` (Dimensions: `1536 × 1024 px`, File size: 305.7 KB).
4. **Reference 4: My Activity** — Source file: `ui-Reference/MyActivities.jpeg` (Dimensions: `1536 × 1024 px`, File size: 201.8 KB).
5. **Reference 5: Leaderboard** — Source file: `ui-Reference/Leaderboard.jpeg` (Dimensions: `1536 × 1024 px`, File size: 218.4 KB).
6. **Reference 6: My Profile** — Source file: `ui-Reference/Profile_page.jpeg` (Dimensions: `1600 × 900 px`, File size: 226.6 KB).

### Rigor Methodology:
To maintain complete integrity, each analysis separates:
- **[OBSERVED]**: Concrete visual details directly visible in the reference screenshots.
- **[INFERRED]**: Logical design extrapolations (e.g., hover states, animations, mobile collapse).
- **[UNDETERMINED]**: Attributes not ascertainable from static desktop screenshots (e.g., scroll behaviors, dynamic tooltips).

---

## 2. Analysis of Reference 2: Volunteer Dashboard

**Source File**: `ui-Reference/Dashboard.jpeg` (`1536 × 1024 px`)

### 2.1 Layout Composition & Grid
- **[OBSERVED]**: Two-column layout with a fixed-width left navigation rail (~260px) and a wide main content container (~1240px) set on a warm cream canvas (`#FAF8F5`).
- **[OBSERVED]**: Main container consists of four vertical tiers:
  1. Top header line with breadcrumb / portal title and profile pill.
  2. Full-width curved golden hero welcome banner.
  3. "Your Contribution at a Glance" 4-metric KPI row with year dropdown selector.
  4. Asymmetric split content section (2/3 left column for upcoming & recommended events, 1/3 right column for guide & progress).
- **[INFERRED]**: On tablet (<1024px), the asymmetric split stacks into a single column. On mobile (<640px), the sidebar collapses into an accessible slide-over drawer.

### 2.2 Header & Left Navigation Rail
- **[OBSERVED]**: Left rail is styled as an independent, floating white card (`#FFFFFF`, `rounded-2xl`, subtle border `#EFECE6`, soft ambient shadow).
- **[OBSERVED]**: Top features the official Maatram Foundation logo (Tamil script + English).
- **[OBSERVED]**: Navigation items:
  - *Dashboard* (Active): Soft yellow pill background (`#FFF8E7` / `#FDE68A`), dark charcoal text (`#1F2421`), Home icon.
  - *Discover Events*: Ghost link, Compass icon.
  - *My Activity*: Ghost link, CalendarCheck icon.
  - *Leaderboard*: Ghost link, Trophy icon.
  - *My Profile*: Ghost link, User icon.
  - *Notifications*: Ghost link, Bell icon, bright red circular badge with count `"3"`.
- **[OBSERVED]**: Bottom of sidebar includes:
  - User summary card: Circular avatar badge `"P"`, username `"priya.s"`, role `"Student Volunteer"`, chevron right.
  - Volunteer Helpdesk card: Headset icon, `"Volunteer Helpdesk"`, email `volunteers@maatramfoundation.org`.
  - Botanical flourish: Gentle golden wheat/leaves watermark decorating the bottom-left corner of the sidebar canvas.
- **[OBSERVED]**: Top header bar displays `"MAATRAM VOLUNTEERING & MENTORSHIP PORTAL"` in crisp, small uppercase tracking, notification bell with red indicator dot, and user avatar pill `"PR priya.s v"`.

### 2.3 Hero Welcome Banner
- **[OBSERVED]**: Curved, elongated banner with warm golden-yellow gradient background (`#FFF8E1` via `#FEE48A` to `#F5B817`).
- **[OBSERVED]**: Top badges:
  - `[Student Volunteer]`: Warm amber pill (`#FEF3C7`, text `#78350F`).
  - `[Approved]`: Soft mint green pill with checkmark (`#DCFCE7`, text `#166534`).
- **[OBSERVED]**: Headline: `"Welcome back, Priya!"` in bold display sans-serif (~32px, `#1F2421`).
- **[OBSERVED]**: Subtitle: `"Thank you for mentoring scholars and supporting higher education access."` (~15px, `#4B5563`).
- **[OBSERVED]**: Right side: Authentic photograph of volunteers wearing black Maatram t-shirts (showing logo in Tamil) looking out across a scenic field toward a large tree under sunlight. Silhouetted birds in flight and gentle tree silhouettes integrate into the golden banner.
- **[OBSERVED]**: Action CTA: Rounded pill button `"Discover Opportunities ->"` in solid canonical gold (`#F5B817`, text `#1F2421`).

### 2.4 Contribution KPI Row
- **[OBSERVED]**: Section title `"Your Contribution at a Glance"` with chart icon and right-aligned dropdown `"Cycle Year: 2026 v"`.
- **[OBSERVED]**: 4 white metric cards (`#FFFFFF`, `rounded-2xl`, subtle border `#EFECE6`, soft shadow):
  1. **Volunteering Points**: Big number `"0"`, subtext `"Events x 10 + Hours x 2"`, yellow star icon in soft yellow circular glow.
  2. **Approved Hours**: Big number `"0.0"`, subtext `"Verified service"`, green clock icon in soft green circular glow with checkmark.
  3. **Events Attended**: Big number `"0"`, subtext `"Completed drives"`, blue calendar icon in soft blue circular glow.
  4. **Current Rank**: Dash `"—"`, subtext `"View leaderboard ->"`, orange trophy icon in soft orange circular glow.

### 2.5 Lower Grid: Participation, Opportunities, Guide, & Progress
- **[OBSERVED]**: Left Column:
  - **Your Upcoming Participation** (`All Activity History ->`):
    - White card with friendly empty state illustration: 3D desk calendar showing Maatram logo, headline `"Your next impact starts here"`, body `"You have no upcoming registrations yet. Explore published opportunities to get involved."`, and golden pill button `"Browse Opportunities"`.
  - **Recently Viewed / Recommended Opportunities** (`View All Events ->`):
    - Section header with flame icon.
    - Two opportunity cards side by side:
      - *School Visit*: Real photo, date `"26 Oct 2025"`, green pill `[Onsite]`, brief description, `"View Event ->"`.
      - *Mock Interview*: Real photo, date `"28 Oct 2025"`, blue pill `[Online]`, brief description, `"View Event ->"`.
- **[OBSERVED]**: Right Column:
  - **Volunteering Guide**:
    - White card with numbered steps 1, 2, 3 in solid yellow circles:
      - `1` Apply for an event
      - `2` Wait for selection
      - `3` Check in and complete your contribution
    - Right graphic: Stylized hand holding golden heart with sunburst rays and slogan `"Together for a better tomorrow"`.
  - **Your Progress** (`View Details ->`):
    - Donut progress chart (62% filled in golden yellow `#F5B817` against cream track).
    - Encouraging copy: `"Keep going, Priya! You're making a difference in the community."`.
    - Golden milestone pill: `"1 more event to reach the next milestone 🎉"`.

---

## 3. Analysis of Reference 3: Discover Events

**Source File**: `ui-Reference/Discover_Events.jpeg` (`1536 × 1024 px`)

### 3.1 Layout Composition & Grid
- **[OBSERVED]**: Consistent left sidebar rail (active item: *Discover Events* with yellow pill background).
- **[OBSERVED]**: Main container consists of:
  1. Golden hero banner: Title `"Discover Events"`, subtitle `"Explore volunteering opportunities, mentor students and make a difference together."`, right photo of volunteers in black Maatram t-shirts.
  2. Prominent full-width search input card with search icon and solid yellow `"Search"` pill button.
  3. Filter pill bar: Category buttons (`All`, `School Visit`, `Mock Interview`, `BGV Support`, `Admissions`, `Panel Interview`) + right-aligned `"Sort by: Most Recent v"` and filter icon button.
  4. Vertical stack of full-width horizontal event opportunity cards.
  5. Sidebar bottom feature: In place of the user card, the left sidebar features a prominent `"Together for a Better Tomorrow"` card with the hand-heart illustration.

### 3.2 Horizontal Event Card Construction
- **[OBSERVED]**: Each event card is a clean, elongated white card (`#FFFFFF`, `rounded-2xl`, border `#EFECE6`, soft shadow):
  - **Left**: Fixed-ratio photographic thumbnail (~240 × 140 px, `rounded-xl`, cover fit):
    - Card 1: School building exterior (Government High School).
    - Card 2: Professional mentor and student in mock interview.
    - Card 3: Clipboard with "BGV" documents on desk.
    - Card 4: Graduates tossing mortarboards in the air (Admissions Guidance).
  - **Middle**:
    - Event Title: Bold sans-serif (~18px, `#1F2421`).
    - Subtitle / Impact hook: E.g., `"Interact with school students and share your journey."`
    - Metadata row: Calendar icon + Date (e.g., `7 Nov 2026`), Clock icon + Time (e.g., `9:00 AM – 1:00 PM`), Pin icon + Location (e.g., `Chennai` or `Online`).
    - Category Tag Pill:
      - `School Visit`: Soft yellow pill (`#FEF3C7`, text `#92400E`).
      - `Mock Interview`: Soft blue pill (`#E0F2FE`, text `#0369A1`).
      - `BGV Support`: Soft lavender pill (`#EDE9FE`, text `#6D28D9`).
      - `Admissions`: Soft peach pill (`#FFEDD5`, text `#C2410C`).
  - **Right**:
    - Top bookmark / save icon.
    - Bottom primary action button: Solid golden yellow pill button `"View Details ->"`.

---

## 4. Analysis of Reference 4: My Activity

**Source File**: `ui-Reference/MyActivities.jpeg` (`1536 × 1024 px`)

### 4.1 Layout Composition & Grid
- **[OBSERVED]**: Consistent left sidebar (active item: *My Activity* with yellow pill background).
- **[OBSERVED]**: Main container consists of:
  1. Golden hero banner: Calendar-check icon badge, Title `"My Activity"`, subtitle `"Track your volunteering journey, view your events and contributions, and monitor your progress in the Maatram community."`, right photo of volunteers in black Maatram t-shirts.
  2. Segmented tab pill bar:
     - `Upcoming (0)`: Active pill (solid yellow `#F5B817`, dark text `#1F2421`, calendar icon).
     - `Ongoing (0)`: Inactive pill (white, border `#E5E7EB`, check-circle icon).
     - `Past (0)`: Inactive pill (white, border `#E5E7EB`, star icon).
     - `Points Ledger`: Inactive pill (white, border `#E5E7EB`, bar chart icon).
  3. Large white card containing the empty state experience.

### 4.2 Empty State Composition
- **[OBSERVED]**: Centered empty state artwork:
  - 3D-styled desk calendar with Maatram brand colors, alongside a floating circular clock with hour and minute hands.
  - Warm sunburst rays and soft golden leaves framing the calendar.
- **[OBSERVED]**: Headline: `"No upcoming activities"` in bold sans-serif (~24px, `#1F2421`).
- **[OBSERVED]**: Body: `"You haven't registered for any upcoming events yet. Discover events and start volunteering today!"` (~15px, `#4B5563`).
- **[OBSERVED]**: Action CTA: Rounded pill button `"Discover Events ->"` with magnifying glass icon in solid golden yellow (`#F5B817`).
- **[OBSERVED]**: Ambient card background: Subtle warm cream wave contours gently framing the bottom and top corners of the card.

---

## 5. Analysis of Reference 5: Leaderboard

**Source File**: `ui-Reference/Leaderboard.jpeg` (`1536 × 1024 px`)

### 5.1 Layout Composition & Hero Banner
- **[OBSERVED]**: Consistent left sidebar (active item: *Leaderboard* with yellow pill background).
- **[OBSERVED]**: Main hero banner:
  - Golden crown icon hovering over bold title `"Leaderboard"`.
  - Subtitle: `"Recognizing dedicated volunteers across mentorship, interviews, and community initiatives."`.
  - Right: Year dropdown filter `"Year: 2025 v"`.
  - Artwork: Large golden trophy with star emblem, framed by a silhouetted crowd of cheering volunteers with raised hands in golden monochrome.

### 5.2 Category Filter Bar
- **[OBSERVED]**: Horizontal pill tabs:
  - `Overall`: Active pill (solid yellow `#F5B817`, trophy icon).
  - `Students`: Inactive pill (white, border `#E5E7EB`, graduation cap icon).
  - `Alumni`: Inactive pill (white, border `#E5E7EB`, user-group icon).
  - `Corporate`: Inactive pill (white, border `#E5E7EB`, building icon).

### 5.3 Top 3 Podium Presentation
- **[OBSERVED]**: Distinctive 3-step physical podium pedestal:
  - **1st Place (Center — Elevated)**:
    - Tallest golden pedestal (`#FEF08A` to `#FDE047` gradient base).
    - Gold crown icon `#1` floating above avatar.
    - Large circular portrait photo (Priya S.) framed in golden border with flanking laurel wreath branches.
    - Name: `"Priya S."` in bold sans-serif (~18px).
    - Points: `"580 pts"` in bold charcoal (~16px).
  - **2nd Place (Left — Mid height)**:
    - Silver pedestal base (`#E2E8F0` to `#CBD5E1`).
    - Silver crown badge `#2`.
    - Circular portrait photo (Arun K.).
    - Name: `"Arun K."`, Points: `"520 pts"`.
  - **3rd Place (Right — Lowest height)**:
    - Bronze pedestal base (`#FED7AA` to `#FDBA74`).
    - Bronze crown badge `#3`.
    - Circular portrait photo (Sneha R.).
    - Name: `"Sneha R."`, Points: `"460 pts"`.
- **[OBSERVED]**: Celebratory golden confetti rays radiate outward behind the top-3 pedestals.

### 5.4 Ranking Data Table
- **[OBSERVED]**: White card table below podium with crisp headers:
  - `#` | `VOLUNTEER` | `CATEGORY` | `POINTS` | `HOURS` | `TREND`
- **[OBSERVED]**: Rank Rows:
  - Rank 1: Yellow circle badge `1`, user icon, name `"Priya S."`, pill `You`, category `STUDENT`, points `580`, hours `48`, upward green trend arrow. Entire row highlighted in soft warm yellow (`#FEF9C3`).
  - Rank 2: Grey circle badge `2`, user icon, `"Arun K."`, category `STUDENT`, points `520`, hours `46`, neutral dash.
  - Rank 3: Orange circle badge `3`, user icon, `"Sneha R."`, category `STUDENT`, points `460`, hours `40`, neutral dash.
  - Rank 4: Plain number `4`, `"Karthik V."`, category `STUDENT`, points `420`, hours `36`, upward green trend arrow.
  - Rank 5: Plain number `5`, `"Meena L."`, category `ALUMNI`, points `380`, hours `32`, downward red trend arrow.

---

## 6. Analysis of Reference 6: My Profile

**Source File**: `ui-Reference/Profile_page.jpeg` (`1600 × 900 px`)

### 6.1 Layout Composition & Header
- **[OBSERVED]**: Consistent left sidebar (active item: *My Profile* with yellow pill background).
- **[OBSERVED]**: Top header: Title `"My Profile"` with a vertical golden accent bar on the left, subtitle `"Manage your volunteer identity, academic details, preferences and contribution settings."`.
- **[OBSERVED]**: Layout splits into:
  - Left column (~320px): Identity summary card.
  - Right column (~960px): Tabbed editing panels and bottom dual cards (Privacy toggles + Achievements).

### 6.2 Left Column: Identity Card
- **[OBSERVED]**: White card with warm golden wave background header.
- **[OBSERVED]**: Centered circular portrait photo with camera overlay icon for photo uploads.
- **[OBSERVED]**: Name: `"Priya S."` (~22px bold).
- **[OBSERVED]**: Status badge: Mint green pill `[Approved]` with checkmark.
- **[OBSERVED]**: Volunteer category pill: Golden pill `[STUDENT VOLUNTEER]`.
- **[OBSERVED]**: Short bio: `"Passionate about volunteering and creating a positive impact in the community."`.
- **[OBSERVED]**: Contact & Academic list with clean icons:
  - Email: `priya.s@maatram.org`
  - Mobile: `+91 9876543210`
  - College: `Sathyabama Institute of Science and Technology`
  - Degree: `B.E. | ECE`
  - Year: `2nd Year`
- **[OBSERVED]**: 3-metric mini KPI bar at bottom of card:
  - Clock icon: `24 Approved Hours`
  - Star icon: `180 Points`
  - Calendar icon: `8 Events`
- **[OBSERVED]**: Action button: Outline pill button with edit pencil icon: `"Edit Profile"`.

### 6.3 Right Column: Tabbed Edit Forms
- **[OBSERVED]**: Tab rail with clean icons and bottom highlight on active tab:
  - *Personal Information* (Active — yellow underline)
  - *Volunteer Preferences*
  - *Consents & Privacy*
  - *Achievements*
- **[OBSERVED]**: Form fields arranged in 2-column grid:
  - First Name (`Priya`), Last Name (`S.`)
  - Email (`priya.s@maatram.org` with lock icon and `Read Only` tag), Mobile Number (`+91 9876543210`)
  - Short Bio textarea (with character counter `72 / 200`)
  - College / Organization (`Sathyabama Institute of Science and Technology`)
  - Degree dropdown (`B.E. v`), Department dropdown (`ECE v`)
  - Current Year / Graduation Year dropdown (`2nd Year v`)
  - Skills & Areas of Interest: Dismissible chip tags (`Mentoring x`, `Communication x`, `Interview Support x`) + `[+ Add Skill]` pill.
- **[OBSERVED]**: Bottom form action bar: `Cancel` text link and solid golden button `"Save Changes"` with disk icon.

### 6.4 Right Column Lower Cards: Privacy & Consent Governance vs Screenshot
- **[OBSERVED IN SCREENSHOT]**: The sub-card *"Privacy & Visibility at a Glance"* displays 4 switches.
- **[CRITICAL ARCHITECTURAL RECONCILIATION]**:
  The backend database and canonical Phase 5 model (`ConsentRecord` in `server/src/models/consent.py`) persistently track **all six independent affirmative consent preferences**:
  1. `leaderboard_visible`: Show profile on the public leaderboard.
  2. `name_visible`: Show real volunteer name on public leaderboard (if false, displays as Anonymous Volunteer).
  3. `thank_you_emails`: Receive event and milestone thank-you communications.
  4. `linkedin_content`: Allow achievements to be drafted for LinkedIn celebration.
  5. `contact_available`: Share contact details with event coordinators.
  6. `media_usage`: Allow photos and videos featuring the volunteer in Maatram communications.
  
  **Rule**: The UI implementation must account for **all six independent preferences**. No consent setting is combined, omitted, or renamed. Each remains individually opt-in and bound to `ConsentRecord`.

### 6.5 Right Column Lower Cards: Achievement Governance
- **[OBSERVED IN SCREENSHOT]**: The sub-card *"My Achievements"* displays 3 illustrated badges (*First Contribution*, *Community Mentor*, *Consistent Volunteer*).
- **[CRITICAL ARCHITECTURAL RECONCILIATION]**:
  These three illustrated badges are **visual design examples only**.
  **Rule**: The UI will strictly render achievements earned by the volunteer through backend records (`VolunteerAchievement`), linked to approved `AchievementDefinition` records. No new eligibility criteria, arbitrary thresholds, or hardcoded achievements will be introduced.

---

## 7. Analysis of Reference 1: Public Landing Page

**Source**: Extracted from mentor visual language and approved Milestone 2 homepage redesign (`docs/execution-groups/MILESTONE_2_VISUAL_CORRECTION_REPORT.md`).

### 7.1 Layout Composition
- **[OBSERVED]**: Full-width public layout using `PublicHeader` and `PublicFooter` with the warm ivory background canvas (`#FAF8F5`).
- **[OBSERVED]**: Hero section: Two-column editorial composition:
  - Left column: Community tag pill, bold headline (*"Transform Education Through Meaningful Mentorship"*), empathetic description, primary golden CTA (*"Become a Volunteer"*), secondary outline CTA (*"Explore Opportunities"*), and trust indicators.
  - Right column: High-resolution authentic photography of mentor-student engagement in a rounded-3xl container with an integrated editorial impact card.
- **[OBSERVED]**: Signature Opportunities section: Three structured cards (Government School Visits, 1-on-1 Mock Interviews, BGV Support Drives) featuring authentic photography, delivery tags, and direct links to `/events`.
- **[OBSERVED]**: How Volunteering Works: 4-step progressive timeline (`01` Register → `02` Discover → `03` Guide → `04` Earn Recognition).
- **[OBSERVED]**: Mission Storytelling: Editorial quote and direct link to `/about`.
- **[OBSERVED]**: Public Trust Footer with privacy policy and consent guidelines.

---

## 8. Cross-Reference Visual Synthesis & Canonical Standards

| Visual Attribute | Mentor Reference Standard | Implementation Token |
| :--- | :--- | :--- |
| **Canvas Background** | Warm off-white / ivory cream | `#FAF8F5` |
| **Card Surface** | Pure white, rounded-2xl to rounded-3xl | `#FFFFFF` |
| **Borders** | Subtle warm stone line | `#EFECE6` |
| **Primary Brand Color** | Canonical Radiant Golden-Yellow | `#F5B817` |
| **Primary Text** | Deep charcoal | `#1F2421` |
| **Secondary Text** | Medium slate grey | `#4B5563` |
| **Active Nav Item** | Golden yellow pill (`#FFF8E7` / `#FDE68A`) with dark text | `bg-[#FFF8E7] text-stone-900 border-[#F5B817]` |
| **Hero Banners** | Asymmetric curved golden gradient with photography/art | Custom SVG curve + radial gradient |
| **Badges / Tags** | Fully rounded pills (`rounded-full`) in soft pastels | Green, Blue, Lavender, Peach, Yellow |
| **Botanical Flourish** | Gentle wheat/leaf watermark accents | SVG vector assets in corners |
| **Consent Toggles** | All 6 affirmative consent preferences | Individual switches bound to `ConsentRecord` |
| **Achievements** | Visual medal examples; dynamic data | Dynamically populated from backend |
