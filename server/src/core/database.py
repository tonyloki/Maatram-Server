"""SQLAlchemy 2.0+ asynchronous database configuration and session management."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings
from src.core.logging import logger


def get_engine_args(database_url: str) -> dict[str, Any]:
    """Build engine connection and pool arguments according to dialect and topology."""
    connect_args: dict[str, Any] = {}
    engine_kwargs: dict[str, Any] = {
        "echo": settings.DEBUG and settings.ENVIRONMENT == "development",
        "future": True,
    }

    if "sqlite" in database_url:
        connect_args["check_same_thread"] = False
        engine_kwargs["connect_args"] = connect_args
    else:
        # PostgreSQL / asyncpg configuration
        # Disable prepared statement caching when connecting via transaction-mode poolers (pgbouncer)
        connect_args["statement_cache_size"] = 0
        connect_args["command_timeout"] = 60

        engine_kwargs.update(
            {
                "connect_args": connect_args,
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "pool_recycle": settings.DB_POOL_RECYCLE,
                "pool_pre_ping": settings.DB_POOL_PRE_PING,
            }
        )

    return engine_kwargs


# Primary application async engine (runtime transaction pooler)
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **get_engine_args(settings.DATABASE_URL),
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency for obtaining an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db_connections() -> None:
    """Dispose engine connections cleanly on application shutdown."""
    logger.info("Closing database engine connections...")
    await engine.dispose()
    logger.info("Database connections closed.")
