# Security & Privacy Audit Report
**Maatram Volunteering & Mentorship Portal**  
**Audit Stream 3: Cryptography, Authentication, Authorization, CSRF, Privacy, and Infrastructure Hygiene**  
**Conducted**: November 5, 2026  
**Auditor**: Independent DeepMind Production-Readiness Agent  
**Status**: COMPLETE  

---

## 1. Executive Summary

This independent security and privacy audit evaluates the vulnerability posture, cryptographic rigor, identity and access management (IAM), Cross-Site Request Forgery (CSRF) defenses, Broken Object-Level Authorization (BOLA/IDOR), and privacy consent governance across the **Maatram Volunteering & Mentorship Portal** backend (`server/`).

### Overall Security Posture
- **Strengths**:
  - **Argon2id Password Hashing**: State-of-the-art parameters ($m=64\,\text{MB}, t=3, p=4$) executed in a dedicated bounded thread pool (`max_workers=4`) to eliminate event loop latency.
  - **Replay-Resistant Session Architecture**: Refresh tokens are 256-bit entropy random tokens, stored exclusively as SHA-256 hashes. Refresh token presentation rotates both tokens; presenting a previously rotated token triggers immediate revocation of the entire session lineage with `TOKEN_REUSE_DETECTED` audit logs.
  - **Role-Based & Object-Level Access Control (BOLA)**: Strict RBAC dependency injection guards admin functionality. Volunteer profile and registration endpoints enforce ownership checks (`profile.user_id == current_user.id or role in ("ADMIN", "SUPER_ADMIN")`).
  - **Zero Credential Leaks in Git**: Git log history analysis (`git log --all -- server/.env .env`) confirms 0 commits. Root `.gitignore` correctly ignores all environment files.
  - **Sanitized Error Responses**: Production error handlers intercept unhandled 500 exceptions, logging full tracebacks internally while returning clean JSON error envelopes (`INTERNAL_SERVER_ERROR`) without leaking stack traces.
- **Critical Vulnerabilities & Security Gaps**:
  - **High [P1]**: The `verify_csrf` dependency in `server/src/api/deps.py` only verifies that the `X-CSRF-Token` header is non-empty. It never invokes the cryptographic HMAC verification function `verify_csrf_token()` and does not compare the header to the cookie.
  - **High [P1]**: Mutative endpoints across `consent.py` (`PUT /consent/me`), `volunteers.py` (`PATCH /volunteers/me`), and `applications.py` (`POST /applications/{id}/approve`, `POST /applications/{id}/reject`) lack the `Depends(verify_csrf)` dependency entirely.
  - **Medium [P2]**: An account enumeration timing and status oracle exists on `POST /auth/password-reset/request`, where existing accounts return 429 after 3 attempts while non-existent accounts always return 200.
  - **Medium [P2]**: `server/.env` contains `COOKIE_SECURE=False` and `DEBUG=True`, creating severe security risks if deployed to production without environment overrides.

---

## 2. Authentication & Cryptographic Rigor

### 2.1 Password Hashing (Argon2id)
- **Implementation**: Located in `server/src/core/security.py:33-56`.
- **Configuration**:
  - Algorithm: `argon2.Type.ID` (Argon2id hybrid defense against GPU cracking and side-channel attacks).
  - Memory Cost: $65,536\,\text{KB}$ ($64\,\text{MB}$).
  - Time Cost: $3$ iterations.
  - Parallelism: $4$ lanes/threads.
  - Salt Length: $16\,\text{bytes}$.
  - Hash Length: $32\,\text{bytes}$.
- **Thread Pool Concurrency**: CPU-bound Argon2id hashing is offloaded via `asyncio.get_running_loop().run_in_executor(_crypto_executor, ...)` to a dedicated `ThreadPoolExecutor(max_workers=4, thread_name_prefix="argon2_worker")`. This guarantees the async event loop is never blocked by password hashing.
- **Verification**: Verified passing unit test in `tests/test_auth_security.py:29-45`.

