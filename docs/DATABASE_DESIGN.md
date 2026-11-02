# DATABASE_DESIGN.md — Comprehensive Database Engineering Plan
**Maatram Volunteering & Gamification Portal**

---

## 1. Database Architecture & Engineering Standards

The backend interfaces with a managed **Supabase PostgreSQL 16+** database instance. The database is the single source of truth for all business state. FastAPI utilizes **SQLAlchemy 2.x** with the asynchronous **asyncpg** driver, and **Alembic** manages version-controlled schema migrations.

### 1.1 Standard Engineering Invariants:
1. **Primary Keys**: Every table uses a `UUID` primary key with default generation via `gen_random_uuid()` (UUIDv4/v7).
2. **Temporal Standards**: All timestamps are stored in UTC using `TIMESTAMPTZ`. Explicit IANA timezone strings (e.g., `'Asia/Kolkata'`) are stored alongside local event schedules.
3. **Audit Standards**: Core entity tables include `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` and `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
4. **Referential Integrity & Deletion Safeguards**:
   - **Historical Volunteering Data**: Tables preserving volunteering records (`event_registrations`, `attendance_records`, `point_transactions`, `audit_logs`) enforce `ON DELETE RESTRICT` on foreign keys. Destructive cascading deletes of historical contribution records are strictly prohibited.
   - **Ephemeral Records**: Ephemeral authentication tokens and active sessions enforce `ON DELETE CASCADE` when the parent identity is purged.
   - **Optional Media/Asset Links**: Profile avatars, consent documents, and cover media enforce `ON DELETE SET NULL`.
5. **Soft Deletions**: Deletions of core entities (users, events) are modeled as state transitions (`status = 'SUSPENDED'`, `status = 'CANCELLED'`) or flag columns (`is_deleted BOOLEAN NOT NULL DEFAULT FALSE`).

---

### 1.2 Point Precision & Fractional Hour Arithmetic
- **Raw Duration vs. Credited Hours**:
  - Raw attendance is captured as integer minutes: `attendance_records.duration_minutes INTEGER` derived from $(T_{out} - T_{in})\text{ in seconds} / 60$.
  - Credited hours $H$ are computed from duration in minutes. In mathematics, converting minutes to hours yields repeating fractions (e.g., $20\text{ minutes} = \frac{20}{60} = 0.3333...\text{ hours}$; $40\text{ minutes} = \frac{40}{60} = 0.6666...\text{ hours}$).
- **Precision Limitation of `NUMERIC(8, 2)` & Decimal Modeling**:
  - `point_transactions` stores `hours_credited NUMERIC(8, 2)`, `event_points NUMERIC(8, 2)`, `hour_points NUMERIC(8, 2)`, and `total_points NUMERIC(8, 2)`.
  - Storing credited hours as `NUMERIC(8, 2)` introduces intermediate precision rounding (e.g. $20\text{ minutes} \rightarrow 0.33\text{ hrs} \times 2 = 0.66\text{ points}$, whereas exact rational arithmetic yields $\frac{20}{60} \times 2 = 0.6666... \approx 0.67\text{ points}$).
  - **Engineering Resolution**: Python business logic operates strictly with Python `Decimal` (never `float`). The exact credited-hour rounding rule (e.g. rounding before multiplication vs. rounding total points after exact fraction evaluation) remains explicitly **PENDING MAATRAM APPROVAL** in `OPEN_QUESTIONS.md`. The database schema cleanly accommodates both via `NUMERIC(8, 2)`.

---

### 1.3 Immutable Point Ledger & Database Role Privileges
To guarantee mathematical auditability and prevent tampering:
1. **Engine-Level Trigger Enforcement**:
   The `point_transactions` table is protected by a PostgreSQL trigger `trg_prevent_point_ledger_mutation` that aborts any `UPDATE` or `DELETE` attempt:
   ```sql
   CREATE OR REPLACE FUNCTION prevent_point_ledger_mutation()
   RETURNS TRIGGER AS $$
   BEGIN
       RAISE EXCEPTION 'Point transactions ledger is strictly append-only. UPDATE and DELETE operations are forbidden.';
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER trg_prevent_point_ledger_mutation
   BEFORE UPDATE OR DELETE ON point_transactions
   FOR EACH ROW EXECUTE FUNCTION prevent_point_ledger_mutation();
   ```
2. **Database Role Privileges & Least Privilege Architecture**:
   - **Migration Role (`maatram_migration_admin`)**: Owns tables, triggers, and schema definitions. Used exclusively by Alembic CI/CD pipelines.
   - **Application Runtime Role (`maatram_app_user`)**: Used by FastAPI application pods.
     - `GRANT SELECT, INSERT ON point_transactions TO maatram_app_user;`
     - `REVOKE UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON point_transactions FROM maatram_app_user;`
   - **TRUNCATE & Trigger Tampering Protection**:
     - `maatram_app_user` does **not** own `point_transactions` and lacks `ALTER` or `DROP` privileges.
     - Under PostgreSQL security rules, `ALTER TABLE ... DISABLE TRIGGER` and `TRUNCATE` require table ownership or superuser status. Therefore, the application role is cryptographically and architecturally incapable of bypassing ledger protections or clearing tables.
3. **Compensating Transactions**:
   All administrative reversals or corrections are recorded as new rows with `transaction_type = 'COMPENSATION_REVERSAL'`, negative point values, and foreign key pointers to `related_transaction_id`.

---

### 1.4 Outbox Attempts & Worker Crash Recovery
1. **Attempts Definition**:
   `communication_jobs.attempts` tracks the exact number of dispatch attempts executed.
   - When a worker claims a job via `SKIP LOCKED`, it immediately executes:
     `attempts = attempts + 1, status = 'PROCESSING', locked_at = NOW(), worker_id = :worker_id`.
   - Initial dispatch = Attempt 1.
   - Retry 1 = Attempt 2.
   - Retry 2 = Attempt 3.
   - Retry 3 = Attempt 4.
2. **Max Retries Policy**:
   `max_retries = 3` defines the maximum allowed retries *after* the initial failure. Under this rule, a job is granted **exactly four total dispatch attempts** (1 initial + 3 retries) before transitioning to `DEAD_LETTER`.
3. **Lease Timeout & Sweeper**:
   If a worker crashes or drops connection during processing, `status` remains `'PROCESSING'`. A periodic background recovery sweeper scans for `status = 'PROCESSING' AND locked_at < NOW() - INTERVAL '5 minutes'`.
   - If `attempts <= max_retries + 1` (i.e. $\le 4$), it resets `status = 'PENDING', locked_at = NULL, worker_id = NULL`.
   - If `attempts > 4`, it transitions `status = 'DEAD_LETTER', locked_at = NULL`.

---

### 1.5 Minor Volunteer Safeguarding & Parental Consent Architecture
1. **Separation of Evidence, Submission, and Verification**:
   - An applicant can **never** self-verify parental consent via a simple public checkbox.
   - The volunteer registration process records parental consent **submission** (`parental_consent_submitted = TRUE`), guardian contact info, and an optional signed PDF/image (`parental_consent_document_media_id`).
   - The verified status `parental_consent_status` remains `PENDING_VERIFICATION` until an authorized `ADMIN` or `SUPER_ADMIN` independently verifies the document/contact and records `parental_consent_status = 'VERIFIED'`, their `user_id`, a timestamp, and audit notes.

---

## 2. Entity-Relationship Architecture

```
                    +--------------------+
                    |       users        |
                    +---------+----------+
                              | 1
                              |
         +--------------------+--------------------+--------------------+
         | 1                  | 1                  | 1                  | 1
         v                    v                    v                    v
