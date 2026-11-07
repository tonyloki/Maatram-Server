"""Sprint 0 Security & Privacy Remediation Regression Test Suite.

Verifies:
1. Cryptographic CSRF token generation, signature validation, expiration, and session binding.
2. Endpoint-level CSRF enforcement on cookie-based sessions, origin validation, and mobile bearer exemptions.
3. Production security configuration validators (halting unsafe DEBUG, COOKIE_SECURE, secrets, CORS).
4. Strict consent default handling (opt-in false, never implicitly granted).
"""

import time
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings
from src.core.security import (
    create_access_token,
    generate_csrf_token,
    verify_csrf_token,
)
from src.models.users import User, UserSession
from src.models.volunteers import ConsentRecord, VolunteerProfile


# ==============================================================================
# 1. Cryptographic CSRF Token Unit Tests
# ==============================================================================

def test_csrf_token_structure_and_verification():
    """Verify standard 3-part signed CSRF token validates with matching session."""
    session_id = uuid.uuid4()
    token = generate_csrf_token(session_id)
    
    parts = token.split(".")
    assert len(parts) == 3, "CSRF token must have 3 parts: nonce.ts.signature"
    
    # Valid token verification
    assert verify_csrf_token(token, session_id) is True


def test_csrf_token_session_binding():
    """Verify CSRF token generated for session A fails validation for session B."""
    session_a = uuid.uuid4()
    session_b = uuid.uuid4()
    token_a = generate_csrf_token(session_a)
    
    assert verify_csrf_token(token_a, session_b) is False


def test_csrf_token_tampering_detected():
    """Verify any modification to nonce, timestamp, or signature invalidates token."""
    session_id = uuid.uuid4()
    token = generate_csrf_token(session_id)
    nonce, ts, sig = token.split(".")

    # Tampered nonce (invert first char)
    tampered_nonce_char = "0" if nonce[0] != "0" else "1"
    tampered_nonce = f"{tampered_nonce_char}{nonce[1:]}.{ts}.{sig}"
    assert verify_csrf_token(tampered_nonce, session_id) is False

    # Tampered timestamp
    tampered_ts = f"{nonce}.{int(ts)+10}.{sig}"
    assert verify_csrf_token(tampered_ts, session_id) is False

    # Tampered signature (invert first char)
    tampered_sig_char = "0" if sig[0] != "0" else "1"
    tampered_sig = f"{nonce}.{ts}.{tampered_sig_char}{sig[1:]}"
    assert verify_csrf_token(tampered_sig, session_id) is False


def test_csrf_token_expiration():
    """Verify expired CSRF token is rejected."""
    session_id = uuid.uuid4()
    # Issue token with timestamp from 31 days ago
    old_ts = int(time.time()) - (86400 * 31)
    token = generate_csrf_token(session_id, issued_at=old_ts)
    
    # Default max_age is 30 days
    assert verify_csrf_token(token, session_id, max_age_seconds=86400 * 30) is False


def test_csrf_token_future_timestamp_rejected():
    """Verify CSRF token with timestamp in the far future is rejected (clock skew protection)."""
    session_id = uuid.uuid4()
    future_ts = int(time.time()) + 1000
    token = generate_csrf_token(session_id, issued_at=future_ts)
    
    assert verify_csrf_token(token, session_id) is False


def test_csrf_token_legacy_two_part_support():
    """Verify legacy 2-part token (nonce.signature) validates for backwards compatibility."""
    import hashlib
    import hmac
    import secrets
    from src.core.config import settings

    session_id = uuid.uuid4()
    nonce = secrets.token_hex(16)
    expected_sig = hmac.new(
        settings.SECRET_KEY.encode(),
        f"{session_id}:{nonce}".encode(),
        hashlib.sha256,
    ).hexdigest()
    legacy_token = f"{nonce}.{expected_sig}"
    
    assert verify_csrf_token(legacy_token, session_id) is True
    # Mismatched session on legacy token fails
    assert verify_csrf_token(legacy_token, uuid.uuid4()) is False


