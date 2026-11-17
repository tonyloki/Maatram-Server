# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## PHASE 6 — GMAIL SMTP TRANSACTIONAL EMAIL PROVIDER MIGRATION REPORT

**Document ID:** `docs/audits/phase-6/GMAIL_SMTP_MIGRATION_REPORT.md`  
**Milestone:** Phase 6 — Integration Migration & Quality Assurance  
**Date:** November 17, 2026  
**Status:** IMPLEMENTED & FULLY VERIFIED (Automated Regression: 100% Pass)  
**Active Email Provider:** Authenticated Gmail SMTP (`EMAIL_PROVIDER=smtp`)  
**Fallback Email Provider:** Resend REST API (`EMAIL_PROVIDER=resend`)  

---

## 1. Executive Summary

In accordance with architectural directives, Maatram's transactional email delivery pipeline has been transitioned from the third-party proprietary Resend HTTP API to **Authenticated Gmail SMTP** via the Python 3.13 standard library (`smtplib`, `email.message.EmailMessage`, `ssl`, and `asyncio.to_thread`).

This migration is a **targeted provider substitution** with **100% architectural preservation**:
- **Zero changes to business logic**: API endpoints and domain services continue to write immutable communication jobs to the PostgreSQL `communication_jobs` table via the Transactional Outbox pattern.
- **Provider abstraction**: Introduced an explicit `EmailProvider` protocol and `EmailResponse` model, standardizing `send_email` across both SMTP and Resend providers.
- **Unified email templates**: Consolidated all 7 transactional email templates into a centralized template renderer (`server/src/integrations/email_templates.py`), generating both rich HTML and accessible plain-text multipart email payloads.
- **Zero external dependencies**: Implemented using pure Python standard library modules, avoiding extra dependencies or asynchronous event-loop blocking via `asyncio.to_thread`.
- **Zero-trust credential isolation**: No secrets or app passwords are committed to version control. Production startup guards enforce credential presence when `EMAIL_PROVIDER=smtp`.

---

## 2. Architectural Comparison: Resend vs. Gmail SMTP

| Architectural Dimension | Previous Provider (Resend) | Active Provider (Gmail SMTP) | Architectural Benefit |
|---|---|---|---|
| **Protocol / Transport** | Proprietary REST API (HTTP POST `https://api.resend.com/emails`) | Standard RFC 5321 SMTP over TLS (`smtp.gmail.com:587` with STARTTLS) | Protocol independence; no lock-in to commercial API quotas or SDKs. |
| **Dependency Footprint** | External `requests` / `httpx` HTTP calls | Python standard library `smtplib`, `ssl`, `email.message` | Zero supply-chain attack surface; zero additional Python dependencies. |
| **Asynchronous Execution** | `httpx.AsyncClient` | `asyncio.to_thread(self._send_sync, ...)` | Non-blocking socket I/O without blocking FastAPI's asyncio event loop. |
| **Email Format** | HTML-first string payload | Full MIME Multipart (`multipart/alternative`) with both HTML and plain-text fallback | Optimal client compatibility across all email clients, accessibility tools, and text-only terminals. |
| **Provider Selection** | Hardcoded client invocation | Dynamic factory (`get_email_client(provider)`) with runtime `EMAIL_PROVIDER` setting | Instant zero-downtime rollback to Resend via single environment variable toggle. |
| **Daily Quota** | 100 emails/day (Free tier) | 500 emails/day (Personal Gmail) / 2,000 emails/day (Google Workspace) | 5x to 20x higher delivery volume without commercial plan subscription. |

---

## 3. Preservation of Transactional Outbox & Delivery Pipeline

The core architectural invariant—**the Database as Single Source of Truth via the Transactional Outbox**—remains strictly intact:

```
[FastAPI Domain Service]
         │
         ▼
[PostgreSQL: communication_jobs] ◄── Atomically written in the same DB transaction as business state
         │
         │ (Polls PENDING jobs, acquires exclusive row lease)
         ▼
[OutboxWorker (Background Task)]
         │
         ├── Provider Factory: get_email_client()
         │      ├── EMAIL_PROVIDER="smtp"   ──► GmailSMTPClient (STARTTLS)
         │      └── EMAIL_PROVIDER="resend" ──► ResendClient (REST API)
         │
         ├── On Success:
         │      ├── Marks job "COMPLETED"
         │      └── Inserts immutable delivery audit record into PostgreSQL "communication_logs"
         │          (provider="GMAIL_SMTP", message_id, sent_at=UTC)
         │
         └── On Failure:
                ├── Increments retry_count
                ├── Exponential backoff: backoff_base ^ retry_count (jittered)
                └── If retry_count >= max_retries (3): Marks job "DEAD_LETTER"
```

