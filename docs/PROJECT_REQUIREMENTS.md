# PROJECT_REQUIREMENTS.md — Comprehensive Requirements Specification
**Maatram Volunteering & Gamification Portal**

---

## 1. Executive Summary

The Maatram Volunteering & Gamification Portal is an enterprise-grade digital platform developed for the **Maatram Foundation**. The foundation empowers deserving students from underprivileged backgrounds by providing free higher education, mentorship, life-skills training, and placement assistance. 

To scale its operational impact, the foundation requires a centralized, database-driven platform to manage:
- Volunteer onboarding, classification, verification, and governance.
- Both online and offline volunteering events and opportunities.
- Event registration, volunteer selection, capacity protection, and waitlisting.
- Accurate attendance tracking, checkout verification, and contribution hour logging.
- Transparent, gamified volunteer engagement with verifiable decimal point ledgers (`NUMERIC(8, 2)`) and multi-tier leaderboards.
- Privacy-first consent management for public recognition, media usage, and communications.
- Automated multi-channel communications (Email via Resend with outbox lease recovery, Push via Firebase Cloud Messaging with selective token invalidation).
- Centralized reporting and analytics for administrative decision-making.

The platform serves two primary frontends:
1. **Next.js Web Application**: Responsive web portal for volunteers and administrative staff.
2. **Flutter Mobile Application**: Native iOS/Android app for on-the-go volunteer engagement, check-in/out, and push notifications.

Both clients interact with a unified **FastAPI** backend and a managed **Supabase PostgreSQL** database.

---

## 2. User Roles & Permission Hierarchy

### 2.1 User Roles
1. **Volunteer**:
   - Registered individual seeking to contribute time and skills.
   - Profile state transitions: `PENDING` -> `APPROVED` (or `REJECTED`).
   - Permissions: Browse published events, register for open events, view own registrations and attendance, inspect earned points/achievements, view public leaderboards, manage personal profile and privacy consent settings.
2. **Admin**:
   - Foundation operational team member or authorized program coordinator.
   - Permissions: Manage volunteers (review applications, approve/reject), create/manage events, oversee registration and selection, execute check-in/check-out and attendance corrections ($\le 2\text{ hours}$ by default), trigger event completion workflows, send manual notifications, view standard reports.
3. **Super Admin**:
   - Executive leadership and technical administrators.
   - Permissions: All Admin privileges, plus: assign/revoke Admin roles, access full system audit logs, configure system-wide parameters (gamification rules, leaderboard cycles), approve major attendance corrections ($> 2\text{ hours}$), execute administrative point adjustments via compensating ledger transactions, inspect and requeue dead-letter outbox jobs, export sensitive data, and manage integration credentials.

### 2.2 Volunteer Categories (Profile Classifications)
Categories define profile schemas and skill sets; they are **not** separate authentication roles:
1. **Student Volunteer**:
   - Current college students (often Maatram beneficiaries or student ambassadors).
   - Specific fields: College name, Degree, Department, Current year of study, Batch year, Maatram Registration Number.
2. **Alumni Volunteer**:
   - Graduated beneficiaries or past volunteers now active in the workforce.
   - Specific fields: Current organisation, Job role/designation, Total years of experience, Professional location, Core skills, College name, Degree, Department, Batch year, Graduation year.
3. **Corporate Panelist**:
   - Working professionals offering domain expertise for mock interviews, panel interviews, resume reviews, or corporate mentorship.
   - Specific fields: Current organisation, Corporate designation, Total years of experience, Work location, Domain expertise/skills.

---

## 3. Operational Volunteering Activities

The portal models both **Online** (virtual) and **Offline** (in-person) activities:
1. **School Visits**: Field visits to rural/government schools to conduct awareness sessions, student outreach, and scholarship intake tests (Offline).
2. **Admissions Support**: Document verification, student intake processing, and applicant logistics (Offline/Online).
3. **Background Verification (BGV)**: In-depth telephone and in-person home verification of applicant socioeconomic backgrounds to determine scholarship eligibility (Offline/Online).
4. **Mock Interviews**: Practice interview sessions designed to prepare final-year students for corporate campus placements (Online/Offline).
5. **Admission Panel Interviews**: Structured evaluation panels assessing candidates for scholarship award cohorts (Online/Offline).
6. **Other Volunteering Activities**: General administrative, content creation, translation, mentorship, and ad-hoc community initiatives.

---

## 4. Functional Requirements Decomposition