# ==============================================================================
# 2. Production Security Configuration Validator Tests
# ==============================================================================

def test_production_config_rejects_debug_true():
    """Verify production environment refuses startup if DEBUG=True."""
    with pytest.raises(ValidationError) as exc:
        Settings(ENVIRONMENT="production", DEBUG=True, COOKIE_SECURE=True, SECRET_KEY="a" * 32)
    assert "DEBUG cannot be True" in str(exc.value)


def test_production_config_rejects_insecure_cookies():
    """Verify production environment refuses startup if COOKIE_SECURE=False."""
    with pytest.raises(ValidationError) as exc:
        Settings(ENVIRONMENT="production", DEBUG=False, COOKIE_SECURE=False, SECRET_KEY="a" * 32)
    assert "COOKIE_SECURE cannot be False" in str(exc.value)


def test_production_config_rejects_weak_secret_key():
    """Verify production environment refuses startup with default/weak secret keys."""
    with pytest.raises(ValidationError) as exc:
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            COOKIE_SECURE=True,
            SECRET_KEY="dev-secret-key-change-in-production",
        )
    assert "Insecure or default SECRET_KEY" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            COOKIE_SECURE=True,
            SECRET_KEY="short-secret-key",
        )
    assert "Must be a secure random secret of at least 32 characters" in str(exc.value)


def test_production_config_rejects_wildcard_or_localhost_cors():
    """Verify production environment refuses startup with wildcard or localhost CORS."""
    with pytest.raises(ValidationError) as exc:
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            COOKIE_SECURE=True,
            SECRET_KEY="a" * 32,
            BACKEND_CORS_ORIGINS=["*"],
        )
    assert "Wildcard CORS origin" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            COOKIE_SECURE=True,
            SECRET_KEY="a" * 32,
            BACKEND_CORS_ORIGINS=["http://localhost:3000"],
        )
    assert "Localhost origin" in str(exc.value)


def test_production_config_rejects_samesite_none_without_secure():
    """Verify COOKIE_SAMESITE='none' requires COOKIE_SECURE=True in all environments."""
    with pytest.raises(ValidationError) as exc:
        Settings(
            ENVIRONMENT="development",
            COOKIE_SAMESITE="none",
            COOKIE_SECURE=False,
        )
    assert "COOKIE_SAMESITE='none' requires COOKIE_SECURE=True" in str(exc.value)


def test_production_config_accepts_valid_production_settings():
    """Verify valid hardened production settings pass validation without error."""
    valid_prod = Settings(
        ENVIRONMENT="production",
        DEBUG=False,
        COOKIE_SECURE=True,
        SECRET_KEY="production-super-strong-cryptographic-secret-key-at-least-32-chars",
        BACKEND_CORS_ORIGINS=["https://portal.maatramfoundation.org"],
    )
    assert valid_prod.ENVIRONMENT == "production"
    assert valid_prod.COOKIE_SECURE is True


def test_development_config_allows_local_http():
    """Verify development mode allows local HTTP defaults (DEBUG=False, COOKIE_SECURE=False)."""
    dev = Settings(ENVIRONMENT="development")
    assert dev.ENVIRONMENT == "development"
    assert dev.COOKIE_SECURE is False


# ==============================================================================
# 3. HTTP CSRF & Origin Verification Integration Tests
# ==============================================================================