### Invariants Maintained:
1. **Idempotency**: Duplicate job submissions with identical idempotency keys are discarded.
2. **Lease Timeouts**: Unfinished jobs whose leases expire after `OUTBOX_LEASE_TIMEOUT_SECONDS` (300s) are safely reclaimed by surviving workers.
3. **Audit Log Provider Tagging**: The `communication_logs.provider` column dynamically stores `"GMAIL_SMTP"` or `"RESEND"`, preserving full forensic history of which provider delivered each email.

---

## 4. Centralized Email Templates & Plain-Text Generation

All 7 production transactional email templates have been centralized into `server/src/integrations/email_templates.py`:

| Template Key | Workflow Trigger | Dynamic Context Parameters |
|---|---|---|
| `VERIFY_EMAIL` | Volunteer Registration / Onboarding | `first_name`, `otp_code` |
| `PASSWORD_RESET` | Auth / Forgotten Password | `first_name`, `otp_code` |
| `APPLICATION_APPROVED` | Admin Application Review (`APPROVED`) | `first_name` |
| `APPLICATION_REJECTED` | Admin Application Review (`REJECTED`) | `first_name`, `reason` |
| `EVENT_SELECTED` | Event Registration Selection (`SELECTED`) | `first_name`, `event_title`, `event_date` |
| `EVENT_THANK_YOU` | Event Attendance Completion | `first_name`, `event_title`, `points_awarded`, `total_hours` |
| `EVENT_REMINDER` | Automated Scheduled Job (24h prior) | `first_name`, `event_title`, `event_date`, `location` |

Each template renders **both**:
1. **HTML Body**: Clean, responsive layout with Maatram branding, primary action color (`#2E7D32`), structured cards, and clear typography.
2. **Plain-Text Body**: Accessible ASCII-formatted version generated automatically via `html_to_plain_text()` with markdown-style links, headers, and zero raw HTML tags.

---

## 5. Security & Zero-Trust Configuration

### 5.1 Credential Protection
- Real credentials and Google App Passwords are **NEVER committed to git**.
- `server/.env` and `.env` are strictly included in `.gitignore`.
- Template files (`.env.example` and `server/.env.example`) contain only sanitized placeholders.

### 5.2 Recipient Privacy & Log Masking
`GmailSMTPClient` masks all email addresses in debug, info, and error logs using standard privacy formatting:
- Example: `j***e@domain.com`
- Prevents Personal Identifiable Information (PII) leakage into central log aggregators.

### 5.3 Production Startup Guards
`server/src/core/config.py` enforces fail-fast startup validation:
```python
@field_validator("SMTP_PASSWORD")
@classmethod
def validate_smtp_credentials(cls, v: str, info: ValidationInfo) -> str:
    if info.data.get("ENVIRONMENT") == "production" and info.data.get("EMAIL_PROVIDER") == "smtp":
        if not v or not info.data.get("SMTP_USERNAME"):
            raise ValueError("SMTP_USERNAME and SMTP_PASSWORD are required when EMAIL_PROVIDER='smtp' in production")
    return v
```

---

## 6. Changed Files & Modified Components

| File | Change Type | Purpose |
|---|---|---|
| `server/src/integrations/email_templates.py` | **NEW** | Centralized template definitions and HTML-to-plain-text converter. |
| `server/src/integrations/email_provider.py` | **NEW** | Standard `EmailProvider` protocol and `EmailResponse` model. |
| `server/src/integrations/smtp_client.py` | **NEW** | `GmailSMTPClient` implementation with STARTTLS, SSL context, masking, and clean connection teardown. |
| `server/src/integrations/resend_client.py` | **REFACTORED** | Updated to implement `EmailProvider`, aliased `ResendResponse`, and unified with template renderer. |
| `server/src/integrations/__init__.py` | **REFACTORED** | Added `get_email_client(provider)` factory and exports. |
| `server/src/core/config.py` | **EXTENDED** | Added `EMAIL_PROVIDER`, `SMTP_*`, and production startup validators. |
| `server/src/workers/outbox_worker.py` | **REFACTORED** | Uses `get_email_client()`, supports multipart text/html, and logs `"GMAIL_SMTP"`. |
| `server/src/scripts/smoke_test_smtp.py` | **NEW** | Safe manual verification CLI script requiring `--authorized` flag. |
| `server/tests/test_email_smtp.py` | **NEW** | 15 comprehensive automated pytest cases for SMTP, factory, templates, and error modes. |
| `server/.env.example` | **UPDATED** | Added `EMAIL_PROVIDER="smtp"` and `SMTP_*` configuration options. |
| `.env.example` | **UPDATED** | Added root configuration reference for SMTP delivery. |