+------------------+  +---------------+  +------------------+  +--------------------+
|volunteer_profiles|  |consent_records|  |  user_sessions   |  | admin_permissions  |
+--------+---------+  +-------+-------+  +------------------+  +--------------------+
         | 1                  | 1
         |                    v
         |            +---------------+
         |            |consent_history|
         |            +---------------+
   +-----+-----+
   |     |     | (1:1 Polymorphic Profiles)
   v     v     v
+-----+ +----+ +---------+
|stud | |alum| |corporate|
|prof | |prof| | profile |
+-----+ +----+ +---------+
   |
   | (1:N)
   v
+--------------------------+          +-------------------------+
|   event_registrations    | <------- |         events          |
+------------+-------------+          +------------+------------+
             | 1                                   | 1
             v                                     v
+--------------------------+          +-------------------------+
|    attendance_records    |          |      event_photos       |
+------------+-------------+          +-------------------------+
             | 1
             v
+--------------------------+
|  attendance_corrections  |
+--------------------------+
             | (1:N from volunteer & event)
             v
+--------------------------+
|    point_transactions    | (Append-Only Trigger Protected, REVOKE UPDATE/DELETE)
+--------------------------+
```

---

## 3. Detailed Table Specifications

---

### Module 1: Identity & Authentication

#### 1. `users`
- **Purpose**: Canonical authentication and base user identity record.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `email` (VARCHAR(255), NOT NULL, lowercase)
  - `password_hash` (VARCHAR(255), NOT NULL, Argon2id encoded string)
  - `role` (VARCHAR(30), NOT NULL, Check: `role IN ('VOLUNTEER', 'ADMIN', 'SUPER_ADMIN')`)
  - `status` (VARCHAR(30), NOT NULL, default `'UNVERIFIED'`, Check: `status IN ('UNVERIFIED', 'PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED')`)
  - `is_active` (BOOLEAN, NOT NULL, default `TRUE`)
  - `failed_login_attempts` (INTEGER, NOT NULL, default 0)
  - `locked_until` (TIMESTAMPTZ, NULL)
  - `last_login_at` (TIMESTAMPTZ, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: None
- **Unique Constraints**: `uq_users_email` (`email`)
- **Check Constraints**: `chk_users_role`, `chk_users_status`, `chk_users_failed_attempts_non_negative` (`failed_login_attempts >= 0`)
- **Indexes**:
  - `ix_users_email` (`email`)
  - `ix_users_role_status` (`role`, `status`)
- **Retention**: Indefinite. Soft deactivated via `is_active = FALSE` or `status = 'SUSPENDED'`.

#### 2. `user_sessions`
- **Purpose**: Active server-tracked client sessions for refresh token rotation and remote revocation.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `user_id` (UUID, NOT NULL)
  - `refresh_token_hash` (VARCHAR(255), NOT NULL)
  - `device_info` (VARCHAR(255), NULL)
  - `ip_address` (INET, NULL)
  - `client_type` (VARCHAR(20), NOT NULL, Check: `client_type IN ('WEB', 'MOBILE')`)
  - `is_revoked` (BOOLEAN, NOT NULL, default `FALSE`)
  - `expires_at` (TIMESTAMPTZ, NOT NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `last_used_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_user_sessions_user_id` -> `users(id)` ON DELETE CASCADE
- **Unique Constraints**: `uq_user_sessions_refresh_token_hash` (`refresh_token_hash`)
- **Indexes**:
  - `ix_user_sessions_user_id` (`user_id`)
  - `ix_user_sessions_expires_at` (`expires_at`)
  - `ix_user_sessions_active` (`user_id`, `is_revoked`) WHERE `is_revoked = FALSE`
- **Retention**: Automated cron purges revoked or expired sessions older than 30 days.

#### 3. `email_verifications`
- **Purpose**: One-time email ownership verification tokens.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `user_id` (UUID, NOT NULL)
  - `token_hash` (VARCHAR(255), NOT NULL)
  - `expires_at` (TIMESTAMPTZ, NOT NULL)
  - `is_used` (BOOLEAN, NOT NULL, default `FALSE`)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_email_verifications_user_id` -> `users(id)` ON DELETE CASCADE
