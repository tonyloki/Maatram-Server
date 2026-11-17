# MAATRAM VOLUNTEER APP — INTERACTION AUDIT REPORT
**Comprehensive Functional Verification of Buttons, Gestures, Inputs & Navigation**

---

## 1. Executive Summary

This report documents the functional interaction audit across all screens and user controls in the Maatram Flutter volunteer application.

Every button, form input, navigation target, gesture handler, and list affordance has been tested and classified into five precise interaction categories:
1. **Working**: Complete user interaction with state change, navigation, or API dispatch.
2. **Partially Working**: Interacts visually or locally, but missing full integration or target route.
3. **Visual Only**: Renders a clickable affordance (e.g. arrow, icon, chevron) with no `onTap` handler attached.
4. **Broken**: Throws an exception, causes overflow, or fails validation unexpectedly.
5. **Not Implemented**: Feature/screen reference exists but is absent from the application.

### Overall Interaction Score: **71 / 100** (Core Authentication & Home Functional; Secondary Tabs Visual Only)

---

## 2. Interaction Audit Matrix by Screen

### 2.1 Authentication & Registration Flows

| Screen | UI Control / Interaction | Behavior & Outcome | Classification | Status Notes |
|---|---|---|---|---|
| **Login** | Email Input | Validates format; displays red inline helper when invalid. | **Working** | Proper keyboard action & regex validation. |
| **Login** | Password Obscurity Eye | Toggles password masking between bullets and plain text. | **Working** | Preserves cursor position. |
| **Login** | "Sign In" Button | Dispatches auth request, shows loading spinner, saves tokens on 200, shows error on 401. | **Working** | Fully integrated with backend `/auth/login`. |
| **Login** | "Forgot Password?" Link | Navigates to `/forgot-password`. | **Working** | Clean router transition. |
| **Login** | "Register Here" Link | Navigates to `/register`. | **Working** | Clean router transition. |
| **Registration** | Stepper Navigation | Forward navigation upon valid inputs; Back button preserves data. | **Working** | Riverpod form state preserves entered fields. |
| **Registration** | Category Selection | Selects Student, Alumni, or Corporate Panelist with dynamic fields. | **Working** | Correctly morphs Step 3 form fields. |
| **Registration** | Minor Consent Toggle | Displays parent/guardian consent inputs when age < 18. | **Working** | Safeguarding compliance enforced. |
| **Registration** | "Submit Application" | Sends `RegistrationPayload` to `/auth/register`. | **Working** | Advances to `/verify-email`. |
| **Verify Email** | OTP / Token Input | Formats token, dispatches verification to backend. | **Working** | Successfully routes to pending verification. |
| **Verify Email** | Resend Timer | 60-second countdown before enabling Resend link. | **Working** | Prevents rate limit abuse. |
| **Forgot Password** | Submit Reset Link | Sends password reset email via `/auth/forgot-password`. | **Working** | Validates email field. |
| **Reset Password** | New Password Validation| Enforces 8+ chars, uppercase, lowercase, digit, symbol. | **Working** | Strict credential validation. |

---

### 2.2 Onboarding & Application Status Screens

| Screen | UI Control / Interaction | Behavior & Outcome | Classification | Status Notes |
|---|---|---|---|---|
| **Pending Verification** | "Refresh Status" Button | Re-fetches `/volunteers/me` to check updated status. | **Working** | Allows self-service refresh. |
| **Pending Verification** | "Log Out" Action | Clears secure tokens and returns to `/login`. | **Working** | Clean session termination. |
| **Pending Approval** | "Refresh Status" Button | Re-checks if admin has approved application. | **Working** | Automatically transitions to Home when approved. |
| **Pending Approval** | Contact Support Mailto | Opens default email client to `support@maatram.org`. | **Partially Working** | Triggers launcher; needs platform fallback. |
| **Rejected** | "Reapply / Contact" | Provides explanation copy and contact button. | **Working** | Clear empathetic messaging. |
| **Post-Approval Welcome**| "Enter Portal" Button | Marks first-launch completed and navigates to `/home`. | **Working** | Sets local storage flag. |

