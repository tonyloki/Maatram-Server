# PRODUCTION MOCK DATA AUDIT REPORT
**Maatram Volunteering & Gamification Portal — Flutter Mobile Client**
**Audit Scope:** Elimination of Hardcoded Demonstration Data, Artificial Fallbacks & Static Mock Repositories
**Date:** November 17, 2026
**Single Source of Truth:** FastAPI Canonical Backend (`server/src/api/v1/`)

---

## 1. Executive Summary

A comprehensive source-code and runtime audit was conducted across every Flutter screen, widget, Riverpod provider, repository, model, and network adapter in `mobile/lib/` to verify that zero hardcoded demonstration data exists in production code.

### Core Findings:
1. **Priya S. Demonstration Persona Removed:**
   - Eradicated all occurrences of hardcoded "Priya S." in production code.
   - Removed development auto-login fallback in `mobile/lib/core/auth/auth_controller.dart` lines 58–76 which previously attempted to sign in as `priya.s@maatram.org` when no session was present. Unauthenticated launches now cleanly transition to `AuthState.unauthenticated()`.
2. **Impact Statistics ("24 hours", "5 events", "2 drives", "Rank #1"):**
   - Verified that `impact_statistics_row.dart` contains zero hardcoded numbers. All 4 cards ("Hours", "Events", "This Year", "Rank") bind dynamically to `GamificationSummaryModel` fetched from `GET /api/v1/gamification/summary`.
   - Distinct state semantics ensure that unloaded states display shimmering skeletons or `'—'`, genuine zeros display `'0'`, and rankings display `'#X'` only when computed by the backend.
3. **Foundation Institution Fallback Eliminated:**
   - In `volunteer_profile_points_card.dart`, eliminated `volunteer?.institution ?? 'Maatram Foundation'`. Volunteer category/college/company displays only authentic values from `VolunteerProfileModel`. If not provided, it gracefully displays only the category without fabricating foundation employment.
4. **Event Venue Fallback Corrected:**
   - In `event_model.dart` line 88, replaced `'Maatram Foundation Centre'` with `'Venue TBD'` (or `'Online / Virtual Session'` for virtual events).
5. **Legacy M1 Placeholder Screen Removed:**
   - Deleted unused file `mobile/lib/features/leaderboard/presentation/leaderboard_placeholder_screen.dart`, ensuring no stale mock files linger in production directories.
6. **No Mock Repositories in Production Dependency Graph:**
   - Verified that Riverpod provider definitions (`eventsRepositoryProvider`, `leaderboardRepositoryProvider`, `moreRepositoryProvider`, `gamificationRepositoryProvider`, `authRepositoryProvider`, `homeRepositoryProvider`) instantiate real repositories configured with `ApiClient` using `Dio`. Mock repositories are strictly isolated inside `mobile/test/`.

---

## 2. Production Source Inspection Findings

| Component / File | Inspected Element | Previous Risk / Demonstration Code | Corrected Production State | API Source |
|---|---|---|---|---|
| `auth_controller.dart`<br>(lines 55–65) | `checkInitialSession()` | Attempted dev login with `priya.s@maatram.org` on empty session. | Removed auto-login. Unauthenticated launches emit `AuthState.unauthenticated()`. | `FlutterSecureStorage` |
| `volunteer_profile_points_card.dart`<br>(lines 30–45) | Profile Subtitle & Points | Fallback `'Maatram Foundation'` if institution null. Conflated missing points with 0. | Binds to `profile?.subtitle`. Points display shimmer (loading), real value, or `'—'` (unavailable). | `GET /api/v1/volunteers/me`<br>`GET /api/v1/gamification/summary` |
| `impact_statistics_row.dart`<br>(lines 25–45) | 4 Stat Cards | Risk of showing hardcoded numbers or disguising API error as 0. | `isLoading` renders shimmer. Real zero `0` rendered only when API returns 0; unavailable shows `'—'`. | `GET /api/v1/gamification/summary` |
| `event_model.dart`<br>(line 88) | Location fallback | Fallback `'Maatram Foundation Centre'` if venue missing. | Replaced with `'Venue TBD'` (or `'Online / Virtual Session'`). | `GET /api/v1/events` |
| `leaderboard_screen.dart`<br>(lines 120–160) | Top 3 Podium & List | Risk of static podium filler volunteers. | Pure dynamic binding to `state.items`. If empty, renders authentic `_buildEmptyState()` ("No Leaderboard Data Yet"). | `GET /api/v1/gamification/leaderboard` |
| `events_screen.dart`<br>(lines 90–120) | Events Catalog | Risk of static sample events. | Pure dynamic binding to `state.events`. If empty, renders clean empty state with filter reset action. | `GET /api/v1/events?status=PUBLISHED` |
| `my_activity_screen.dart`<br>(lines 80–110) | Volunteer Registrations | Risk of fabricated hours or fake attendance logs. | Maps real registrations from API. If empty, renders `_buildEmptyActivitiesCard()` with "Explore Events" button. | `GET /api/v1/registrations/me`<br>`GET /api/v1/attendance/me` |
| `leaderboard_placeholder_screen.dart` | Whole File | Unused M1 prototype file with hardcoded `Karthik R`. | **Deleted permanently from repository.** | N/A |

---

## 3. Automated Scanning Proof

A full-codebase regex and AST scan of `mobile/lib/` for demonstration keywords ("Priya", "24 hours", "5 events", "2 drives", "Rank #1", "Sathyabama", "Arun K", "Meena R", "Karthik") yielded **0 occurrences** in production code:

```
Command: python scan_production_keywords.py
Scope: mobile/lib/**/*.dart
Keywords: ['Priya', '24 hours', '24 hrs', '5 events', '2 drives', 'Rank #1', 'Sathyabama', 'Karthik', 'Meena', 'Arun K']
Result: ZERO demonstration keyword occurrences found in mobile/lib!
```

---

## 4. Test Fixtures vs. Production Isolation

All mock data, test fixtures, and synthetic API responses are strictly constrained to `mobile/test/`:
- `mobile/test/audit/phase4_all_38_screens_capture_test.dart` uses `CaptureHomeMock` and `CaptureMockEventsRepo` solely to produce visual comparison artifacts in headless CI.
- `mobile/test/auth/auth_flow_test.dart` uses mock responses to validate form validation and state transitions.
- Production dependency graph (`mobile/lib/`) contains zero references to `mobile/test/` or mock classes.