### 2.2 JWT Access Tokens
- **Implementation**: `server/src/core/security.py:80-127`.
- **Algorithm**: `HS256` signed using `settings.SECRET_KEY`.
- **Lifetime**: 15 minutes (`settings.ACCESS_TOKEN_EXPIRE_MINUTES = 15`).
- **Required Claims**: `sub` (User UUID), `role` (`VOLUNTEER`, `ADMIN`, `SUPER_ADMIN`), `status` (`PENDING_APPROVAL`, `APPROVED`, `SUSPENDED`, `REJECTED`), `session_id` (UserSession UUID), `iat`, and `exp`.
- **Validation**: Enforced using strict claim requirements in `jwt.decode(..., options={"require": ["sub", "role", "status", "session_id", "exp", "iat"]})`.

### 2.3 Refresh Token Rotation & Token Theft Detection
- **Implementation**: `server/src/services/auth_service.py:383-515`.
- **Entropy**: Cryptographically secure 256-bit random URL-safe tokens (`rt_` + `secrets.token_urlsafe(32)`).
- **Storage**: Raw refresh tokens are never stored in the database. Only SHA-256 hashes (`hash_token(raw_token)`) are saved in `user_sessions.refresh_token_hash`.
- **Rotation**: On every `POST /api/v1/auth/refresh`, the presented token is invalidated, a new refresh token is issued, and the previous token hash is recorded in an immutable audit log (`action="TOKEN_ROTATED"`).
- **Theft Detection & Family Invalidation**: If an expired or already rotated refresh token is presented again:
  1. `find_session_by_rotated_token_hash()` matches the consumed token hash in the audit logs.
  2. The service detects potential token replay / session hijacking.
  3. It immediately revokes the entire compromised session (`user_repository.revoke_session()`).
  4. It logs a high-severity security audit event: `action="TOKEN_REUSE_DETECTED"`, reason: `"Consumed refresh token presented again; potential token hijacking. Session invalidated."`

---

## 3. Cookie Architecture & Transport Security

Authentication cookies are configured in `server/src/api/deps.py:145-191`:

| Cookie Name | Scope / Path | HttpOnly | Secure Flag | SameSite | Max Age | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `refresh_token` | `/api/v1/auth` | `True` | Per config (`False` in dev) | `Lax` | 30 days | Restricts refresh token transmission exclusively to auth routes |
| `csrf_token` | `/` | `False` | Per config (`False` in dev) | `Lax` | 30 days | Accessible to JavaScript for double-submit header injection |

### Transport Risks
- In `server/.env`, `COOKIE_SECURE=False` is set for local HTTP development.
- In `server/src/core/config.py`, `COOKIE_SECURE` defaults to `False`.
- **Production Vulnerability**: If deployed to staging or production without explicitly overriding `COOKIE_SECURE=True`, browser cookies will be transmitted over unencrypted HTTP connections, exposing session credentials to man-in-the-middle (MitM) eavesdropping.

---

## 4. Cross-Site Request Forgery (CSRF) Analysis

### 4.1 The Intended Architecture
`server/src/core/security.py:139-156` defines an HMAC-SHA256 session-bound CSRF token architecture:
```python
def generate_csrf_token(session_id: uuid.UUID | str) -> str:
    nonce = secrets.token_hex(16)
    message = f"{session_id}:{nonce}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"{nonce}.{signature}"

def verify_csrf_token(csrf_token: str, session_id: uuid.UUID | str) -> bool:
    ...
```

### 4.2 The Flawed Enforcement Implementation
In `server/src/api/deps.py:114-143`, `verify_csrf` is implemented as:
```python
async def verify_csrf(
    request: Request,
    auth_header: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> None:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    if auth_header and auth_header.credentials:
        return

    if refresh_token_cookie:
        origin = request.headers.get("origin")
        if origin and origin not in settings.BACKEND_CORS_ORIGINS:
            raise CSRFValidationException("Origin not permitted.")

        if not x_csrf_token or not x_csrf_token.strip():
            raise CSRFValidationException(
                "X-CSRF-Token header missing on cookie-authenticated request."
            )
```

