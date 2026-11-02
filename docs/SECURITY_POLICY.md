# SECURITY_POLICY.md — Authentication, Authorization & Security Architecture
**Maatram Volunteering & Gamification Portal**

---

## 1. Authentication Architecture

The Maatram platform uses a **FastAPI-Managed Dual-Token Authentication Scheme** with server-side session tracking, cryptographic token rotation, and distinct credential transport models for Web and Mobile clients.

```
+------------------------------------+        +-----------------------------------+
|      Next.js Web Client            |        |       Flutter Mobile App          |
| (portal.maatram.org / localhost)   |        |  (iOS Keychain / Android Keystore)|
+-----------------+------------------+        +-----------------+-----------------+
                  |                                             |
                  | Short-Lived Access Token (In-Memory JS)     | Access Token (In-Memory / Storage)
                  | HttpOnly Refresh Cookie + Anti-CSRF Header  | Refresh Token (Hardware Keystore)
                  | (SameSite=Lax / None - See Section 1.4)     | (Authorization: Bearer <token>)
                  +----------------------+----------------------+
                                         |
                                         v
                          +-----------------------------+
                          |      FastAPI Backend        |
                          | (api.maatram.org / Render)  |
                          |   JWT Validation & Sessions |
                          +--------------+--------------+
                                         |
                                         v
                          +-----------------------------+
                          |   PostgreSQL user_sessions  |
                          | (Hashed Token & State)      |
                          +-----------------------------+
```

### 1.1 Password Hashing Specification
- **Algorithm**: `Argon2id` (RFC 9106)
- **Parameters**:
  - Memory Cost: $64\text{ MB}$ (`m=65536`)
  - Time Cost: $3$ iterations (`t=3`)
  - Parallelism: $4$ lanes (`p=4`)
  - Salt Length: $16$ bytes (cryptographically secure random via `os.urandom`)
  - Hash Length: $32$ bytes
- **Rationale**: State-of-the-art resistance to GPU/ASIC parallel cracking and side-channel timing attacks.

### 1.2 Access & Refresh Token Lifecycles

#### Access Tokens:
- **Format**: Cryptographically signed JSON Web Token (JWT) using `HS256` (or `RS256` asymmetric keys in production).
- **Lifespan**: $15\text{ minutes}$ ($900\text{ seconds}$).
- **Claims**:
  - `sub`: User UUID (`users.id`).
  - `role`: Role string (`VOLUNTEER`, `ADMIN`, `SUPER_ADMIN`).
  - `status`: User status (`UNVERIFIED`, `PENDING`, `APPROVED`, etc.).
  - `session_id`: UUID of the parent `user_sessions` record.
  - `jti`: Unique token identifier (UUIDv4) for blacklisting/tracing.
  - `exp`: UTC expiration timestamp ($T + 15\text{m}$).
  - `iat`: UTC issuance timestamp.

#### Refresh Tokens & Rotation:
- **Format**: High-entropy 256-bit cryptographically secure random string (`secrets.token_urlsafe(32)`).
- **Storage**: The plain-text refresh token is **never** persisted in the database. Only its `SHA-256` hash is stored in `user_sessions.refresh_token_hash`.
- **Lifespan**: $30\text{ days}$ ($2,592,000\text{ seconds}$).
- **Automatic Rotation**: Every invocation of `/api/v1/auth/refresh` immediately marks the presented refresh token as consumed and issues a newly generated access and refresh token pair.

#### Refresh Token Reuse Detection & Session Invalidation:
- When a refresh token is rotated, its SHA-256 hash in `user_sessions` is replaced with the new token's hash.
- If a client presents a refresh token that has already been consumed or does not match the active session record, the backend flags **potential token theft/hijacking**:
  1. The server immediately **revokes the entire session lineage** (`is_revoked = TRUE`).
  2. All access tokens bearing that `session_id` are rejected upon subsequent database validation.
  3. A high-priority security alert is logged in `audit_logs`.
  4. The client receives `401 Unauthorized` with error code `TOKEN_REUSE_DETECTED`.

#### Session Revocation:
- Explicit logout (`POST /api/v1/auth/logout`) sets `user_sessions.is_revoked = TRUE` and clears client cookies.
- Password change or reset automatically marks all existing active sessions for that `user_id` as revoked.
- Administrative suspension of a volunteer immediately revokes all active sessions.

---

### 1.3 Client Credential Transport Models

#### 1. Web Clients (Next.js):
- **Access Token**: Stored strictly in volatile browser JavaScript memory (React state / closure). Never written to `localStorage` or `sessionStorage` (preventing extraction via XSS).
- **Refresh Token**: Transmitted via an `HttpOnly`, `Secure` cookie. Inaccessible to client JavaScript.
- **CSRF Token**: Transmitted via a separate readable cookie or response header, echoed in the `X-CSRF-Token` request header.

