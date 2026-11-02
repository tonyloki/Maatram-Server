import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings


async def verify():
    target_url = settings.DIRECT_URL or settings.DATABASE_URL
    print(f"Connecting to: {target_url.split('@')[-1]}")
    engine = create_async_engine(target_url, connect_args={"statement_cache_size": 0})
    async with engine.connect() as conn:
        # 1. Query tables
        res = await conn.execute(
            text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE'
              AND table_name != 'alembic_version'
            ORDER BY table_name;
        """)
        )
        tables = [row[0] for row in res.fetchall()]
        print(f"=== Total User Tables in Supabase PostgreSQL: {len(tables)} ===")
        for i, t in enumerate(tables, 1):
            print(f"{i:2d}. {t}")
        assert len(tables) == 29, f"Expected 29 tables, found {len(tables)}"

        # 2. Query Triggers on point_transactions
        res_trg = await conn.execute(
            text("""
            SELECT trigger_name, event_manipulation, action_statement 
            FROM information_schema.triggers 
            WHERE event_object_table = 'point_transactions';
        """)
        )
        triggers = res_trg.fetchall()
        print(f"\n=== Triggers on point_transactions: {len(triggers)} ===")
        for trg in triggers:
            print(f"Trigger: {trg[0]}, Events: {trg[1]}")
        assert len(triggers) > 0, (
            "Expected trigger trg_prevent_point_ledger_mutation on point_transactions"
        )

        # 3. Check trigger function
        res_fn = await conn.execute(
            text("""
            SELECT proname FROM pg_proc WHERE proname = 'prevent_point_ledger_mutation';
        """)
        )
        fn = res_fn.scalar()
        print(f"Trigger function present: {fn}")
        assert fn == "prevent_point_ledger_mutation"

    await engine.dispose()
    print("\nALL 29 TABLES AND TRIGGERS VERIFIED ON SUPABASE POSTGRESQL!")


if __name__ == "__main__":
    asyncio.run(verify())
