# Maatram Volunteer App — M3.5 Interaction & Navigation Wiring Audit Report
**Consolidated Phase 13 Milestone — User Interaction & State Transitions**

---

## 1. Overview & Navigation Architecture

The Maatram Volunteer mobile application features a modern, responsive navigation system built on GoRouter 14.8.1 with Riverpod 2.6.1 state management.

The root architecture implements:
- **`StatefulShellRoute.indexedStack`**: Ensures seamless switching across the 4 primary tabs (`Home`, `Events`, `Leaderboard`, `More`) while maintaining scroll positions and form states without costly widget rebuilds.
- **Declarative Route Guards**: Protects authenticated volunteer routes, redirecting unauthenticated users to `/welcome` or `/login`, and handling the 4 post-authentication onboarding states (`PENDING_VERIFICATION`, `PENDING_ADMIN_APPROVAL`, `REJECTED`, `APPROVED`).
- **Modal Layer Management**: Accessible bottom sheets with backdrop blur and drag-to-dismiss handles.

---

## 2. Comprehensive Navigation Routing Table

| Route Path | Screen / Destination | Navigation Trigger | Presentation Type | Guard / Constraint |
|---|---|---|---|---|
| `/welcome` | `WelcomeSplashScreen` | App initial launch (unauthenticated) | Root Page | Public |
| `/login` | `LoginScreen` | "Sign In" link from Welcome screen | Root Page | Public |
| `/register` | `RegistrationFlowScreen` | "Get Started" / "Register Here" CTA | Root Page (6 steps) | Public |
| `/forgot-password`| `ForgotPasswordScreen` | "Forgot Password?" text button | Root Page | Public |
| `/reset-password` | `ResetPasswordScreen` | Deep link / OTP flow | Root Page | Public |
| `/verify-email` | `VerifyEmailScreen` | Post-registration verification | Root Page | `PENDING_VERIFICATION` |
| `/pending-verification` | `PendingVerificationScreen` | Pending email verification | Root Page | `PENDING_VERIFICATION` |
| `/pending-approval` | `PendingApprovalScreen` | Volunteer application review | Root Page | `PENDING_ADMIN_APPROVAL` |
| `/rejected` | `RejectedScreen` | Rejected volunteer status | Root Page | `REJECTED` |
| `/home` | `HomeScreen` | Bottom Nav Tab 0 / Post-auth | Shell Branch 0 | `APPROVED` |
| `/events` | `EventsScreen` | Bottom Nav Tab 1 / "View All" | Shell Branch 1 | `APPROVED` |
| `/leaderboard` | `LeaderboardScreen` | Bottom Nav Tab 2 | Shell Branch 2 | `APPROVED` |
| `/more` | `MoreScreen` | Bottom Nav Tab 3 | Shell Branch 3 | `APPROVED` |
| `/activity` | `MyActivityScreen` | More Menu -> "My Activities" | Root Page with Back Action | `APPROVED` |
| `/profile` | `ProfileScreen` | Avatar tap / More Menu -> "My Profile" | Root Page with Back Action | `APPROVED` |
| `/privacy` | `PrivacyScreen` | More Menu -> "Privacy & Consents" | Root Page with Back Action | `APPROVED` |
| `/notifications` | `NotificationsScreen` | Notification bell tap / More Menu | Root Page with Back Action | `APPROVED` |

---

## 3. Interactive Workflows & State Transitions

### 1. Events Discovery & Registration Flow
1. **Search & Filtering**: User enters text into `MaatramSearchField` or taps category filter pills (`All`, `Education`, `Mentoring`, `Career`).
2. **Controller Query**: `EventsController` queries `/api/v1/events` with active filters and debounced query string.
3. **Card Selection**: Tapping an event card opens `_showEventDetailsModal` bottom sheet displaying event date, time, venue, mode, and spot capacity.
4. **Registration Action**: Tapping "Register for Event" calls `/api/v1/events/{id}/register`.
   - On success: State updates instantly; button transforms to "Registered"; Home and My Activity reflect the new registration.
   - On full capacity or conflict: Friendly error snackbar displays explanation.

### 2. Leaderboard Category Switching Flow
1. User taps category selector: `Overall`, `Students`, or `Alumni`.
2. `LeaderboardController.setCategory(category)` triggers targeted cache-first fetch from `/api/v1/gamification/leaderboard/{category}`.
3. Podium dynamically re-renders top 3 profiles with smooth height adjustments and gold crown re-positioning.

### 3. My Activity Tab Navigation Flow
1. Segmented tabs allow instant switching between:
   - **Upcoming**: Filtered from `/api/v1/events/registrations/me` where event start time > now.
   - **Completed**: Filtered from verified attendance records via `/api/v1/attendance/me`.
   - **Cancelled**: Filtered from withdrawn or cancelled registrations.
2. Sliding indicator animates smoothly without screen jump or reloading spinners.

### 4. Sign Out Workflow
1. User taps "Sign Out" in `MoreScreen`.
2. Hardware storage clears all JWT tokens and cached user sessions via `TokenStorage.clearTokens()`.
3. `authController.logout()` notifies `appRouter`, redirecting instantly to `/welcome`.
