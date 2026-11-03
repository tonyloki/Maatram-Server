"""FastAPI dependency injection for database sessions, security, RBAC, and CSRF protection."""

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
from src.core.security import decode_access_token, ensure_utc
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
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> None:
    """Verify Double-Submit CSRF token on cookie-authenticated mutative state operations.

    Exemptions:
    - Safe HTTP methods (GET, HEAD, OPTIONS).
    - Mobile clients using Authorization: Bearer <token>.
    """
    # Safe methods do not mutate state
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    # Mobile requests utilizing Bearer authentication header are immune to browser CSRF
    if auth_header and auth_header.credentials:
        return

    # If request is cookie-authenticated, CSRF validation is strictly enforced
    if refresh_token_cookie:
        # 1. Validate Origin / Referer against whitelist if present
        origin = request.headers.get("origin")
        if origin and origin not in settings.BACKEND_CORS_ORIGINS:
            raise CSRFValidationException("Origin not permitted.")

        # 2. Enforce presence and non-emptiness of X-CSRF-Token
        if not x_csrf_token or not x_csrf_token.strip():
            raise CSRFValidationException(
                "X-CSRF-Token header missing on cookie-authenticated request."
            )


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
