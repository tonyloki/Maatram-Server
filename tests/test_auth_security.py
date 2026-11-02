"""Unit tests for cryptographic security utilities: Argon2id, JWT, tokens, and CSRF."""

import uuid
from datetime import timedelta

import pytest

from src.core.exceptions import (
    DomainException,
    InvalidTokenException,
    TokenExpiredException,
)
from src.core.security import (
    create_access_token,
    decode_access_token,
    generate_csrf_token,
    generate_otp,
    generate_refresh_token,
    get_password_hash,
    hash_otp,
    hash_token,
    validate_password_strength,
    verify_csrf_token,
    verify_otp,
    verify_password,
)


def test_argon2id_hashing_and_verification():
    """Verify Argon2id password hashing produces valid hashes and verifies correctly."""
    password = "CorrectHorseBatteryStaple123!"
    hashed = get_password_hash(password)

    # Must start with argon2id algorithm prefix
    assert hashed.startswith("$argon2id$")
    assert "m=65536,t=3,p=4" in hashed

    # Verification must pass for correct password
    assert verify_password(password, hashed) is True

    # Verification must fail for incorrect password
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_password_strength_validation():
    """Verify password length policy (min 8 chars); character complexity rules pending approval."""
    # Valid passwords (length >= 8)
    validate_password_strength("ValidPass123!")
    validate_password_strength("My$ecureP@ssw0rd")
    validate_password_strength("simplepass123")
    validate_password_strength("onlylowercasepass")

    # Too short (< 8 chars)
    with pytest.raises(DomainException) as exc_info:
        validate_password_strength("Short1!")
    assert exc_info.value.code == "WEAK_PASSWORD"


def test_jwt_access_token_lifecycle():
    """Verify JWT access token generation, claims, and decoding."""
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    role = "VOLUNTEER"
    status = "APPROVED"

    token = create_access_token(
        user_id=user_id,
        role=role,
        status=status,
        session_id=session_id,
        expires_delta=timedelta(minutes=15),
    )
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["session_id"] == str(session_id)
    assert payload["role"] == role
    assert payload["status"] == status
    assert "jti" in payload
    assert payload["exp"] > payload["iat"]


def test_jwt_access_token_expiration():
    """Verify expired JWT access tokens raise TokenExpiredException."""
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    # Create already expired token
    expired_token = create_access_token(
        user_id=user_id,
        role="VOLUNTEER",
        status="APPROVED",
        session_id=session_id,
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(TokenExpiredException):
        decode_access_token(expired_token)


def test_jwt_access_token_malformed():
    """Verify malformed JWT raises InvalidTokenException."""
    with pytest.raises(InvalidTokenException):
        decode_access_token("not.a.valid.jwt.token")


def test_refresh_token_generation_and_hashing():
    """Verify high-entropy refresh token generation and SHA-256 persistence hashing."""
    token1 = generate_refresh_token()
    token2 = generate_refresh_token()

    assert token1.startswith("rt_")
    assert token2.startswith("rt_")
    assert token1 != token2
    assert len(token1) >= 40

    hash1 = hash_token(token1)
    hash2 = hash_token(token2)
    assert len(hash1) == 64  # SHA-256 hex digest
    assert hash1 != hash2
    assert hash_token(token1) == hash1  # Deterministic hashing


def test_double_submit_csrf_token():
    """Verify signed double-submit CSRF token generation and validation."""
    session_id = uuid.uuid4()
    other_session_id = uuid.uuid4()

    csrf_token = generate_csrf_token(session_id)
    assert "." in csrf_token

    # Valid validation for matching session
    assert verify_csrf_token(csrf_token, session_id) is True

    # Failed validation for mismatched session
    assert verify_csrf_token(csrf_token, other_session_id) is False

    # Failed validation for tampered token
    tampered = csrf_token[:-4] + "dead"
    assert verify_csrf_token(tampered, session_id) is False
    assert verify_csrf_token("invalid_token", session_id) is False


def test_otp_generation_and_verification():
    """Verify 6-digit numeric OTP generation, hashing, and constant-time verification."""
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()

    otp_hash = hash_otp(otp)
    assert len(otp_hash) == 64

    assert verify_otp(otp, otp_hash) is True
    assert verify_otp("000000" if otp != "000000" else "111111", otp_hash) is False