#### 2. Mobile Clients (Flutter):
- **Access & Refresh Tokens**: Transmitted via standard JSON responses on `/login` and `/refresh`.
- **Client Storage**: Persisted using hardware-backed secure storage:
  - **iOS**: Apple Keychain Services via `flutter_secure_storage` with `kSecAttrAccessibleAfterFirstUnlock`.
  - **Android**: Android Keystore Provider via `flutter_secure_storage` utilizing hardware-backed AES-256-GCM encryption.
- **Request Transport**: Sent via HTTP header `Authorization: Bearer <access_token>`.

---

### 1.4 Browser Cookie Policy, Same-Site vs Cross-Origin & Topology Analysis

#### Conceptual Distinction: Cross-Origin vs. Cross-Site
1. **Origin**: Defined by `Scheme + Hostname + Port` (e.g., `https://portal.maatram.org:443` vs `https://api.maatram.org:443`). Because the hostnames differ, requests between them are **cross-origin** and require CORS negotiation (`Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials: true`).
2. **Site**: Defined by `Scheme + eTLD+1` (effective Top-Level Domain plus one level, per the Mozilla Public Suffix List). Both `portal.maatram.org` and `api.maatram.org` share the apex registrable domain `maatram.org` and scheme `https`. Therefore, requests between them are **same-site**!
3. **SameSite Cookie Behavior in Same-Site Cross-Origin Contexts**:
   - The browser's `SameSite` enforcement inspects **site boundaries (eTLD+1)**, not origin boundaries.
   - For an asynchronous fetch request with `credentials: 'include'` from `https://portal.maatram.org` to `https://api.maatram.org`, the request is **same-site cross-origin**.
   - Under this same-site condition, browsers **do** attach `SameSite=Strict` cookies.
4. **Why `SameSite=Lax` is Selected for Production over `SameSite=Strict`**:
   - `SameSite=Strict` prevents cookies from being sent on **any** top-level navigation originating from an external site. If a volunteer clicks an email verification link, password reset link, or email notification in Gmail/Outlook leading to `portal.maatram.org`, `SameSite=Strict` completely strips the authentication cookie on that landing request. The volunteer would appear logged out upon arrival.
   - `SameSite=Lax` permits cookies on safe top-level navigations (`GET` links from external sources) while strictly withholding cookies on cross-site sub-requests (`POST`, `PUT`, `DELETE`, `<iframe>`, `<img>`).
   - Combined with scoped cookie domains (`Domain=.maatram.org; Path=/api/v1/auth`), `SameSite=Lax` provides the optimal balance of usability, cross-subdomain support, and CSRF protection.

| Deployment Topology | Web Host / API Host | Cookie Attributes | Technical Explanation & Trade-offs |
| :--- | :--- | :--- | :--- |
| **Production Target (Custom Apex Domain)** | Web: `https://portal.maatram.org`<br>API: `https://api.maatram.org` | `Domain=.maatram.org; Path=/api/v1/auth; HttpOnly; Secure; SameSite=Lax` | **Same-site, cross-origin**.<br>Cookie is shared across all `.maatram.org` subdomains. `SameSite=Lax` permits top-level external email links while blocking cross-site CSRF on mutative sub-requests. |
| **Development / Multi-SaaS Staging** | Web: `https://maatram-web.vercel.app`<br>API: `https://maatram-api.onrender.com` | `Path=/api/v1/auth; HttpOnly; Secure; SameSite=None` (`Domain` unset) | **Cross-site, cross-origin**.<br>`vercel.app` and `onrender.com` are separate public suffixes. Browsers treat this as cross-site and block both `Lax` and `Strict` cookies. `SameSite=None; Secure` is mandatory and must be paired with strict Origin checks and anti-CSRF headers. |
| **Local Development** | Web: `http://localhost:3000`<br>API: `http://localhost:8000` | `Path=/api/v1/auth; HttpOnly; SameSite=Lax` (`Secure=False` over HTTP) | Works natively across localhost port boundaries under standard browser rules without HTTPS requirement. |

#### Environment-Specific Configuration Variables:
```python
COOKIE_SAMESITE: Literal['lax', 'none', 'strict'] = 'lax'  # 'none' for staging; 'lax' for prod
COOKIE_SECURE: bool = True                                    # False only for local http://localhost
COOKIE_DOMAIN: str | None = '.maatram.org'                    # None for multi-SaaS staging
COOKIE_PATH: str = '/api/v1/auth'
```

---

### 1.5 CSRF Protection for Cookie-Authenticated Requests

To protect cookie-authenticated web sessions against Cross-Site Request Forgery (CSRF):