- **Unique Constraints**: `uq_email_verifications_token_hash` (`token_hash`)
- **Indexes**:
  - `ix_email_verifications_user_id` (`user_id`)
- **Retention**: Automated purge of records older than 7 days.

#### 4. `password_reset_tokens`
- **Purpose**: Numerical OTP or hashed tokens for password reset flows.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `user_id` (UUID, NOT NULL)
  - `otp_hash` (VARCHAR(255), NOT NULL)
  - `attempt_count` (INTEGER, NOT NULL, default 0)
  - `max_attempts` (INTEGER, NOT NULL, default 5)
  - `expires_at` (TIMESTAMPTZ, NOT NULL)
  - `is_used` (BOOLEAN, NOT NULL, default `FALSE`)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_password_reset_tokens_user_id` -> `users(id)` ON DELETE CASCADE
- **Check Constraints**: `chk_password_reset_attempts` (`attempt_count <= max_attempts`)
- **Indexes**:
  - `ix_password_reset_user_id` (`user_id`)
- **Retention**: Automated purge of records older than 7 days.

---

### Module 2: Volunteer Profiles & Classifications

#### 5. `volunteer_profiles`
- **Purpose**: Base volunteer attributes shared across all volunteer categories, including minor safeguarding.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `user_id` (UUID, NOT NULL)
  - `first_name` (VARCHAR(100), NOT NULL)
  - `last_name` (VARCHAR(100), NOT NULL)
  - `mobile_number` (VARCHAR(20), NOT NULL)
  - `age` (INTEGER, NOT NULL)
  - `gender` (VARCHAR(20), NOT NULL, Check: `gender IN ('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY')`)
  - `category` (VARCHAR(30), NOT NULL, Check: `category IN ('STUDENT', 'ALUMNI', 'CORPORATE')`)
  - `avatar_media_id` (UUID, NULL)
  - `bio` (TEXT, NULL)
  - `parent_guardian_name` (VARCHAR(150), NULL)
  - `parent_guardian_relationship` (VARCHAR(50), NULL)
  - `parent_guardian_contact` (VARCHAR(20), NULL)
  - `parental_consent_submitted` (BOOLEAN, NOT NULL, default `FALSE`)
  - `parental_consent_document_media_id` (UUID, NULL)
  - `parental_consent_status` (VARCHAR(30), NOT NULL, default `'NOT_REQUIRED'`, Check: `parental_consent_status IN ('NOT_REQUIRED', 'PENDING_VERIFICATION', 'VERIFIED', 'REJECTED')`)
  - `parental_consent_verified_by_user_id` (UUID, NULL)
  - `parental_consent_verified_at` (TIMESTAMPTZ, NULL)
  - `parental_consent_notes` (TEXT, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_volunteer_profiles_user_id` -> `users(id)` ON DELETE RESTRICT
  - `fk_volunteer_profiles_media` -> `media_assets(id)` ON DELETE SET NULL
  - `fk_volunteer_profiles_consent_doc` -> `media_assets(id)` ON DELETE SET NULL
  - `fk_volunteer_profiles_consent_verifier` -> `users(id)` ON DELETE RESTRICT
- **Unique Constraints**:
  - `uq_volunteer_profiles_user_id` (`user_id`)
  - `uq_volunteer_profiles_mobile` (`mobile_number`)
