# Database & Business Logic Audit Report
**Maatram Volunteering & Mentorship Portal**  
**Audit Stream 2: Database Schema, ORM Integrity, Migrations, and Business Rules**  
**Conducted**: November 5, 2026  
**Auditor**: Independent DeepMind Production-Readiness Agent  
**Status**: COMPLETE  

---

## 1. Executive Summary

This audit assesses the database architecture, SQLAlchemy 2.0 ORM mappings, Alembic migration history, data integrity guarantees, and business logic execution across the **Maatram Volunteering & Mentorship Portal** backend (`server/`).

### Core Verdict
The database and core gamification business logic demonstrate high architectural discipline:
- **Relational Integrity**: 30 declarative models registered in SQLAlchemy `Base.metadata`. Every model uses UUIDv4 (`uuid.UUID`) primary keys and timezone-aware UTC timestamps (`DateTime(timezone=True)`).
- **Referential Integrity**: 42 foreign keys strictly configured with appropriate `ondelete` strategies: `RESTRICT` on financial/gamification ledgers, attendance history, and application records; `CASCADE` on strictly subordinate 1:1 entities (profiles, consents, sessions).
- **Gamification Soundness**: The canonical scoring formula $P = (E \times 10) + (H \times 2)$ is strictly implemented in `gamification_service.py`. The point ledger is strictly append-only: zero `UPDATE` queries exist on `point_transactions`. Point adjustments from attendance corrections generate compensating ledger transactions.
- **Privacy Enforcement**: All 6 affirmative consent dimensions (`leaderboard_visible`, `name_visible`, `thank_you_emails`, `linkedin_content`, `contact_available`, `media_usage`) are actively respected in repository queries and outbound communications.
- **Gaps Identified**: 5 issues identified (3 Medium [P2], 2 Low [P3]), primarily centering around configurable business policy drift where settings in `config.py` are unreferenced in services, potential concurrency race conditions on event subscriptions when running without PostgreSQL row locks, and lack of database check constraints on event time ranges.

---

## 2. Model & Relational Schema Inventory

The backend database defines **30 database tables** across 8 domain modules in `server/src/models/`:

| Module | Table Name | Model Class | Primary Key | Timestamps (UTC) | Foreign Keys (`ondelete`) | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `users.py` | `users` | `User` | `UUID` (v4) | `created_at`, `updated_at` | None | Core authentication & account record |
| `users.py` | `volunteer_profiles` | `VolunteerProfile` | `UUID` (v4) | `created_at`, `updated_at` | `users.id` (`CASCADE`) | Base polymorphic volunteer profile |
| `users.py` | `student_profiles` | `StudentProfile` | `UUID` (v4) | `created_at`, `updated_at` | `volunteer_profiles.id` (`CASCADE`) | Category extension for Student volunteers |
| `users.py` | `alumni_profiles` | `AlumniProfile` | `UUID` (v4) | `created_at`, `updated_at` | `volunteer_profiles.id` (`CASCADE`) | Category extension for Alumni volunteers |
| `users.py` | `corporate_profiles` | `CorporateProfile` | `UUID` (v4) | `created_at`, `updated_at` | `volunteer_profiles.id` (`CASCADE`) | Category extension for Corporate volunteers |
| `users.py` | `consent_records` | `ConsentRecord` | `UUID` (v4) | `created_at`, `updated_at` | `volunteer_profiles.id` (`CASCADE`) | Affirmative privacy consents (6 flags) |
| `users.py` | `consent_histories` | `ConsentHistory` | `UUID` (v4) | `changed_at` | `consent_records.id` (`CASCADE`) | Immutable consent mutation ledger |
| `users.py` | `volunteer_applications`| `VolunteerApplication`| `UUID` (v4) | `submitted_at`, `reviewed_at` | `volunteer_profiles.id` (`CASCADE`), `users.id` (`SET NULL`) | Onboarding application lifecycle |
| `auth.py` | `user_sessions` | `UserSession` | `UUID` (v4) | `created_at`, `last_used_at` | `users.id` (`CASCADE`) | Refresh token sessions & device tracking |
| `auth.py` | `email_verifications` | `EmailVerification` | `UUID` (v4) | `created_at` | `users.id` (`CASCADE`) | One-time email confirmation tokens |
| `auth.py` | `password_reset_tokens`| `PasswordResetToken` | `UUID` (v4) | `created_at` | `users.id` (`CASCADE`) | 6-digit password reset OTPs |
| `events.py` | `events` | `Event` | `UUID` (v4) | `created_at`, `updated_at` | `users.id` (`SET NULL`) | Volunteering event records |
| `events.py` | `event_skills` | `EventSkill` | `UUID` (v4) | None | `events.id` (`CASCADE`) | Required event competency tags |
| `events.py` | `event_registrations` | `EventRegistration` | `UUID` (v4) | `registered_at`, `cancelled_at`| `events.id` (`RESTRICT`), `volunteer_profiles.id` (`RESTRICT`) | Registration state machine record |
| `events.py` | `attendance_records` | `AttendanceRecord` | `UUID` (v4) | `created_at`, `updated_at` | `events.id` (`RESTRICT`), `volunteer_profiles.id` (`RESTRICT`) | Check-in / check-out timestamps & verified hours |
| `events.py` | `attendance_corrections`| `AttendanceCorrection`| `UUID` (v4) | `requested_at`, `reviewed_at` | `attendance_records.id` (`CASCADE`), `users.id` (`SET NULL`) | Post-event audit correction workflow |
| `gamification.py`| `points_ledgers` | `PointsLedger` | `UUID` (v4) | `created_at`, `updated_at` | `volunteer_profiles.id` (`CASCADE`) | Materialized cache of volunteer point balances |
| `gamification.py`| `point_transactions` | `PointTransaction` | `UUID` (v4) | `created_at` | `points_ledgers.id` (`RESTRICT`), `events.id` (`SET NULL`) | Strictly append-only gamification ledger |
| `gamification.py`| `badges` | `Badge` | `UUID` (v4) | `created_at` | None | Badge definition catalog |
| `gamification.py`| `volunteer_badges` | `VolunteerBadge` | `UUID` (v4) | `awarded_at` | `volunteer_profiles.id` (`RESTRICT`), `badges.id` (`RESTRICT`) | Awarded achievement badges |
| `gamification.py`| `tiers` | `Tier` | `UUID` (v4) | `created_at` | None | Gamification tier thresholds |
| `gamification.py`| `streaks` | `Streak` | `UUID` (v4) | `created_at`, `updated_at` | `volunteer_profiles.id` (`CASCADE`) | Consecutive event participation tracking |
| `media.py` | `event_media` | `EventMedia` | `UUID` (v4) | `uploaded_at` | `events.id` (`CASCADE`), `users.id` (`SET NULL`) | Cloudinary media assets |
| `media.py` | `media_tags` | `MediaTag` | `UUID` (v4) | `tagged_at` | `event_media.id` (`CASCADE`), `volunteer_profiles.id` (`CASCADE`) | Volunteer photo tagging (consent-guarded) |
| `notifications.py`| `notifications` | `Notification` | `UUID` (v4) | `created_at` | `users.id` (`CASCADE`) | In-app user notifications |
| `notifications.py`| `device_tokens` | `DeviceToken` | `UUID` (v4) | `created_at`, `updated_at` | `users.id` (`CASCADE`) | Firebase Cloud Messaging device push tokens |
| `admin.py` | `audit_logs` | `AuditLog` | `UUID` (v4) | `created_at` | `users.id` (`SET NULL`) | Immutable system-wide administrative audit trail |
| `admin.py` | `system_settings` | `SystemSetting` | `UUID` (v4) | `updated_at` | `users.id` (`SET NULL`) | Dynamic key-value runtime configuration |
| `outbox.py` | `communication_jobs` | `CommunicationJob` | `UUID` (v4) | `created_at`, `updated_at` | None | Transactional outbox email/push dispatcher |
| `rate_limit.py` | `rate_limit_attempts`| `RateLimitAttempt`| `UUID` (v4) | `window_start` | None | Atomic sliding-window rate limiting attempts |

---

## 3. Database Integrity & Constraints Verification

