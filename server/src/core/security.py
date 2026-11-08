"""Core security and cryptographic module.

Implements Argon2id password hashing, JWT access token generation and validation,
high-entropy refresh token hashing, double-submit CSRF token management,
and OTP generation/verification.
"""

import asyncio
import hashlib
import hmac
import ipaddress
import secrets
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from typing import Any

import argon2
import jwt
from argon2.exceptions import VerifyMismatchError
from fastapi import Request

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

# Dedicated bounded thread pool for CPU-bound cryptographic operations (Argon2id)
# Bounded to 4 worker threads to protect CPU cores and prevent event loop starvation
_crypto_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="argon2_worker")


def get_password_hash(password: str) -> str:
    """Hash password using Argon2id synchronously."""
    return _argon2_hasher.hash(password)


async def get_password_hash_async(password: str) -> str:
    """Hash password using Argon2id offloaded to a bounded worker thread."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_crypto_executor, get_password_hash, password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored Argon2id hash synchronously."""
    try:
        return _argon2_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored Argon2id hash offloaded to a bounded worker thread."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _crypto_executor, verify_password, plain_password, hashed_password
    )


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


def generate_csrf_token(session_id: uuid.UUID | str, issued_at: int | None = None) -> str:
    """Generate cryptographically signed anti-CSRF token bound to session and timestamp."""
    nonce = secrets.token_hex(16)
    ts = issued_at if issued_at is not None else int(datetime.now(UTC).timestamp())
    message = f"{session_id}:{nonce}:{ts}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"{nonce}.{ts}.{signature}"


def verify_csrf_token(
    csrf_token: str,
    session_id: uuid.UUID | str,
    max_age_seconds: int = 86400 * 30,
) -> bool:
    """Validate signed double-submit CSRF token against session binding, signature, and expiration."""
    if not csrf_token or "." not in csrf_token:
        return False

    parts = csrf_token.split(".")
    # 3-part token: nonce.timestamp.signature
    if len(parts) == 3:
        nonce, ts_str, signature = parts
        try:
            ts = int(ts_str)
        except ValueError:
            return False

        # Expiration check
        now = int(datetime.now(UTC).timestamp())
        if now - ts > max_age_seconds or ts > now + 300:  # Allow 5 min clock skew
            return False

        message = f"{session_id}:{nonce}:{ts}".encode()
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)

    # 2-part token (legacy backward compatibility): nonce.signature
    if len(parts) == 2:
        nonce, signature = parts
        message = f"{session_id}:{nonce}".encode()
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)

    return False


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


def _is_ip_in_network_list(
    ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
    network_strings: list[str],
) -> bool:
    """Check if an IP address belongs to any configured CIDR or IP in network_strings."""
    for net_str in network_strings:
        try:
            net = ipaddress.ip_network(net_str.strip(), strict=False)
            if ip in net:
                return True
        except (ValueError, TypeError):
            continue
    return False


def extract_client_ip(request: Request) -> str:
    """Extract authenticated client IP using right-to-left traversal of trusted proxies.

    Security rules:
    1. If request.client is None or host is missing, fallback to '127.0.0.1'.
    2. Parse immediate peer IP. If invalid/unparseable, fallback to '127.0.0.1'.
    3. Check if immediate peer is trusted (in TRUSTED_PROXY_IPS or CLOUDFLARE_PROXY_IPS if enabled).
       If NOT trusted: Ignore all forwarded headers (prevents spoofing) and return immediate peer IP.
    4. If immediate peer IS trusted:
       a. If Cloudflare is enabled and immediate peer is in CLOUDFLARE_PROXY_IPS:
          check 'cf-connecting-ip' header. If present and valid IP, return it.
       b. Inspect 'x-forwarded-for' header:
          Split by comma and traverse right-to-left (upstream to downstream).
          Find first untrusted IP in the chain and return it.
          If all IPs in the chain are trusted, return the leftmost IP.
       c. If no 'x-forwarded-for' header, inspect 'x-real-ip'. If present and valid IP, return it.
       d. Fallback safely to immediate peer IP if any header is empty or malformed.
    """
    if not request.client or not request.client.host:
        return "127.0.0.1"

    raw_peer = request.client.host.strip()
    try:
        peer_ip = ipaddress.ip_address(raw_peer)
    except ValueError:
        return "127.0.0.1"

    # Assemble trusted networks
    trusted_networks = list(settings.TRUSTED_PROXY_IPS)
    if settings.TRUST_CLOUDFLARE_PROXIES:
        trusted_networks.extend(settings.CLOUDFLARE_PROXY_IPS)

    peer_is_trusted = _is_ip_in_network_list(peer_ip, trusted_networks)
    if not peer_is_trusted:
        # Direct client or untrusted proxy: forwarded headers MUST NOT be trusted
        return str(peer_ip)

    # Trusted proxy detected: check Cloudflare CF-Connecting-IP
    if settings.TRUST_CLOUDFLARE_PROXIES:
        if _is_ip_in_network_list(peer_ip, settings.CLOUDFLARE_PROXY_IPS):
            cf_ip = request.headers.get("cf-connecting-ip")
            if cf_ip:
                cf_ip = cf_ip.strip()
                try:
                    parsed_cf = ipaddress.ip_address(cf_ip)
                    return str(parsed_cf)
                except ValueError:
                    pass

    # Inspect X-Forwarded-For
    xff = request.headers.get("x-forwarded-for")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            # Validate all parts; if any is completely corrupt, fallback to immediate peer
            parsed_ips: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
            valid = True
            for p in parts:
                try:
                    parsed_ips.append(ipaddress.ip_address(p))
                except ValueError:
                    valid = False
                    break

            if valid and parsed_ips:
                # Traverse right-to-left
                for parsed_ip in reversed(parsed_ips):
                    if not _is_ip_in_network_list(parsed_ip, trusted_networks):
                        return str(parsed_ip)
                # All hops were trusted proxies; leftmost is the originating client
                return str(parsed_ips[0])

    # Inspect X-Real-IP fallback
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        x_real_ip = x_real_ip.strip()
        try:
            parsed_real = ipaddress.ip_address(x_real_ip)
            return str(parsed_real)
        except ValueError:
            pass

    return str(peer_ip)
