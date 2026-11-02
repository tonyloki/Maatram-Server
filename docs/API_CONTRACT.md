# API_CONTRACT.md — REST API Interface Specification (v1)
**Maatram Volunteering & Gamification Portal**

---

## 1. Global API Conventions

- **Base Path**: `/api/v1`
- **Protocol**: HTTPS / REST
- **Payload Format**: `application/json` (except multipart upload requests)
- **Time Representation**: All timestamps are formatted in ISO-8601 with UTC indicator `Z` (e.g., `2026-11-02T13:00:00Z`).
- **Numeric Precision**: All point and hour metrics are handled internally as Python `Decimal` and serialized with exact 2-decimal precision (e.g., `10.00`, `1.50`, `0.75`). Python `float` is never mixed with `Decimal`.
- **Standard Pagination Query Parameters**:
  - `page`: Integer $\ge 1$ (default: `1`)
  - `limit`: Integer between `1` and `100` (default: `20`)
- **Standard Paginated Response Envelope**:
  ```json
  {
    "items": [...],
    "total": 142,
    "page": 1,
    "limit": 20,
    "total_pages": 8
  }
  ```
- **Standard Error Response Envelope**:
  ```json
  {
    "error_code": "RESOURCE_NOT_FOUND",
    "message": "Event with id 2a87d890-faf2-46b8-8ca4-a43c8d899b2f was not found.",
    "details": {},
    "timestamp": "2026-11-02T13:00:00Z"
  }
  ```
- **Idempotency Header**:
  All mutating state operations (`POST /api/v1/events/{id}/register`, `POST /api/v1/events/{id}/complete`, `POST /api/v1/attendance/{id}/correct`, `POST /api/v1/reports/export`, `POST /api/v1/admin/outbox/{id}/requeue`) accept an optional or mandatory `Idempotency-Key: <UUID>` header to guard against duplicate network retries.

---

## 2. Authentication & Session Endpoints (`/api/v1/auth`)

### `POST /api/v1/auth/register`
- **Purpose**: Initiates volunteer registration with multi-stage profile submission.
- **Auth**: Public
- **Role/Permission**: None
- **Object-Level Authorization**: N/A
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "first_name": "Logesh",
    "last_name": "K",
    "mobile_number": "+919876543210",
    "age": 21,
    "gender": "MALE",
    "category": "STUDENT",
    "parent_guardian_name": null,
    "parent_guardian_relationship": null,
    "parent_guardian_contact": null,
    "parental_consent_submitted": false,
    "parental_consent_document_media_id": null,
    "student_details": {
      "college_name": "Anna University",
      "degree": "B.Tech",
      "department": "IT",
      "batch_year": 2026,
      "current_year": 4,
      "maatram_reg_number": "MAAT-2022-094"
    },
    "consent": {
      "leaderboard_visible": false,
      "name_visible": false,
      "thank_you_emails": false,
      "linkedin_content": false,
      "contact_available": false,
      "media_usage": false
    }
  }
  ```
- **Validation**:
  - Email: Valid format, lowercased, unique.
  - Password: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character.
  - Mobile: E.164 format, unique.
  - Age: $0 < \text{age} \le 120$. Minimum eligibility is evaluated against configurable policy `MINIMUM_VOLUNTEER_AGE` [POLICY: PENDING_APPROVAL].
  - Minor Safeguarding: If $\text{age} < 18$, `parental_consent_submitted` must be `True`, and `parent_guardian_name` and `parent_guardian_contact` are required. (Applicants **cannot** self-verify consent; `parental_consent_status` initializes as `PENDING_VERIFICATION`).
  - Category: One of `STUDENT`, `ALUMNI`, `CORPORATE`. Category details strictly validated against corresponding schema.
- **Expected Response**: `201 Created`
  ```json
  {
    "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "email": "user@example.com",
    "status": "UNVERIFIED",
    "parental_consent_status": "NOT_REQUIRED",
    "message": "Registration submitted. Please verify your email."
  }
  ```
- **Errors**: `400 Bad Request` (Validation error), `409 Conflict` (`EMAIL_ALREADY_EXISTS`, `MOBILE_ALREADY_EXISTS`), `422 Unprocessable Entity`.

---

### `POST /api/v1/auth/login`
- **Purpose**: Authenticates credentials and issues access & refresh tokens.
- **Auth**: Public
- **Role/Permission**: None
- **Object-Level Authorization**: N/A
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "client_type": "WEB",
    "device_info": "Chrome on Windows 11"
  }
  ```
