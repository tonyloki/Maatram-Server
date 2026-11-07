"""FastAPI dependency injection for database sessions, security, RBAC, and CSRF protection."""

import hmac
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Cookie, Depends, Header, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db as get_db
from src.core.exceptions import (
    AccountSuspendedException,
    CSRFValidationException,
    ForbiddenException,
    InvalidTokenException,
    SessionRevokedException,
    TokenExpiredException,
    UnauthorizedException,
)
from src.core.security import decode_access_token, ensure_utc, verify_csrf_token
from src.models.users import User, UserSession
from src.repositories.user_repo import user_repository

# Optional Bearer security scheme so OpenAPI documents Bearer auth
bearer_scheme = HTTPBearer(auto_error=False)


async def get_token_str(
    request: Request,
    auth_header: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    access_token_cookie: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> str:
    """Extract raw JWT access token from Authorization header or cookie."""
    if auth_header and auth_header.credentials:
        return auth_header.credentials
    if access_token_cookie:
        return access_token_cookie
    raise UnauthorizedException("Authentication credentials missing.")


async def get_current_session(
    token: Annotated[str, Depends(get_token_str)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> tuple[UserSession, dict[str, str]]:
    """Verify JWT access token and active server-side database session."""
    payload = decode_access_token(token)
    session_id_str = payload.get("session_id")
    if not session_id_str:
        raise InvalidTokenException("Missing session identifier in token.")

    try:
        session_id = uuid.UUID(session_id_str)
    except (ValueError, TypeError):
        raise InvalidTokenException("Invalid session UUID format.") from None

    session = await user_repository.get_session_by_id(db, session_id)
    if not session or session.is_revoked:
        raise SessionRevokedException("Session has been revoked.")

    now = datetime.now(UTC)
    if ensure_utc(session.expires_at) < now:
        raise TokenExpiredException("Session has expired.")

    return session, payload


async def get_current_user(
    session_and_payload: Annotated[
        tuple[UserSession, dict[str, str]], Depends(get_current_session)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolve and validate the active authenticated user record."""
    session, payload = session_and_payload
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise InvalidTokenException("Missing subject user ID in token.")

    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise InvalidTokenException("Invalid user ID UUID format.") from None

    user = await user_repository.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("User account does not exist or is inactive.")

    if user.status == "SUSPENDED":
        raise AccountSuspendedException()

    return user


def require_role(*allowed_roles: str) -> Callable[[User], User]:
    """Enforce declarative Role-Based Access Control (RBAC)."""

    def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                message=f"Access denied. Required roles: {', '.join(allowed_roles)}.",
                code="INSUFFICIENT_PERMISSIONS",
            )
        return current_user

    return role_checker


async def verify_csrf(
    request: Request,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    auth_header: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    csrf_token_cookie: Annotated[str | None, Cookie(alias="csrf_token")] = None,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
    access_token_cookie: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> None:
    """Verify Double-Submit CSRF token on cookie-authenticated mutative state operations.

    Exemptions:
    - Safe HTTP methods (GET, HEAD, OPTIONS).
    - Mobile clients using Authorization: Bearer <token> without ambient browser cookies.
    """
    # 1. Safe methods do not mutate state
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    # 2. Check for genuinely authenticated Bearer credentials
    # Bearer-token exemption requires a genuinely valid, unexpired token signed by our SECRET_KEY,
    # preventing any dummy/invalid Authorization header from bypassing CSRF verification.
    is_authenticated_bearer = False
    bearer_payload: dict[str, Any] | None = None
    if auth_header and auth_header.credentials:
        try:
            bearer_payload = decode_access_token(auth_header.credentials)
            is_authenticated_bearer = True
        except (TokenExpiredException, InvalidTokenException):
            is_authenticated_bearer = False

    # 3. Check if ambient browser cookies are present
    has_cookies = bool(refresh_token_cookie or access_token_cookie or csrf_token_cookie)

    # 4. Genuinely authenticated Bearer requests (e.g. mobile clients, programmatic API calls)
    # that do not use cookie authentication are exempt from CSRF
    if is_authenticated_bearer and not access_token_cookie:
        return

    # 5. If request has no cookies at all and no valid bearer token, it cannot mutate protected state
    if not has_cookies:
        return

    # 5. Cookie-authenticated request requires strict CSRF validation:
    # A. Origin / Referer validation if present
    origin = request.headers.get("origin")
    if origin and origin not in settings.BACKEND_CORS_ORIGINS:
        raise CSRFValidationException("Origin not permitted.")

    referer = request.headers.get("referer")
    if referer and not any(referer.startswith(allowed) for allowed in settings.BACKEND_CORS_ORIGINS):
        raise CSRFValidationException("Referer origin not permitted.")

    # B. Enforce presence and non-emptiness of X-CSRF-Token
    if not x_csrf_token or not x_csrf_token.strip():
        raise CSRFValidationException(
            "X-CSRF-Token header missing on cookie-authenticated request."
        )

    clean_header_token = x_csrf_token.strip()

    # C. Validate double-submit cookie comparison if csrf_token cookie is present
    if csrf_token_cookie:
        clean_cookie_token = csrf_token_cookie.strip()
        if not hmac.compare_digest(clean_header_token, clean_cookie_token):
            raise CSRFValidationException(
                "CSRF token mismatch between header and cookie."
            )

    # D. Cryptographic verification & session binding
    payload = bearer_payload
    if not payload and access_token_cookie:
        try:
            payload = decode_access_token(access_token_cookie)
        except (TokenExpiredException, InvalidTokenException):
            raise CSRFValidationException(
                "CSRF token validation failed: authentication token expired or invalid."
            )

    if payload:
        session_id = payload.get("session_id")
        if session_id:
            if not verify_csrf_token(clean_header_token, session_id):
                raise CSRFValidationException(
                    "CSRF token cryptographic signature invalid or expired."
                )
    else:
        # If no access token is available (e.g. only refresh_token_cookie provided),
        # verify token structure at minimum
        if "." not in clean_header_token:
            raise CSRFValidationException("CSRF token format invalid.")


def set_auth_cookies(
    response: Response,
    refresh_token: str,
    csrf_token: str,
) -> None:
    """Set secure HttpOnly refresh token and readable CSRF cookies according to topology policy."""
    domain = settings.COOKIE_DOMAIN if settings.COOKIE_DOMAIN else None

    # Refresh Token: HttpOnly, Secure (per env), SameSite
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=domain,
        path=settings.COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    # CSRF Token: Readable by JS, SameSite
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=domain,
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear refresh token and CSRF cookies upon logout."""
    domain = settings.COOKIE_DOMAIN if settings.COOKIE_DOMAIN else None

    response.delete_cookie(
        key="refresh_token",
        domain=domain,
        path=settings.COOKIE_PATH,
    )
    response.delete_cookie(
        key="csrf_token",
        domain=domain,
        path="/",
    )
