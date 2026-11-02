"""Custom domain exceptions and centralized global error handlers."""

from datetime import UTC, datetime
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.logging import logger


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_SERVER_ERROR",
        details: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class DomainException(AppException):
    """Domain rule violation exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "BAD_REQUEST",
        details: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=status_code, code=code, details=details)


class NotFoundException(DomainException):
    """Resource not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message, status_code=status.HTTP_404_NOT_FOUND, code=code, details=details
        )


class ConflictException(DomainException):
    """Resource conflict or duplicate constraint violation."""

    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message, status_code=status.HTTP_409_CONFLICT, code=code, details=details
        )


class UnauthorizedException(DomainException):
    """Authentication required or failed."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "UNAUTHORIZED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED, code=code, details=details
        )


class ForbiddenException(DomainException):
    """Authorization permission denied."""

    def __init__(
        self,
        message: str = "Permission denied",
        code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message, status_code=status.HTTP_403_FORBIDDEN, code=code, details=details
        )


# Phase 3 Specific Authentication & Authorization Exceptions
class InvalidCredentialsException(UnauthorizedException):
    """Bad email or password."""

    def __init__(
        self,
        message: str = "Invalid email or password.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="INVALID_CREDENTIALS", details=details)


class TokenExpiredException(UnauthorizedException):
    """Token expiration."""

    def __init__(
        self,
        message: str = "Token has expired.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="TOKEN_EXPIRED", details=details)


class InvalidTokenException(UnauthorizedException):
    """Malformed or invalid token."""

    def __init__(
        self,
        message: str = "Invalid authentication token.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="INVALID_TOKEN", details=details)


class TokenReuseDetectedException(UnauthorizedException):
    """Token theft detected; session lineage revoked."""

    def __init__(
        self,
        message: str = "Potential token theft detected. Session revoked.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="TOKEN_REUSE_DETECTED", details=details)


class SessionRevokedException(UnauthorizedException):
    """Session has been explicitly revoked or invalidated."""

    def __init__(
        self,
        message: str = "Session has been revoked.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="SESSION_REVOKED", details=details)


class AccountSuspendedException(ForbiddenException):
    """Account has been administratively suspended."""

    def __init__(
        self,
        message: str = "Account is suspended.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="ACCOUNT_SUSPENDED", details=details)


class AccountLockedException(ForbiddenException):
    """Account temporarily locked due to repeated failed login attempts."""

    def __init__(
        self,
        message: str = "Account is temporarily locked due to multiple failed login attempts. Please try again later.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="ACCOUNT_LOCKED", details=details)


class EmailAlreadyExistsException(ConflictException):
    """Email already registered."""

    def __init__(
        self,
        message: str = "Email is already registered.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="EMAIL_ALREADY_EXISTS", details=details)


class MobileAlreadyExistsException(ConflictException):
    """Mobile number already registered."""

    def __init__(
        self,
        message: str = "Mobile number is already registered.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="MOBILE_ALREADY_EXISTS", details=details)


class CSRFValidationException(ForbiddenException):
    """Double-submit CSRF verification failed."""

    def __init__(
        self,
        message: str = "CSRF token validation failed.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="CSRF_VALIDATION_FAILED", details=details)


class RateLimitExceededException(DomainException):
    """Rate limit threshold exceeded."""

    def __init__(
        self,
        message: str = "Too many requests. Please try again later.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handle custom application and domain exceptions with canonical envelope."""
    logger.warning(
        f"DomainException [{exc.code}] on {request.method} {request.url.path}: {exc.message}"
    )
    now_iso = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": now_iso,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Format Pydantic schema validation errors into standard error schema."""
    logger.info(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    formatted_errors = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", []))
        formatted_errors.append(
            {
                "field": loc,
                "message": err.get("msg", "Validation error"),
                "type": err.get("type", "value_error"),
            }
        )

    now_iso = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Input validation failed",
            "details": formatted_errors,
            "timestamp": now_iso,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": formatted_errors,
            },
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all unhandled server error handler."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    now_iso = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
            "details": {},
            "timestamp": now_iso,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
                "details": {},
            },
        },
    )