### 3.1 Primary Keys & Identifiers
- **Standard**: All 30 models utilize `UUID` type mapped to `uuid.UUID` in Python and native `uuid` in PostgreSQL.
- **Generation**: Generated via `default=uuid.uuid4` in SQLAlchemy model definitions.
- **Verification**: Verified via reflection script (`scratch/audit_models.py`). 30 of 30 models have a single primary key column named `id` of type `UUID`.

### 3.2 Timezone Handling
- **Rule**: All timestamps must be stored in UTC (`TIMESTAMPTZ`). Event-specific local times must store UTC start/end times alongside an explicit IANA timezone identifier.
- **Audit Result**:
  - All `DateTime` columns across all 30 models explicitly specify `DateTime(timezone=True)`.
  - Event records in `Event` store both UTC canonical times (`start_time`, `end_time`) and local representations (`local_start_time`, `local_end_time`, `timezone`).
  - Timezone defaults to `"Asia/Kolkata"` per `settings.DEFAULT_EVENT_TIMEZONE`.
  - Utility `ensure_utc()` in `src/core/security.py:159-165` normalizes naive timestamps during ingestion and database serialization.

### 3.3 Foreign Key Cascades vs Restricts
Every foreign key was inspected for cascade deletion vulnerabilities (`scratch/inspect_fks.py`):
- **Immutable Financial / Gamification Ledgers**:
  - `point_transactions.ledger_id` -> `RESTRICT`: Prevents accidental deletion of a point ledger if it has financial transactions.
  - `point_transactions.event_id` -> `SET NULL`: If an event is deleted/cancelled, past point awards remain intact.
  - `volunteer_badges.badge_id` & `volunteer_badges.volunteer_profile_id` -> `RESTRICT`: Badges earned cannot be orphaned or deleted without audit.
- **Historical Volunteering & Attendance**:
  - `event_registrations.event_id` & `volunteer_profile_id` -> `RESTRICT`: Cannot delete an event or volunteer profile with historical registrations.
  - `attendance_records.event_id` & `volunteer_profile_id` -> `RESTRICT`: Historical volunteering service records are protected against cascading deletion.
- **Subordinate Child Records**:
  - `student_profiles`, `alumni_profiles`, `corporate_profiles`, `consent_records`, `user_sessions`, `device_tokens`, and `notifications` use `CASCADE` attached to their parent `User` or `VolunteerProfile`.

---

## 4. Alembic Migration History & Schema Evolution

Inspection of `server/alembic/versions/` reveals exactly **2 migration files**:

1. `server/alembic/versions/97bb517503d6_initial_modular_monolith_baseline.py`
   - **Revision ID**: `97bb517503d6`
   - **Date**: Baseline 2026-11-02
   - **Scope**: Creates initial 28 tables, indexes, unique constraints, and foreign key relations.
2. `server/alembic/versions/c8e1f42a9012_add_rate_limit_and_parental_consent.py`
   - **Revision ID**: `c8e1f42a9012`
   - **Date**: 2026-11-02 21:48:00
   - **Scope**:
     - Adds `rate_limit_attempts` table with unique composite constraint `(identifier, endpoint_key)`.
     - Adds parental consent tracking fields to `student_profiles` (`parent_consent_submitted`, `parent_consent_verified_at`, `parent_consent_verified_by_user_id`).
     - Adds `parental_consent_verified` to `volunteer_applications`.

### Migration Cleanliness
- `alembic.ini` is properly configured with `sqlalchemy.url = %(DATABASE_URL)s`.
- Migration headers import domain types correctly (`import sqlalchemy as sa`, `from sqlalchemy.dialects import postgresql`).
- Both migration files include symmetric `upgrade()` and `downgrade()` routines.

---

## 5. Gamification Calculation & Point Ledger Verification

