# PHASE_0_SIGNOFF_CANDIDATE.md — Comprehensive Resolution Matrix & Verification Specifications
**Maatram Volunteering & Gamification Portal**
**Phase 0: Master Engineering Specification — Sign-off Candidate**

---

> [!IMPORTANT]
> **FORMAL GOVERNANCE NOTICE**:
> This document constitutes the **Phase 0 Sign-Off Candidate Package** for the Maatram Volunteering & Gamification Portal backend architecture.
> In accordance with non-negotiable operational directives:
> 1. **Phase 0 is NOT yet marked approved.** Status remains `IN_REVIEW` pending explicit authorization from the User / Maatram Foundation Leadership.
> 2. **Zero backend implementation has been performed.** No application source code has been written, no migrations generated, and no database instances modified.
> 3. **Phase 1 has NOT been initiated.**
> 4. All five technical audit findings identified during independent review have been comprehensively resolved across all canonical architecture specifications and individual phase documents.

---

## 1. Executive Summary & Audit Context

Following the secondary independent review of the Phase 0 documentation package, five specific technical discrepancies were highlighted:
1. **Gamification Point Precision & Duration Units**: Ambiguity between integer duration minutes and credited hours, potential float contamination, repeating hour fractions ($20\text{ min} = 0.333...\text{ hrs}$), and unapproved rounding assumptions.
2. **Transactional Outbox Attempt Lifecycle**: Ambiguity in attempt increment timing, state transitions, lease expiry recovery, and the definition of `max_retries = 3` (4 total attempts).
3. **Mobile Push Notification (FCM) Delivery Semantics**: Absence of explicit at-least-once acknowledgement, lack of canonical database source-of-truth definition, missing mobile client deduplication contract, and unacknowledged isolate crash windows.
4. **Point Ledger Immutability & Database Role Privileges**: Relying solely on triggers without revoking `TRUNCATE` or table modification privileges from the application database user (`maatram_app_user`).
5. **Minor Parental Consent Governance**: Permitting an unverified applicant self-attestation boolean to represent legal consent, rather than separating applicant evidence submission from authorized administrative verification.

All five items have been resolved with mathematical and architectural rigor.

---

## 2. Five-Point Technical Resolution Matrix

