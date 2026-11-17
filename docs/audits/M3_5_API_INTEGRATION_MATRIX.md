# Maatram Volunteer App — M3.5 API Integration Matrix & Dynamic Data Audit
**Consolidated Phase 13 Milestone — End-to-End Real Backend Integration & Data Integrity Audit**

---

## 1. Architectural Principles & Zero Fabricated Data Directive

In strict adherence to the project's Core Operating Principles:
- **Zero Fabricated Production Data**: Every statistic, profile attribute, points balance, and event record is bound to canonical FastAPI endpoints (`http://127.0.0.1:8000/api/v1`). No hardcoded mock values (e.g. "Priya S.", "180 points", "24 hours", "5 events", "#1", "75%") exist in production endpoints or production widget logic.
- **Single Source of Truth**: All volunteer profile attributes, gamification summaries, event registrations, and attendance hours are sourced directly from PostgreSQL via FastAPI.
- **Section-Isolated State Management**: Screens do not use a monolithic page-level loader. Each section (`profile`, `gamification`, `events`, `registrations`, `notifications`) handles loading, error, and empty states independently via Riverpod `AsyncValue`.
- **Honest Non-Fabricated Progress Display**: If the backend does not provide an arbitrary progress target, the UI displays genuine earned badge milestones or contribution callouts rather than a fabricated numerical percentage.

---

## 2. Comprehensive Field-by-Field Dynamic Data Audit Matrix

| # | UI Component | Source API Endpoint | Response Property | Transformation / Calculation | Fallback Behavior | Dynamic Status |
|---|---|---|---|---|---|---|
| **01** | `HomeHeader` (Avatar) | `GET /api/v1/volunteers/me` | `avatar_url` | Rendered via `MaatramAvatar` with network cache. | Initial monogram circle generated from user's full name. | **100% Dynamic** |
| **02** | `HomeHeader` (Unread Badge) | `GET /api/v1/notifications/unread-count` | `unread_count` | Integer count. If `unread_count > 0`, renders red badge. | Badge is hidden if `0` or on network error. | **100% Dynamic** |
| **03** | `IllustratedWelcomeBanner` | `GET /api/v1/volunteers/me` | `first_name`, `last_name` | Formatted as `"Hello, $firstName ${lastName[0]}. 👋"` | Falls back to `UserSession.firstName` or `"Volunteer"`. | **100% Dynamic** |
| **04** | `VolunteerProfilePointsCard` (Name) | `GET /api/v1/volunteers/me` | `first_name`, `last_name` | Full name or abbreviated display name (`Priya S.`). | Session `first_name` or `"Volunteer"`. | **100% Dynamic** |
| **05** | `VolunteerProfilePointsCard` (Status) | `GET /api/v1/volunteers/me` | `status` | Capitalized / mapped to `"Approved"` badge with green checkmark. | Mapped from active session status. | **100% Dynamic** |
| **06** | `VolunteerProfilePointsCard` (Subtitle) | `GET /api/v1/volunteers/me` | `category`, `student_profile.college_name` | Mapped to `"$category • $collegeName"` (e.g. "Student • Sathyabama Institute of Science and Technology"). | `"Active Volunteer • Maatram Foundation"`. | **100% Dynamic** |
| **07** | `VolunteerProfilePointsCard` (Points) | `GET /api/v1/gamification/summary` | `total_points` | Formatted as integer if whole, or 1 decimal (`0`, `180`, etc.). | Defaults to `"0"` if ledger unseeded. | **100% Dynamic** |
| **08** | `ImpactStatisticsRow` (Hours) | `GET /api/v1/gamification/summary` | `total_hours` | Computed by backend from verified attendance records. | Defaults to `"0"` if no attendance recorded. | **100% Dynamic** |
| **09** | `ImpactStatisticsRow` (Events) | `GET /api/v1/gamification/summary` | `completed_events_count` | Total count of completed events attended. | Defaults to `"0"`. | **100% Dynamic** |
| **10** | `ImpactStatisticsRow` (This Year) | `GET /api/v1/gamification/summary` | `completed_events_count` / `cycle_year` | Events completed during active calendar year cycle. | Defaults to `"0"`. | **100% Dynamic** |
| **11** | `ImpactStatisticsRow` (Rank) | `GET /api/v1/gamification/summary` | `rank` | Formatted as `"#$rank"` (e.g. `"#1"`). If null, rendered as `"—"`. | Label displays `"Top Volunteer"` if rank <= 3, else `"Leaderboard"`. | **100% Dynamic** |
| **12** | `UpcomingEventsSection` (Cards) | `GET /api/v1/events?status=PUBLISHED` | `items[]` (`title`, `category`, `start_time`, `location_name`, `banner_url`) | Date formatted as `"d MMM yyyy"`, time as `"h:mm a"`. | Pre-cached hero volunteering photograph if image URL empty. | **100% Dynamic** |
| **13** | `UpcomingEventsSection` (Status) | `GET /api/v1/registrations/me` | `items[].status` | Mapped by `event_id` to determine registration state (`Registered`, `Selected`). | Button shows `"Register"` CTA if unregistered. | **100% Dynamic** |
| **14** | `YourProgressSection` | `GET /api/v1/gamification/summary` | `badges_earned_count` | Earned badge count displayed in golden milestone emblem; honest milestone encouragement. | "Every Contribution Counts" callout if 0 badges. | **100% Dynamic** |
| **15** | `MyActivityScreen` (Upcoming) | `GET /api/v1/registrations/me` & `/events` | `registrations.items[]`, `events.items[]` | Filtered for current/future events with user registration. | Empty state illustration if no upcoming registrations. | **100% Dynamic** |
| **16** | `MyActivityScreen` (Past) | `GET /api/v1/attendance/me` | `items[]` (`event_id`, `hours_credited`, `status`, `check_in_time`) | Formatted date, hours credited badge, `"Completed"` status pill. | Empty state illustration if no past activity. | **100% Dynamic** |

---

## 3. End-to-End API Integration Specification

### 3.1 Authentication & Session Management
- **POST `/api/v1/auth/login`**: Authenticates credentials (`email`, `password`, `client_type`). Returns JWT `access_token` (15 min expiry), `refresh_token` (7 day rolling), CSRF token, and user session entity.
- **GET `/api/v1/users/me`**: Validates token freshness and retrieves active user status and permissions.
- **POST `/api/v1/auth/logout`**: Revokes session and deletes hardware-stored tokens.

### 3.2 Volunteer Profile & Gamification
- **GET `/api/v1/volunteers/me`**: Returns `VolunteerProfileResponse` with nested category details (`student_profile`, `alumni_profile`, `corporate_profile`), status, and contact info.
- **GET `/api/v1/gamification/summary`**: Returns `GamificationSummaryResponse` containing total verified points, eligible service hours, completed event count, and leaderboard rank.
- **GET `/api/v1/notifications/unread-count`**: Returns real-time unread notification count (`{"unread_count": int}`).

### 3.3 Event Participation & Attendance
- **GET `/api/v1/events`**: Returns paginated event catalog filtered by `status=PUBLISHED`.
- **GET `/api/v1/registrations/me`**: Returns active volunteer's event registrations and status.
- **GET `/api/v1/attendance/me`**: Returns volunteer's verified attendance records with credited hours.
- **POST `/api/v1/events/{id}/register`**: Handles volunteer event registration.
- **POST `/api/v1/registrations/{id}/withdraw`**: Handles voluntary withdrawal.

---

## 4. Verification and Audit Signoff

All displayed values on both Home Screen and My Activity Screen are verified to be strictly dynamic and backed by canonical database records. There is zero fabricated demonstration data in production pathways.