- **Validation**: Email format; `client_type IN ('WEB', 'MOBILE')`.
- **Expected Response**: `200 OK`
  - Sets HttpOnly, Secure cookie `refresh_token` for `WEB` clients.
  - Response Body:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "expires_in": 900,
      "refresh_token": "rt_secure_token_string",
      "csrf_token": "csrf_sec_token",
      "user": {
        "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "email": "user@example.com",
        "role": "VOLUNTEER",
        "status": "APPROVED"
      }
    }
    ```
- **Errors**: `401 Unauthorized` (`INVALID_CREDENTIALS`), `403 Forbidden` (`ACCOUNT_LOCKED`, `ACCOUNT_SUSPENDED`), `429 Too Many Requests`.

---

### `POST /api/v1/auth/refresh`
- **Purpose**: Rotates refresh token and issues a new access token. Detects token reuse.
- **Auth**: Public (Cookie-based or Bearer header)
- **Role/Permission**: None
- **Request Body**: `{"refresh_token": "optional_if_cookie_present"}`
- **Expected Response**: `200 OK` (New access token, rotated refresh token, new CSRF token).
- **Errors**: `401 Unauthorized` (`INVALID_TOKEN`, `TOKEN_REUSE_DETECTED`, `SESSION_REVOKED`).

---

### `POST /api/v1/auth/logout`
- **Purpose**: Revokes current session and clears refresh token cookie.
- **Auth**: Authenticated
- **Role/Permission**: Any active user
- **Object-Level Authorization**: Revokes caller's active session.
- **Expected Response**: `200 OK` (`{"message": "Logged out successfully"}`)

---

### `POST /api/v1/auth/verify-email`
- **Purpose**: Confirms email address using verification token.
- **Auth**: Public
- **Request Body**: `{"token": "verif_token_string"}`
- **Expected Response**: `200 OK` (`{"status": "PENDING", "message": "Email verified successfully."}`)
- **Errors**: `400 Bad Request` (`TOKEN_EXPIRED`, `INVALID_TOKEN`).

---

### `POST /api/v1/auth/password-reset/request`
- **Purpose**: Requests 6-digit numeric OTP sent via transactional email.
- **Auth**: Public
- **Request Body**: `{"email": "user@example.com"}`
- **Expected Response**: `200 OK` (`{"message": "If the account exists, a reset code has been sent."}`)
- **Errors**: `429 Too Many Requests`.

---

### `POST /api/v1/auth/password-reset/confirm`
- **Purpose**: Validates OTP and updates password.
- **Auth**: Public
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "otp": "492810",
    "new_password": "NewSecurePassword123!"
  }
  ```
- **Validation**: OTP 6 digits; new password complexity verified.
- **Expected Response**: `200 OK` (`{"message": "Password reset successfully. Please log in with your new credentials."}`)
- **Errors**: `400 Bad Request` (`INVALID_OTP`, `OTP_EXPIRED`, `MAX_ATTEMPTS_EXCEEDED`).

---

## 3. Users & Volunteer Profiles (`/api/v1/users`, `/api/v1/volunteers`)

### `GET /api/v1/users/me`
- **Purpose**: Returns authenticated user identity, role, and application status.
- **Auth**: Authenticated
- **Role/Permission**: Any authenticated user
- **Object-Level Authorization**: Restricts data to `current_user.id`.
- **Expected Response**: `200 OK`

---

### `GET /api/v1/volunteers/me`
- **Purpose**: Returns complete volunteer profile including category attributes and consent.
- **Auth**: Authenticated
- **Role/Permission**: `VOLUNTEER`
- **Object-Level Authorization**: `volunteer.user_id == current_user.id`.
- **Expected Response**: `200 OK`

---