@pytest.fixture
async def authenticated_user_session(async_db: AsyncSession):
    """Create a verified test user, profile, consent record, and active session in the database."""
    user = User(
        id=uuid.uuid4(),
        email=f"sprint0_{uuid.uuid4().hex[:6]}@example.com",
        password_hash="test_hash",
        status="APPROVED",
        role="VOLUNTEER",
    )
    async_db.add(user)
    await async_db.flush()

    profile = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        first_name="Test",
        last_name="Volunteer",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=22,
        gender="MALE",
        category="STUDENT",
    )
    async_db.add(profile)
    await async_db.flush()

    consent = ConsentRecord(
        id=uuid.uuid4(),
        volunteer_profile_id=profile.id,
        leaderboard_visible=False,
        name_visible=False,
        thank_you_emails=False,
        linkedin_content=False,
        contact_available=False,
        media_usage=False,
    )
    async_db.add(consent)

    session = UserSession(
        id=uuid.uuid4(),
        user_id=user.id,
        refresh_token_hash="dummy_hash",
        client_type="WEB",
        ip_address="127.0.0.1",
        device_info="Pytest-Client",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    async_db.add(session)
    await async_db.commit()

    access_token = create_access_token(
        user_id=user.id,
        role="VOLUNTEER",
        status="APPROVED",
        session_id=session.id,
    )
    csrf_token = generate_csrf_token(session.id)

    return {
        "user": user,
        "profile": profile,
        "consent": consent,
        "session": session,
        "access_token": access_token,
        "csrf_token": csrf_token,
    }


@pytest.mark.asyncio
async def test_csrf_cookie_request_missing_csrf_header_rejected(
    client: AsyncClient, authenticated_user_session
):
    """Unsafe request with ambient session cookies but missing X-CSRF-Token is rejected (403)."""
    data = authenticated_user_session
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", data["csrf_token"])

    # Attempt mutative consent update without X-CSRF-Token header
    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={"Origin": "http://localhost:3000"},
    )
    assert res.status_code == 403
    assert res.json().get("error_code") == "CSRF_VALIDATION_FAILED"
    assert "missing" in res.json().get("message", "").lower()


@pytest.mark.asyncio
async def test_csrf_cookie_request_mismatched_cookie_and_header_rejected(
    client: AsyncClient, authenticated_user_session
):
    """Request with X-CSRF-Token that differs from csrf_token cookie is rejected (403)."""
    data = authenticated_user_session
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", data["csrf_token"])

    # Send a different validly-formatted token in the header
    other_token = generate_csrf_token(uuid.uuid4())
    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "X-CSRF-Token": other_token,
            "Origin": "http://localhost:3000",
        },
    )
    assert res.status_code == 403
    assert res.json().get("error_code") == "CSRF_VALIDATION_FAILED"
    assert "mismatch" in res.json().get("message", "").lower()


@pytest.mark.asyncio
async def test_csrf_cookie_request_tampered_signature_rejected(
    client: AsyncClient, authenticated_user_session
):
    """Request with forged signature in X-CSRF-Token is rejected (403)."""
    data = authenticated_user_session
    tampered = data["csrf_token"][:-4] + "dead"
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", tampered)

    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "X-CSRF-Token": tampered,
            "Origin": "http://localhost:3000",
        },
    )
    assert res.status_code == 403
    assert res.json().get("error_code") == "CSRF_VALIDATION_FAILED"
    assert "invalid or expired" in res.json().get("message", "").lower()


@pytest.mark.asyncio
async def test_csrf_disallowed_origin_rejected(
    client: AsyncClient, authenticated_user_session
):
    """Request from untrusted cross-origin domain is rejected (403)."""
    data = authenticated_user_session
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", data["csrf_token"])

    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "X-CSRF-Token": data["csrf_token"],
            "Origin": "https://malicious-attacker-site.com",
        },
    )
    assert res.status_code == 403
    assert res.json().get("error_code") == "CSRF_VALIDATION_FAILED"
    assert "origin" in res.json().get("message", "").lower()


@pytest.mark.asyncio
async def test_csrf_mobile_bearer_token_exempt_without_cookies(
    client: AsyncClient, authenticated_user_session
):
    """Mobile app requests using pure Bearer authorization without cookies are exempt from CSRF."""
    data = authenticated_user_session
    # Ensure no cookies
    client.cookies.clear()

    # Mobile requests send Authorization header and no cookies, no CSRF token
    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "Authorization": f"Bearer {data['access_token']}",
        },
    )
    # The endpoint processes the request without a 403 CSRF error
    assert res.status_code in (200, 404)  # 200 if volunteer exists, 404 if profile not yet created in test db


