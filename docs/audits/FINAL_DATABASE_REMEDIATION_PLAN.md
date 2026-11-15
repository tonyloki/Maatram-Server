# Final Database Lifecycle Correction & Remediation Plan
**Maatram Volunteering & Gamification Portal**
**Document Date:** November 2026  
**Status:** Audit & Plan Only (Zero Writes Executed)  

---

## 1. Context & Operational Boundaries

Following the completion of the portal product changes, UI redesigns, and full verification suite, this document establishes the formal investigation and safe remediation plan for the two backfilled volunteer application records in the shared Supabase PostgreSQL development database (`aws-0-eu-west-1.pooler.supabase.com:6543`, project ref: `xaktatkymllxgsvbiehq`).

### Strict Directives Followed:
- **Zero Database Writes**: No `INSERT`, `UPDATE`, `DELETE`, or migration operations were executed.
- **Zero Status Alterations**: Account and application statuses remain untouched.
- **Zero Fabrication**: No artificial review or audit entries have been manufactured.
- **Zero Git Push / Deploy**: All artifacts remain strictly local.
- **Full Privacy Protection**: All personal identifiers (names, emails, phones, tokens) are redacted using synthetic identifiers (`Volunteer-Record-A` and `Volunteer-Record-B`).

---

## 2. Issue 1 — Record A: Existing APPROVED Application

### 2.1 Current State
- **Application ID**: `988aafc3-33c4-49d7-8ebb-e8339f8a357d`
- **Volunteer Profile ID**: `5dfd1235-0897-48d2-90f1-50107e1585ce` (Synthetic Label: `Volunteer-Record-A`)
- **Associated User ID**: `9beb841d-d291-418c-b358-531cf3d0b8b7`
- **Application Status**: `APPROVED`
- **User Account Status**: `APPROVED` (`is_active = True`, `role = "VOLUNTEER"`)
- **Profile Creation Timestamp**: `2026-11-03 12:27:18.766714 UTC`
- **Application `submitted_at`**: `2026-11-13 13:13:27.639364 UTC` (+10 days skew)
- **Age & Safeguarding**: Age 21 (Adult 18+). `parental_consent_verified = True`.
- **Statutory Consent**: Consent record version 3 active.
- **Application Reviews**: **0 records** in `application_reviews`.
- **Audit Logs**: **0 records** in `audit_logs`.
- **Outbox Notifications**: **0 records** in `communication_jobs` / `notifications`.

### 2.2 Root Cause Analysis
During early Phase 0–4 development, this volunteer account was created and approved before Phase 5 introduced the canonical `volunteer_applications` and `application_reviews` schema. During the recent audit, an emergency SQL statement directly inserted a row into `volunteer_applications`:
```sql
INSERT INTO volunteer_applications (id, volunteer_profile_id, status, submitted_at, created_at, updated_at)
VALUES ('988aafc3-...', '5dfd1235-...', 'APPROVED', NOW(), NOW(), NOW())
ON CONFLICT (volunteer_profile_id) DO NOTHING;
```
Because this was a raw SQL backfill:
1. It bypassed `ApplicationService.approve_application()`.
2. No `ApplicationReview` row was generated.
3. No `AuditLog` row (`action="APPLICATION_APPROVED"`) was generated.
4. No welcome notification job was enqueued.
5. The `submitted_at` timestamp was populated with `NOW()` (`2026-11-13`) rather than the historical registration date (`2026-11-03`).

### 2.3 Service Architecture Analysis: System-Bootstrap Event
Inspection of `ApplicationService` in `server/src/services/application_service.py`:
- `approve_application()` explicitly requires `reviewer_user: User` and validates that `reviewer_user.role in ("ADMIN", "SUPER_ADMIN")`.
- `ApplicationReview.reviewer_id` is a database `NOT NULL` foreign key pointing to `users.id`.
- The service does **not** currently contain a headless or system-bootstrap review method.
- Creating an `ApplicationReview` attributed to an arbitrary administrator would **falsify** administrative audit history by claiming a specific human reviewed and approved the application when they did not.

### 2.4 Proposed Remediation
Two safe options are available:

#### Option 1 (Recommended — Zero Mutation / Status Quo Preserved)
- **Rationale**: The application runtime and API do not break when an application has 0 reviews (`ApplicationDetailResponse.reviews` defaults cleanly to `[]`). The volunteer is active, verified, can log in, discover events, and view their dashboard.
- **Action**: Leave the database records as-is. Document in project audit logs that `Volunteer-Record-A` is a Phase 0 pre-seed legacy account.