1. **Origin & Referer Header Verification**:
   - FastAPI middleware validates the HTTP `Origin` (or `Referer`) header on all state-modifying requests (`POST`, `PUT`, `PATCH`, `DELETE`).
   - If the `Origin` header does not match an allowed domain in `ALLOWED_CORS_ORIGINS`, the request is rejected immediately with `403 Forbidden`.
2. **Double-Submit Anti-CSRF Token Requirement**:
   - Upon authentication, the backend generates a cryptographically random, signed CSRF token.
   - For all cookie-authenticated state modifications on `/api/v1/*`, the client must send the CSRF token in the `X-CSRF-Token` request header.
   - Mobile clients using `Authorization: Bearer <token>` are exempt from CSRF checks because browsers do not automatically attach Bearer headers.
3. **Custom Header Guard**:
   - Browsers prevent cross-site execution of custom HTTP headers without CORS preflight approval (`OPTIONS`). Requiring `X-Requested-With: XMLHttpRequest` or `X-CSRF-Token` ensures simple HTML `<form>` submissions cannot forge requests.

---

### 1.6 CORS Configuration & Cross-Origin Requirements

- **Strict Origin Whitelist**: Wildcard origins (`*`) are **strictly prohibited** when `allow_credentials=True`.
- **Allowed Origins**: Loaded from `CORS_ALLOWED_ORIGINS` (e.g., `["https://portal.maatram.org", "http://localhost:3000"]`).
- **Allowed Methods**: `GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD`.
- **Allowed Headers**: `Authorization, Content-Type, X-CSRF-Token, X-Requested-With, Idempotency-Key`.
- **Exposed Headers**: `Idempotency-Key, Content-Disposition`.
- **Preflight Cache**: `max_age=86400` ($24\text{ hours}$) to eliminate redundant `OPTIONS` round-trips.

---

### 1.7 Browser Integration Test Plan Across Topologies

To verify cookie transport, SameSite semantics, and CORS across all environments prior to production:

```
[ Automated Browser Test Matrix (Playwright / Cypress) ]
  ├── 1. Production Topology Test (portal.maatram.org <-> api.maatram.org)
  │     ├── Test 1.1: Login -> Verify 'Set-Cookie' has Domain=.maatram.org; SameSite=Lax; Secure; HttpOnly
  │     ├── Test 1.2: Asynchronous fetch('/api/v1/auth/refresh') carries cookie with credentials='include'
  │     ├── Test 1.3: External link navigation to portal -> Cookie preserved on top-level GET
  │     └── Test 1.4: Cross-site POST forgery attempt from malicious.com -> Cookie stripped by Lax
  ├── 2. Staging Multi-SaaS Topology Test (vercel.app <-> onrender.com)
  │     ├── Test 2.1: Login -> Verify 'Set-Cookie' has SameSite=None; Secure; HttpOnly
  │     ├── Test 2.2: Cross-site fetch carries cookie with credentials='include'
  │     └── Test 2.3: Verify X-CSRF-Token header validation blocks forged requests lacking custom header
  └── 3. Local Development Test (localhost:3000 <-> localhost:8000)
        ├── Test 3.1: Login over HTTP -> Verify Secure=False allows cookie storage
        └── Test 3.2: Refresh endpoint functions cleanly over localhost port boundary
```

---

## 2. Password Reset OTP Security

- **Generation**: Cryptographically secure 6-digit numeric OTP generated via `secrets.SystemRandom().randint(100000, 999999)`.
- **Hashing**: OTP is never stored in plaintext; stored as `SHA-256` hash in `password_reset_tokens`.
- **TTL**: 15 minutes (`expires_at = NOW() + INTERVAL '15 minutes'`).
- **Brute-Force Guard**: Maximum 5 failed verification attempts per OTP. Upon reaching attempt 5, the token is permanently invalidated.
- **Rate Limit**: Maximum 3 reset requests per email address per 24 hours.

---

## 3. Authorization & Access Control

### 3.1 Role-Based Access Control (RBAC) Matrix

| Resource / Endpoint | Public | Volunteer (Pending) | Volunteer (Approved) | Admin | Super Admin |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Health Check | Yes | Yes | Yes | Yes | Yes |
| Registration & Login | Yes | Yes | Yes | Yes | Yes |
| Email Verify & Password Reset | Yes | Yes | Yes | Yes | Yes |
| Onboarding Status Check | No | Yes | Yes | Yes | Yes |
| Profile / Consent Self-Service | No | Yes | Yes | Yes | Yes |
| Browse Published Events | No | No | Yes | Yes | Yes |
| Register / Withdraw Events | No | No | Yes | No | No |
| Check-in / Check-out Roster | No | No | No | Yes | Yes |
| Event CRUD & Lifecycle | No | No | No | Yes | Yes |
| Application Review (Approve/Reject) | No | No | No | Yes | Yes |
| Attendance Corrections ($\le 2\text{ hrs}$) | No | No | No | Yes | Yes |
| Attendance Corrections ($> 2\text{ hrs}$) | No | No | No | No | Yes |
| Event Completion Finalization | No | No | No | Yes | Yes |
| Manual Point Adjustments | No | No | No | No | Yes |
| Outbox Dead-Letter Inspection & Requeue | No | No | No | No | Yes |
| System Audit Logs | No | No | No | No | Yes |
| Manage Admin Roles / Permissions | No | No | No | No | Yes |

