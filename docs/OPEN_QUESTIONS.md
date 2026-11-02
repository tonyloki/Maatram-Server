# OPEN_QUESTIONS.md — Unresolved Business Policies & Governance Questions
**Maatram Volunteering & Gamification Portal**

---

> [!IMPORTANT]
> **GOVERNANCE NOTICE**:
> All policies cataloged in this document are **UNAPPROVED** and pending formal ratification by the **Maatram Foundation Leadership**. 
> In accordance with zero-assumption engineering principles, **no proposed recommendation may silently become an enforced production rule**.
> The backend architecture treats these rules as **configurable policy parameters** in `core/config.py` with zero hardcoding. Where legally or operationally significant decisions are concerned (e.g., minor consent, data retention, affirmative consent defaults, eligibility age), strict unapproved status is maintained until formal legal and board sign-off.

---

### Question 1: Leaderboard Cycle — Calendar Year vs. Financial Year vs. Academic Year
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable setting `LEADERBOARD_CYCLE_TYPE: Literal['CALENDAR_YEAR', 'FINANCIAL_YEAR', 'ACADEMIC_YEAR'] = 'CALENDAR_YEAR'`.
- **Why Decision is Needed**: Leaderboards reset point accumulations at cycle boundaries while preserving historical records. The system requires an exact calendar partition.
- **System Impact**: Affects `point_transactions.cycle_year`, ranking window queries, and annual badge evaluations.
- **Options**:
  - *Option A*: Calendar Year (Jan 1 – Dec 31).
  - *Option B*: Indian Financial Year (Apr 1 – Mar 31).
  - *Option C*: Academic Year (Jul 1 – Jun 30), aligned with student cohorts.
- **Recommendation (Non-binding)**: Option A for operational simplicity across mixed student and corporate cohorts.
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 2: Credited-Hour Rounding & Fractional Point Precision
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Database schema stores exact decimal precision (`NUMERIC(8, 2)`) for `hours_credited`, `event_points`, `hour_points`, and `total_points`. Attendance raw duration is strictly recorded in integer minutes (`duration_minutes INTEGER`). Configurable setting `HOURS_ROUNDING_MODE: Literal['EXACT_DECIMAL_2', 'NEAREST_15_MIN', 'FLOOR_HALF_HOUR'] = 'EXACT_DECIMAL_2'`. Calculations use Python `Decimal` exclusively with no float conversions.
- **Why Decision is Needed**: Exact attendance timestamps ($T_{out} - T_{in}$) yield duration in minutes. The gamification formula $P = (E \times 10) + (H \times 2)$ supports fractional points. However, converting integer minutes to hours introduces repeating fractions (e.g., $20\text{ mins} = 0.333...\text{ hrs}$, $40\text{ mins} = 0.666...\text{ hrs}$). Storing intermediate hours as `NUMERIC(8, 2)` yields $0.33\text{ hrs} \times 2 = 0.66\text{ pts}$ (or $0.67\text{ hrs} \times 2 = 1.34\text{ pts}$), whereas computing directly from minutes ($\frac{20 \times 2}{60} = \frac{40}{60} \approx 0.67\text{ pts}$) creates a 0.01 discrepancy. A formal rounding policy (rounding mode, intermediate vs final rounding, precision boundary) must be ratified by Maatram Foundation.
- **System Impact**: Affects `attendance_records.duration_minutes`, `point_transactions.hours_credited`, and `GamificationService`.
- **Options**:
  - *Option A*: Intermediate hours rounded to 2 decimal places using `ROUND_HALF_UP`, then multiplied by 2 ($0.33 \times 2 = 0.66$).
  - *Option B*: Exact minute arithmetic in Python Decimal $\frac{M \times 2}{60}$ rounded once at the final point value ($20\text{ mins} \rightarrow 0.67\text{ pts}$).
  - *Option C*: Round minutes to nearest 15-minute increment (0.25 hr) prior to point calculation.
  - *Option D*: Truncate (floor) to full or half hours.