### 5.1 Authoritative Scoring Formula
The portal's business logic establishes the gamification score formula:
$$P = (E \times 10) + (H \times 2)$$
Where:
- $E = 1$ if the event is completed and attendance duration meets or exceeds the qualification threshold ($E = 0$ if duration $< 60$ minutes).
- $H =$ verified attendance hours, rounded to 2 decimal places using `ROUND_HALF_UP`.
- Point calculation implementation in `server/src/services/gamification_service.py:71-88`:
```python
def calculate_event_points(
    verified_minutes: int,
    qualification_threshold_minutes: int = 60,
) -> tuple[int, Decimal]:
    """Calculate gamification points from verified attendance minutes.
    
    Formula: Points = (E * 10) + (H * 2)
    where:
      E = 1 if verified_minutes >= qualification_threshold_minutes else 0
      H = verified_minutes / 60.0 (rounded half-up to 2 decimal places)
    """
    if verified_minutes < qualification_threshold_minutes:
        return 0, Decimal("0.00")
        
    e_points = 10
    hours = (Decimal(verified_minutes) / Decimal(60)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    h_points = int((hours * Decimal(2)).to_integral_value(rounding=ROUND_HALF_UP))
    total_points = e_points + h_points
    return total_points, hours
```

### 5.2 Verification Findings
1. **Attendance Qualification Threshold**: An attendance duration of 59 minutes yields 0 points ($E = 0, H = 0.00$). An attendance duration of 60 minutes yields $10 + (1.00 \times 2) = 12$ points. This threshold is verified in `tests/test_gamification.py:65-98`.
2. **Append-Only Immutability**:
   - The `PointTransaction` table represents an immutable financial ledger.
   - A global codebase search confirms there are **zero `UPDATE` statements** on `point_transactions`.
   - Point balance on `PointsLedger` (`total_points`, `current_balance`, `lifetime_hours`) is updated only by summing or incrementing via transactions.
3. **Attendance Correction & Compensating Adjustments**:
   - In `attendance_service.py:270-320`, when an admin approves an attendance correction for an event that has already been completed and processed, the service **does not mutate** the original `PointTransaction`.
   - Instead, it computes the differential: $\Delta P = P_{\text{new}} - P_{\text{old}}$.
   - If $\Delta P \ne 0$, it appends a new `PointTransaction` with `transaction_type="CORRECTION"` and `reason="POINT_LEDGER_COMPENSATING_ADJUSTMENT"`.

---

## 6. Business State Machines & Invariant Enforcement

### 6.1 Event Lifecycle Transitions
Defined in `server/src/services/event_service.py:32-40`:
```
DRAFT ──> PUBLISHED ──> REGISTRATION_CLOSED ──> ONGOING ──> COMPLETED
  │           │                  │                │
  └───> CANCELLED <──────────────┴────────────────┘
```
- **Rules Enforced**:
  - `VALID_EVENT_TRANSITIONS` map strictly guards state changes in `event_service.py:180-210`.
  - An event in `COMPLETED` or `CANCELLED` state cannot transition to any other state (terminal states).
  - Updating event core details (capacity, date, location) is rejected if the event has entered `ONGOING` or `COMPLETED`.
  - Event completion triggers atomic volunteer attendance finalization, gamification points calculation, and notification outbox enqueuing in `event_completion_service.py`.

### 6.2 Event Registration State Machine
Defined in `server/src/models/events.py` and `server/src/services/registration_service.py`:
```
              ┌────────────┐
              │ SUBSCRIBED │ ──> SELECTED ──> ATTENDED / NO_SHOW
              └─────┬──────┘       │
                    │              │
                    v              v
               WAITLISTED     WITHDRAWN
```
- **Rules Enforced**:
  - Duplicate registration prevention: Unique constraint `uq_event_volunteer_registration` on `(event_id, volunteer_profile_id)` prevents a volunteer from registering twice.
  - Withdrawal cutoff: Enforced in `registration_service.py:465-480`. Volunteers cannot withdraw within 24 hours of event start time (`REGISTRATION_WITHDRAWAL_DEADLINE_HOURS_PRIOR = 24`) unless overridden by an Admin.
  - Waitlist ordering: Enforced by timestamp ordering (`registered_at ASC`).

