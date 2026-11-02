# BUSINESS_RULES.md — Business Workflows, State Machines & Logic
**Maatram Volunteering & Gamification Portal**

---

> [!NOTE]
> **GOVERNANCE DIRECTIVE**:
> All business parameters, thresholds, and default policies marked with `[POLICY: PENDING_APPROVAL]` are **configurable baseline settings** defined in `core/config.py`. They do not represent final, immutable organizational rules until formally ratified by Maatram Foundation.

---

## 1. State Machines

### 1.1 Volunteer Application State Machine

```
      [ Registration Form Submitted ]
                     |
                     v
             +---------------+
             |  UNVERIFIED   |
             +-------+-------+
                     |
                     | Email Verified (Verification Token)
                     v
             +---------------+
             |    PENDING    | <---------------+
             +-------+-------+                 |
                     |                         | Re-apply (if permitted by policy)
         +-----------+-----------+             |
         |                       |             |
         v (Admin Approve)       v (Admin Reject)
 +---------------+       +---------------+     |
 |   APPROVED    |       |   REJECTED    +-----+
 +-------+-------+       +---------------+
         |
         | (Admin Action)
         v
 +---------------+
 |   SUSPENDED   |
 +---------------+
```

#### State Transition Rules:
1. **UNVERIFIED -> PENDING**: Occurs automatically upon successful email ownership confirmation. Pending volunteers may authenticate but are restricted to an onboarding status page.
2. **PENDING -> APPROVED**: Executed by Admin. Requires verification of category details and, for minor applicants, verification of parental consent evidence. Triggers welcome communication.
3. **PENDING -> REJECTED**: Executed by Admin. Requires mandatory rejection reason. Triggers rejection notification.
4. **REJECTED -> PENDING**: Allowed for documentation resubmissions if `APPLICATION_RESUBMISSION_ALLOWED = True` [POLICY: PENDING_APPROVAL].
5. **APPROVED -> SUSPENDED**: Executed by Admin/Super Admin for disciplinary or security reasons. Immediately revokes active sessions.

---

### 1.2 Event Lifecycle State Machine

```
               [ Event Draft Created ]
                          |
                          v
                  +---------------+
                  |     DRAFT     |
                  +-------+-------+
                          |
                          | Admin Action: Publish
                          v
                  +---------------+
                  |   PUBLISHED   | <---------------+
                  +-------+-------+                 |
                          |                         |
       +------------------+------------------+      | Re-open
       |                                     |      |
       v (Deadline Reached or Admin Action)  v      |
+---------------------+              +---------------+
| REGISTRATION_CLOSED |              |   CANCELLED   |
+----------+----------+              +---------------+
           |
           | Scheduled Start Reached / Admin Starts Event
           v
   +---------------+
   |    ONGOING    |
   +-------+-------+
           |
           | Event Concluded & Completion Finalized
           v
   +---------------+
   |   COMPLETED   |
   +---------------+
```

#### State Invariants:
1. An event in `DRAFT` is never visible to non-admin volunteers.
2. Event registrations are strictly prohibited once an event enters `REGISTRATION_CLOSED`, `ONGOING`, `COMPLETED`, or `CANCELLED`.
3. Event transition from `ONGOING` to `COMPLETED` can only occur through the **Atomic Event Completion** process.
4. A `COMPLETED` event is immutable: its attendance records, point allocations, and completion metrics cannot be altered except via audited Super Admin compensating transactions.

---

### 1.3 Event Registration State Machine

```
                 [ Volunteer Registers ]
                            |
           +----------------+----------------+
           | Capacity Open                   | Capacity Full
           v                                 v
   +---------------+                 +---------------+
   |  SUBSCRIBED   |                 |  WAITLISTED   |
   +-------+-------+                 +-------+-------+
           |                                 |
     +-----+-----+                     +-----+-----+
     |           |                     |           |
     | Admin     | Admin               | Promoted  | Admin
     | Selects   | Passes              | (FIFO/Man)| Passes
     v           v                     v           v
+----------+ +--------------+    +----------+ +--------------+
| SELECTED | | NOT_SELECTED |    | SELECTED | | NOT_SELECTED |
+----+-----+ +--------------+    +----+-----+ +--------------+
     |                                |
     +---------------+----------------+
                     |
       +-------------+-------------+
       | Volunteer   | Volunteer   | Event
       | Attends     | Declines    | Withdrawn
       v             v             v
+------------+ +----------+ +-----------+
|  ATTENDED  | | DECLINED | | WITHDRAWN |
+------------+ +----------+ +-----------+
```

#### Selection & Capacity Rules:
1. Volunteers can register only for `PUBLISHED` events where `NOW() < registration_deadline`.
2. A volunteer cannot register for two events whose start and end time windows overlap.
3. Registration withdrawal is permitted up to the `REGISTRATION_WITHDRAWAL_DEADLINE_HOURS_PRIOR` [POLICY: PENDING_APPROVAL; baseline: 24 hours prior to `start_time`].