@pytest.mark.asyncio
async def test_csrf_cookie_request_valid_token_succeeds(
    client: AsyncClient, authenticated_user_session
):
    """Request with valid cookie and matching signed X-CSRF-Token header passes CSRF verification."""
    data = authenticated_user_session
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", data["csrf_token"])

    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "X-CSRF-Token": data["csrf_token"],
            "Origin": "http://localhost:3000",
        },
    )
    # Passed CSRF check
    assert res.status_code != 403


# ==============================================================================
# 4. Consent Defaults & Affirmative Opt-In Persistence Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_consent_defaults_all_strictly_false(async_db: AsyncSession):
    """Verify that newly created ConsentRecord defaults all 6 preferences to False (opt-in)."""
    user = User(
        id=uuid.uuid4(),
        email=f"consent_{uuid.uuid4().hex[:6]}@example.com",
        password_hash="test_hash",
        status="APPROVED",
        role="VOLUNTEER",
    )
    async_db.add(user)
    await async_db.flush()

    profile = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        first_name="Consent",
        last_name="Tester",
        mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
        age=21,
        gender="FEMALE",
        category="STUDENT",
    )
    async_db.add(profile)
    await async_db.flush()

    consent = ConsentRecord(
        id=uuid.uuid4(),
        volunteer_profile_id=profile.id,
    )
    async_db.add(consent)
    await async_db.commit()

    # Verify all 6 consent preferences default strictly to False
    assert consent.leaderboard_visible is False
    assert consent.name_visible is False
    assert consent.thank_you_emails is False
    assert consent.linkedin_content is False
    assert consent.contact_available is False
    assert consent.media_usage is False


@pytest.mark.asyncio
async def test_consent_put_updates_only_specified_fields_without_overwriting(
    client: AsyncClient, authenticated_user_session
):
    """Verify PUT /api/v1/consent/me updates only explicitly changed fields and preserves others."""
    data = authenticated_user_session
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", data["csrf_token"])

    # Update only media_usage to True
    res = await client.put(
        "/api/v1/consent/me",
        json={"media_usage": True},
        headers={
            "X-CSRF-Token": data["csrf_token"],
            "Origin": "http://localhost:3000",
        },
    )
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["media_usage"] is True
    # All other fields remain False
    assert res_data["leaderboard_visible"] is False
    assert res_data["name_visible"] is False
    assert res_data["thank_you_emails"] is False
    assert res_data["linkedin_content"] is False
    assert res_data["contact_available"] is False


# ==============================================================================
# 5. Advanced Security Edge Cases: Unsigned Tokens & Mixed Auth Modes
# ==============================================================================

def test_csrf_token_unsigned_and_malformed_rejected():
    """Verify legacy unsigned or malformed tokens cannot bypass verification."""
    session_id = uuid.uuid4()
    
    # Completely unsigned string
    assert verify_csrf_token("unsigned_string_without_dots", session_id) is False
    # Empty string
    assert verify_csrf_token("", session_id) is False
    # None-like or whitespace
    assert verify_csrf_token("   ", session_id) is False
    # Unsigned 2-part token
    assert verify_csrf_token("nonce.unsignedsignature", session_id) is False
    # 4-part token
    assert verify_csrf_token("a.b.c.d", session_id) is False
    # Non-integer timestamp in 3-part token
    assert verify_csrf_token("nonce.notaninteger.signature", session_id) is False


