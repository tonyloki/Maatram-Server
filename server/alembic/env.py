"""Alembic environment script configured for asynchronous SQLAlchemy with safety guards."""

import asyncio
import os
import re
from logging.config import fileConfig
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from alembic.runtime.migration import MigrationStep
from src.core.config import settings
from src.models import Base

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support (all 29 domain tables)
target_metadata = Base.metadata


def get_target_schema() -> str:
    """Return target database schema, defaulting to 'public'."""
    x_args = context.get_x_argument(as_dictionary=True)
    schema = x_args.get("schema") or os.getenv("ALEMBIC_SCHEMA") or "public"
    # Basic identifier sanitization
    if not re.match(r"^[a-zA-Z0-9_]+$", schema):
        raise ValueError(f"Invalid schema name: {schema}")
    return schema


def get_migration_url() -> str:
    """Return database URL for migrations (prefers direct port 5432 connection if provided)."""
    if settings.DIRECT_URL:
        return settings.DIRECT_URL
    return settings.DATABASE_URL


def validate_destructive_operation(target_schema: str, is_downgrade: bool) -> None:
    """Strict safeguard preventing destructive downgrade/reset on production or shared databases."""
    if not is_downgrade:
        return

    url = get_migration_url().lower()
    env = settings.ENVIRONMENT.lower()

    # Rule 1: Never allow downgrade on production or staging environments
    if env in ("production", "staging"):
        raise RuntimeError(
            f"CRITICAL MIGRATION SAFETY VIOLATION: Destructive downgrade migrations are "
            f"strictly prohibited in '{env}' environment!"
        )

    # Rule 2: Never allow downgrade on public schema of cloud-hosted/shared databases (Supabase)
    is_supabase = "supabase.com" in url or "supabase.co" in url or "pooler.supabase.com" in url
    if is_supabase and target_schema == "public":
        raise RuntimeError(
            "CRITICAL MIGRATION SAFETY VIOLATION: Destructive downgrade migrations against "
            "the 'public' schema of the shared Supabase database are strictly forbidden to "
            "protect data integrity. Downgrade tests must execute only in an isolated, "
            "disposable sandbox schema (e.g. test_migration_sandbox) with "
            "ALLOW_DESTRUCTIVE_MIGRATION=true."
        )

    # Rule 3: For any downgrade, require explicit ALLOW_DESTRUCTIVE_MIGRATION=true
    allow_destructive = os.getenv("ALLOW_DESTRUCTIVE_MIGRATION", "").lower()
    if allow_destructive != "true":
        raise RuntimeError(
            "MIGRATION SAFETY SAFEGUARD: Destructive downgrade migration blocked. "
            "If running within an isolated, disposable test database or schema, set "
            "ALLOW_DESTRUCTIVE_MIGRATION=true to confirm execution."
        )


def _install_migration_safety_interceptor(schema: str) -> None:
    """Intercept migrations before execution to enforce safety policies."""
    migration_context = context.get_context()
    original_fn = migration_context._migrations_fn
    if original_fn:
        def safe_migrations_fn(heads, mig_context):
            steps = list(original_fn(heads, mig_context))
            for step in steps:
                if getattr(step, "is_downgrade", False):
                    validate_destructive_operation(schema, is_downgrade=True)
                yield step
        migration_context._migrations_fn = safe_migrations_fn


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode emitting SQL statements."""
    url = get_migration_url()
    schema = get_target_schema()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        version_table_schema=schema if schema != "public" else None,
    )

    _install_migration_safety_interceptor(schema)

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations on the synchronous connection wrapper."""
    schema = get_target_schema()
    if schema != "public":
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        connection.execute(text(f'SET search_path TO "{schema}"'))

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        version_table_schema=schema if schema != "public" else None,
    )

    _install_migration_safety_interceptor(schema)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and run migrations online."""
    url = get_migration_url()
    schema = get_target_schema()
    connect_args = {}
    if "postgresql" in url:
        connect_args["statement_cache_size"] = 0

    # If targeting a non-public isolated schema, ensure schema exists first and bind search_path
    if schema != "public":
        bootstrap_engine = create_async_engine(
            url,
            poolclass=pool.NullPool,
            connect_args=connect_args.copy(),
        )
        async with bootstrap_engine.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        await bootstrap_engine.dispose()
        connect_args["server_settings"] = {"search_path": f'"{schema}"'}

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