---

### 1.4 Attendance State Machine

```
              [ Volunteer Selected & Arrives ]
                             |
                             v
                     +---------------+
                     |  IN_PROGRESS  | (Check-in logged)
                     +-------+-------+
                             |
             +---------------+---------------+
             |                               |
             | Valid Check-out Logged        | Event Ends without Check-out
             v                               v
     +---------------+               +---------------+
     |   COMPLETED   |               |  INCOMPLETE   |
     +---------------+               +-------+-------+
                                             |
                                             | Admin Review / Correction
                                             v
                                     +---------------+
                                     |   COMPLETED   | (Corrected)
                                     +---------------+
```

#### Invariants:
- Check-out timestamp $T_{out}$ must satisfy $T_{out} \ge T_{in}$.
- System **never** automatically checks out a volunteer at the scheduled event end time.
- Unresolved `INCOMPLETE` records award zero hours and zero points until corrected by an Admin.

---

## 2. Attendance & Duration Calculation Rules

1. **Raw Duration Calculation (Integer Minutes)**:
   $$\text{Duration (minutes)} = \text{round}\left(\frac{T_{out} - T_{in}}{60}\right)$$
   Recorded strictly as an integer in `attendance_records.duration_minutes`.
2. **Credited Hours Conversion & Repeating Fractions**:
   $$\text{Exact Credited Hours} = \frac{\text{Duration (minutes)}}{60}$$
   - Converting minutes to hours yields repeating fractions (e.g. $20\text{ minutes} = \frac{1}{3} = 0.3333...\text{ hours}$; $40\text{ minutes} = \frac{2}{3} = 0.6666...\text{ hours}$).
   - `point_transactions.hours_credited` is stored as `NUMERIC(8, 2)` in PostgreSQL.
   - **Precision Limitation Note**: If credited hours are rounded to 2 decimal places prior to point computation, $20\text{ minutes} \rightarrow 0.33\text{ hrs} \times 2 = 0.66\text{ points}$, whereas exact rational arithmetic yields $\frac{20}{60} \times 2 = \frac{2}{3} \approx 0.67\text{ points}$.
   - **Policy Status**: The exact rounding timing (whether to round hours before multiplying by 2, or multiply exact minutes and round the final point total) remains **PENDING MAATRAM APPROVAL** (`HOURS_ROUNDING_MODE`).
   - **Coding Requirement**: All computations in `GamificationService` must utilize Python `Decimal` (from `decimal import Decimal, ROUND_HALF_UP`) consistently. **Do not mix Python `float` and `Decimal`**.
3. **Minimum Qualifying Duration for Event Points ($E=1$)** [POLICY: PENDING_APPROVAL]:
   Configurable baseline: A volunteer must contribute at least `EVENT_QUALIFICATION_MIN_MINUTES` (baseline: 60 verified minutes) to qualify for event completion points ($E = 1$). Less than the qualifying duration awards only the proportional hour points ($H \times 2$), with $E = 0$.
4. **Attendance Corrections**:
   Any modification of `check_in_time` or `check_out_time` requires:
   - Authenticated Admin identity.
   - Non-empty explanatory reason.
   - Recording an immutable record in `attendance_corrections`.
   - Adjustments exceeding `CORRECTION_SUPER_ADMIN_THRESHOLD_MINUTES` [POLICY: PENDING_APPROVAL; baseline: 120 minutes] require Super Admin authorization.

---

## 3. Official Gamification & Scoring System

### 3.1 Scoring Formula & Decimal Numeric Precision

$$P = (E \times 10) + (H \times 2)$$

Where:
- $P$ = Total Points awarded (represented strictly as Python `Decimal` and PostgreSQL `NUMERIC(8, 2)`).
- $E$ = Number of qualifying completed events ($E \in \{0, 1\}$; value is `Decimal('10.00')` if qualified, `Decimal('0.00')` otherwise).
- $H$ = Approved volunteering hours credited (represented strictly as Python `Decimal` and PostgreSQL `NUMERIC(8, 2)`).

#### Exact Decimal Calculation Examples:
- **Standard Full Day**: 5 hours attended at a completed qualifying event ($E=1$, $H=\text{Decimal('5.00')}$):
  $$P = (1 \times 10.00) + (5.00 \times 2.00) = 10.00 + 10.00 = 20.00\text{ points}$$
- **Extended Day**: 7.5 hours attended at a completed qualifying event ($E=1$, $H=\text{Decimal('7.50')}$):
  $$P = (1 \times 10.00) + (7.50 \times 2.00) = 10.00 + 15.00 = 25.00\text{ points}$$