- **Recommendation (Non-binding)**: Keep rounding policy pending Maatram approval; default to Python `Decimal` with `ROUND_HALF_UP` on intermediate hours (`NUMERIC(8, 2)`) to ensure consistency between stored `hours_credited` and `hour_points`.
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 3: Partial Attendance & Event Point ($E=1$) Qualification Threshold
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable setting `EVENT_QUALIFICATION_MIN_MINUTES: int = 60`.
- **Why Decision is Needed**: If an event is scheduled for 8 hours and a volunteer attends for only 20 minutes, awarding the full $10.00\text{ event points}$ ($E = 1$) distorts gamification integrity.
- **System Impact**: Affects qualification logic in `GamificationService` during atomic completion.
- **Options**:
  - *Option A*: Fixed minimum duration threshold (e.g., at least 60 verified minutes).
  - *Option B*: Percentage threshold (e.g., at least 50% of scheduled event duration).
  - *Option C*: Binary attendance (any check-in/out awards $E=1$).
  - *Option D*: Discretionary Admin toggle during completion preview.
- **Recommendation (Non-binding)**: Option A with a 60-minute threshold as an adjustable baseline.
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 4: Volunteer Inactivity Threshold & Re-engagement Outreach
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable setting `INACTIVE_VOLUNTEER_DAYS_THRESHOLD: int = 180`.
- **Why Decision is Needed**: Foundation operations need to identify inactive volunteers for re-engagement or roster hygiene.
- **System Impact**: Administrative reporting queries (`GET /api/v1/reports/inactive-volunteers`) and automated outreach filters.
- **Options**:
  - *Option A*: 90 days without event participation.
  - *Option B*: 180 days without verified attendance.
  - *Option C*: 365 days without participation.
- **Recommendation (Non-binding)**: Option B (180 days).
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 5: Registration Withdrawal Deadline & Late Cancellation Policy
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable setting `REGISTRATION_WITHDRAWAL_DEADLINE_HOURS_PRIOR: int = 24`.
- **Why Decision is Needed**: Late withdrawals prevent coordinators from backfilling seats from the waitlist, jeopardizing field operations.
- **System Impact**: Validation in `RegistrationService.withdraw_registration` and waitlist auto-dispatch.
- **Options**:
  - *Option A*: Free self-service withdrawal permitted up to 24 hours prior to `event.start_time`; within 24 hours requires contacting an Admin.
  - *Option B*: Free withdrawal up to the event `registration_deadline`.
  - *Option C*: Unrestricted withdrawal up to the scheduled start time.
- **Recommendation (Non-binding)**: Option A (24-hour cutoff).
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 6: Waitlist Promotion Mechanism (FIFO vs Manual vs Hybrid)
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable setting `WAITLIST_PROMOTION_MODE: Literal['MANUAL', 'FIFO_AUTOMATIC', 'HYBRID'] = 'MANUAL'`.
- **Why Decision is Needed**: When a selected volunteer withdraws or event capacity expands, how are waitlisted volunteers promoted?
- **System Impact**: Affects `RegistrationService`, capacity management transactions, and notification dispatch.
- **Options**:
  - *Option A*: Automatic FIFO (First-In, First-Out) promotion to `SELECTED`.
  - *Option B*: Manual Admin selection based on demographic/category balance.
  - *Option C*: Hybrid (Automatic FIFO if $> 48\text{ hours}$ before event; manual within 48 hours).
- **Recommendation (Non-binding)**: Option B initially, migrating to Option C upon operational stabilization.
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 7: Rejected Application Retention & Resubmission Window
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable setting `APPLICATION_RESUBMISSION_ALLOWED: bool = True`, `RESUBMISSION_COOLDOWN_DAYS: int = 0`.
- **Why Decision is Needed**: When an onboarding application is rejected due to minor documentation issues, can the applicant reapply or edit their submission?
- **System Impact**: State transitions in `volunteer_applications` and unique constraints on email/mobile.
- **Options**:
  - *Option A*: Permanent rejection; cannot reapply with same email/mobile without Super Admin intervention.
  - *Option B*: 30-day cooling-off cooldown period.
  - *Option C*: Immediate resubmission allowed for documentation fixes; permanent rejection reserved for misconduct.