### Vulnerability Mechanics
1. **No Cryptographic Validation**: `verify_csrf` **never calls** `verify_csrf_token()`. It does not verify the HMAC signature, nor does it compare `x_csrf_token` against the `csrf_token` cookie. An attacker only needs to ensure an `X-CSRF-Token: arbitrary_value` header is sent.
2. **Missing Cookie Comparison**: Double-submit CSRF protection fundamentally relies on checking that the value in the HTTP header matches the value in the cookie (`x_csrf_token == csrf_cookie`). In `verify_csrf`, the `csrf_token` cookie is not even requested as a parameter.
3. **Missing Dependency on Mutative Endpoints**:
   A comprehensive scan reveals that `Depends(verify_csrf)` is completely missing from numerous critical state-modifying endpoints:
   - `PUT /api/v1/consent/me` (`consent.py`): Attackers can tamper with volunteer privacy consent preferences.
   - `PATCH /api/v1/volunteers/me` (`volunteers.py`): Attackers can mutate volunteer profile details.
   - `POST /api/v1/applications/{id}/approve` (`applications.py`): Attackers can trick an authenticated admin into approving volunteer applications.
   - `POST /api/v1/applications/{id}/reject` (`applications.py`): Attackers can force application rejections.
   - `POST /api/v1/events/{id}/media` (`media.py`): Attackers can trigger unauthorized media uploads or file associations.
   - `PATCH /api/v1/notifications/{id}/read` (`notifications.py`): Mark notifications read without user intent.
   - `POST /api/v1/admin/settings` (`admin.py`): Modify system-level settings.

---

## 5. Authorization & Broken Object-Level Authorization (BOLA/IDOR)

### 5.1 Role-Based Access Control (RBAC)
Role hierarchy is enforced via dependency `require_role(*roles)` in `server/src/api/deps.py:80-112`:
- Defined roles: `VOLUNTEER`, `ADMIN`, `SUPER_ADMIN`.
- Account status: The dependency verifies that `current_user.status == "APPROVED"`. Any suspended or pending user receives `HTTP 403 Forbidden` (`ACCOUNT_NOT_ACTIVE`).
- Endpoint protection: All administrative routes under `/api/v1/admin/` and administrative application management endpoints require `ADMIN` or `SUPER_ADMIN`.
- Live probe verification:
  - `GET /api/v1/admin/dashboard` without token: `401 Unauthorized`.
  - Volunteer token accessing `/api/v1/test/admin-only`: `403 Forbidden` (`INSUFFICIENT_PERMISSIONS`).

### 5.2 Object-Level Authorization (IDOR)
Every profile, registration, and attendance query was audited for object ownership validation:
- **Volunteer Profile (`GET /api/v1/volunteers/{profile_id}`)**:
  Protected in `volunteer_service.py:42-45`:
  ```python
  if current_user.role not in ("ADMIN", "SUPER_ADMIN") and profile.user_id != current_user.id:
      raise ForbiddenException("You do not have permission to view this volunteer profile.")
  ```
- **Event Registrations (`GET /api/v1/registrations/{id}`)**:
  Protected in `registration_service.py:699-702`:
  ```python
  is_owner = reg.volunteer_profile and reg.volunteer_profile.user_id == requesting_user.id
  if not (is_admin or is_owner):
      raise ForbiddenException("You do not have permission to view this registration.")
  ```
- **Registration Withdrawal (`DELETE /api/v1/registrations/{id}`)**:
  Protected in `registration_service.py:458-461`: only the owner or an admin can cancel/withdraw a registration.
- **Attendance Corrections (`POST /api/v1/attendance/{id}/corrections`)**:
  Volunteers can only request corrections for their own attendance records. Reviewing corrections is restricted to `ADMIN` or `SUPER_ADMIN`.

---

## 6. Rate Limiting & Denial of Service Protection

The backend provides dual rate limiting engines in `server/src/core/rate_limiter.py`:
1. `PostgreSQLRateLimiter`: Sliding-window counter backed by canonical PostgreSQL table `rate_limit_attempts` using atomic `INSERT ... ON CONFLICT DO UPDATE` queries.
2. `InMemoryRateLimiter`: Fallback dictionary with `asyncio.Lock` for local testing.

### Rate Limiting Coverage Matrix