- **Check Constraints**: `chk_volunteer_age_sanity` (`age > 0 AND age <= 120`) [POLICY NOTE: Minimum volunteer eligibility age is governed by configurable application policy `MINIMUM_VOLUNTEER_AGE` pending formal Maatram legal approval].
- **Indexes**:
  - `ix_volunteer_profiles_category` (`category`)
  - `ix_volunteer_profiles_mobile` (`mobile_number`)
  - `ix_volunteer_profiles_names` (`last_name`, `first_name`)
  - `ix_volunteer_profiles_consent_status` (`parental_consent_status`)
- **Retention**: Indefinite. Protected by deletion restrictions.

#### 6. `student_profiles`
- **Purpose**: Specific attributes for active student volunteers.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `volunteer_profile_id` (UUID, NOT NULL)
  - `college_name` (VARCHAR(255), NOT NULL)
  - `degree` (VARCHAR(100), NOT NULL)
  - `department` (VARCHAR(100), NOT NULL)
  - `batch_year` (INTEGER, NOT NULL)
  - `current_year` (INTEGER, NOT NULL, Check: `current_year BETWEEN 1 AND 5`)
  - `maatram_reg_number` (VARCHAR(50), NOT NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_student_profiles_volunteer_id` -> `volunteer_profiles(id)` ON DELETE CASCADE
- **Unique Constraints**:
  - `uq_student_profiles_volunteer_id` (`volunteer_profile_id`)
  - `uq_student_profiles_maatram_reg` (`maatram_reg_number`)
- **Indexes**:
  - `ix_student_profiles_college` (`college_name`)
  - `ix_student_profiles_batch` (`batch_year`)

#### 7. `alumni_profiles`
- **Purpose**: Specific attributes for graduated alumni volunteers.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `volunteer_profile_id` (UUID, NOT NULL)
  - `organisation` (VARCHAR(255), NOT NULL)
  - `job_role` (VARCHAR(150), NOT NULL)
  - `years_of_experience` (NUMERIC(4, 1), NOT NULL, Check: `years_of_experience >= 0`)
  - `location` (VARCHAR(150), NOT NULL)
  - `skills` (TEXT[], NOT NULL DEFAULT '{}')
  - `college_name` (VARCHAR(255), NOT NULL)
  - `degree` (VARCHAR(100), NOT NULL)
  - `department` (VARCHAR(100), NOT NULL)
  - `batch_year` (INTEGER, NOT NULL)
  - `graduation_year` (INTEGER, NOT NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_alumni_profiles_volunteer_id` -> `volunteer_profiles(id)` ON DELETE CASCADE
- **Unique Constraints**: `uq_alumni_profiles_volunteer_id` (`volunteer_profile_id`)
- **Indexes**:
  - `ix_alumni_profiles_org` (`organisation`)
  - `ix_alumni_profiles_skills` USING GIN (`skills`)
  - `ix_alumni_profiles_location` (`location`)

#### 8. `corporate_profiles`
- **Purpose**: Specific attributes for corporate panelist volunteers.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `volunteer_profile_id` (UUID, NOT NULL)
  - `organisation` (VARCHAR(255), NOT NULL)
  - `designation` (VARCHAR(150), NOT NULL)
  - `years_of_experience` (NUMERIC(4, 1), NOT NULL, Check: `years_of_experience >= 0`)
  - `location` (VARCHAR(150), NOT NULL)
  - `skills` (TEXT[], NOT NULL DEFAULT '{}')
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_corporate_profiles_volunteer_id` -> `volunteer_profiles(id)` ON DELETE CASCADE
- **Unique Constraints**: `uq_corporate_profiles_volunteer_id` (`volunteer_profile_id`)
- **Indexes**:
  - `ix_corporate_profiles_org` (`organisation`)
  - `ix_corporate_profiles_skills` USING GIN (`skills`)

---

### Module 3: Applications & Review

#### 9. `volunteer_applications`
- **Purpose**: Volunteer onboarding application state and submission record.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `volunteer_profile_id` (UUID, NOT NULL)
  - `status` (VARCHAR(30), NOT NULL, default `'PENDING'`, Check: `status IN ('PENDING', 'APPROVED', 'REJECTED')`)
  - `submitted_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `current_stage` (INTEGER, NOT NULL, default 6)
  - `notes` (TEXT, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_volunteer_applications_profile_id` -> `volunteer_profiles(id)` ON DELETE RESTRICT
- **Unique Constraints**: `uq_volunteer_applications_profile_id` (`volunteer_profile_id`)
- **Indexes**:
  - `ix_volunteer_applications_status` (`status`)
  - `ix_volunteer_applications_submitted` (`submitted_at`)

#### 10. `application_reviews`
- **Purpose**: Administrative decision history for onboarding applications.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `application_id` (UUID, NOT NULL)
  - `reviewer_id` (UUID, NOT NULL)
  - `action` (VARCHAR(30), NOT NULL, Check: `action IN ('APPROVED', 'REJECTED')`)
  - `reason` (TEXT, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_application_reviews_app_id` -> `volunteer_applications(id)` ON DELETE RESTRICT
  - `fk_application_reviews_reviewer_id` -> `users(id)` ON DELETE RESTRICT
- **Indexes**:
  - `ix_application_reviews_app_id` (`application_id`)
  - `ix_application_reviews_reviewer` (`reviewer_id`)

---

### Module 4: Privacy & Consent

#### 11. `consent_records`
- **Purpose**: Current affirmative consent status across all privacy dimensions.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `volunteer_profile_id` (UUID, NOT NULL)
  - `leaderboard_visible` (BOOLEAN, NOT NULL, default `FALSE`) [POLICY: PENDING_APPROVAL]
  - `name_visible` (BOOLEAN, NOT NULL, default `FALSE`) [POLICY: PENDING_APPROVAL]
  - `thank_you_emails` (BOOLEAN, NOT NULL, default `FALSE`) [POLICY: PENDING_APPROVAL]
  - `linkedin_content` (BOOLEAN, NOT NULL, default `FALSE`) [POLICY: PENDING_APPROVAL]
  - `contact_available` (BOOLEAN, NOT NULL, default `FALSE`) [POLICY: PENDING_APPROVAL]
  - `media_usage` (BOOLEAN, NOT NULL, default `FALSE`) [POLICY: PENDING_APPROVAL]
  - `version` (INTEGER, NOT NULL, default 1)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_consent_records_profile_id` -> `volunteer_profiles(id)` ON DELETE CASCADE
- **Unique Constraints**: `uq_consent_records_profile_id` (`volunteer_profile_id`)
- **Indexes**: None (1:1 with profile)

#### 12. `consent_history`
- **Purpose**: Immutable audit log of all consent changes.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `consent_record_id` (UUID, NOT NULL)
  - `dimension` (VARCHAR(50), NOT NULL)
  - `old_value` (BOOLEAN, NOT NULL)
  - `new_value` (BOOLEAN, NOT NULL)
  - `changed_by_user_id` (UUID, NOT NULL)
  - `ip_address` (INET, NULL)
  - `user_agent` (VARCHAR(255), NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_consent_history_record_id` -> `consent_records(id)` ON DELETE CASCADE
  - `fk_consent_history_user_id` -> `users(id)` ON DELETE RESTRICT
- **Indexes**:
  - `ix_consent_history_record_id` (`consent_record_id`)
  - `ix_consent_history_created_at` (`created_at`)

---

### Module 5: Events & Registrations

#### 13. `events`
- **Purpose**: Volunteering opportunities and events.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `title` (VARCHAR(255), NOT NULL)
  - `description` (TEXT, NOT NULL)
  - `category` (VARCHAR(50), NOT NULL, Check: `category IN ('SCHOOL_VISIT', 'BGV', 'ADMISSIONS', 'MOCK_INTERVIEW', 'PANEL_INTERVIEW', 'OTHER')`)
  - `mode` (VARCHAR(20), NOT NULL, Check: `mode IN ('ONLINE', 'OFFLINE')`)
  - `location` (VARCHAR(255), NOT NULL)
  - `start_time` (TIMESTAMPTZ, NOT NULL)
  - `end_time` (TIMESTAMPTZ, NOT NULL)
  - `timezone` (VARCHAR(50), NOT NULL, default `'Asia/Kolkata'`)
  - `capacity_required` (INTEGER, NOT NULL)
  - `registration_deadline` (TIMESTAMPTZ, NOT NULL)
  - `status` (VARCHAR(30), NOT NULL, default `'DRAFT'`, Check: `status IN ('DRAFT', 'PUBLISHED', 'REGISTRATION_CLOSED', 'ONGOING', 'COMPLETED', 'CANCELLED')`)
  - `cover_media_id` (UUID, NULL)
  - `created_by_user_id` (UUID, NOT NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_events_media_id` -> `media_assets(id)` ON DELETE SET NULL
  - `fk_events_creator_id` -> `users(id)` ON DELETE RESTRICT
- **Check Constraints**:
  - `chk_events_times` (`end_time > start_time`)
  - `chk_events_deadline` (`registration_deadline <= start_time`)
  - `chk_events_capacity_positive` (`capacity_required > 0`)
- **Indexes**:
  - `ix_events_status_start` (`status`, `start_time`)
  - `ix_events_category` (`category`)
  - `ix_events_created_by` (`created_by_user_id`)

#### 14. `event_registrations`
- **Purpose**: Volunteer applications to participate in specific events.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `event_id` (UUID, NOT NULL)
  - `volunteer_profile_id` (UUID, NOT NULL)
  - `status` (VARCHAR(30), NOT NULL, default `'SUBSCRIBED'`, Check: `status IN ('SUBSCRIBED', 'SELECTED', 'WAITLISTED', 'NOT_SELECTED', 'DECLINED', 'WITHDRAWN')`)
  - `selected_at` (TIMESTAMPTZ, NULL)
  - `withdrawn_at` (TIMESTAMPTZ, NULL)
  - `notes` (TEXT, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_registrations_event_id` -> `events(id)` ON DELETE RESTRICT
  - `fk_registrations_volunteer_id` -> `volunteer_profiles(id)` ON DELETE RESTRICT
- **Unique Constraints**: `uq_event_registrations_event_volunteer` (`event_id`, `volunteer_profile_id`)
- **Indexes**:
  - `ix_registrations_event_status` (`event_id`, `status`)
  - `ix_registrations_volunteer` (`volunteer_profile_id`)
  - `ix_registrations_created_at` (`created_at`)

#### 15. `registration_history`
- **Purpose**: Audit trail of registration state transitions.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `registration_id` (UUID, NOT NULL)
  - `old_status` (VARCHAR(30), NOT NULL)
  - `new_status` (VARCHAR(30), NOT NULL)
  - `changed_by_user_id` (UUID, NOT NULL)
  - `reason` (TEXT, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_reg_history_registration_id` -> `event_registrations(id)` ON DELETE CASCADE
  - `fk_reg_history_user_id` -> `users(id)` ON DELETE RESTRICT
- **Indexes**:
  - `ix_reg_history_reg_id` (`registration_id`)

---

### Module 6: Attendance Tracking & Corrections

#### 16. `attendance_records`
- **Purpose**: Physical or virtual attendance logs for selected volunteers.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `event_registration_id` (UUID, NOT NULL)
  - `check_in_time` (TIMESTAMPTZ, NOT NULL)
  - `check_out_time` (TIMESTAMPTZ, NULL)
  - `duration_minutes` (INTEGER, NULL)
  - `status` (VARCHAR(30), NOT NULL, default `'IN_PROGRESS'`, Check: `status IN ('IN_PROGRESS', 'COMPLETED', 'INCOMPLETE', 'ABSENT')`)
  - `verified_by_user_id` (UUID, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `updated_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_attendance_registration_id` -> `event_registrations(id)` ON DELETE RESTRICT
  - `fk_attendance_verifier_id` -> `users(id)` ON DELETE RESTRICT
- **Unique Constraints**: `uq_attendance_registration_id` (`event_registration_id`)
- **Check Constraints**:
  - `chk_attendance_checkout_after_checkin` (`check_out_time IS NULL OR check_out_time >= check_in_time`)
  - `chk_attendance_duration_non_negative` (`duration_minutes IS NULL OR duration_minutes >= 0`)
- **Indexes**:
  - `ix_attendance_status` (`status`)
  - `ix_attendance_registration` (`event_registration_id`)

#### 17. `attendance_corrections`
- **Purpose**: Auditable administrative overrides of attendance durations.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `attendance_record_id` (UUID, NOT NULL)
  - `admin_id` (UUID, NOT NULL)
  - `old_check_in_time` (TIMESTAMPTZ, NOT NULL)
  - `new_check_in_time` (TIMESTAMPTZ, NOT NULL)
  - `old_check_out_time` (TIMESTAMPTZ, NULL)
  - `new_check_out_time` (TIMESTAMPTZ, NOT NULL)
  - `old_duration_minutes` (INTEGER, NULL)
  - `new_duration_minutes` (INTEGER, NOT NULL)
  - `reason` (TEXT, NOT NULL)
  - `super_admin_approved_by` (UUID, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_corrections_attendance_id` -> `attendance_records(id)` ON DELETE RESTRICT
  - `fk_corrections_admin_id` -> `users(id)` ON DELETE RESTRICT
  - `fk_corrections_super_admin_id` -> `users(id)` ON DELETE RESTRICT
- **Indexes**:
  - `ix_corrections_attendance_id` (`attendance_record_id`)
  - `ix_corrections_admin` (`admin_id`)

---

### Module 7: Gamification & Points (Trigger-Protected Immutable Ledger)

#### 18. `point_transactions`
- **Purpose**: Append-only ledger recording all awarded gamification points with decimal precision.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `volunteer_profile_id` (UUID, NOT NULL)
  - `event_id` (UUID, NULL)
  - `related_transaction_id` (UUID, NULL) -- Pointer for compensating reversals
  - `event_points` (NUMERIC(8, 2), NOT NULL, default 0.00)
  - `hour_points` (NUMERIC(8, 2), NOT NULL, default 0.00)
  - `total_points` (NUMERIC(8, 2), NOT NULL)
  - `hours_credited` (NUMERIC(8, 2), NOT NULL, default 0.00)
  - `transaction_type` (VARCHAR(30), NOT NULL, Check: `transaction_type IN ('EVENT_COMPLETION', 'MANUAL_ADJUSTMENT', 'ACHIEVEMENT_BONUS', 'COMPENSATION_REVERSAL')`)
  - `awarded_by_user_id` (UUID, NULL)
  - `reason` (TEXT, NULL)
  - `cycle_year` (INTEGER, NOT NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_points_volunteer_id` -> `volunteer_profiles(id)` ON DELETE RESTRICT
  - `fk_points_event_id` -> `events(id)` ON DELETE RESTRICT
  - `fk_points_admin_id` -> `users(id)` ON DELETE RESTRICT
  - `fk_points_related_tx` -> `point_transactions(id)` ON DELETE RESTRICT
- **Unique Constraints**: `uq_points_volunteer_event` (`volunteer_profile_id`, `event_id`) WHERE `event_id IS NOT NULL AND transaction_type = 'EVENT_COMPLETION'`
- **Check Constraints**:
  - `chk_points_sum` (`total_points = event_points + hour_points`)
- **Database Engine Trigger**:
  Protected by `trg_prevent_point_ledger_mutation` terminating any `UPDATE` or `DELETE` statement.
- **Runtime Role Permissions**:
  `REVOKE UPDATE, DELETE, TRUNCATE, TRIGGER ON point_transactions FROM maatram_app_user;`
- **Indexes**:
  - `ix_points_volunteer_cycle` (`volunteer_profile_id`, `cycle_year`)
  - `ix_points_cycle_points` (`cycle_year`, `total_points` DESC)
  - `ix_points_created_at` (`created_at`)

#### 19. `achievement_definitions`
- **Purpose**: System catalog of badge and recognition criteria.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `code` (VARCHAR(50), NOT NULL)
  - `title` (VARCHAR(100), NOT NULL)
  - `description` (TEXT, NOT NULL)
  - `icon_url` (VARCHAR(255), NOT NULL)
  - `category` (VARCHAR(50), NOT NULL)
  - `criteria_type` (VARCHAR(50), NOT NULL, Check: `criteria_type IN ('TOTAL_HOURS', 'TOTAL_EVENTS', 'CATEGORY_EVENTS', 'STREAK')`)
  - `criteria_threshold` (NUMERIC(8, 2), NOT NULL)
  - `is_active` (BOOLEAN, NOT NULL, default `TRUE`)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Unique Constraints**: `uq_achievements_code` (`code`)

#### 20. `volunteer_achievements`
- **Purpose**: Badges earned by volunteers.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `volunteer_profile_id` (UUID, NOT NULL)
  - `achievement_id` (UUID, NOT NULL)
  - `awarded_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_vol_achievements_profile_id` -> `volunteer_profiles(id)` ON DELETE RESTRICT
  - `fk_vol_achievements_def_id` -> `achievement_definitions(id)` ON DELETE RESTRICT
- **Unique Constraints**: `uq_volunteer_achievement` (`volunteer_profile_id`, `achievement_id`)
- **Indexes**:
  - `ix_vol_achievements_profile` (`volunteer_profile_id`)

---

### Module 8: Notifications & Push Devices

#### 21. `notifications`
- **Purpose**: In-app notifications inbox. Source of truth for notification delivery and read status.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `user_id` (UUID, NOT NULL)
  - `title` (VARCHAR(150), NOT NULL)
  - `message` (TEXT, NOT NULL)
  - `type` (VARCHAR(50), NOT NULL)
  - `action_url` (VARCHAR(255), NULL)
  - `is_read` (BOOLEAN, NOT NULL, default `FALSE`)
  - `read_at` (TIMESTAMPTZ, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_notifications_user_id` -> `users(id)` ON DELETE CASCADE
- **Indexes**:
  - `ix_notifications_user_unread` (`user_id`, `is_read`, `created_at` DESC)

#### 22. `device_tokens`
- **Purpose**: Registered Firebase Cloud Messaging (FCM) tokens for Flutter clients.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `user_id` (UUID, NOT NULL)
  - `fcm_token` (VARCHAR(255), NOT NULL)
  - `device_platform` (VARCHAR(20), NOT NULL, Check: `device_platform IN ('ANDROID', 'IOS')`)
  - `is_active` (BOOLEAN, NOT NULL, default `TRUE`)
  - `last_seen_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_device_tokens_user_id` -> `users(id)` ON DELETE CASCADE
- **Unique Constraints**: `uq_device_tokens_fcm` (`fcm_token`)
- **Indexes**:
  - `ix_device_tokens_user_active` (`user_id`, `is_active`)

---

### Module 9: Communications & Transactional Outbox

#### 23. `communication_jobs`
- **Purpose**: Transactional outbox table for reliable asynchronous email and push notification delivery.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `channel` (VARCHAR(20), NOT NULL, Check: `channel IN ('EMAIL', 'PUSH')`)
  - `recipient` (VARCHAR(255), NOT NULL)
  - `template_name` (VARCHAR(100), NOT NULL)
  - `payload` (JSONB, NOT NULL)
  - `status` (VARCHAR(20), NOT NULL, default `'PENDING'`, Check: `status IN ('PENDING', 'PROCESSING', 'SENT', 'FAILED', 'DEAD_LETTER')`)
  - `attempts` (INTEGER, NOT NULL, default 0) -- Increments on each dispatch claim; total attempts allowed = 1 initial + max_retries = 4
  - `max_retries` (INTEGER, NOT NULL, default 3) -- Maximum allowed retries after initial failure
  - `last_error` (TEXT, NULL)
  - `idempotency_key` (VARCHAR(255), NOT NULL)
  - `scheduled_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
  - `locked_at` (TIMESTAMPTZ, NULL) -- Timestamp when job was claimed by worker
  - `worker_id` (VARCHAR(100), NULL) -- Worker/pod identifier holding the lease
  - `sent_at` (TIMESTAMPTZ, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Unique Constraints**: `uq_comm_jobs_idempotency` (`idempotency_key`)
- **Indexes**:
  - `ix_comm_jobs_worker_poll` (`status`, `scheduled_at`, `created_at`) WHERE `status = 'PENDING'`
  - `ix_comm_jobs_lease_recovery` (`status`, `locked_at`) WHERE `status = 'PROCESSING'`
  - `ix_comm_jobs_dead_letter` (`status`, `created_at` DESC) WHERE `status = 'DEAD_LETTER'`

#### 24. `communication_logs`
- **Purpose**: Permanent delivery audit archive.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `job_id` (UUID, NULL)
  - `channel` (VARCHAR(20), NOT NULL)
  - `recipient` (VARCHAR(255), NOT NULL)
  - `provider` (VARCHAR(50), NOT NULL)
  - `provider_message_id` (VARCHAR(100), NULL)
  - `status` (VARCHAR(30), NOT NULL)
  - `error_message` (TEXT, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_comm_logs_job_id` -> `communication_jobs(id)` ON DELETE SET NULL
- **Indexes**:
  - `ix_comm_logs_recipient` (`recipient`)
  - `ix_comm_logs_created_at` (`created_at`)

---

### Module 10: Media Assets & Event Photos

#### 25. `media_assets`
- **Purpose**: Cloudinary uploaded media registry with ownership and metadata.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `public_id` (VARCHAR(255), NOT NULL)
  - `secure_url` (VARCHAR(512), NOT NULL)
  - `asset_type` (VARCHAR(50), NOT NULL, Check: `asset_type IN ('AVATAR', 'EVENT_COVER', 'EVENT_GALLERY', 'DOCUMENT', 'PARENTAL_CONSENT')`)
  - `format` (VARCHAR(20), NOT NULL)
  - `byte_size` (INTEGER, NOT NULL)
  - `width` (INTEGER, NULL)
  - `height` (INTEGER, NULL)
  - `uploaded_by_user_id` (UUID, NOT NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_media_assets_uploader_id` -> `users(id)` ON DELETE RESTRICT
- **Unique Constraints**: `uq_media_assets_public_id` (`public_id`)
- **Indexes**:
  - `ix_media_assets_uploader` (`uploaded_by_user_id`)

#### 26. `event_photos`
- **Purpose**: Associative gallery linking media assets to events.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `event_id` (UUID, NOT NULL)
  - `media_asset_id` (UUID, NOT NULL)
  - `caption` (VARCHAR(255), NULL)
  - `is_featured` (BOOLEAN, NOT NULL, default `FALSE`)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_event_photos_event_id` -> `events(id)` ON DELETE CASCADE
  - `fk_event_photos_media_id` -> `media_assets(id)` ON DELETE RESTRICT
- **Unique Constraints**: `uq_event_photos_pair` (`event_id`, `media_asset_id`)

---

### Module 11: Administration, Permissions & Audit Logging

#### 27. `admin_permissions`
- **Purpose**: Granular privilege assignments for Admin and Super Admin users.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `user_id` (UUID, NOT NULL)
  - `permission_key` (VARCHAR(100), NOT NULL)
  - `granted_by_user_id` (UUID, NOT NULL)
  - `granted_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_admin_perms_user_id` -> `users(id)` ON DELETE CASCADE
  - `fk_admin_perms_granter_id` -> `users(id)` ON DELETE RESTRICT
- **Unique Constraints**: `uq_admin_permissions_user_key` (`user_id`, `permission_key`)

#### 28. `audit_logs`
- **Purpose**: Immutable security and administrative activity log.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `actor_user_id` (UUID, NULL)
  - `action` (VARCHAR(100), NOT NULL)
  - `resource_type` (VARCHAR(50), NOT NULL)
  - `resource_id` (VARCHAR(100), NOT NULL)
  - `ip_address` (INET, NULL)
  - `user_agent` (VARCHAR(255), NULL)
  - `old_state` (JSONB, NULL)
  - `new_state` (JSONB, NULL)
  - `reason` (TEXT, NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**: `fk_audit_logs_actor_id` -> `users(id)` ON DELETE SET NULL
- **Indexes**:
  - `ix_audit_logs_resource` (`resource_type`, `resource_id`)
  - `ix_audit_logs_actor` (`actor_user_id`)
  - `ix_audit_logs_created_at` (`created_at` DESC)

---

### Module 12: Reporting & Data Exports

#### 29. `report_exports`
- **Purpose**: Tracking asynchronous report and CSV generation jobs.
- **Columns**:
  - `id` (UUID, PK, default `gen_random_uuid()`)
  - `requested_by_user_id` (UUID, NOT NULL)
  - `report_type` (VARCHAR(50), NOT NULL)
  - `parameters` (JSONB, NOT NULL DEFAULT '{}')
  - `file_media_id` (UUID, NULL)
  - `status` (VARCHAR(30), NOT NULL, default `'PENDING'`, Check: `status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')`)
  - `error_message` (TEXT, NULL)
  - `expires_at` (TIMESTAMPTZ, NOT NULL)
  - `created_at` (TIMESTAMPTZ, NOT NULL, default `NOW()`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `fk_report_exports_user_id` -> `users(id)` ON DELETE RESTRICT
  - `fk_report_exports_media_id` -> `media_assets(id)` ON DELETE SET NULL
- **Indexes**:
  - `ix_report_exports_user` (`requested_by_user_id`)
  - `ix_report_exports_status` (`status`)
