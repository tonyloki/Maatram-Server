"""Isolated migration lifecycle verification script.

Tests fresh upgrade head, downgrade base, and re-upgrade strictly inside
a disposable, isolated PostgreSQL schema (`test_migration_sandbox`)
without affecting the canonical 'public' schema.
"""

import asyncio
import os
import subprocess
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings

ISOLATED_SCHEMA = "test_migration_sandbox"


async def get_tables_in_schema(engine, schema: str) -> list[str]:
    """Retrieve list of table names in the given schema."""
    async with engine.connect() as conn:
        res = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = :schema AND table_type = 'BASE TABLE' "
                "ORDER BY table_name"
            ),
            {"schema": schema},
        )
        return [row[0] for row in res.fetchall()]


def run_alembic_command(cmd_name: str, revision: str, schema: str):
    """Run alembic command targeted to an isolated schema in a subprocess."""
    env = os.environ.copy()
    env["ALEMBIC_SCHEMA"] = schema
    env["ALLOW_DESTRUCTIVE_MIGRATION"] = "true"

    cmd = [
        sys.executable,
        "-m",
        "alembic",
        "-x",
        f"schema={schema}",
        cmd_name,
        revision,
    ]
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    print(f"    alembic {cmd_name} {revision} stdout: {res.stdout.strip()}")
    print(f"    alembic {cmd_name} {revision} stderr: {res.stderr.strip()}")
    if res.returncode != 0:
        raise RuntimeError(f"Alembic {cmd_name} {revision} failed with exit code {res.returncode}")


async def main():
    print("=== ISOLATED MIGRATION LIFECYCLE TEST ===")
    print(f"Direct URL: {settings.DIRECT_URL.split('@')[-1] if settings.DIRECT_URL else 'None'}")
    print(f"Target Isolated Schema: {ISOLATED_SCHEMA}")

    engine = create_async_engine(
        settings.DIRECT_URL or settings.DATABASE_URL,
        connect_args={"statement_cache_size": 0},
    )

    # 1. Inspect public schema before starting
    public_tables_before = await get_tables_in_schema(engine, "public")
    print(f"[1] Public schema table count before test: {len(public_tables_before)}")
    assert len(public_tables_before) >= 29, "Public schema must contain baseline tables"

    # 2. Setup isolated schema
    async with engine.begin() as conn:
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{ISOLATED_SCHEMA}" CASCADE'))
        await conn.execute(text(f'CREATE SCHEMA "{ISOLATED_SCHEMA}"'))
    print(f"[2] Created isolated schema '{ISOLATED_SCHEMA}'")

    try:
        # 3. Test upgrade head in isolated schema
        print(f"[3] Running 'alembic upgrade head' into '{ISOLATED_SCHEMA}'...")
        run_alembic_command("upgrade", "head", ISOLATED_SCHEMA)
        tables_after_upgrade = await get_tables_in_schema(engine, ISOLATED_SCHEMA)
        print(f"    Tables in '{ISOLATED_SCHEMA}' after upgrade: {len(tables_after_upgrade)}")
        assert "alembic_version" in tables_after_upgrade, (
            "alembic_version table missing in isolated schema"
        )
        domain_tables = [t for t in tables_after_upgrade if t != "alembic_version"]
        assert len(domain_tables) == 29, (
            f"Expected 29 domain tables, got {len(domain_tables)}: {domain_tables}"
        )
        print(f"    SUCCESS: All 29 tables verified in '{ISOLATED_SCHEMA}'")

        # 4. Verify public schema was NOT touched during isolated upgrade
        public_tables_during = await get_tables_in_schema(engine, "public")
        assert public_tables_before == public_tables_during, "CRITICAL: Public schema was modified!"
        print("    Verified public schema untouched during upgrade.")

        # 5. Test downgrade base in isolated schema
        print(f"[4] Running 'alembic downgrade base' in '{ISOLATED_SCHEMA}'...")
        run_alembic_command("downgrade", "base", ISOLATED_SCHEMA)
        tables_after_downgrade = await get_tables_in_schema(engine, ISOLATED_SCHEMA)
        print(f"    Tables in '{ISOLATED_SCHEMA}' after downgrade: {tables_after_downgrade}")
        domain_tables_after_down = [t for t in tables_after_downgrade if t != "alembic_version"]
        assert len(domain_tables_after_down) == 0, (
            f"Expected 0 domain tables after downgrade, got: {domain_tables_after_down}"
        )
        print(f"    SUCCESS: Clean downgrade verified in '{ISOLATED_SCHEMA}'")

        # 6. Verify public schema was NOT touched during isolated downgrade
        public_tables_after_down = await get_tables_in_schema(engine, "public")
        assert public_tables_before == public_tables_after_down, (
            "CRITICAL: Public schema was modified during downgrade!"
        )
        print("    Verified public schema untouched during downgrade.")

        # 7. Test re-upgrade head in isolated schema
        print(f"[5] Running re-upgrade 'alembic upgrade head' in '{ISOLATED_SCHEMA}'...")
        run_alembic_command("upgrade", "head", ISOLATED_SCHEMA)
        tables_after_reupgrade = await get_tables_in_schema(engine, ISOLATED_SCHEMA)
        domain_tables_reup = [t for t in tables_after_reupgrade if t != "alembic_version"]
        assert len(domain_tables_reup) == 29, (
            f"Expected 29 domain tables after reupgrade, got: {len(domain_tables_reup)}"
        )
        print(
            f"    SUCCESS: Clean re-upgrade verified in '{ISOLATED_SCHEMA}' ({len(domain_tables_reup)} tables)"
        )

        # 8. Verify public schema was NOT touched during isolated re-upgrade
        public_tables_final = await get_tables_in_schema(engine, "public")
        assert public_tables_before == public_tables_final, (
            "CRITICAL: Public schema was modified during re-upgrade!"
        )
        print("    Verified public schema untouched during re-upgrade.")

    finally:
        # 9. Clean up isolated schema
        print(f"[6] Cleaning up isolated schema '{ISOLATED_SCHEMA}'...")
        async with engine.begin() as conn:
            await conn.execute(text(f'DROP SCHEMA IF EXISTS "{ISOLATED_SCHEMA}" CASCADE'))
        print(f"    Schema '{ISOLATED_SCHEMA}' dropped successfully.")
        await engine.dispose()

    print("=== ALL ISOLATED MIGRATION TESTS PASSED PERFECTLY ===")


if __name__ == "__main__":
    asyncio.run(main())