| # | Audit Finding | Root Architectural Gap | Canonical Resolution & Enforcement | Canonical Documents Updated | Affected Phase Specifications |
|---|---|---|---|---|---|
| **1** | **Point Precision & Arithmetic** | Ambiguity between raw attendance duration (minutes) and credited hours; potential precision loss or rounding mismatch on repeating fractions ($20\text{ min} = 0.333...\text{ hrs}$); mixing `float` and `Decimal`. | - Raw attendance is stored strictly in integer minutes (`duration_minutes INTEGER`).<br>- Credited hours are stored as `NUMERIC(8, 2)`.<br>- All gamification fields (`event_points`, `hour_points`, `total_points`, `hours_credited`) are defined as `NUMERIC(8, 2)` in PostgreSQL and Python `Decimal` in Pydantic/SQLAlchemy.<br>- Float types are strictly forbidden in point calculations.<br>- Precision limitation of `NUMERIC(8, 2)` on repeating fractions is formally documented.<br>- Credited hour rounding policy is explicitly flagged as `UNAPPROVED` pending Maatram ratification. | `DATABASE_DESIGN.md`<br>`BUSINESS_RULES.md`<br>`API_CONTRACT.md`<br>`OPEN_QUESTIONS.md`<br>`PROJECT_REQUIREMENTS.md` | `PHASE_02_DATABASE.md`<br>`PHASE_09_GAMIFICATION.md` |
| **2** | **Outbox Attempt Lifecycle** | Ambiguous increment timing on job claim; inconsistency between initial failure vs retry failure vs lease timeout; undefined boundary count for `max_retries = 3`. | - Worker atomically increments `attempts = attempts + 1` upon claiming a job for `PROCESSING`.<br>- Initial dispatch failure constitutes attempt 1.<br>- `max_retries = 3` allows up to 3 retries (attempts 2, 3, 4). On the 4th failure, the job transitions to `DEAD_LETTER`. Exactly 4 total dispatch attempts occur.<br>- Crash recovery sweeper resets expired leases (`locked_at < NOW() - 5m`) to `PENDING` if `attempts <= max_retries`, or `DEAD_LETTER` if exhausted.<br>- Provider idempotency key (`Idempotency-Key: {job_id}`) guarantees at-most-once provider dispatch upon worker crash recovery. | `DATABASE_DESIGN.md`<br>`ARCHITECTURE.md`<br>`DECISION_LOG.md (ADR-010)` | `PHASE_11_MEDIA_COMMUNICATIONS.md`<br>`PHASE_12_REPORTS_ADMIN.md` |
| **3** | **FCM Push Delivery Semantics** | Unrealistic assumption of exactly-once push delivery; missing database authority definition; missing mobile deduplication contract. | - FCM push delivery is formally documented as **at-least-once / best-effort**; exactly-once push delivery is explicitly denied.<br>- PostgreSQL `notifications` table is the sole canonical source of truth for all notifications.<br>- Push payloads carry an immutable `notification_id` (UUIDv7/v4).<br>- Flutter client maintains a persistent local SQLite deduplication table (`processed_push_notifications`) with a 7-day sliding TTL.<br>- Crash window between background push receipt and local SQLite commit is explicitly documented; opening a notification triggers idempotent reconciliation with the backend. | `ARCHITECTURE.md`<br>`PROJECT_REQUIREMENTS.md`<br>`DECISION_LOG.md (ADR-013)` | `PHASE_10_NOTIFICATIONS.md` |
| **4** | **Ledger Database Role Privileges** | Application role (`maatram_app_user`) could theoretically execute `TRUNCATE point_transactions` or `ALTER TABLE point_transactions DISABLE TRIGGER` if granted broad table permissions. | - Database user isolation: Table `point_transactions` is owned by `maatram_migration_admin`.<br>- Runtime application role (`maatram_app_user`) is granted strictly `SELECT, INSERT` on `point_transactions`.<br>- Permissions `UPDATE, DELETE, TRUNCATE, TRIGGER` are explicitly `REVOKE`d from `maatram_app_user`.<br>- Engine trigger `trg_prevent_point_ledger_mutation` blocks any mutation even from privileged migration scripts unless intentionally bypassed in controlled rollback migrations. | `DATABASE_DESIGN.md`<br>`PROJECT_REQUIREMENTS.md`<br>`DECISION_LOG.md (ADR-011)` | `PHASE_02_DATABASE.md`<br>`PHASE_09_GAMIFICATION.md`<br>`PHASE_14_PRODUCTION.md` |
| **5** | **Minor Parental Consent Governance** | Relying on a self-attested boolean (`parental_consent_verified`) supplied by the public applicant during onboarding. | - Strict two-step decoupling: Applicant submits evidence (`parental_consent_submitted = TRUE`, guardian name, relationship, contact, consent document media ID).<br>- Verification status is tracked separately via `parental_consent_status` (`NOT_REQUIRED`, `PENDING_VERIFICATION`, `VERIFIED`, `REJECTED`).<br>- Initial status defaults to `PENDING_VERIFICATION` for minors; self-asserted verified status is rejected with `422`.<br>- Only an Admin or Super Admin can transition status to `VERIFIED` via `POST /api/v1/applications/{id}/verify-parental-consent`, generating an immutable audit log entry.<br>- Application approval is blocked if minor status is not `VERIFIED`. | `DATABASE_DESIGN.md`<br>`ARCHITECTURE.md`<br>`BUSINESS_RULES.md`<br>`API_CONTRACT.md`<br>`OPEN_QUESTIONS.md`<br>`DECISION_LOG.md (ADR-014)` | `PHASE_04_VOLUNTEERS.md`<br>`PHASE_05_APPLICATIONS_CONSENT.md` |

---

## 3. Detailed Technical Specifications

### 3.1 Point Precision, Decimal Calculations & Repeating Fractions
1. **Attendance Duration vs. Credited Hours**:
   - `attendance_records.duration_minutes`: Integer representing exact physical elapsed time $(T_{out} - T_{in}) / 60$.
   - `point_transactions.hours_credited`: `NUMERIC(8, 2)` representing approved volunteering hours credited to the volunteer.