### `PATCH /api/v1/volunteers/me`
- **Purpose**: Self-service profile updates (bio, phone, category-specific fields).
- **Auth**: Authenticated
- **Role/Permission**: `VOLUNTEER`
- **Object-Level Authorization**: `volunteer.user_id == current_user.id`.
- **Request Body**: Partial update fields. (Cannot update `parental_consent_status`).
- **Expected Response**: `200 OK`
- **Errors**: `400 Bad Request` (Validation error), `403 Forbidden`.

---

### `GET /api/v1/volunteers`
- **Purpose**: Administrative search and directory query.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Query Params**: `page`, `limit`, `category`, `status`, `college`, `organisation`, `search`
- **Expected Response**: `200 OK` (Paginated volunteer summaries).

---

## 4. Applications & Reviews (`/api/v1/applications`)

### `GET /api/v1/applications`
- **Purpose**: List onboarding applications with filtering.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Query Params**: `page`, `limit`, `status`, `category`
- **Expected Response**: `200 OK` (Paginated application items).

---

### `GET /api/v1/applications/{application_id}`
- **Purpose**: Full inspection of an applicant's submitted data, parental consent evidence, and review history.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Expected Response**: `200 OK`

---

### `POST /api/v1/applications/{application_id}/verify-parental-consent`
- **Purpose**: Administrative review and authorized verification of parental consent for minor applicants.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Request Body**:
  ```json
  {
    "status": "VERIFIED",
    "notes": "Parent spoken with over phone; signed consent form verified."
  }
  ```
- **Validation**: `status IN ('VERIFIED', 'REJECTED')`; notes mandatory (min 10 characters).
- **Expected Response**: `200 OK` (`{"parental_consent_status": "VERIFIED"}`)
- **Audit**: Writes to `application_reviews` and `audit_logs`.

---

### `POST /api/v1/applications/{application_id}/approve`
- **Purpose**: Approves volunteer onboarding application.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Validation**: If applicant age < 18, `parental_consent_status` must be `VERIFIED`.
- **Request Body**: `{"notes": "Optional approval comments"}`
- **Expected Response**: `200 OK` (`{"status": "APPROVED", "application_id": "..."}`)
- **Audit**: Writes to `application_reviews` and `audit_logs`. Enqueues welcome email.

---

### `POST /api/v1/applications/{application_id}/reject`
- **Purpose**: Rejects volunteer onboarding application.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Request Body**: `{"reason": "Incomplete college identification documentation"}`
- **Validation**: Reason is mandatory (min 10 characters).
- **Expected Response**: `200 OK` (`{"status": "REJECTED", "application_id": "..."}`)
- **Audit**: Writes to `application_reviews` and `audit_logs`. Enqueues rejection email.

---

## 5. Privacy & Consent (`/api/v1/consent`)

### `GET /api/v1/consent/me`
- **Purpose**: Inspect current affirmative consent settings.
- **Auth**: Authenticated
- **Role/Permission**: `VOLUNTEER`
- **Object-Level Authorization**: `volunteer.user_id == current_user.id`.
- **Expected Response**: `200 OK` (Status across all 6 boolean dimensions).

---

### `PUT /api/v1/consent/me`
- **Purpose**: Update affirmative consent preferences.
- **Auth**: Authenticated
- **Role/Permission**: `VOLUNTEER`
- **Object-Level Authorization**: `volunteer.user_id == current_user.id`.
- **Request Body**:
  ```json
  {
    "leaderboard_visible": true,
    "name_visible": true,
    "thank_you_emails": true,
    "linkedin_content": false,
    "contact_available": true,
    "media_usage": false
  }
  ```
- **Expected Response**: `200 OK`
- **Audit**: Appends differential modifications to `consent_history`.

---

## 6. Event Management (`/api/v1/events`)

### `GET /api/v1/events`
- **Purpose**: List events (public volunteers receive only `PUBLISHED` events; admins receive all statuses).
- **Auth**: Authenticated
- **Query Params**: `page`, `limit`, `status`, `category`, `mode`, `from_date`, `to_date`
- **Expected Response**: `200 OK` (Paginated list of events).

---

### `GET /api/v1/events/{event_id}`
- **Purpose**: Detailed event information.
- **Auth**: Authenticated
- **Object-Level Authorization**: Volunteers cannot view `DRAFT` events.
- **Expected Response**: `200 OK`