| Route | Method | Rate Limit Policy | Implementation Status | Risk Assessment |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/auth/register` | `POST` | 5 attempts / 60 min (IP) | Active via `pg_rate_limiter` | Protected |
| `/api/v1/auth/login` | `POST` | 5 attempts / 15 min (IP & Account) | Active via `pg_rate_limiter` | Protected (triggers account lockout) |
| `/api/v1/auth/refresh` | `POST` | None | **Missing** | Moderate risk of token generation flooding |
| `/api/v1/auth/password-reset/request` | `POST` | 3 requests / 24 hr (Per Account) | Active in `auth_service.py` | **Vulnerable to Account Enumeration** |
| `/api/v1/auth/password-reset/confirm` | `POST` | 5 attempts max (Per Token) | Enforced by token attempt count | Missing IP rate limit |
| `/api/v1/auth/verify-email` | `POST` | 5 attempts max (Per Token) | Enforced by token attempt count | Missing IP rate limit |

---

## 7. Secrets Management & Repository Hygiene

### 7.1 Git Commit History Audit
An exhaustive search of git history was conducted:
```powershell
git log --all -- server/.env .env
```
- **Result**: Exactly **0 commits returned**. Neither `.env` nor `server/.env` has ever been checked into git history.
- **Gitignore Inspection**: Root `.gitignore` explicitly includes `.env`, `.env.*`, `server/.env`, and `web/.env*.local`.

### 7.2 Configuration Key Inspection
Inspection of `server/.env` revealed active external service API keys:
- Supabase PostgreSQL connection URI (containing database password)
- Resend API key (`re_hmiPixwL_...`)
- Cloudinary credentials (cloud name, API key, API secret)
- **Directive**: These keys exist solely in the untracked `.env` file for local development. Before public production release, keys must be rotated and injected strictly via server environment variables or a secrets manager (e.g., AWS Secrets Manager or Google Cloud Secret Manager).

---

## 8. Detailed Security & Privacy Findings

### ISSUE-SEC-001 [P1 - High]
- **Route/File**: `server/src/api/deps.py:138-143`
- **Description**: Ineffective CSRF Token Validation in `verify_csrf` Dependency
- **Evidence**:
  Lines 138-143 in `server/src/api/deps.py`:
  ```python
  # 2. Enforce presence and non-emptiness of X-CSRF-Token
  if not x_csrf_token or not x_csrf_token.strip():
      raise CSRFValidationException(
          "X-CSRF-Token header missing on cookie-authenticated request."
      )
  ```
  The dependency verifies only that `x_csrf_token` is a non-empty string. It does not inspect the `csrf_token` cookie, does not compare the two values, and never calls `verify_csrf_token(x_csrf_token, session_id)`.
- **Impact**: Any cross-origin or malicious request that includes an arbitrary header (`X-CSRF-Token: test`) satisfies this check. The portal effectively has zero cryptographic CSRF defense for cookie-authenticated browser sessions.
- **Recommendation**: Update `verify_csrf` to receive both the `x_csrf_token` header and the `csrf_token` cookie, verify equality between the two, and call `verify_csrf_token(x_csrf_token, session.id)` using the authenticated session ID.

---

### ISSUE-SEC-002 [P1 - High]
- **Route/File**: `server/src/api/v1/consent.py:35`, `server/src/api/v1/volunteers.py:38`, `server/src/api/v1/applications.py:97,126`
- **Description**: Missing `verify_csrf` Dependency on Mutative Endpoints
- **Evidence**:
  - `PUT /api/v1/consent/me` (`consent.py:35-46`): Defines no dependencies.
  - `PATCH /api/v1/volunteers/me` (`volunteers.py:38-49`): Defines no dependencies.
  - `POST /api/v1/applications/{id}/approve` (`applications.py:97-104`): Only specifies `Depends(require_role("ADMIN", "SUPER_ADMIN"))`.
  - `POST /api/v1/applications/{id}/reject` (`applications.py:126-133`): Only specifies `Depends(require_role("ADMIN", "SUPER_ADMIN"))`.
- **Impact**: If an authenticated volunteer or admin visits a malicious website, the attacker can silently issue cross-origin requests using browser cookies to modify volunteer privacy settings, alter profiles, or approve/reject volunteer applications.
- **Recommendation**: Add `dependencies=[Depends(verify_csrf)]` to all mutative (`POST`, `PUT`, `PATCH`, `DELETE`) route decorators across the API.

---

### ISSUE-SEC-003 [P2 - Medium]
- **Route/File**: `server/src/services/auth_service.py:661-676`, `server/src/api/v1/auth.py:269-290`
- **Description**: Account Enumeration Oracle on Password Reset Endpoint
- **Evidence**:
  In `auth_service.py:request_password_reset`:
  ```python
  user = await user_repository.get_by_email(db, normalized_email)
  if not user:
      return MessageResponse(message=generic_msg)

  now = datetime.now(UTC)
  recent_count = await token_repository.count_recent_password_reset_requests(
      db, user.id, since=now - timedelta(hours=24)
  )
  if recent_count >= 3:
      raise RateLimitExceededException(
          "Maximum password reset requests exceeded for this email in 24 hours."
      )
  ```
  If an attacker queries `POST /api/v1/auth/password-reset/request` 4 times for an email:
  - If the account does NOT exist, all 4 responses return `200 OK` (`{"message": "If the account exists..."}`).
  - If the account DOES exist, the 4th request returns `429 Too Many Requests` (`"Maximum password reset requests exceeded..."`).
- **Impact**: Attackers can reliably enumerate valid registered volunteer and administrator emails by sending repeated password reset requests.
- **Recommendation**: Apply IP-level rate limiting on `POST /auth/password-reset/request` before querying the database. If an account has exceeded its 3 reset requests, log the event internally and return the identical generic `200 OK` response without throwing a 429 exception.

---

### ISSUE-SEC-004 [P2 - Medium]
- **Route/File**: `server/src/api/v1/auth.py:190-244`
- **Description**: Missing IP-Level Rate Limiting on Refresh Token Endpoint
- **Evidence**:
  While `register` and `login` routes in `auth.py` invoke `pg_rate_limiter.check_and_increment()`, the `POST /api/v1/auth/refresh` route has no rate limit decorator or check.
- **Impact**: An attacker with a compromised refresh token can flood `/refresh` to rapidly rotate tokens or test replay behaviors, consuming database connection pool bandwidth.
- **Recommendation**: Add sliding-window IP rate limiting (e.g. 60 requests / minute) on `POST /auth/refresh`.

---

### ISSUE-SEC-005 [P2 - Medium]
- **Route/File**: `server/.env:2-3,21`, `server/src/core/config.py:48,88`
- **Description**: Insecure Production Defaults (`COOKIE_SECURE=False` and `DEBUG=True`)
- **Evidence**:
  - `server/.env` contains `DEBUG=True` and `COOKIE_SECURE=False`.
  - `server/src/core/config.py` defaults `COOKIE_SECURE: bool = False`.
- **Impact**: In a production environment without strict HTTPS cookie enforcement, authentication cookies can be transmitted in plain text over non-TLS connections, risking session theft.
- **Recommendation**: Set `COOKIE_SECURE=True` and `DEBUG=False` as mandatory defaults when `ENVIRONMENT="production"`. Add a startup assertion in `main.py` that halts server startup if `ENVIRONMENT="production"` and `COOKIE_SECURE=False`.

---

### ISSUE-SEC-006 [P3 - Low]
- **Route/File**: `server/src/core/config.py:24,82-85`
- **Description**: CORS Whitelist Omission of Frontend Port 3001 in Defaults
- **Evidence**:
  `config.py` defines fallback CORS origins as:
  ```python
  ["http://localhost:3000", "http://localhost:8000"]
  ```
  The active Next.js web application is running on port 3001 (`http://localhost:3001`). If `server/.env` is omitted in containerized testing or CI environments, API requests from the frontend are blocked by CORS.