---

### 2.3 Volunteer Home Screen

| UI Control / Interaction | Target / Purpose | Actual Runtime Behavior | Classification | Status Notes |
|---|---|---|---|---|
| **Notification Bell** | Open Notifications Center | Tap triggers ink ripple, but **no route or modal is opened**. | **Visual Only** | Notifications screen not yet implemented. |
| **Profile Avatar Pencil** | Open Profile Editor | Tap has no attached `onTap` listener. | **Visual Only** | Profile editing route not yet connected. |
| **Impact Stat Cards** | View Hours/Events Ledger | Tapping "24 Hours" or "5 Events" has no response. | **Visual Only** | Cards are static containers without tap handlers. |
| **Upcoming Events Carousel**| Horizontal Touch Scroll | Smooth horizontal scroll with snapping physics. | **Working** | Renders multiple event cards smoothly. |
| **Upcoming Events "View All &rarr;"**| Navigate to Events Tab | Text button renders gold arrow, but has no `onTap`. | **Visual Only** | Should switch to Events shell branch (Tab 1). |
| **Event Card Tap** | View Event Details | Tapping event card does nothing. | **Visual Only** | Event details screen (`/events/:id`) not implemented. |
| **Pull to Refresh** | Refresh Home Data | Pull gesture triggers spinner; re-fetches profile, stats, and events concurrently. | **Working** | Smooth asynchronous refresh with `RefreshIndicator`. |
| **Isolated Section Retry** | Recover Failed Section | Tapping "Retry" in Upcoming Events re-fetches only `/events` without reloading entire page. | **Working** | Excellent error isolation. |

---

### 2.4 Secondary Shell Tabs

| Tab Screen | UI Control / Interaction | Actual Runtime Behavior | Classification | Status Notes |
|---|---|---|---|---|
| **Events Tab** (`/events`) | Search Field | Types query, but does not filter backend events. | **Visual Only** | Mockup placeholder only. |
| **Events Tab** (`/events`) | Event Card Action | Cards display mock data; taps have no target. | **Visual Only** | Full Events feature scheduled for M4+. |
| **Leaderboard** (`/leaderboard`)| Podium Selection | Podiums are static colored boxes with hardcoded names. | **Visual Only** | Full Leaderboard scheduled for M5+. |
| **More Tab** (`/more`) | "My Volunteering Activity"| Renders list tile with arrow, but has no `onTap`. | **Visual Only** | Reference 3 (`My Activity`) not implemented. |
| **More Tab** (`/more`) | "Gamification & Badges"| Renders list tile with arrow, but has no `onTap`. | **Visual Only** | Secondary flow placeholder. |
| **More Tab** (`/more`) | "M1 Design Showcase" | Navigates to `/dev/showcase`. | **Working** | Functional engineering screen. |
| **Bottom Navigation Bar** | Switch between 4 Tabs | Tapping Home, Events, Leaderboard, More switches active branch. | **Working** | Stateful navigation shell functions properly. |

---

## 3. Summary Interaction Scorecard

| Domain | Weight | Score | Summary |
|---|---:|---:|---|
| Authentication & Registration | 30 | 28 | Comprehensive validation, form navigation, and token flow. |
| Onboarding & Statuses | 15 | 14 | Refresh, logout, and contact actions functional. |
| Home Screen Features | 30 | 18 | Pull-to-refresh & horizontal scroll work; headers/cards lack routes. |
| Shell Navigation (4 Tabs) | 15 | 11 | Bottom nav works cleanly; placeholder tab contents are visual only. |
| Error Resilience & Retries | 10 | 10 | Isolated section retries and network recovery fully functional. |
| **Total Interaction Score** | **100** | **71** | **Strong Foundation, Missing Sub-Route Destinations** |