---

### `POST /api/v1/events`
- **Purpose**: Create a new volunteering event.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Request Body**:
  ```json
  {
    "title": "Chennai Mega Admissions Interview Panel",
    "description": "Annual intake panel interview for rural scholarship candidates.",
    "category": "PANEL_INTERVIEW",
    "mode": "OFFLINE",
    "location": "Loyola College Campus, Chennai",
    "start_time": "2026-12-10T09:00:00Z",
    "end_time": "2026-12-10T17:00:00Z",
    "timezone": "Asia/Kolkata",
    "capacity_required": 25,
    "registration_deadline": "2026-12-05T23:59:59Z"
  }
  ```
- **Validation**: `end_time > start_time`; `registration_deadline <= start_time`; `capacity_required > 0`.
- **Expected Response**: `201 Created`

---

### `PATCH /api/v1/events/{event_id}`
- **Purpose**: Update event details.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Expected Response**: `200 OK`

---

### `POST /api/v1/events/{event_id}/publish`
- **Purpose**: Publishes draft event to volunteers.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Expected Response**: `200 OK` (`{"status": "PUBLISHED"}`)

---

### `POST /api/v1/events/{event_id}/cancel`
- **Purpose**: Cancels an event and notifies registered volunteers.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Request Body**: `{"reason": "Severe weather alert"}`
- **Expected Response**: `200 OK` (`{"status": "CANCELLED"}`)

---

### `GET /api/v1/events/{event_id}/completion-preview`
- **Purpose**: Preview completion metrics before final execution.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Expected Response**: `200 OK`
  ```json
  {
    "event_id": "...",
    "selected_volunteers_count": 25,
    "attended_volunteers_count": 23,
    "total_hours_credited": "184.00",
    "incomplete_attendances_count": 2,
    "total_points_to_award": "598.00",
    "draft_thank_you_recipients_count": 21,
    "linkedin_copy_draft": "Proud to celebrate 23 dedicated volunteers..."
  }
  ```

---

### `POST /api/v1/events/{event_id}/complete`
- **Purpose**: Atomic finalization of event, locking attendance, awarding points, and queueing communications.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Headers**: `Idempotency-Key: <UUID>` (Mandatory)
- **Request Body**: `{"confirm_completion": true}`
- **Validation**: All attendances must be resolved (no `IN_PROGRESS` or `INCOMPLETE` records).
- **Expected Response**: `200 OK`
  ```json
  {
    "status": "COMPLETED",
    "points_awarded_total": "598.00",
    "volunteers_credited": 23,
    "communication_jobs_queued": 21
  }
  ```
- **Errors**: `400 Bad Request` (`UNRESOLVED_ATTENDANCE_RECORDS`), `409 Conflict` (`EVENT_ALREADY_COMPLETED`).

---

## 7. Event Registrations (`/api/v1/events/{event_id}/registrations`, `/api/v1/registrations`)

### `POST /api/v1/events/{event_id}/register`
- **Purpose**: Volunteer registers for an open event.
- **Auth**: Authenticated
- **Role/Permission**: `VOLUNTEER` (Approved status required)
- **Headers**: `Idempotency-Key: <UUID>` (Optional)
- **Expected Response**: `201 Created` (`{"status": "SUBSCRIBED"}` or `{"status": "WAITLISTED"}`)
- **Errors**: `400 Bad Request` (`DEADLINE_EXPIRED`, `SCHEDULE_CONFLICT`), `409 Conflict` (`ALREADY_REGISTERED`).

---

### `POST /api/v1/events/{event_id}/withdraw`
- **Purpose**: Volunteer withdraws their registration prior to the cutoff deadline.
- **Auth**: Authenticated
- **Role/Permission**: `VOLUNTEER`
- **Object-Level Authorization**: `registration.volunteer_profile_id == current_volunteer.id`.
- **Expected Response**: `200 OK` (`{"status": "WITHDRAWN"}`)
- **Errors**: `400 Bad Request` (`WITHDRAWAL_DEADLINE_PASSED`).

---

### `GET /api/v1/events/{event_id}/registrations`
- **Purpose**: List registrations for an event.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Query Params**: `page`, `limit`, `status`
- **Expected Response**: `200 OK`