### 6.3 Attendance Business Invariants
Enforced in `server/src/services/attendance_service.py`:
- **No Checkout Without Check-In**: An attempt to record check-out for a volunteer without a prior check-in timestamp raises `AttendanceValidationException("Volunteer has not checked in.")`.
- **Duplicate Check-In Prevention**: An attempt to check in an already checked-in volunteer raises `AttendanceConflictException("Volunteer already checked in.")`.
- **Chronological Validity**: Check-out timestamp cannot precede check-in timestamp (`check_out_time > check_in_time`).
- **Verified Hours Calculation**:
  $$\text{verified\_minutes} = \max\left(0, \left\lfloor\frac{\text{checkout} - \text{checkin}}{60}\right\rfloor - \text{break\_minutes}\right)$$
  Verified hours are strictly computed from these minutes.

---

## 7. Affirmative Consent Enforcement Verification

Maatram enforces 6 affirmative consent dimensions defined in `ConsentRecord`:

| Consent Dimension | Default | Enforced Route / Service | Verification Evidence |
| :--- | :--- | :--- | :--- |
| `leaderboard_visible` | `False` | `gamification_repo.py:75-95` (`get_leaderboard`) | Query appends `WHERE cr.leaderboard_visible = TRUE`. Volunteers who opted out are completely excluded from leaderboard rankings. |
| `name_visible` | `False` | `gamification_service.py:180-210` & `media_service.py` | If `name_visible = False`, display name is masked to `"Anonymous Volunteer"` in leaderboard entries and LinkedIn social copy. |
| `thank_you_emails` | `False` | `event_completion_service.py:140-165` | Outbox communication job `TEMPLATE_THANK_YOU_EVENT` is enqueued only if `consent.thank_you_emails = True`. |
| `linkedin_content` | `False` | `media_service.py:280-310` (`generate_linkedin_draft`) | Volunteers with `linkedin_content = False` are strictly excluded from generated social copy tags and mentions. |
| `contact_available` | `False` | `report_repo.py:110-135` (`get_volunteer_interview_export`) | If `contact_available = False`, phone numbers and personal emails are masked to `"[CONSENT_WITHHELD]"` in administrative interview exports. |
| `media_usage` | `False` | `media_service.py:150-185` (`tag_volunteer_in_media`) | Tagging a volunteer in an event photo raises `ConsentRequiredException` if `media_usage = False`. |

---

## 8. Detailed Findings & Issues

### ISSUE-DB-001 [P2 - Medium]
- **Route/File**: `server/src/core/config.py:91-109`, `server/src/services/gamification_service.py`, `server/src/services/registration_service.py`
- **Description**: Unimplemented Configurable Business Policies in Service Logic
- **Evidence**:
  The application defines several business configuration options in `Settings`:
  - `LEADERBOARD_CYCLE_TYPE`: Literal["CALENDAR_YEAR", "FINANCIAL_YEAR", "ACADEMIC_YEAR"] = "CALENDAR_YEAR"
  - `HOURS_ROUNDING_MODE`: Literal["EXACT_DECIMAL_2", "NEAREST_15_MIN", "FLOOR_HALF_HOUR"] = "EXACT_DECIMAL_2"
  - `WAITLIST_PROMOTION_MODE`: Literal["MANUAL", "FIFO_AUTOMATIC", "HYBRID"] = "MANUAL"
  - `APPLICATION_RESUBMISSION_ALLOWED`: bool = True
  - `RESUBMISSION_COOLDOWN_DAYS`: int = 0
  - `EVENT_OVERBOOKING_PERCENTAGE`: float = 0.0

  However, inspection of `gamification_service.py` and `registration_service.py` reveals that only the default mode is implemented:
  - `gamification_service.py` hardcodes calendar year date ranges and `ROUND_HALF_UP` 2-decimal rounding.
  - `registration_service.py` only implements manual waitlist promotion; `FIFO_AUTOMATIC` and `HYBRID` branches are unreferenced.
  - `registration_service.py` does not apply `EVENT_OVERBOOKING_PERCENTAGE`.
- **Impact**: Changing these configuration settings in `.env` has no effect on system behavior, creating a false operational expectation for administrators.
- **Recommendation**: Either implement conditional branching in the services to honor the non-default options, or add a startup validation check that warns/aborts if unsupported configuration values are specified.

---