### 3.2 Broken Object-Level Authorization (BOLA) Prevention
- Every volunteer self-service endpoint executes an object-level tenancy check:
  `volunteer_profile.user_id == current_user.id`.
- Attempts to query or mutate another volunteer's profile, registration history, attendance records, or consent settings result in `403 Forbidden`.

---

## 4. Rate Limiting & Abuse Prevention

Enforced at the FastAPI middleware layer:

| Route Group | Limit / Threshold | Action on Breach |
| :--- | :--- | :--- |
| `POST /api/v1/auth/login` | 5 failed attempts per 15 mins per IP | Temporarily lock IP; return `429 Too Many Requests` |
| `POST /api/v1/auth/register` | 3 registrations per hour per IP | Return `429 Too Many Requests` |
| `POST /api/v1/auth/password-reset/*` | 3 requests per 24 hours per email | Return `429 Too Many Requests` |
| Authenticated User APIs | 120 requests per minute per user | Return `429 Too Many Requests` |
| Report Export Generation | 5 export requests per hour per admin | Return `429 Too Many Requests` |

---

## 5. Media Upload Security (Cloudinary)

1. **No Secret Exposure**: The `CLOUDINARY_API_SECRET` is stored strictly on the backend and never packaged into client distributions.
2. **Signed Upload Parameters**: The backend issues an HMAC-SHA256 signature binding the upload to:
   - Specific folder (`avatars/{user_id}/` or `events/{event_id}/`).
   - Specific allowed file formats (`jpg`, `png`, `webp`).
   - Short expiration timestamp ($T + 10\text{ minutes}$).
3. **File Validation**:
   - Avatars: Maximum $5\text{ MB}$; dimensions validated upon registration.
   - Event Photos: Maximum $10\text{ MB}$; verified as valid image streams.
4. **Ownership Verification**:
   - `POST /api/v1/media/register` verifies that `uploaded_by_user_id == current_user.id` or that the user has `ADMIN` role.

---

## 6. OWASP API Security Top 10 (2023) Compliance Checklist

| OWASP Vulnerability | Risk Level | Architectural Mitigation in Maatram Portal |
| :--- | :--- | :--- |
| **API1:2023 Broken Object Level Authorization (BOLA)** | Critical | Strict tenancy check `volunteer.user_id == current_user.id` enforced on all `/me`, profile, registration, and attendance endpoints. |
| **API2:2023 Broken Authentication** | Critical | Argon2id hashing; short-lived access tokens (15m); rotating refresh tokens with reuse detection; server-tracked sessions with instant revocation; OTP attempt limits. |
| **API3:2023 Broken Object Property Level Authorization** | High | Strict Pydantic input models (`CreateDTO`, `UpdateDTO`) preventing mass-assignment of sensitive fields (`role`, `status`, `points`). |
| **API4:2023 Unrestricted Resource Consumption** | High | Mandatory pagination limits (max `limit=100`); rate limiting on public and reporting endpoints; database query timeouts. |
| **API5:2023 Broken Function Level Authorization (BFLA)** | Critical | Declarative FastAPI role dependencies (`require_role(Role.ADMIN)`); permission guards on Super Admin actions (ledger adjustments, audit logs). |
| **API6:2023 Unrestricted Access to Sensitive Business Flows** | High | Concurrency-safe event capacity checks (`SELECT FOR UPDATE`); check-out requires prior check-in; duplicate point awards prevented by DB constraints. |
| **API7:2023 Server Side Request Forgery (SSRF)** | Medium | External integrations (Resend, Cloudinary, FCM) use fixed, vetted API base URLs; no user-supplied outbound webhook endpoints accepted. |
| **API8:2023 Security Misconfiguration** | High | Explicit CORS whitelist; non-root Docker container execution; production mode masks stack traces and disables public Swagger docs in untrusted environments. |
| **API9:2023 Improper Inventory Management** | Medium | Versioned API paths (`/api/v1/*`); OpenAPI schema synchronized directly from Pydantic types; deprecated endpoints removed across phase milestones. |
| **API10:2023 Unsafe Consumption of APIs** | Medium | Outbound payloads to Resend and Cloudinary strictly validated; TLS certificate verification enforced; retry backoffs prevent downstream cascading failures. |