2. **Repeating Fraction Reality**:
   - Converting integer minutes to decimal hours can yield repeating fractions ($\frac{20}{60} = 0.3333...\text{ hrs}$, $\frac{40}{60} = 0.6666...\text{ hrs}$).
   - Storing intermediate hours as `NUMERIC(8, 2)` with `ROUND_HALF_UP` yields $0.33\text{ hrs}$ and $0.67\text{ hrs}$.
   - Multiplied by 2:
     - Intermediate rounded: $0.33 \times 2 = 0.66\text{ pts}$; $0.67 \times 2 = 1.34\text{ pts}$.
     - Direct minute arithmetic: $\frac{20 \times 2}{60} = 0.666... \approx 0.67\text{ pts}$; $\frac{40 \times 2}{60} = 1.333... \approx 1.33\text{ pts}$.
   - **Architectural Policy**: In accordance with Question 2 in `OPEN_QUESTIONS.md`, the formal rounding mode remains explicitly **PENDING MAATRAM APPROVAL**. The implementation defaults to calculating intermediate `hours_credited` via Python `Decimal` with `ROUND_HALF_UP` to ensure mathematical consistency between stored `hours_credited` and stored `hour_points` ($H \times 2.00$).
3. **Data Type Uniformity**:
   - PostgreSQL: `NUMERIC(8, 2)` for `hours_credited`, `event_points`, `hour_points`, `total_points`.
   - SQLAlchemy Models: `mapped_column(Numeric(8, 2))` representing Python `decimal.Decimal`.
   - Pydantic Schemas: `condecimal(max_digits=8, decimal_places=2)` or `Decimal`. Floats are strictly prohibited.

### 3.2 Outbox State Machine & Attempt Increment Contract
1. **Atomic Claim**:
   ```sql
   UPDATE communication_jobs
   SET status = 'PROCESSING',
       attempts = attempts + 1,
       locked_at = NOW(),
       worker_id = :worker_id
   WHERE id = (
       SELECT id FROM communication_jobs
       WHERE status = 'PENDING'
         AND scheduled_at <= NOW()
       ORDER BY scheduled_at ASC
       FOR UPDATE SKIP LOCKED
       LIMIT 1
   )
   RETURNING id, channel, recipient, subject, template_id, template_data, attempts, max_retries;
   ```
2. **Transition Rules**:
   - Initial dispatch failure: Job was claimed (`attempts=1`). Upon failure, worker checks if `attempts <= max_retries` ($1 \le 3$). True $\rightarrow$ status set to `PENDING` with exponential backoff (`scheduled_at = NOW() + INTERVAL '60 seconds'`).
   - Retry 1 failure: Job claimed (`attempts=2`). $2 \le 3$ $\rightarrow$ set to `PENDING` with backoff ($120\text{s}$).
   - Retry 2 failure: Job claimed (`attempts=3`). $3 \le 3$ $\rightarrow$ set to `PENDING` with backoff ($240\text{s}$).
   - Retry 3 failure: Job claimed (`attempts=4`). $4 > 3$ $\rightarrow$ set to `DEAD_LETTER`.
   - Total attempts made: Exactly 4 ($1\text{ initial} + 3\text{ retries}$).
3. **Lease Crash Recovery Sweeper**:
   ```sql
   UPDATE communication_jobs
   SET status = CASE WHEN attempts >= max_retries + 1 THEN 'DEAD_LETTER' ELSE 'PENDING' END,
       locked_at = NULL,
       worker_id = NULL,
       scheduled_at = CASE WHEN attempts >= max_retries + 1 THEN scheduled_at ELSE NOW() + INTERVAL '30 seconds' END
   WHERE status = 'PROCESSING'
     AND locked_at < NOW() - INTERVAL '5 minutes';
   ```

### 3.3 FCM At-Least-Once Semantics & Durable Mobile Deduplication
1. **Push Architecture**:
   - FCM is fundamentally a best-effort transport. Network handoffs, provider retries, or app crashes can cause duplicate receipts.
   - The PostgreSQL `notifications` table is canonical.