- **Recommendation (Non-binding)**: Option C.
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 8: Achievement Badge Catalog & Milestone Thresholds
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Stored as dynamic records in `achievement_definitions` table with `criteria_threshold NUMERIC(8, 2)`; milestones populated via seed data rather than hardcoded logic.
- **Why Decision is Needed**: Gamification badges must align with Maatram's organizational values and recognition philosophy.
- **System Impact**: Seed migrations and badge evaluation workers.
- **Options**:
  - Standard proposed milestone tiers:
    - *Bronze Volunteer*: 25.00 Hours or 3 Events.
    - *Silver Volunteer*: 50.00 Hours or 7 Events.
    - *Gold Volunteer*: 100.00 Hours or 15 Events.
    - *Maatram Pillar*: 250.00 Hours or 30 Events.
- **Recommendation (Non-binding)**: Seed this 4-tier model with configurable database definitions.
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 9: Admin vs. Super Admin Privilege Separation & Multi-Tier Approvals
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Granular permissions in `admin_permissions` and declarative RBAC checks (`require_permission`).
- **Why Decision is Needed**: Field coordinators require day-to-day event operations tools, but destructive actions (ledger modifications, role assignments, audit log queries, outbox requeues) must be restricted.
- **System Impact**: RBAC middleware and API route dependencies.
- **Options**:
  - *Admin*: Create/edit events, select volunteers, log check-in/out, submit attendance corrections ($\le 2\text{ hrs}$), preview event completion.
  - *Super Admin*: Approve major attendance corrections ($> 2\text{ hrs}$), finalize/re-open events, adjust point ledgers, view audit logs, grant Admin roles, requeue dead-letter outbox jobs.
- **Recommendation (Non-binding)**: Enforce this two-tier separation.
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 10: Default Consent Toggles & Affirmative Opt-In Governance
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: All optional consent columns in `consent_records` (`thank_you_emails`, `leaderboard_visible`, `name_visible`, `linkedin_content`, `contact_available`, `media_usage`) default strictly to `False` in compliance with strict affirmative opt-in principles unless formally ratified otherwise.
- **Why Decision is Needed**: Under the Digital Personal Data Protection (DPDP) Act of India and international privacy standards, pre-ticked consent checkboxes for public recognition or communications violate explicit consent mandates.
- **System Impact**: `consent_records` column defaults, onboarding DTO validation, and email/leaderboard masking services.
- **Options**:
  - *Option A (Strict Privacy-First)*: All consent toggles default to `False`. The user must affirmatively opt into every dimension.
  - *Option B (Operational Convenience)*: Operational communications (`thank_you_emails`, `contact_available`, `leaderboard_visible`) default to `True`; public media usage (`media_usage`, `linkedin_content`) default to `False`.
- **Recommendation (Non-binding)**: Option A is the legally conservative choice. If Option B is preferred for operational efficiency, explicit written approval from Maatram Legal is required.
- **Maatram Approval Required**: **MANDATORY (LEGAL / STATUTORY)**.

---

### Question 11: Volunteer Eligibility Age & Minor Safeguarding
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Database enforces physical sanity only (`age > 0 AND age <= 120`). Minimum eligibility age is **NOT hardcoded in schemas**; it is evaluated against a configurable setting `MINIMUM_VOLUNTEER_AGE: int | None = None`. If an applicant is under 18, statutory minor safeguarding requires affirmative parental/guardian consent with a strict separation between applicant self-attestation and administrative verification. The system stores applicant-provided data (`parental_consent_submitted = TRUE`, `guardian_name`, `guardian_relationship`, `guardian_contact`, `parental_consent_media_id`), while verification status (`parental_consent_status`) is set to `PENDING_VERIFICATION` and can only be set to `VERIFIED` or `REJECTED` by an authorized Admin or Super Admin after reviewing documentary evidence (`POST /api/v1/applications/{id}/verify-parental-consent`).
- **Why Decision is Needed**: First-year college students may be 16 or 17 years old. Storing PII and event photos of minors invokes legal safeguarding requirements under Indian DPDP law. Whether Maatram allows minors to volunteer, whether age 16 or 18 is the minimum, and what specific documentary evidence is required are executive and legal decisions that must be formally signed off.
- **System Impact**: Registration schemas, parental consent verification endpoints, admin review workflows, and Cloudinary media safeguarding.
- **Options**:
  - *Option A*: Strict minimum age of 18; under-18 applicants are rejected automatically.
  - *Option B*: Permit ages 16–17 provided affirmative guardian/parental consent is captured, documentary proof is uploaded, and an Admin verifies and audits the consent prior to application approval.