---

### `POST /api/v1/events/{event_id}/registrations/{registration_id}/select`
- **Purpose**: Selects a subscribed or waitlisted volunteer.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Expected Response**: `200 OK` (`{"status": "SELECTED"}`)

---

## 8. Attendance Management (`/api/v1/events/{event_id}/attendance`, `/api/v1/attendance`)

### `POST /api/v1/events/{event_id}/attendance/check-in`
- **Purpose**: Log volunteer check-in (individual or bulk).
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Request Body**:
  ```json
  {
    "volunteer_profile_ids": ["uuid-1", "uuid-2"],
    "check_in_time": "2026-12-10T09:05:00Z"
  }
  ```
- **Validation**: Event must be `ONGOING`; volunteer must be in `SELECTED` status; no duplicate check-in.
- **Expected Response**: `200 OK`

---

### `POST /api/v1/events/{event_id}/attendance/check-out`
- **Purpose**: Log volunteer check-out and compute duration in minutes.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Request Body**:
  ```json
  {
    "volunteer_profile_ids": ["uuid-1", "uuid-2"],
    "check_out_time": "2026-12-10T17:10:00Z"
  }
  ```
- **Validation**: Check-out cannot occur without active check-in; $T_{out} \ge T_{in}$.
- **Expected Response**: `200 OK`

---