### 4.1 Volunteer Registration & Onboarding
- **Multi-Stage Onboarding Flow**:
  1. *Stage 1 — Basic Details*: First name, Last name, Email address, Mobile number (E.164 format), Age ($0 < \text{age} \le 120$), Gender (`MALE`, `FEMALE`, `OTHER`, `PREFER_NOT_TO_SAY`). Eligibility age is evaluated against configurable policy `MINIMUM_VOLUNTEER_AGE` [POLICY: PENDING_APPROVAL]. If $\text{age} < 18$, the applicant submits guardian details and consent evidence (`parental_consent_submitted = TRUE`), while verification (`parental_consent_status`) is reserved for administrative documentary verification and audit [POLICY: PENDING_APPROVAL].
  2. *Stage 2 — Category Selection*: Choose Student, Alumni, or Corporate Panelist.
  3. *Stage 3 — Category-Specific Details*: Capture schema-validated category attributes.
  4. *Stage 4 — Privacy & Consent*: Granular affirmative opt-in consent toggles (defaulting to `False` in compliance with statutory affirmative opt-in guidelines unless explicitly altered by Maatram Legal) [POLICY: PENDING_APPROVAL].
  5. *Stage 5 — Credentials*: Password entry adhering to strict complexity rules (minimum 8 characters, uppercase, lowercase, number, symbol), hashed using Argon2id.
  6. *Stage 6 — Review & Submission*: Summary review and final submission.
- **Email Verification**: Following submission, generate a secure, short-lived verification token sent via Resend. The volunteer must verify email ownership.
- **Account State Machine**:
  - `UNVERIFIED`: Email verification pending.
  - `PENDING`: Email verified, awaiting administrative review.
  - `APPROVED`: Admin approved; full volunteer privileges granted.
  - `REJECTED`: Admin rejected; restricted dashboard with rejection notification.
  - `SUSPENDED`: Temporarily deactivated by Admin.

### 4.2 Administrative Application Review
- Admins can list, filter, search, and inspect pending volunteer applications.
- Approval workflow:
  - Transition state to `APPROVED`.
  - Record reviewer ID, review timestamp, and optional approval notes.
  - Enqueue welcome/onboarding confirmation email job via transactional outbox.
- Rejection workflow:
  - Transition state to `REJECTED`.
  - Mandatory rejection reason required for auditability.
  - Enqueue rejection notification email.

### 4.3 Privacy & Consent Governance
- Consent cannot be bundled or assumed. Explicit affirmative opt-in is provided for:
  - `leaderboard_visible`: Displaying volunteer name/stats on public/peer leaderboards.
  - `name_visible`: Showing volunteer name in public event participation lists.
  - `thank_you_emails`: Receiving post-event recognition and appreciation emails.
  - `linkedin_content`: Inclusion in LinkedIn appreciation drafts and social media shoutouts.
  - `contact_available`: Sharing contact info with event leads/coordinators for operational dispatch.
  - `media_usage`: Permission to capture and publish photographs/videos taken during events.
- Audit Trail: All consent state modifications must be persisted in `consent_history` with actor, IP address, timestamp, previous value, and new value.

### 4.4 Event Management Lifecycle
- Event Attributes: Title, Description, Category, Mode (`ONLINE`, `OFFLINE`), Location/Meeting URL, Scheduled Start (UTC), Scheduled End (UTC), Timezone (explicit IANA string, default: `'Asia/Kolkata'`), Volunteer Capacity, Registration Deadline (UTC), Cover Image URL, Admin notes.
- Lifecycle States:
  - `DRAFT`: Initial creation; invisible to volunteers.
  - `PUBLISHED`: Open for discovery and registration (if deadline not passed).
  - `REGISTRATION_CLOSED`: Registrations frozen automatically at deadline or manually by Admin.
  - `ONGOING`: Event is currently in progress.
  - `COMPLETED`: Event concluded, attendance finalized, points credited.
  - `CANCELLED`: Event cancelled; notifications dispatched to registered volunteers.

### 4.5 Registration & Capacity Protection
- Volunteers can register for open, published events prior to the registration deadline.
- Statuses:
  - `SUBSCRIBED`: Registered by volunteer; pending selection.
  - `SELECTED`: Confirmed by Admin to attend.
  - `WAITLISTED`: Capacity full; placed in queue.
  - `NOT_SELECTED`: Admin did not select for this occurrence.
  - `DECLINED`: Selected volunteer declined assignment.
  - `WITHDRAWN`: Volunteer retracted registration prior to withdrawal deadline (`REGISTRATION_WITHDRAWAL_DEADLINE_HOURS_PRIOR` [POLICY: PENDING_APPROVAL]).
- Concurrency & Double-Booking: Use database transactions with pessimistic locking (`SELECT ... FOR UPDATE`) when evaluating capacity to prevent overbooking. Check for overlapping event registrations for the same volunteer.

### 4.6 Attendance Tracking & Correction
- Exact timestamps for check-in and check-out.
- System Invariants:
  - Check-in cannot occur before an event is `ONGOING`.
  - Check-out requires an existing valid check-in.
  - Duration in minutes = `(check_out_time - check_in_time) in minutes`.
  - Zero auto-checkout: Missing check-out remains flagged as `INCOMPLETE` and requires administrative review.
  - Corrections: Administrative overrides must create an audit record in `attendance_corrections` storing old hours, new hours, admin ID, reason, and timestamp. Adjustments exceeding `CORRECTION_SUPER_ADMIN_THRESHOLD_MINUTES` [POLICY: PENDING_APPROVAL; baseline: 120 minutes] require Super Admin approval.