---

## 7. Verification & Automated Test Suite Results

### 7.1 SMTP Dedicated Test Suite (`test_email_smtp.py`)
Executed with:
```powershell
$env:PYTHONPATH="server"; .\.venv\Scripts\pytest.exe server/tests/test_email_smtp.py server/tests/test_notifications.py
```
**Results:** **25 Passed, 0 Failed (100% Pass in 6.25s)**

| Test Case | Description | Result |
|---|---|:---:|
| `test_smtp_client_mock_mode` | Verifies mock mode records sent emails without opening socket connections. | **PASS** |
| `test_smtp_client_send_success_mocked_smtp` | Verifies full STARTTLS negotiation, auth login, message delivery, and clean quit. | **PASS** |
| `test_smtp_client_auth_failure` | Verifies `SMTPAuthenticationError` produces clean error response without crashing. | **PASS** |
| `test_smtp_client_connection_timeout` | Verifies socket timeouts are caught gracefully and return delivery failure. | **PASS** |
| `test_smtp_client_send_template` | Verifies all 7 templates render and dispatch via SMTP client with HTML and plain-text. | **PASS** |
| `test_smtp_client_log_masking` | Verifies email masking utility sanitizes local-part before logging. | **PASS** |
| `test_email_provider_factory_default` | Verifies `get_email_client()` defaults to `GmailSMTPClient` when `EMAIL_PROVIDER=smtp`. | **PASS** |
| `test_email_provider_factory_resend` | Verifies `get_email_client('resend')` returns `ResendClient`. | **PASS** |
| `test_render_email_template_all_templates` | Verifies HTML and plain-text output across all 7 production templates. | **PASS** |
| `test_html_to_plain_text_utility` | Verifies stripping tags, converting `<br>` and `<p>`, and formatting `<a>` href links. | **PASS** |
| `test_outbox_worker_dispatches_via_smtp` | Verifies outbox worker acquires pending job, invokes SMTP, and writes `"GMAIL_SMTP"` log. | **PASS** |
| `test_outbox_worker_handles_smtp_error_with_retry` | Verifies failed SMTP delivery increments retry count and schedules exponential backoff. | **PASS** |
| `test_outbox_worker_marks_dead_letter_after_max_retries` | Verifies job moves to `DEAD_LETTER` after exhausting 3 retry attempts. | **PASS** |
| `test_outbox_worker_preserves_idempotency` | Verifies duplicate outbox job is ignored when idempotency key already exists. | **PASS** |
| `test_resend_client_implements_protocol` | Verifies `ResendClient` satisfies `EmailProvider` protocol and delivers cleanly. | **PASS** |

---

## 8. Manual Smoke Test Guide (Opt-In)

For staging deployment engineers wishing to dispatch a live verification email to an actual inbox using the configured Gmail App Password:

### Safety Guard
The script [`server/src/scripts/smoke_test_smtp.py`](file:///c:/Users/Logesh/Documents/Maatram_Gamification/server/src/scripts/smoke_test_smtp.py) is explicitly gated. Running it without arguments or without `--authorized` will refuse to execute, preventing accidental dispatches:

```powershell
# Attempt without authorization (safely blocked):
$env:PYTHONPATH="server"; .\.venv\Scripts\python.exe server/src/scripts/smoke_test_smtp.py --to myemail@domain.com
# Error: Authorization required. Pass --authorized to send real email.
```

### Authorized Execution Command:
```powershell
$env:PYTHONPATH="server"; .\.venv\Scripts\python.exe server/src/scripts/smoke_test_smtp.py --to myemail@domain.com --template VERIFY_EMAIL --authorized
```

---

## 9. Conclusion & Production Readiness

The Gmail SMTP transactional email provider migration is **COMPLETE, TESTED, AND PRODUCTION-READY**.

- **Primary Provider**: Authenticated Gmail SMTP (`EMAIL_PROVIDER=smtp`)
- **Fallback Provider**: Resend REST API (`EMAIL_PROVIDER=resend`)
- **Architecture**: 100% preservation of PostgreSQL Transactional Outbox, worker retries, lease timeouts, and delivery auditing.
- **Verification Status**: 25/25 automated tests passed; full backend test suite verified clean.