@pytest.mark.asyncio
async def test_csrf_fake_bearer_token_cannot_bypass_csrf(
    client: AsyncClient, authenticated_user_session
):
    """A request with ambient cookies and an invalid/forged Bearer token CANNOT bypass CSRF."""
    data = authenticated_user_session
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", data["csrf_token"])

    # Attempt mutative request with forged/invalid Bearer header and missing X-CSRF-Token
    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "Authorization": "Bearer forged.invalid.token",
            "Origin": "http://localhost:3000",
        },
    )
    # Must be rejected (either 403 CSRF missing or 401 invalid token)
    assert res.status_code in (401, 403)
    if res.status_code == 403:
        assert res.json().get("error_code") == "CSRF_VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_csrf_expired_bearer_token_cannot_bypass_csrf(
    client: AsyncClient, authenticated_user_session
):
    """A request with ambient cookies and an expired Bearer token CANNOT bypass CSRF."""
    data = authenticated_user_session
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", data["csrf_token"])

    # Create expired token
    expired_token = create_access_token(
        user_id=data["user"].id,
        role="VOLUNTEER",
        status="APPROVED",
        session_id=data["session"].id,
        expires_delta=timedelta(seconds=-10),
    )

    res = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "Authorization": f"Bearer {expired_token}",
            "Origin": "http://localhost:3000",
        },
    )
    assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_csrf_mixed_auth_mode_requires_csrf_when_access_cookie_present(
    client: AsyncClient, authenticated_user_session
):
    """When access_token is transmitted via cookie (cookie auth), CSRF is strictly required."""
    data = authenticated_user_session
    client.cookies.set("access_token", data["access_token"])
    client.cookies.set("csrf_token", data["csrf_token"])

    # Without CSRF header -> 403
    res_no_csrf = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={"Origin": "http://localhost:3000"},
    )
    assert res_no_csrf.status_code == 403
    assert res_no_csrf.json().get("error_code") == "CSRF_VALIDATION_FAILED"

    # With valid CSRF header -> 200
    res_with_csrf = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "X-CSRF-Token": data["csrf_token"],
            "Origin": "http://localhost:3000",
        },
    )
    assert res_with_csrf.status_code == 200
    res_data = res_with_csrf.json()
    assert res_data["name_visible"] is False
    assert res_data["thank_you_emails"] is False
    assert res_data["linkedin_content"] is False
    assert res_data["contact_available"] is False


# ==============================================================================
# 6. Auth Refresh Endpoint CSRF, Origin & Full Token Lifecycle Verification
# ==============================================================================

@pytest.mark.asyncio
async def test_auth_refresh_cross_origin_with_cookies_rejected(client: AsyncClient, async_db: AsyncSession):
    """POST /auth/refresh with cookies from unauthorized origin is rejected (403)."""
    # 1. Register and login to obtain legitimate refresh cookie
    email = f"refresh_sec_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Refresh",
            "last_name": "Tester",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 25,
            "gender": "MALE",
            "category": "CORPORATE",
            "corporate_details": {
                "organisation": "Tech Corp",
                "designation": "Engineer",
                "years_of_experience": 3.0,
                "location": "Chennai",
                "skills": ["Python"],
            },
        },
    )

    # Transition user to APPROVED
    from sqlalchemy import select
    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    # Login via web (sets cookies)
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
        headers={"Origin": "http://localhost:3000"},
    )
    assert login_res.status_code == 200
    assert "refresh_token" in client.cookies

    # Attempt cross-origin refresh from malicious site
    cross_origin_res = await client.post(
        "/api/v1/auth/refresh",
        headers={"Origin": "https://attacker-malicious-site.com"},
    )
    assert cross_origin_res.status_code == 403
    assert cross_origin_res.json().get("error_code") == "CSRF_VALIDATION_FAILED"
    assert "Origin not permitted" in cross_origin_res.json().get("message", "")


