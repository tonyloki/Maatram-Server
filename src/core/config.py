"""Application configuration module using Pydantic Settings."""

from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str]:
    """Parse CORS origins from a comma-separated string, JSON list, or list."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list):
        return [str(i) for i in v]
    import json

    if isinstance(v, str):
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return [str(i) for i in parsed]
        except Exception:
            pass
    return ["http://localhost:3000", "http://localhost:8000"]


def parse_bool(v: Any) -> bool:
    """Parse boolean safely even if host environment contains arbitrary strings like 'release'."""
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "t", "yes", "debug")
    return bool(v)


class Settings(BaseSettings):
    """Core application settings with environment variable bindings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # General
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: Annotated[bool, BeforeValidator(parse_bool)] = False
    PROJECT_NAME: str = "Maatram Volunteering & Gamification Portal"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(
        default="development-insecure-secret-key-change-in-production-min-32-chars",
        description="Master secret key for token signing and cryptographic operations",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OTP_EXPIRE_MINUTES: int = 15
    MAX_OTP_ATTEMPTS: int = 5
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15
    USE_DB_RATE_LIMITER: bool = True

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./test.db",
        description="PostgreSQL async connection string (asyncpg)",
    )
    DIRECT_URL: str | None = Field(
        default=None,
        description="Direct session connection string for migrations/DDL",
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 300

    # CORS & Cookies
    BACKEND_CORS_ORIGINS: Annotated[list[str], BeforeValidator(parse_cors)] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    COOKIE_DOMAIN: str | None = None
    COOKIE_PATH: str = "/api/v1/auth"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # Configurable Business Policies (Pending Maatram Approval)
    LEADERBOARD_CYCLE_TYPE: Literal["CALENDAR_YEAR", "FINANCIAL_YEAR", "ACADEMIC_YEAR"] = (
        "CALENDAR_YEAR"
    )
    HOURS_ROUNDING_MODE: Literal["EXACT_DECIMAL_2", "NEAREST_15_MIN", "FLOOR_HALF_HOUR"] = (
        "EXACT_DECIMAL_2"
    )
    EVENT_QUALIFICATION_MIN_MINUTES: int = 60
    INACTIVE_VOLUNTEER_DAYS_THRESHOLD: int = 180
    REGISTRATION_WITHDRAWAL_DEADLINE_HOURS_PRIOR: int = 24
    WAITLIST_PROMOTION_MODE: Literal["MANUAL", "FIFO_AUTOMATIC", "HYBRID"] = "MANUAL"
    APPLICATION_RESUBMISSION_ALLOWED: bool = True
    RESUBMISSION_COOLDOWN_DAYS: int = 0
    CORRECTION_SUPER_ADMIN_THRESHOLD_MINUTES: int = 120
    MINIMUM_VOLUNTEER_AGE: int | None = None
    DEFAULT_EVENT_TIMEZONE: str = "Asia/Kolkata"
    EVENT_OVERBOOKING_PERCENTAGE: float = 0.0

    # Outbox Settings
    OUTBOX_MAX_RETRIES: int = 3
    OUTBOX_LEASE_TIMEOUT_SECONDS: int = 300

    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME: str = "maatram"
    CLOUDINARY_API_KEY: str = "test-cloudinary-key"
    CLOUDINARY_API_SECRET: str = "test-cloudinary-secret"
    CLOUDINARY_MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Resend & Email Settings
    RESEND_API_KEY: str = "re_test_key"
    RESEND_FROM_EMAIL: str = "noreply@maatram.org"

    # Firebase FCM Settings
    FIREBASE_CREDENTIALS_PATH: str | None = None

    # Reporting Settings
    REPORT_EXPORT_EXPIRE_DAYS: int = 7


settings = Settings()
