"""Pytest global configuration and fixtures."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database import get_db
from src.core.rate_limiter import rate_limiter
from src.main import app
from src.models import Base

# Shared in-memory SQLite database across connections via cache=shared URI
TEST_DATABASE_URL = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

_schema_initialized = False


@pytest_asyncio.fixture(autouse=True)
async def clean_database() -> AsyncGenerator[None]:
    """Ensure schema is initialized and tables are truncated between tests."""
    global _schema_initialized
    if not _schema_initialized:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _schema_initialized = True

    await rate_limiter.reset()
    yield

    # Clean tables after test
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def async_db() -> AsyncGenerator[AsyncSession]:
    """Provide isolated async database session for test setup."""
    async with TestingSessionLocal() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Provide asynchronous HTTP test client with database dependency override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