### `POST /api/v1/attendance/{attendance_id}/correct`
- **Purpose**: Auditable correction of attendance timestamps and hours.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN` (if adjustment $\le 2\text{ hours}$), `SUPER_ADMIN` (if adjustment $> 2\text{ hours}$).
- **Headers**: `Idempotency-Key: <UUID>` (Mandatory)
- **Request Body**:
  ```json
  {
    "new_check_in_time": "2026-12-10T09:00:00Z",
    "new_check_out_time": "2026-12-10T17:00:00Z",
    "reason": "Scanner hardware failure at morning gate"
  }
  ```
- **Validation**: Reason is mandatory (min 15 characters).
- **Expected Response**: `200 OK`
- **Audit**: Persists audit entry in `attendance_corrections`.

---

## 9. Gamification & Leaderboards (`/api/v1/gamification`, `/api/v1/leaderboards`)

### `GET /api/v1/gamification/summary`
- **Purpose**: Volunteer personal summary (total points, verified hours, completed events, earned badges).
- **Auth**: Authenticated
- **Role/Permission**: `VOLUNTEER`
- **Object-Level Authorization**: `volunteer.user_id == current_user.id`.
- **Expected Response**: `200 OK`
  ```json
  {
    "volunteer_id": "...",
    "total_points": "340.50",
    "total_hours": "100.25",
    "completed_events_count": 14,
    "badges_earned_count": 3
  }
  ```

---

### `GET /api/v1/gamification/ledger`
- **Purpose**: Itemized append-only point transaction history with exact decimal precision (`Decimal`).
- **Auth**: Authenticated
- **Role/Permission**: `VOLUNTEER`
- **Object-Level Authorization**: `volunteer.user_id == current_user.id`.
- **Query Params**: `page`, `limit`, `cycle_year`
- **Expected Response**: `200 OK`
  ```json
  {
    "items": [
      {
        "id": "...",
        "event_id": "...",
        "related_transaction_id": null,
        "event_points": "10.00",
        "hour_points": "1.50",
        "total_points": "11.50",
        "hours_credited": "0.75",
        "transaction_type": "EVENT_COMPLETION",
        "created_at": "2026-12-10T18:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 20
  }
  ```

---

### `GET /api/v1/leaderboards`
- **Purpose**: Fetch leaderboard rankings with category and cycle year filters.
- **Auth**: Authenticated
- **Role/Permission**: Any authenticated user
- **Query Params**: `category` (`ALL`, `STUDENT`, `ALUMNI`, `CORPORATE`), `cycle_year`, `page`, `limit`
- **Expected Response**: `200 OK`
  ```json
  {
    "cycle_year": 2026,
    "category": "ALL",
    "items": [
      {
        "rank": 1,
        "volunteer_name": "Arun Kumar",
        "category": "ALUMNI",
        "total_points": "340.50",
        "events_attended": 14,
        "total_hours": "100.25",
        "is_anonymous": false
      },
      {
        "rank": 2,
        "volunteer_name": "Anonymous Volunteer",
        "category": "STUDENT",
        "total_points": "310.00",
        "events_attended": 15,
        "total_hours": "80.00",
        "is_anonymous": true
      }
    ]
  }
  ```

---

## 10. Media Management (`/api/v1/media`)

### `POST /api/v1/media/sign-upload`
- **Purpose**: Generates signed parameters for direct-to-Cloudinary upload.
- **Auth**: Authenticated
- **Role/Permission**: Any approved volunteer or admin
- **Request Body**:
  ```json
  {
    "asset_type": "AVATAR",
    "file_format": "jpg"
  }
  ```
- **Validation**: Format must be `jpg`, `png`, `webp`, or `pdf` (for `PARENTAL_CONSENT`).
- **Expected Response**: `200 OK`
  ```json
  {
    "upload_url": "https://api.cloudinary.com/v1_1/maatram/image/upload",
    "api_key": "123456789",
    "timestamp": 1730550000,
    "signature": "e9b5f...",
    "folder": "avatars/9b1deb4d..."
  }
  ```

---

### `POST /api/v1/media/register`
- **Purpose**: Confirms and records Cloudinary asset metadata.
- **Auth**: Authenticated
- **Role/Permission**: Any authenticated user
- **Object-Level Authorization**: Verifies `uploaded_by_user_id == current_user.id`.
- **Request Body**:
  ```json
  {
    "public_id": "avatars/9b1deb4d.../img_01",
    "secure_url": "https://res.cloudinary.com/.../img_01.jpg",
    "asset_type": "AVATAR",
    "format": "jpg",
    "byte_size": 245012,
    "width": 800,
    "height": 800
  }
  ```
- **Expected Response**: `201 Created`

---

## 11. Reports & Administration (`/api/v1/reports`, `/api/v1/admin`)

### `GET /api/v1/reports/volunteer-stats`
- **Purpose**: Aggregated demographic and category breakdown.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Expected Response**: `200 OK`

---

### `GET /api/v1/reports/contribution-hours`
- **Purpose**: Verified hours grouped by event category and month.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Query Params**: `from_date`, `to_date`, `category`
- **Expected Response**: `200 OK`

---

### `POST /api/v1/reports/export`
- **Purpose**: Asynchronous CSV/Excel report generation.
- **Auth**: Authenticated
- **Role/Permission**: `ADMIN`, `SUPER_ADMIN`
- **Headers**: `Idempotency-Key: <UUID>` (Optional)
- **Request Body**:
  ```json
  {
    "report_type": "ALUMNI_CONTRIBUTIONS",
    "parameters": {"year": 2026}
  }
  ```
- **Expected Response**: `202 Accepted` (`{"export_id": "...", "status": "PENDING"}`)

---

### `GET /api/v1/admin/audit-logs`
- **Purpose**: Inspect security and business audit logs.
- **Auth**: Authenticated
- **Role/Permission**: `SUPER_ADMIN`
- **Query Params**: `page`, `limit`, `resource_type`, `actor_id`, `from_date`
- **Expected Response**: `200 OK`

---

### `GET /api/v1/admin/outbox/dead-letter`
- **Purpose**: Query dead-lettered communication jobs for administrative inspection.
- **Auth**: Authenticated
- **Role/Permission**: `SUPER_ADMIN`
- **Query Params**: `page`, `limit`, `channel`
- **Expected Response**: `200 OK`

---

### `POST /api/v1/admin/outbox/{job_id}/requeue`
- **Purpose**: Manually requeues a dead-lettered communication job after fixing external causes.
- **Auth**: Authenticated
- **Role/Permission**: `SUPER_ADMIN`
- **Headers**: `Idempotency-Key: <UUID>` (Mandatory)
- **Expected Response**: `200 OK` (`{"status": "PENDING", "job_id": "...", "message": "Job successfully requeued"}`)
- **Errors**: `400 Bad Request` (`JOB_NOT_IN_DEAD_LETTER_STATE`), `404 Not Found`.
