# MAATRAM MOBILE — M3 API INTEGRATION MATRIX
**Volunteer Home Screen Dynamic API Integration, Data Mapping & Error Resilience**

---

## 1. Overview

The M3 Home Screen is 100% dynamically driven by canonical FastAPI backend endpoints. All communications use strict Bearer token authentication via `AuthInterceptor` with automatic token refresh, token rotation, and session recovery.

**Zero Hardcoded Data Policy**: No static demonstration numbers, mock rankings, fabricated percentage rings, or artificial notification badges exist in production code.

---

## 2. Dynamic API Integration Matrix

| Endpoint | HTTP Method | Target UI Section | Request Parameters / Headers | Canonical Backend DTO Response | Data Integrity & Transformation | Fallback & Fault Tolerance |
|---|---|---|---|---|---|---|
| `/api/v1/volunteers/me` | `GET` | **Section 1 (Header)**<br>**Section 2 (Welcome Greeting)**<br>**Section 3 (Profile Card)** | `Authorization: Bearer <token>` | `VolunteerProfileResponse`<br>- `first_name`, `last_name`<br>- `category` (`STUDENT`, `ALUMNI`, `CORPORATE_PANELIST`)<br>- `avatar_url` (nullable)<br>- `parental_consent_verified` (bool)<br>- `student_profile.college`<br>- `alumni_profile.company`<br>- `corporate_profile.company_name` | **Live Backend Data**:<br>- Short name resolved as `first_name` + `last_name[0]`. (e.g. `Karthik R.`)<br>- Full name for profile card.<br>- Subtitle resolved dynamically from category and institution/company.<br>- Verification pill checks `parental_consent_verified`. | Fallback hierarchy: `profile.shortName` &rarr; `session.firstName` &rarr; `'Volunteer'`. Subtitle defaults to category display name if college/company is absent. |
| `/api/v1/gamification/summary` | `GET` | **Section 3 (Profile Card Points)**<br>**Section 4 (Impact Statistics)**<br>**Section 6 (Your Progress / Journey)** | `Authorization: Bearer <token>` | `GamificationSummaryResponse`<br>- `volunteer_profile_id` (UUID)<br>- `total_points` (Decimal)<br>- `total_hours` (Decimal)<br>- `completed_events_count` (int)<br>- `badges_earned_count` (int)<br>- `rank` (int \| null)<br>- `cycle_year` (int) | **Live Canonical Ledger Data**:<br>- `total_points`: Formatted without trailing `.00`.<br>- `total_hours`: Converted to formatted hours string.<br>- `completed_events_count`: Integer count.<br>- `badges_earned_count`: Genuine badges earned from canonical badge awards ledger.<br>- `rank`: If non-null, displays `#{rank}` with `"Rank"` label. If `null`, displays `"—"` with `"Leaderboard"` label (Never displays fabricated `"#1"` or `"Top Volunteer"`). | In case of gamification calculation pending or new volunteer, `GamificationSummaryModel.empty()` provides neutral zeros (`0 Points`, `0 Hours`, `0 Events`, `— Rank`). |
| `/api/v1/events` | `GET` | **Section 5 (Upcoming Events Carousel)** | `status=PUBLISHED`<br>`limit=10`<br>`page=1` | `EventListResponse`<br>- `items`: `List<EventResponse>`<br>- `total`, `page`, `page_size` | **Live Event Schedule**:<br>- `title`, `description`<br>- `start_time`, `end_time` (Formatted in local timezone via `DateFormat`)<br>- `category` (Humanized display name, e.g. `"Mock Interview"`)<br>- `location` (Physical venue or virtual)<br>- `cover_image_url` (Cloudinary CDN URL with local asset category fallback). | When empty (`items.isEmpty`), renders genuine empty state card (`"No upcoming events scheduled"`). In case of network error, renders isolated error banner with **Retry** button without crashing home page. |
| `/api/v1/volunteers/me/registrations` | `GET` | **Section 5 (Upcoming Events Badges)** | `limit=20`<br>`page=1` | `RegistrationListResponse`<br>- `items`: `List<RegistrationResponse>` (`event_id`, `status`) | **Live Volunteer Registration Status**:<br>- Matches `event_id` to determine user's participation status.<br>- Maps backend enum: `REGISTERED` &rarr; `"Registered"`, `CONFIRMED`/`SELECTED` &rarr; `"Confirmed"`, `WAITLISTED` &rarr; `"Waitlist"`. | Non-blocking secondary call. If registrations endpoint fails or volunteer has not registered, event card renders cleanly without a registration pill. |
| `/api/v1/notifications` | `GET` | **Section 1 (Header Bell Badge)** | `limit=20` | `NotificationListResponse`<br>- `items`: `List<NotificationResponse>` (`id`, `title`, `read_at`) | **Live Notifications Ledger**:<br>- Computes unread count strictly where `read_at == null`.<br>- If `unreadCount == 0`, **no badge circle is rendered** (zero badge fabrication).<br>- If `unreadCount > 0`, renders badge with numeric count (`"9+"` if `> 9`). | Defaults to 0 unread if endpoint is unreachable. |