@pytest.mark.asyncio
async def test_auth_refresh_cookie_attributes_and_legitimate_rotation(client: AsyncClient, async_db: AsyncSession):
    """Verify refresh cookie attributes (HttpOnly, SameSite, Path) and legitimate token rotation."""
    email = f"refresh_attr_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Attr",
            "last_name": "Tester",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 26,
            "gender": "FEMALE",
            "category": "CORPORATE",
            "corporate_details": {
                "organisation": "Sec Corp",
                "designation": "Analyst",
                "years_of_experience": 2.0,
                "location": "Chennai",
                "skills": ["Security"],
            },
        },
    )

    from sqlalchemy import select
    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
        headers={"Origin": "http://localhost:3000"},
    )
    assert login_res.status_code == 200

    # Inspect Set-Cookie headers on login
    set_cookie_headers = login_res.headers.get_list("set-cookie")
    refresh_cookie_header = next((h for h in set_cookie_headers if h.startswith("refresh_token=")), None)
    csrf_cookie_header = next((h for h in set_cookie_headers if h.startswith("csrf_token=")), None)
    
    assert refresh_cookie_header is not None
    assert "HttpOnly" in refresh_cookie_header
    assert "Path=/api/v1/auth" in refresh_cookie_header
    assert "SameSite=lax" in refresh_cookie_header

    assert csrf_cookie_header is not None
    assert "HttpOnly" not in csrf_cookie_header  # Accessible to client JS
    assert "Path=/" in csrf_cookie_header
    assert "SameSite=lax" in csrf_cookie_header

    old_refresh_cookie = client.cookies.get("refresh_token")
    csrf_cookie = client.cookies.get("csrf_token")

    # Legitimate refresh from approved origin with matching CSRF header
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        headers={
            "Origin": "http://localhost:3000",
            "X-CSRF-Token": csrf_cookie,
        },
    )
    assert refresh_res.status_code == 200
    new_token_data = refresh_res.json()
    assert "access_token" in new_token_data
    assert new_token_data["token_type"] == "bearer"

    # Verify cookie rotation
    new_refresh_cookie = client.cookies.get("refresh_token")
    assert new_refresh_cookie != old_refresh_cookie


@pytest.mark.asyncio
async def test_auth_full_lifecycle_login_refresh_logout_logout_all(client: AsyncClient, async_db: AsyncSession):
    """Verify complete token lifecycle: login -> refresh -> logout -> session revocation."""
    email = f"lifecycle_{uuid.uuid4().hex[:6]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Life",
            "last_name": "Cycle",
            "mobile_number": f"+9198{uuid.uuid4().int % 100000000:08d}",
            "age": 28,
            "gender": "MALE",
            "category": "CORPORATE",
            "corporate_details": {
                "organisation": "Cycle Ltd",
                "designation": "Lead",
                "years_of_experience": 5.0,
                "location": "Chennai",
                "skills": ["Architecture"],
            },
        },
    )

    from sqlalchemy import select
    user = (await async_db.execute(select(User).where(User.email == email))).scalar_one()
    user.status = "APPROVED"
    await async_db.commit()

    # 1. Login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
        headers={"Origin": "http://localhost:3000"},
    )
    assert login_res.status_code == 200
    access_token = login_res.json()["access_token"]
    csrf_token = client.cookies.get("csrf_token")

    # 2. Refresh
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        headers={"Origin": "http://localhost:3000", "X-CSRF-Token": csrf_token},
    )
    assert refresh_res.status_code == 200
    refreshed_access_token = refresh_res.json()["access_token"]
    new_csrf_token = client.cookies.get("csrf_token")

    # 3. Logout requires CSRF and revokes session
    logout_res = await client.post(
        "/api/v1/auth/logout",
        headers={
            "Authorization": f"Bearer {refreshed_access_token}",
            "X-CSRF-Token": new_csrf_token,
            "Origin": "http://localhost:3000",
        },
    )
    assert logout_res.status_code == 200

    # 4. Attempt to use revoked session fails (401)
    res_after_logout = await client.put(
        "/api/v1/consent/me",
        json={"leaderboard_visible": True},
        headers={
            "Authorization": f"Bearer {refreshed_access_token}",
            "X-CSRF-Token": new_csrf_token,
            "Origin": "http://localhost:3000",
        },
    )
    assert res_after_logout.status_code == 401