2. **Client-Side Deduplication Contract**:
   - Every FCM push data payload contains:
     ```json
     {
       "notification_id": "0194db45-728b-7e12-8921-9d22fa01a88b",
       "type": "EVENT_ANNOUNCEMENT",
       "entity_id": "0194db40-c301-7000-8000-000000000001",
       "click_action": "FLUTTER_NOTIFICATION_CLICK"
     }
     ```
   - Flutter client SQLite schema:
     ```sql
     CREATE TABLE IF NOT EXISTS processed_push_notifications (
         notification_id TEXT PRIMARY KEY,
         received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
     );
     CREATE INDEX IF NOT EXISTS idx_processed_push_received_at ON processed_push_notifications(received_at);
     ```
   - On background push receipt:
     1. Query `SELECT 1 FROM processed_push_notifications WHERE notification_id = ?`.
     2. If found $\rightarrow$ drop message silently (suppress UI banner and alert chime).
     3. If not found $\rightarrow$ insert into `processed_push_notifications`, then display OS notification.
     4. Purge records older than 7 days: `DELETE FROM processed_push_notifications WHERE received_at < datetime('now', '-7 days')`.
3. **Crash Window**: If the OS terminates the app isolate after displaying the push banner but before the SQLite write commits, a duplicate banner may render upon OS re-dispatch. However, user interaction triggers `GET /api/v1/notifications`, which pulls idempotent, verified records from PostgreSQL.

### 3.4 Ledger Immutability & Database Role Privilege Separation
1. **Role Architecture**:
   - `maatram_migration_admin`: Database role executing Alembic migrations. Owns all tables, triggers, and sequences.
   - `maatram_app_user`: Database role used by FastAPI web service and outbox worker.
2. **Permission Grants**:
   ```sql
   -- Standard tables
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO maatram_app_user;

   -- Point Ledger Hardening
   REVOKE UPDATE, DELETE, TRUNCATE, TRIGGER ON point_transactions FROM maatram_app_user;
   GRANT SELECT, INSERT ON point_transactions TO maatram_app_user;
   ```
3. **Defense-in-Depth**:
   - If an attacker compromises the application backend or executes arbitrary SQL under `maatram_app_user`:
     - `UPDATE point_transactions ...` $\rightarrow$ Denied by DB role permissions (`ERROR: permission denied for table point_transactions`) AND rejected by trigger `trg_prevent_point_ledger_mutation`.
     - `DELETE FROM point_transactions ...` $\rightarrow$ Denied by DB role permissions AND rejected by trigger.
     - `TRUNCATE point_transactions` $\rightarrow$ Denied by DB role permissions (`ERROR: permission denied for table point_transactions`).
     - `ALTER TABLE point_transactions DISABLE TRIGGER ALL` $\rightarrow$ Denied because `maatram_app_user` is not the table owner (`ERROR: must be owner of table point_transactions`).

### 3.5 Parental Consent Verification & Minor Safeguarding
1. **Applicant Submission (Onboarding)**:
   - Applicant submits profile data with `age < 18`.
   - Mandatory fields: `guardian_name`, `guardian_relationship`, `guardian_contact`, `parental_consent_submitted = TRUE`.
   - Optional evidence upload: `parental_consent_media_id` (UUID of signed physical form uploaded to Cloudinary).
   - Applicant cannot set `parental_consent_status = VERIFIED`. Any payload providing `parental_consent_status` is stripped or rejected with `422`.
   - Initial status set to `PENDING_VERIFICATION` (or `NOT_REQUIRED` if age $\ge 18$).
2. **Administrative Verification Workflow**:
   - Admin/Super Admin inspects application and documentary evidence.
   - Admin calls:
     ```http
     POST /api/v1/applications/{id}/verify-parental-consent
     {
       "status": "VERIFIED",
       "verification_notes": "Signed physical consent letter verified from guardian phone call."
     }
     ```
   - Sets `parental_consent_status = 'VERIFIED'`, `parental_consent_verified_at = NOW()`, `parental_consent_verified_by_id = {admin_id}`.
   - Appends audit entry to `audit_logs`.
3. **Approval Invariant**:
   - `POST /api/v1/applications/{id}/approve` evaluates:
     ```python
     if volunteer.age < 18 and volunteer.parental_consent_status != ParentalConsentStatus.VERIFIED:
         raise DomainException(
             status_code=400,
             code="PARENTAL_CONSENT_NOT_VERIFIED",
             message="Minor application cannot be approved without verified parental consent."
         )
     ```

---

## 4. Verification Test Specifications

The following test suites specify the automated validation checks required during Phase 2 through Phase 14:

```python
# test_gamification_precision.py
from decimal import Decimal
import pytest

def test_point_formula_exact_fractions():
    # 45 minutes = 0.75 hours
    # Formula: P = (1 * 10.00) + (0.75 * 2.00) = 11.50
    E = Decimal("1.00")
    H = Decimal("0.75")
    P = (E * Decimal("10.00")) + (H * Decimal("2.00"))
    assert P == Decimal("11.50")
    assert isinstance(P, Decimal)

def test_point_repeating_fractions_behavior():
    # 20 minutes = 0.333... hours
    # Documented intermediate rounded representation (NUMERIC(8, 2)):
    H_intermediate = (Decimal("20") / Decimal("60")).quantize(Decimal("0.01"))
    assert H_intermediate == Decimal("0.33")
    P_intermediate = (Decimal("1.00") * Decimal("10.00")) + (H_intermediate * Decimal("2.00"))
    assert P_intermediate == Decimal("10.66")

def test_no_float_mixing():
    with pytest.raises(TypeError):
        _ = Decimal("10.00") + 1.50  # Python forbids mixing Decimal and float
```

```python
# test_outbox_lifecycle_boundaries.py
import pytest

@pytest.mark.asyncio
async def test_outbox_four_attempt_boundary(db_session, outbox_worker):
    # 1. Create job with max_retries = 3
    job = await create_outbox_job(status="PENDING", attempts=0, max_retries=3)
    
    # Attempt 1 (Initial Failure)
    job = await outbox_worker.claim_job()
    assert job.attempts == 1
    assert job.status == "PROCESSING"
    await outbox_worker.record_failure(job, error="Provider timeout")
    assert job.status == "PENDING"
    
    # Attempt 2 (Retry 1)
    job = await outbox_worker.claim_job()
    assert job.attempts == 2
    await outbox_worker.record_failure(job, error="Provider timeout")
    assert job.status == "PENDING"
    
    # Attempt 3 (Retry 2)
    job = await outbox_worker.claim_job()
    assert job.attempts == 3
    await outbox_worker.record_failure(job, error="Provider timeout")
    assert job.status == "PENDING"
    
    # Attempt 4 (Retry 3 - Exhaustion)
    job = await outbox_worker.claim_job()
    assert job.attempts == 4
    await outbox_worker.record_failure(job, error="Provider timeout")
    assert job.status == "DEAD_LETTER"
```

```python
# test_ledger_role_isolation.py
import pytest
from sqlalchemy import text

@pytest.mark.asyncio
async def test_app_user_cannot_truncate_ledger(app_user_db_session):
    with pytest.raises(Exception) as exc:
        await app_user_db_session.execute(text("TRUNCATE point_transactions;"))
    assert "permission denied" in str(exc.value).lower()

@pytest.mark.asyncio
async def test_app_user_cannot_disable_trigger(app_user_db_session):
    with pytest.raises(Exception) as exc:
        await app_user_db_session.execute(text("ALTER TABLE point_transactions DISABLE TRIGGER ALL;"))
    assert "must be owner" in str(exc.value).lower()
```

```python
# test_minor_parental_consent_workflow.py
import pytest

@pytest.mark.asyncio
async def test_minor_approval_blocked_without_verified_consent(client, admin_token):
    # 1. Register minor applicant (age 17)
    app_id = await register_minor_applicant(age=17)
    
    # 2. Attempt approval directly -> Must fail with 400
    res = await client.post(f"/api/v1/applications/{app_id}/approve", headers=admin_token)
    assert res.status_code == 400
    assert res.json()["code"] == "PARENTAL_CONSENT_NOT_VERIFIED"
    
    # 3. Verify consent as Admin
    res_verify = await client.post(
        f"/api/v1/applications/{app_id}/verify-parental-consent",
        headers=admin_token,
        json={"status": "VERIFIED", "verification_notes": "Guardian document verified."}
    )
    assert res_verify.status_code == 200
    
    # 4. Now approve application -> Must succeed
    res_approve = await client.post(f"/api/v1/applications/{app_id}/approve", headers=admin_token)
    assert res_approve.status_code == 200
    assert res_approve.json()["status"] == "APPROVED"
```

---

## 5. Canonical Documentation Alignment Audit

The entire documentation repository has been updated and cross-checked:

1. **`AGENTS.md`**: Phase discipline affirmed; zero-backend rule strictly maintained.
2. **`docs/DATABASE_DESIGN.md`**: Section 1.2 (duration vs credited hours, Decimal types, repeating fraction precision), Section 1.3 (runtime role privileges: `REVOKE UPDATE, DELETE, TRUNCATE, TRIGGER`), Section 1.4 (outbox claim attempt increment), Module 2 (parental consent submission vs verification fields), Module 7 (ledger role permissions & trigger), Module 9 (outbox attempt lifecycle).
3. **`docs/ARCHITECTURE.md`**: Section 3 (unified outbox attempt increment, 4 total attempts, crash recovery sweeper, Resend idempotency), Section 4 (at-least-once FCM semantics, PostgreSQL source of truth, Flutter SQLite deduplication cache with 7-day TTL, crash window, selective token invalidation), Section 5 (parental consent document upload).
4. **`docs/BUSINESS_RULES.md`**: Section 2 (raw duration minutes, repeating fraction precision, Decimal arithmetic, unapproved rounding policy), Section 3 (decimal scoring $P=(E\times 10)+(H\times 2)$, compensating transactions), Section 4 (minor parental consent governance, admin verification).
5. **`docs/API_CONTRACT.md`**: Section 1 (Decimal precision), Section 2 (`POST /api/v1/auth/register` with guardian submission fields), Section 4 (added `POST /api/v1/applications/{id}/verify-parental-consent`), Section 9 (Decimal representations for all point DTOs).
6. **`docs/OPEN_QUESTIONS.md`**: Question 2 (credited hour rounding, repeating fractions $20\text{ min} = 0.333...\text{ hrs}$, Decimal precision, pending approval), Question 11 (minor eligibility, separation of applicant submission from admin verification, pending approval).
7. **`docs/DECISION_LOG.md`**: ADR-010 updated (outbox attempt incrementing on claim, 4 total attempts), ADR-011 updated (ledger DB role privilege isolation), ADR-012 updated (FCM error classification), ADR-013 added (FCM at-least-once delivery, PostgreSQL authority, client SQLite deduplication), ADR-014 added (parental consent multi-step governance).
8. **`docs/PROJECT_REQUIREMENTS.md`**: Multi-stage registration aligned with guardian submission; decimal scoring and immutable ledger permissions aligned; at-least-once FCM semantics and client deduplication aligned.
9. **`docs/phases/PHASE_00_SPECIFICATION.md` through `PHASE_14_PRODUCTION.md`**: All 15 phase documents synchronized with precision types, outbox attempt counters, FCM client semantics, ledger role isolation, and browser topology test suites.
10. **`docs/MASTER_PLAN.md` & `docs/PHASE_TRACKER.md`**: Status reflects `IN_REVIEW` candidate status, awaiting formal sign-off.

---

## 6. Phase 0 Definition of Done (DoD) Verification

| DoD Criterion | Status | Verification Evidence |
|---|:---:|---|
| Complete 15-phase specification written | **SATISFIED** | `docs/phases/PHASE_00_SPECIFICATION.md` through `PHASE_14_PRODUCTION.md` fully detailed. |
| 29 database tables fully defined | **SATISFIED** | All tables, foreign keys, cascade rules, indexes, triggers defined in `DATABASE_DESIGN.md`. |
| Complete API inventory with request/response schemas | **SATISFIED** | All 45+ endpoints fully documented in `API_CONTRACT.md`. |
| Unresolved policies explicitly flagged as UNAPPROVED | **SATISFIED** | All 15 questions in `OPEN_QUESTIONS.md` and inline tags marked `PENDING_MAATRAM_APPROVAL`. |
| Zero backend code written | **SATISFIED** | Zero `.py` files in `src/`, zero alembic migrations, zero running containers. |
| All audit findings resolved | **SATISFIED** | 5 audit points addressed in matrix above with full cross-document alignment. |
| Review package ZIP & manifest generated | **SATISFIED** | `docs/MANIFEST.md` and `maatram_phase_0_review_package.zip` regenerated and verified. |

---

## 7. Next Steps & Explicit Sign-off Request

Phase 0 is complete in its entirety and stands as an authoritative engineering blueprint. 
To maintain strict phase discipline:
- **No Phase 1 work will begin.**
- **No backend code will be written.**
- **Phase 0 will remain in `IN_REVIEW` status until you provide explicit authorization to approve Phase 0 and initiate Phase 1.**