---

## 3. UI Element Data Integrity & Dynamic Verification

| UI Component | Screen Section | Canonical Source Endpoint | Canonical Property | Transformation / Calculation | Fallback Behavior | Dynamic Status |
|---|---|---|---|---|---|---|
| Notification Bell Badge | Section 1: Header | `GET /notifications` | `items.where(read_at == null).length` | Filter unread items count | Hidden when `0` (Zero rendered). Never hardcoded. | **100% Dynamic** |
| Header Avatar | Section 1: Header | `GET /volunteers/me` | `avatar_url`, `first_name`, `last_name` | Network image or initials circle | Initials derived from first & last name | **100% Dynamic** |
| Greeting Heading | Section 2: Welcome Banner | `GET /volunteers/me` | `first_name`, `last_name` | `"${first_name} ${last_name[0]}."` | Falls back to session name &rarr; `'Volunteer'` | **100% Dynamic** |
| Profile Avatar & Edit Pill | Section 3: Profile Card | `GET /volunteers/me` | `avatar_url`, `first_name`, `last_name` | Cached network image with initials fallback | Initials avatar | **100% Dynamic** |
| Profile Volunteer Name | Section 3: Profile Card | `GET /volunteers/me` | `first_name`, `last_name` | Full display name | Session name &rarr; `'Volunteer'` | **100% Dynamic** |
| Profile Verification Pill | Section 3: Profile Card | `GET /volunteers/me` | `parental_consent_verified` | Renders `Approved` badge if true | Hidden if unverified | **100% Dynamic** |
| Profile Category & Subtitle | Section 3: Profile Card | `GET /volunteers/me` | `category`, `college`/`company`/`company_name` | `"${categoryDisplay} • ${institution}"` | Category display name alone if institution empty | **100% Dynamic** |
| Profile Points Star & Value | Section 3: Profile Card | `GET /gamification/summary` | `total_points` | Formatted without `.00` (e.g. `350`) | Displays `'0'` if summary empty | **100% Dynamic** |
| Stat Card: Hours | Section 4: Impact Stats | `GET /gamification/summary` | `total_hours` | Formatted integer/decimal string | Displays `'0'` | **100% Dynamic** |
| Stat Card: Events | Section 4: Impact Stats | `GET /gamification/summary` | `completed_events_count` | String representation | Displays `'0'` | **100% Dynamic** |
| Stat Card: This Year | Section 4: Impact Stats | `GET /gamification/summary` | `completed_events_count` (cycle) | String representation | Displays `'0'` | **100% Dynamic** |
| Stat Card: Rank | Section 4: Impact Stats | `GET /gamification/summary` | `rank` | If `rank != null` &rarr; `"#${rank}"`, `"Rank"`. If `null` &rarr; `"—"`, `"Leaderboard"` | `"—"` (Never hardcoded `"#1"` or `"Top Volunteer"`) | **100% Dynamic** |
| Upcoming Events Cards | Section 5: Events Carousel | `GET /events` | `items` | Formatted title, category, date, time, venue, cover | Empty state card if empty list | **100% Dynamic** |
| Event Registration Status | Section 5: Events Carousel | `GET /volunteers/me/registrations` | `items.status` | Maps enum to `Confirmed`, `Registered`, `Waitlist` | No badge if not registered | **100% Dynamic** |
| Volunteer Journey / Progress | Section 6: Your Progress | `GET /gamification/summary` | `badges_earned_count` | Genuine badges earned summary & non-numeric journey milestone encouragement | Motivational card grounded in active volunteer status (Fabricated 75% ring removed) | **100% Dynamic** |
| Inspiration Banner | Section 7: Community Banner | N/A (Static Asset) | Local editorial asset | Maatram mission community artwork & caption | Polished SVG/Asset | **Editorial Visual** |

---

## 4. Verification and Error Resilience Matrix

| Error Scenario | Technical Error | User Experience Impact | Error Recovery Mechanism |
|---|---|---|---|
| **Expired Access Token** | `401 Unauthorized` | Transparent token refresh | `AuthInterceptor` calls `/api/v1/auth/refresh` and automatically replays pending requests. |
| **Network Timeout** | `DioExceptionType.connectionTimeout` | Section error state with retry | Affected section displays inline error with **Retry** button; does not crash other sections. |
| **Events Service Unavailable** | `500 Internal Server Error` on `/events` | Isolated error banner in Events section | Profile, impact stats, and greeting continue rendering smoothly. |
| **Gamification Uncalculated** | `404 Not Found` or empty summary | Stats render graceful zeros and neutral dash | `GamificationSummaryModel.empty()` provides zero points/hours and `"—"` rank. |
| **Pull to Refresh** | User trigger | Seamless re-fetch across all providers | `RefreshIndicator` triggers `homeControllerProvider.notifier.refresh()` concurrently. |