- **Partial Attendance (< 60 minutes qualifying baseline)**: 45 minutes attended ($E=0$, $H=\text{Decimal('0.75')}$):
  $$P = (0 \times 10.00) + (0.75 \times 2.00) = 0.00 + 1.50 = 1.50\text{ points}$$
- **Zero Fractional Truncation**: Points are stored and aggregated as exact decimals (`NUMERIC(8, 2)`). The platform does **not** truncate fractional points to integers. Credited-hour rounding rules remain explicitly **pending Maatram approval**.

### 3.2 Database Ledger Immutability & Compensating Transactions
1. **Engine-Level Immutability**:
   The `point_transactions` ledger is protected by a PostgreSQL trigger `trg_prevent_point_ledger_mutation` that intercepts and terminates any `UPDATE` or `DELETE` statement. No record in `point_transactions` can ever be modified or removed.
2. **Compensating Transactions for Reversals & Adjustments**:
   - If an event was completed in error or an attendance record is revised retrospectively, the original point transaction remains permanently intact.
   - A **compensating transaction** is inserted with `transaction_type = 'COMPENSATION_REVERSAL'`, negative point values (e.g., `event_points = Decimal('-10.00')`, `hour_points = Decimal('-1.50')`, `total_points = Decimal('-11.50')`), a pointer to `related_transaction_id`, and an explicit audit explanation.
   - Leaderboard scores and user balances are computed as aggregate sums of all ledger entries (`SUM(total_points)`), ensuring perfect auditability and ledger balance reconciliation.
3. **Idempotency & Duplicate Prevention**:
   - A unique constraint (`uq_points_volunteer_event`) on `(volunteer_profile_id, event_id)` for `transaction_type = 'EVENT_COMPLETION'` prevents duplicate awards for the same event attendance.

### 3.3 Multi-Tier Leaderboards
1. **Scopes**:
   - **Overall Global**: All active approved volunteers.
   - **Student Leaderboard**: Volunteers with `category = 'STUDENT'`.
   - **Alumni Leaderboard**: Volunteers with `category = 'ALUMNI'`.
   - **Corporate Leaderboard**: Volunteers with `category = 'CORPORATE'`.
2. **Cycle Boundaries** [POLICY: PENDING_APPROVAL]:
   - Configurable baseline: Calendar Year (`LEADERBOARD_CYCLE_TYPE = 'CALENDAR_YEAR'`).
   - Leaderboards reset point tallies at the start of each cycle year.
   - Historical points remain preserved in `point_transactions` and are never wiped.
3. **Anonymity Policy**:
   - If a volunteer sets `consent_records.leaderboard_visible = FALSE`, their points are included in rankings, but their display name appears as `"Anonymous Volunteer"` and their profile avatar is hidden.

---

## 4. Minor Safeguarding & Parental Consent Governance

1. **Separation of Submission, Evidence, and Authorized Verification**:
   - Minor status: Evaluated when an applicant's age is under 18 ($0 < \text{age} < 18$). Minimum volunteer eligibility age is governed by configurable policy `MINIMUM_VOLUNTEER_AGE` [POLICY: PENDING_APPROVAL].
   - **No Self-Verification**: The system strictly rejects self-attested verified flags on public registration.
   - **Submission**: Minor applicants must provide guardian information (`parent_guardian_name`, `parent_guardian_relationship`, `parent_guardian_contact`) and affirmative acknowledgment (`parental_consent_submitted = TRUE`).
   - **Evidence**: Applicants may upload signed guardian consent documentation stored as `parental_consent_document_media_id`.
   - **Verification**: The volunteer application enters status `PENDING` with `parental_consent_status = 'PENDING_VERIFICATION'`.
   - **Administrative Audit**: Only an authorized `ADMIN` or `SUPER_ADMIN` can verify the guardian evidence. Verification requires recording `parental_consent_status = 'VERIFIED'`, `parental_consent_verified_by_user_id`, `parental_consent_verified_at = NOW()`, and audit notes.
   - An application for a minor cannot transition to `APPROVED` until `parental_consent_status == 'VERIFIED'`.

---

## 5. Privacy & Consent Governance Rules

1. **Independent Affirmative Opt-In** [POLICY: PENDING_APPROVAL]:
   Each privacy dimension is stored as an independent boolean flag:
   - `leaderboard_visible`
   - `name_visible`
   - `thank_you_emails`
   - `linkedin_content`
   - `contact_available`
   - `media_usage`
   In compliance with statutory requirements, default values are set to `False` (affirmative opt-in) unless explicitly ratified otherwise by Maatram Legal.
2. **No Bundling**: Consenting to email notifications does not authorize publicizing names or photos.
3. **Real-Time Enforcement**:
   - Before queueing any public-facing or third-party communication, the service queries the current value of the relevant consent flag.
   - If a volunteer revokes `media_usage`, their tagged event photos must not be surfaced in public marketing albums.
4. **Audit History**: Every toggle change appends an immutable differential entry into `consent_history`.