#### Option 2 (Accurately Attributed Historical Remediation)
- **Rationale**: If formal audit completeness is mandated by compliance governance.
- **Action**:
  1. Correct the historical timestamp skew:
     ```sql
     UPDATE volunteer_applications
     SET submitted_at = '2026-11-03 12:27:18.766714+00',
         updated_at = NOW()
     WHERE id = '988aafc3-33c4-49d7-8ebb-e8339f8a357d';
     ```
  2. Insert an audit log entry in `audit_logs` where `actor_user_id = NULL` (which is permitted by schema):
     - `action`: `SYSTEM_BOOTSTRAP_APPROVAL`
     - `resource_type`: `volunteer_application`
     - `resource_id`: `988aafc3-33c4-49d7-8ebb-e8339f8a357d`
     - `reason`: `"Historical backfill for verified pre-seed volunteer created prior to Phase 5 approval workflow"`
  3. Do **not** create a fake `ApplicationReview` pointing to a human admin ID, preserving review truthfulness.

### 2.5 Risks
- *Option 1*: Minimal. Review trail in admin UI displays "No formal reviews recorded".
- *Option 2*: Timestamp mutation must be verified against any reporting jobs querying `submitted_at`.

### 2.6 Required Authorization
- Explicit authorization from the project lead is required before executing Option 2.

### 2.7 Verification Steps After Correction
1. Query `SELECT id, status, submitted_at FROM volunteer_applications WHERE id = '988aafc3-33c4-49d7-8ebb-e8339f8a357d';` and verify `submitted_at == '2026-11-03 12:27:18.766714+00'`.
2. Inspect `GET /api/v1/volunteers/5dfd1235-0897-48d2-90f1-50107e1585ce` and confirm HTTP 200 OK.
3. Access `/admin/volunteers/5dfd1235-0897-48d2-90f1-50107e1585ce` in the browser and confirm read-only rendering.

---

## 3. Issue 2 — Record B: Existing PENDING Application

### 3.1 Current State
- **Application ID**: `1eec99c0-6639-4ac6-bd7a-f1ef01ac1f5c`
- **Volunteer Profile ID**: `464505ee-a5cf-40a1-8259-fd66bcc9c8d2` (Synthetic Label: `Volunteer-Record-B`)
- **Associated User ID**: `6961fc53-683f-4686-9882-8d7d92743c9e`
- **Application Status**: `PENDING`
- **User Account Status**: `PENDING_VERIFICATION` (`is_active = True`, `role = "VOLUNTEER"`)
- **Profile Creation Timestamp**: `2026-11-08 10:40:09.402951 UTC`
- **Application `submitted_at`**: `2026-11-13 13:13:27.639364 UTC` (+5 days skew)
- **Age & Safeguarding**: Age 19 (Adult 18+). `parental_consent_verified = False` (minor rules do not apply).
- **Statutory Consent**: Consent record version 1 active.
- **Email Verification Tokens**: **0 records** in `email_verifications`.

### 3.2 Root Cause Analysis
1. The user was registered on `2026-11-08` during staging. In the canonical flow:
   `Registration` $\to$ `User status: PENDING_VERIFICATION` $\to$ `Email Verification` $\to$ `User status: PENDING_APPROVAL` $\to$ `Admin Review` $\to$ `User status: APPROVED`.
2. The user never completed email verification, leaving `users.status = 'PENDING_VERIFICATION'`.
3. The SQL backfill inserted a `volunteer_applications` row with `status='PENDING'`.
4. This placed the application on the Admin "Pending Approvals" queue (`/admin/volunteers?tab=pending`).
5. **State-Machine Invariant Conflict**: If an administrator clicks "Approve" on this application via `POST /api/v1/applications/{id}/approve`, `ApplicationService.approve_application()` evaluates:
   ```python
   enforce_status_transition(user.status, "APPROVED")
   ```
   Because `user.status` is `PENDING_VERIFICATION`, the transition check raises:
   `DomainException: [INVALID_STATUS_TRANSITION] Cannot transition from PENDING_VERIFICATION to APPROVED directly.`

### 3.3 Email Verification Workflow & Expected Lifecycle
Inspection of `AuthService.verify_email()` in `server/src/services/auth_service.py` (lines 561–653):
1. Accepts `token` (and optional `email`).
2. Looks up `EmailVerification` row by hash; validates `attempt_count < max_attempts`, `is_used == False`, and `expires_at > now`.
3. Sets `verif.is_used = True`.
4. Executes `enforce_status_transition(user.status, "PENDING_APPROVAL")` $\to$ transitions `user.status = "PENDING_APPROVAL"`.
5. Records audit log `EMAIL_VERIFIED`.
6. Once `user.status == "PENDING_APPROVAL"`, the admin approval workflow `POST /api/v1/applications/{id}/approve` succeeds cleanly, creating the review, audit log, outbox job, and transitioning `user.status` to `APPROVED`.

### 3.4 Authoritative Historical Timestamp Correction
- The profile was created on `2026-11-08 10:40:09.402951 UTC`.
- The application `submitted_at` can be corrected authoritatively using:
  ```sql
  UPDATE volunteer_applications
  SET submitted_at = '2026-11-08 10:40:09.402951+00',
      updated_at = NOW()
  WHERE id = '1eec99c0-6639-4ac6-bd7a-f1ef01ac1f5c';
  ```

### 3.5 Proposed Remediation
Two safe paths are available:

#### Path 1 (Canonical Self-Service Verification)
- Generate a fresh `EmailVerification` token and dispatch the verification email to the user's registered mailbox.
- The user clicks the link (`/verify-email?token=...`).
- `user.status` transitions canonically to `PENDING_APPROVAL`.
- Administrator reviews and approves the application normally via `/admin/volunteers` UI.

#### Path 2 (Administrative Alignment for Staging Accounts)
- If the account belongs to internal test/staging data and the mailbox is inactive:
- With explicit written authorization:
  ```sql
  -- Step 1: Advance user to PENDING_APPROVAL
  UPDATE users
  SET status = 'PENDING_APPROVAL',
      updated_at = NOW()
  WHERE id = '6961fc53-683f-4686-9882-8d7d92743c9e'
    AND status = 'PENDING_VERIFICATION';

  -- Step 2: Correct historical submission timestamp
  UPDATE volunteer_applications
  SET submitted_at = '2026-11-08 10:40:09.402951+00',
      updated_at = NOW()
  WHERE id = '1eec99c0-6639-4ac6-bd7a-f1ef01ac1f5c';

  -- Step 3: Record audit log entry
  INSERT INTO audit_logs (id, actor_user_id, action, resource_type, resource_id, reason, created_at)
  VALUES (gen_random_uuid(), NULL, 'ADMIN_STATUS_ALIGNMENT', 'user', '6961fc53-683f-4686-9882-8d7d92743c9e', 'Administrative alignment from PENDING_VERIFICATION to PENDING_APPROVAL for backfilled application', NOW());
  ```
- After Path 2 is executed, the administrator can click "Approve" through the normal UI, and the backend approval logic (safeguarding check, review creation, audit log, outbox job) will execute canonically.

### 3.6 Risks
- *Path 1*: Requires user interaction or accessible mailbox.
- *Path 2*: Advances user status without direct email token proof; must be restricted to verified staging records.

### 3.7 Required Authorization
- Explicit written authorization from the project lead is required before executing either Path 1 or Path 2.

### 3.8 Verification Steps After Correction
1. Query database to confirm `users.status == 'PENDING_APPROVAL'` and `volunteer_applications.submitted_at == '2026-11-08 10:40:09.402951+00'`.
2. Log into the Admin Portal and open `/admin/volunteers?tab=pending`.
3. Locate `Volunteer-Record-B` and click `Approve Volunteer`.
4. Confirm HTTP 200 OK without `INVALID_STATUS_TRANSITION`.
5. Verify an `application_reviews` row is created with reviewer ID and decision notes.
6. Verify an `audit_logs` row is created with `action="APPLICATION_APPROVED"`.

---

## 4. Invariant Verification Checklist

All required system-level invariants were audited across the codebase:

| Invariant | Code Location | Verification Evidence | Status |
| :--- | :--- | :--- | :---: |
| **All 6 Consent Preferences Independently Available** | `server/src/schemas/consent.py`<br>`server/src/services/consent_service.py` | `ConsentUpdate` supports 6 optional fields (`leaderboard_visible`, `name_visible`, `thank_you_emails`, `linkedin_content`, `contact_available`, `media_usage`). Differential `ConsentHistory` recorded per altered dimension. Version counter increments. | **VERIFIED** |
| **Minor Safeguarding Invariant Cannot Be Bypassed** | `server/src/services/application_service.py` (lines 170–175) | `if profile.age < 18 and not profile.parental_consent_verified: raise DomainException(code="MINOR_CONSENT_UNVERIFIED")`. Only `ADMIN` can verify parental consent via `verify_parental_consent()`. | **VERIFIED** |
| **Admin Approval Creates Review, Audit & Outbox Records** | `server/src/services/application_service.py` (lines 185–216) | Atomic transaction creates: (1) `ApplicationReview`, (2) `AuditLog` (`action="APPLICATION_APPROVED"`), and (3) `CommunicationJob` outbox email. | **VERIFIED** |
| **New Registrations Appear in Pending Volunteers Tab** | `server/src/services/auth_service.py`<br>`web/src/app/admin/volunteers/page.tsx` | Registrations create `VolunteerApplication(status="PENDING")`. Admin UI queries `GET /api/v1/applications?status=PENDING`. Verified in browser screenshot `12_admin_volunteers_pending_tab.png`. | **VERIFIED** |
| **Admin Profile Viewing Remains Strictly Read-Only** | `web/src/app/admin/volunteers/[id]/page.tsx` | All form fields rendered with `disabled`, `readOnly`, and `cursor-not-allowed`. Consent toggles are display-only. Edit/upload buttons excluded. Verified in screenshot `15_admin_volunteer_profile_readonly.png`. | **VERIFIED** |

---

## 5. Summary & Next Steps

1. **Investigation Complete**: The exact causes of the missing reviews, missing audit logs, and status transition lock for Records A and B are fully diagnosed and documented.
2. **Zero Writes Executed**: The shared development database was not modified.
3. **Standing by for Authorization**: Upon receiving user authorization, the selected remediation pathway (Option 1 or 2 for Record A; Path 1 or 2 for Record B) can be executed safely with zero service interruption.