### 4.7 Gamification & Scoring System
- **Formula**:
  $$P = (E \times 10) + (H \times 2)$$
  Where:
  - $P$ = Total Points awarded (numeric decimal, `NUMERIC(8, 2)`).
  - $E$ = Number of qualifying completed events attended ($E \in \{0, 1\}$; requires meeting `EVENT_QUALIFICATION_MIN_MINUTES` [POLICY: PENDING_APPROVAL; baseline: 60 minutes]).
  - $H$ = Approved volunteering hours credited (numeric decimal, `NUMERIC(8, 2)`, calculated from integer attendance duration minutes via `HOURS_ROUNDING_MODE` [POLICY: PENDING_APPROVAL]; computed using Python `Decimal` arithmetic exclusively).
- Points are recorded in a strictly append-only, trigger-protected database ledger (`point_transactions`). The application runtime database role possesses only `SELECT, INSERT` privileges with `UPDATE, DELETE, TRUNCATE, TRIGGER` explicitly revoked, and table ownership retained by the migration administrator.
- Reversals and adjustments are handled exclusively via compensating transactions (`COMPENSATION_REVERSAL`) with negative values, preserving full auditability.
- Points are never credited more than once for the same event registration (`uq_points_volunteer_event`).
- Leaderboards:
  - Global All-Time Leaderboard.
  - Annual/Cycle Leaderboard (`LEADERBOARD_CYCLE_TYPE` [POLICY: PENDING_APPROVAL; baseline: Calendar Year]).
  - Filtered Leaderboards: Student, Alumni, Corporate Panelist.
  - Anonymity respect: If `leaderboard_visible = False`, display as "Anonymous Volunteer".

### 4.8 Atomic Event Completion
- **Completion Preview**: Admin invokes preview endpoint to inspect:
  - Selected vs attended count.
  - Total eligible volunteering hours.
  - Flagged incomplete attendances (missing checkouts).
  - Projected points calculation.
  - Draft thank-you email template and recipient list (filtered by consent).
  - Draft LinkedIn celebration copy.
- **Finalization Transaction**:
  - Transition event to `COMPLETED`.
  - Lock attendance records.
  - Write immutable point transaction ledger entries.
  - Enqueue email and push notification jobs into outbox.
  - Ensure atomicity: if ledger creation fails, entire completion rolls back. Notification failures do not undo completion.

### 4.9 Multi-Channel Notifications & Outbox Recovery
- In-app notification inbox backed by canonical PostgreSQL `notifications` table as the single source of truth.
- Transactional emails via Resend with atomic claim attempt incrementing, worker lease timeouts, crash recovery sweeper, provider idempotency keys (`Idempotency-Key: {job_id}`), and dead-letter queueing.
- Push notifications via Firebase Cloud Messaging (FCM) operating under at-least-once, best-effort semantics, with Flutter client durable SQLite deduplication cache and selective token deactivation (only on confirmed token errors; never on payload formatting errors).
- Delivery tracking with retry counter, status (`PENDING`, `PROCESSING`, `SENT`, `FAILED`, `DEAD_LETTER`), error logging.

### 4.10 Cloudinary Media Integration
- Volunteers upload profile avatars; Admins upload event cover images and post-event photo albums.
- Backend provides signed upload parameters (HMAC-SHA256 signature, timestamp, folder) to clients.
- Clients upload directly to Cloudinary using signed payload; client reports asset details (`public_id`, `secure_url`, metadata) to FastAPI backend for verification and storage.
- Cloudinary master API secret is never shared with mobile or web clients.

### 4.11 Administrative Reporting & Analytics
- Dynamic SQL-driven aggregations:
  - Volunteer distribution by category, gender, and college/employer.
  - Top contributing alumni and corporate panels.
  - Inactive volunteer detection (`INACTIVE_VOLUNTEER_DAYS_THRESHOLD` [POLICY: PENDING_APPROVAL; baseline: 180 days]).
  - Total verified hours contributed across date ranges and event categories.
  - CSV/Excel asynchronous export generation.

---

## 5. Non-Functional Requirements

| Metric / Dimension | Requirement |
| :--- | :--- |
| **Performance** | API response time $P_{95} < 200\text{ ms}$ for standard queries; $P_{99} < 500\text{ ms}$ for complex aggregations. |
| **Scalability** | Support 20,000+ active volunteers, 1,000+ concurrent users, and 500+ events per year with horizontal FastAPI scaling on Render. |
| **Availability** | 99.9% uptime target. |
| **Data Integrity** | ACID compliance via PostgreSQL; engine-protected append-only point transactions; foreign keys with restricted deletes on historical records. |
| **Security** | OWASP API Security Top 10 compliance; Argon2id password hashing; HTTP-only SameSite cookies for web; TLS 1.3 in transit; AES-256 at rest (Supabase). |
| **Maintainability** | Layered modular architecture; strict typing; automated test coverage $> 85\%$; automated Alembic migrations. |