### ISSUE-DB-002 [P2 - Medium]
- **Route/File**: `server/src/services/registration_service.py:120-165`
- **Description**: Potential Overbooking Race Condition on Concurrent Event Registrations
- **Evidence**:
  In `registration_service.py:register_for_event`:
  ```python
  current_count = await registration_repo.count_active_registrations(db, event_id)
  if current_count >= event.volunteer_capacity:
      # Put on waitlist
  else:
      # Register as SUBSCRIBED
  ```
  When executed without database row-level locking (`with_for_update()`) on the `Event` row, two concurrent requests arriving simultaneously when 1 spot remains can both read `current_count < capacity` and both receive `SUBSCRIBED` status, exceeding `volunteer_capacity`.
- **Impact**: Popular volunteering events could exceed their designated maximum volunteer headcount under concurrent registration surges.
- **Recommendation**: Acquire a row lock on the `Event` record (`SELECT ... FOR UPDATE`) during the capacity evaluation block inside the transaction.

---

### ISSUE-DB-003 [P2 - Medium]
- **Route/File**: `server/src/core/config.py:100`, `server/src/workers/`
- **Description**: Lack of Automated Inactivity Deactivation Scheduled Job
- **Evidence**:
  `settings.INACTIVE_VOLUNTEER_DAYS_THRESHOLD = 180` is configured in `config.py` to identify dormant volunteers. However, there is no scheduled background task or database query in the codebase that queries volunteers whose last attendance or login was $> 180$ days ago to transition their status to `INACTIVE`.
- **Impact**: Dormant volunteer accounts remain indefinitely `APPROVED`, skewing volunteer directory metrics and active volunteer counts.
- **Recommendation**: Implement an outbox periodic task or background cron job to flag inactive volunteers after 180 days of inactivity.

---

### ISSUE-DB-004 [P3 - Low]
- **Route/File**: `server/src/models/events.py:40-75`
- **Description**: Missing Database-Level Check Constraint for Event Time Ranges
- **Evidence**:
  In `server/src/models/events.py`, the `Event` model defines `start_time` and `end_time` columns, but lacks a PostgreSQL `CheckConstraint("end_time > start_time", name="ck_event_end_after_start")`. The validation currently relies entirely on Pydantic schema validation (`EventCreate`). Direct database inserts or script operations could bypass this invariant.
- **Impact**: Low risk during normal API usage, but database-level integrity is not enforced if raw SQL migrations or data imports occur.
- **Recommendation**: Add `CheckConstraint("end_time > start_time", name="ck_event_end_after_start")` to `Event.__table_args__` in an upcoming Alembic revision.

---

### ISSUE-DB-005 [P3 - Low]
- **Route/File**: `server/alembic/versions/`
- **Description**: Missing Staged Migration Dry-Run Scripts for Live Supabase Pooler
- **Evidence**:
  Alembic versions are limited to 2 migrations. In Supabase deployments with transaction pooling (port 6543), transactional DDL operations that acquire table locks can time out if connection pooling is not temporarily bypassed using direct session connections (`DIRECT_URL` on port 5432).
- **Impact**: Running `alembic upgrade head` through the transaction pooler on AWS Supabase can hang or fail during intensive schema modifications.
- **Recommendation**: Document and enforce that Alembic migrations run against `DIRECT_URL` (port 5432) rather than the pooled connection `DATABASE_URL` (port 6543).

---

## 9. Summary Table of Database & Business Logic Issues

| Issue ID | Severity | File / Component | Title | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-DB-001** | P2 (Medium) | `server/src/core/config.py:91-109` | Unimplemented Business Policy Configurations in Services | OPEN |
| **ISSUE-DB-002** | P2 (Medium) | `server/src/services/registration_service.py:120` | Potential Overbooking Race Condition on Concurrent Registrations | OPEN |
| **ISSUE-DB-003** | P2 (Medium) | `server/src/core/config.py:100` | Lack of Inactivity Auto-Deactivation Scheduled Task | OPEN |
| **ISSUE-DB-004** | P3 (Low) | `server/src/models/events.py:40` | Missing Database Check Constraint on Event Time Range | OPEN |
| **ISSUE-DB-005** | P3 (Low) | `server/alembic/versions/` | Missing Documentation for Direct Connection on Pooler Migrations | OPEN |