- **Impact**: Frontend development or staging deployments running on port 3001 fail with CORS errors if `.env` is missing.
- **Recommendation**: Include `"http://localhost:3001"` in the fallback default `BACKEND_CORS_ORIGINS` in `config.py`.

---

## 9. Summary Table of Security & Privacy Issues

| Issue ID | Severity | File / Component | Title | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-SEC-001** | P1 (High) | `server/src/api/deps.py:138` | Ineffective CSRF Token Validation in `verify_csrf` Dependency | OPEN |
| **ISSUE-SEC-002** | P1 (High) | `server/src/api/v1/consent.py:35` | Missing `verify_csrf` Dependency on Mutative Endpoints | OPEN |
| **ISSUE-SEC-003** | P2 (Medium) | `server/src/services/auth_service.py:674` | Account Enumeration Oracle on Password Reset Endpoint | OPEN |
| **ISSUE-SEC-004** | P2 (Medium) | `server/src/api/v1/auth.py:190` | Missing Rate Limiting on Refresh Token Endpoint | OPEN |
| **ISSUE-SEC-005** | P2 (Medium) | `server/src/core/config.py:88` | Insecure Production Defaults (`COOKIE_SECURE=False`, `DEBUG=True`) | OPEN |
| **ISSUE-SEC-006** | P3 (Low) | `server/src/core/config.py:82` | CORS Whitelist Omission of Frontend Port 3001 in Defaults | OPEN |
