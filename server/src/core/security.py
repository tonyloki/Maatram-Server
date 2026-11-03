"""Core security and cryptographic module.

Implements Argon2id password hashing, JWT access token generation and validation,
high-entropy refresh token hashing, double-submit CSRF token management,
and OTP generation/verification.
"""

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import argon2
import jwt
from argon2.exceptions import VerifyMismatchError

from src.core.config import settings
from src.core.exceptions import (
    DomainException,
    InvalidTokenException,
    TokenExpiredException,
)

# Security constants
ALGORITHM = "HS256"

# Argon2id Hasher configured per SECURITY_POLICY.md Section 1.1:
# Memory: 64 MB (65536 KB), Iterations: 3, Parallelism: 4, Salt: 16 bytes, Hash: 32 bytes
_argon2_hasher = argon2.PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=argon2.Type.ID,
)


def get_password_hash(password: str) -> str:
    """Hash password using Argon2id."""
    return _argon2_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored Argon2id hash."""
    try:
        return _argon2_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def validate_password_strength(password: str) -> None:
    # Password policy: enforces only requirements explicitly documented in Phase 3 specification.
    # Character-class complexity rules (uppercase, lowercase, digit, special) remain PENDING Maatram approval.
    # See OPEN_QUESTIONS.md.
    if len(password) < 8:
        raise DomainException(
            message="Password must be at least 8 characters long.",
            code="WEAK_PASSWORD",
        )


def create_access_token(
    user_id: uuid.UUID,
    role: str,
    status: str,
    session_id: uuid.UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Generate cryptographically signed JWT access token."""
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    claims: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "status": status,
        "session_id": str(session_id),
        "jti": str(uuid.uuid4()),
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate access token claims."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "role", "status", "session_id", "exp", "iat"]},
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredException(message="Access token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenException(message=f"Invalid access token: {exc}") from exc


def generate_refresh_token() -> str:
    """Generate high-entropy 256-bit cryptographically secure random refresh token."""
    return f"rt_{secrets.token_urlsafe(32)}"


def hash_token(token: str) -> str:
    """Hash raw token with SHA-256 for persistent database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_csrf_token(session_id: uuid.UUID | str) -> str:
    """Generate cryptographically signed anti-CSRF token bound to session."""
    nonce = secrets.token_hex(16)
    message = f"{session_id}:{nonce}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"{nonce}.{signature}"


def verify_csrf_token(csrf_token: str, session_id: uuid.UUID | str) -> bool:
    """Validate signed double-submit CSRF token."""
    if not csrf_token or "." not in csrf_token:
        return False
    nonce, signature = csrf_token.split(".", 1)
    message = f"{session_id}:{nonce}".encode()
    expected_signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware in UTC across SQLite and PostgreSQL."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def generate_otp() -> str:
    """Generate secure 6-digit numeric OTP."""
    return f"{secrets.SystemRandom().randint(100000, 999999)}"


def hash_otp(otp: str) -> str:
    """Hash numeric OTP with SHA-256 for persistent storage."""
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Verify numeric OTP using constant-time comparison."""
    computed_hash = hash_otp(plain_otp.strip())
    return hmac.compare_digest(computed_hash, hashed_otp)