- **Recommendation (Non-binding)**: Option B with strict two-step verification (applicant submission + admin documentary verification) if under-18 volunteers are essential to Maatram's intake model.
- **Maatram Approval Required**: **MANDATORY (LEGAL / STATUTORY)**.

---

### Question 12: Data Retention, Inactive Accounts & "Right to be Forgotten"
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Soft deactivation (`is_active = FALSE`, `status = 'SUSPENDED'`) and cryptographic anonymization service replacing PII with salted hashes while keeping aggregate hours/attendance intact.
- **Why Decision is Needed**: Hard deletion of volunteer identities would break past event completion audit trails and historical leaderboard tallies.
- **System Impact**: Foreign key actions (`ON DELETE RESTRICT`) and anonymization worker.
- **Options**:
  - *Option A*: Hard deletion of identity, cascading to all event records (destructive to historical records).
  - *Option B*: Cryptographic Anonymization — Personal identifiers (name, email, mobile, bio, photo) are scrubbed and replaced with hashed placeholders (`deleted_volunteer_uuid`), while anonymized attendance records, hours, and point aggregates remain intact for historical accuracy.
- **Recommendation (Non-binding)**: Option B (Cryptographic Anonymization).
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 13: Event Timezone Default & Cross-Region Support
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable default `DEFAULT_EVENT_TIMEZONE: str = 'Asia/Kolkata'`; events store explicit IANA string.
- **Why Decision is Needed**: Admissions and school visits occur in Tamil Nadu (IST), but corporate mock interview panelists may reside in overseas timezones.
- **System Impact**: `events.timezone` column and client calendar scheduling.
- **Options**:
  - *Option A*: Hardcode all event schedules to `Asia/Kolkata` (IST).
  - *Option B*: Store explicit IANA timezone string per event, defaulting to `Asia/Kolkata`.
- **Recommendation (Non-binding)**: Option B.
- **Maatram Approval Required**: Low operational risk; pending confirmation.

---

### Question 14: Event Capacity Overbooking & Reserve Ratio
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable setting `EVENT_OVERBOOKING_PERCENTAGE: float = 0.0`.
- **Why Decision is Needed**: Field events frequently encounter a 10–20% no-show rate.
- **System Impact**: Selection count verification in `RegistrationService.select_volunteers`.
- **Options**:
  - *Option A*: Strict capacity limit (Never select more than `capacity_required`).
  - *Option B*: Configurable overbooking buffer (e.g., select up to 110% of capacity).
  - *Option C*: Strict capacity with an active waitlist pool.
- **Recommendation (Non-binding)**: Option C (Strict selection limit with active waitlist).
- **Maatram Approval Required**: **MANDATORY**.

---

### Question 15: Attendance Correction Approval Thresholds
- **Current Status**: `PENDING_MAATRAM_APPROVAL (UNAPPROVED)`
- **Architectural Provision**: Configurable setting `CORRECTION_SUPER_ADMIN_THRESHOLD_MINUTES: int = 120`.
- **Why Decision is Needed**: Logging errors in the field need adjustments, but large retrospective hour modifications risk point fabrication.
- **System Impact**: Workflow in `AttendanceService.correct_attendance`.
- **Options**:
  - *Option A*: Single-Admin approval for all corrections with mandatory reason.
  - *Option B*: Adjustments $\le 2\text{ hours}$ require single Admin; adjustments $> 2\text{ hours}$ require Super Admin co-approval.
- **Recommendation (Non-binding)**: Option B.
- **Maatram Approval Required**: **MANDATORY**.
