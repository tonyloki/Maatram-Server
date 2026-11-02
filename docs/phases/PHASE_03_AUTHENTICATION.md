# PHASE 03 — Authentication, Sessions & Authorization

## 1. Objective
Implement secure FastAPI-managed authentication with Argon2id password hashing, short-lived JWT access tokens, rotating refresh tokens in `user_sessions`, session revocation, topology-aware SameSite cookie handlers, Double-Submit CSRF protection, and RBAC dependency guards.

## 2. Scope
- Argon2id password hashing and verification utilities (`core/security.py`).
- JWT token encoding and decoding utilities with claim verification.
- User repository (`repositories/user_repo.py`).
- Authentication service (`services/auth_service.py`).
- Auth API router (`api/v1/auth.py`).
- Security dependency injection (`api/deps.py`) enforcing `get_current_user`, `require_role`, CSRF validation, and session validity.
- Cookie management: `SameSite=Lax; Domain=.maatram.org; Secure` for production apex domains, and `SameSite=None; Secure` for cross-SaaS staging.
- Double-Submit CSRF protection (`X-CSRF-Token` header validation) and Origin/Referer verification on state-modifying requests.
- Password reset OTP request/confirm workflows.
- Email verification token workflows.

## 3. Dependencies
- Phase 2 completed.

## 4. Implementation Tasks
1. Implement `Argon2id` hasher with $m=65536, t=3, p=4$ parameters.
2. Build JWT token factory creating 15-minute access tokens and 30-day random refresh token hashes.
3. Implement `user_sessions` tracking in database; store device metadata, IP address, and client type.
4. Build token rotation logic on `/refresh`: invalidate presented token and issue new token pair; detect reuse attempts and revoke session lineage.
5. Implement cookie handlers for Web supporting configurable topology settings (`COOKIE_SAMESITE`, `COOKIE_DOMAIN`, `COOKIE_SECURE`).
6. Implement CSRF middleware: validate `Origin` matches allowed CORS list, and verify `X-CSRF-Token` on mutative cookie-authenticated requests.
7. Implement `deps.py` dependencies for role validation (`VOLUNTEER`, `ADMIN`, `SUPER_ADMIN`).
8. Implement rate limiting on `/login` and password reset endpoints.

## 5. Database Changes
Operates on `users`, `user_sessions`, `email_verifications`, and `password_reset_tokens`.

## 6. APIs
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/verify-email`
- `POST /api/v1/auth/password-reset/request`
- `POST /api/v1/auth/password-reset/confirm`
- `GET /api/v1/users/me`

## 7. Security Requirements
- Argon2id hashing enforced.
- Refresh token reuse must immediately invalidate the entire session lineage.
- Brute-force rate limiting: max 5 failed logins per 15 minutes.
- Strict Pydantic validation on passwords (minimum 8 characters, upper, lower, digit, special character).
- Double-submit CSRF token validation and Origin verification on cookie requests.

## 8. Test Requirements
- Unit tests for password hashing and verification.
- Integration tests for login, token refresh, token rotation, and session logout.
- Security tests: Verify expired access tokens are rejected; verify revoked refresh tokens fail.
- CSRF test: verify mutative cookie requests without `X-CSRF-Token` fail with `403 Forbidden`.
- Topology test plan: verify cookie serialization under production (`SameSite=Lax`), staging (`SameSite=None`), and local development settings.

## 9. Deliverables
- `src/core/security.py`, `src/services/auth_service.py`, `src/api/v1/auth.py`, `src/api/deps.py`.
- Automated authentication and CSRF test suite.

## 10. Acceptance Criteria
- Login returns valid tokens, sets secure cookies for Web, and emits CSRF tokens.
- Refresh endpoint rotates tokens and revokes old refresh tokens.
- Protected routes reject unauthenticated or under-privileged requests with `401` or `403`.
- Browser integration tests pass for production, staging, and local cookie configurations.

## 11. Definition of Done (DoD)
All authentication and session endpoints functional, secure, and covered by passing automated integration tests.
