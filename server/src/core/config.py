"""Application configuration module using Pydantic Settings."""

from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field, model_validator
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
    return ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]


def parse_bool(v: Any) -> bool:
    """Parse boolean safely even if host environment contains arbitrary strings like 'release'."""
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "t", "yes", "debug")
    return bool(v)


def parse_trusted_proxies(v: Any) -> list[str]:
    """Parse trusted proxy IP addresses and CIDR networks from string, JSON array, or list."""
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return []
        if v.startswith("["):
            import json

            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(i).strip() for i in parsed if str(i).strip()]
            except Exception:
                pass
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list):
        return [str(i).strip() for i in v if str(i).strip()]
    return []


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
    DB_POOL_PRE_PING: bool = True

    # CORS & Cookies
    BACKEND_CORS_ORIGINS: Annotated[list[str], BeforeValidator(parse_cors)] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
    ]
    COOKIE_DOMAIN: str | None = None
    COOKIE_PATH: str = "/api/v1/auth"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # Reverse Proxy & Client IP Extraction
    TRUSTED_PROXY_IPS: Annotated[list[str], BeforeValidator(parse_trusted_proxies)] = []
    TRUST_CLOUDFLARE_PROXIES: Annotated[bool, BeforeValidator(parse_bool)] = False
    CLOUDFLARE_PROXY_IPS: Annotated[list[str], BeforeValidator(parse_trusted_proxies)] = [
        "173.245.48.0/20",
        "103.21.244.0/22",
        "103.22.200.0/22",
        "103.31.4.0/22",
        "141.101.64.0/18",
        "108.162.192.0/18",
        "190.93.240.0/20",
        "188.114.96.0/20",
        "197.234.240.0/22",
        "198.41.128.0/17",
        "162.158.0.0/15",
        "104.16.0.0/13",
        "104.24.0.0/14",
        "172.64.0.0/13",
        "131.0.72.0/22",
        "2400:cb00::/32",
        "2606:4700::/32",
        "2803:f800::/32",
        "2405:b500::/32",
        "2405:8100::/32",
        "2a06:98c0::/29",
        "2c0f:f248::/32",
    ]

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Strictly prevent server startup with insecure configurations."""
        if self.COOKIE_SAMESITE == "none" and not self.COOKIE_SECURE:
            raise ValueError(
                "FATAL: COOKIE_SAMESITE='none' requires COOKIE_SECURE=True."
            )

        if self.ENVIRONMENT in ("staging", "production"):
            if self.DEBUG:
                raise ValueError("FATAL: DEBUG cannot be True in staging/production environments.")

            if not self.COOKIE_SECURE:
                raise ValueError(
                    "FATAL: COOKIE_SECURE cannot be False in staging/production environments."
                )

            insecure_secrets = {
                "dev-secret-key-change-in-production",
                "secret",
                "changeme",
                "test",
                "supersecret",
                "your-secret-key-here",
            }
            if self.SECRET_KEY in insecure_secrets or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "FATAL: Insecure or default SECRET_KEY in staging/production environment. "
                    "Must be a secure random secret of at least 32 characters."
                )

            if self.ENVIRONMENT == "production":
                for origin in self.BACKEND_CORS_ORIGINS:
                    if "*" in origin:
                        raise ValueError(
                            "FATAL: Wildcard CORS origin ('*') is strictly prohibited in production."
                        )
                    if "localhost" in origin.lower() or "127.0.0.1" in origin:
                        raise ValueError(
                            f"FATAL: Localhost origin '{origin}' is strictly prohibited in production. "
                            "Specify explicit production domains in BACKEND_CORS_ORIGINS."
                        )

        return self

    # Configurable Business Policies (Pending Maatram Approval)
    LEADERBOARD_CYCLE_TYPE: Literal["CALENDAR_YEAR", "FINANCIAL_YEAR", "ACADEMIC_YEAR"] = (
        "CALENDAR_YEAR"
    )
    HOURS_ROUNDING_MODE: Literal["EXACT_DECIMAL_2", "NEAREST_15_MIN", "FLOOR_HALF_HOUR"] = (
        "EXACT_DECIMAL_2"
    )
    EVENT_QUALIFICATION_MIN_MINUTES: int = 60
    # Inactivity threshold: Provisional technical default (180 days) pending formal Maatram governance ratification (Question 4 in OPEN_QUESTIONS.md).
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
