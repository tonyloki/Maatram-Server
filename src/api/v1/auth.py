"""Authentication & Session endpoints."""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import (
    clear_auth_cookies,
    get_current_session,
    get_current_user,
    get_db,
    set_auth_cookies,
    verify_csrf,
)
from src.core.config import settings
from src.core.exceptions import RateLimitExceededException
from src.core.rate_limiter import pg_rate_limiter, rate_limiter
from src.models.users import User, UserSession
from src.schemas.auth import (
    LoginRequest,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from src.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication & Sessions"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
    summary="Volunteer registration with multi-stage profile submission",
)
async def register(
    request: Request,
    data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RegisterResponse:
    """Register a new volunteer account with base profile, classification, and privacy selections."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Rate limiting: 10 registrations per hour per IP
    if client_ip:
        if settings.USE_DB_RATE_LIMITER:
            allowed = await pg_rate_limiter.check_and_increment(
                db=db,
                identifier=client_ip,
                endpoint_key="register",
                max_attempts=10,
                window_seconds=3600,
            )
            if not allowed:
                raise RateLimitExceededException(
                    message="Too many registration attempts. Please try again later."
                )
        else:
            await rate_limiter.check_rate_limit(
                key=f"register:{client_ip}",
                max_requests=10,
                window_seconds=3600,
                error_message="Too many registration attempts. Please try again later.",
            )

    return await auth_service.register(
        db=db,
        request=data,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Authenticate credentials and issue access/refresh tokens",
)
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Authenticate user with Argon2id, create server-side session, and issue dual tokens."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Rate limiting: 30 attempts per IP, 20 attempts per account per 15 minutes
    if settings.USE_DB_RATE_LIMITER:
        if client_ip:
            allowed_ip = await pg_rate_limiter.check_and_increment(
                db=db,
                identifier=client_ip,
                endpoint_key="login_ip",
                max_attempts=30,
                window_seconds=900,
            )
            if not allowed_ip:
                raise RateLimitExceededException(
                    message="Too many login attempts from this IP address."
                )
        allowed_acct = await pg_rate_limiter.check_and_increment(
            db=db,
            identifier=data.email.strip().lower(),
            endpoint_key="login_account",
            max_attempts=20,
            window_seconds=900,
        )
        if not allowed_acct:
            raise RateLimitExceededException(message="Too many login attempts for this account.")
    else:
        if client_ip:
            await rate_limiter.check_rate_limit(
                key=f"login:{client_ip}",
                max_requests=30,
                window_seconds=900,
                error_message="Too many login attempts. Please try again later.",
            )

    token_response, raw_refresh_token, csrf_token = await auth_service.login(
        db=db,
        request=data,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    # Set secure HttpOnly cookies for Web clients
    if data.client_type == "WEB":
        set_auth_cookies(
            response=response,
            refresh_token=raw_refresh_token,
            csrf_token=csrf_token,
        )

    return token_response


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Rotate refresh token and issue new token pair",
)
async def refresh_token(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    data: RefreshRequest | None = None,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> TokenResponse:
    """Rotate refresh token. Detects token reuse (theft) and invalidates session lineage."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Extract presented token from body or cookie
    presented_token = (
        data.refresh_token if data and data.refresh_token else None
    ) or refresh_token_cookie

    token_response, new_refresh_token, new_csrf_token = await auth_service.refresh_token(
        db=db,
        presented_token=presented_token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    # Update cookies if client had cookie or presented as web
    if refresh_token_cookie or (data and not data.refresh_token):
        set_auth_cookies(
            response=response,
            refresh_token=new_refresh_token,
            csrf_token=new_csrf_token,
        )

    return token_response


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Revoke current session and clear authentication cookies",
    dependencies=[Depends(verify_csrf)],
)
async def logout(
    request: Request,
    response: Response,
    session_and_payload: Annotated[
        tuple[UserSession, dict[str, str]], Depends(get_current_session)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Revoke active server-side session and clear client cookies."""
    session, _ = session_and_payload
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    clear_auth_cookies(response)
    return await auth_service.logout(
        db=db,
        session_id=session.id,
        user_id=current_user.id,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Revoke all active sessions across all devices",
    dependencies=[Depends(verify_csrf)],
)
async def logout_all(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Revoke all sessions for current user across mobile and web clients."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    clear_auth_cookies(response)
    return await auth_service.logout_all(
        db=db,
        user_id=current_user.id,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    response_model=VerifyEmailResponse,
    summary="Confirm email address using verification token",
)
async def verify_email(
    request: Request,
    data: VerifyEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VerifyEmailResponse:
    """Confirm email ownership with one-time verification token."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await auth_service.verify_email(
        db=db,
        token=data.token,
        email=data.email,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Request 6-digit numeric password reset OTP",
)
async def password_reset_request(
    request: Request,
    data: PasswordResetRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Request password reset OTP sent via transactional email outbox."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await auth_service.request_password_reset(
        db=db,
        email=data.email,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/password-reset/confirm",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Confirm OTP and reset account password",
)
async def password_reset_confirm(
    request: Request,
    data: PasswordResetConfirmRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Validate numeric OTP, update password, and invalidate existing sessions."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await auth_service.confirm_password_reset(
        db=db,
        email=data.email,
        otp=data.otp,
        new_password=data.new_password,
        client_ip=client_ip,
        user_agent=user_agent,
    )
