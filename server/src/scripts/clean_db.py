import asyncio
import uuid
from sqlalchemy import text
from src.core.database import AsyncSessionLocal

ADMIN_ID = uuid.UUID("74fc0b98-9075-486c-9bca-c689f189d805")

async def clean_database():
    print(f"Preserving Admin User ID: {ADMIN_ID}")
    
    tables_to_truncate = [
        "audit_logs",
        "rate_limit_attempts",
        "attendance_corrections",
        "attendance_records",
        "point_transactions",
        "volunteer_achievements",
        "event_photos",
        "registration_history",
        "event_registrations",
        "events",
        "media_assets",
        "notifications",
        "communication_logs",
        "communication_jobs",
        "report_exports",
        "application_reviews",
        "student_profiles",
        "alumni_profiles",
        "corporate_profiles",
        "consent_history",
        "consent_records",
        "volunteer_applications",
        "volunteer_profiles",
        "user_sessions",
        "email_verifications",
        "password_reset_tokens",
        "device_tokens",
        "admin_permissions",
    ]

    async with AsyncSessionLocal() as session:
        # First verify admin exists
        res = await session.execute(
            text("SELECT id, email, role FROM users WHERE id = :admin_id"),
            {"admin_id": ADMIN_ID}
        )
        admin = res.fetchone()
        if not admin:
            raise RuntimeError(f"Admin with ID {ADMIN_ID} not found in database! Aborting.")
        print(f"Confirmed admin: {admin.email} ({admin.role})")

        # Truncate all child/data tables
        for tbl in tables_to_truncate:
            print(f"Clearing table: {tbl}...")
            await session.execute(text(f'TRUNCATE TABLE "{tbl}" CASCADE'))

        # Delete all other users except the admin
        print("Clearing all non-admin users...")
        del_res = await session.execute(
            text("DELETE FROM users WHERE id != :admin_id"),
            {"admin_id": ADMIN_ID}
        )
        print(f"Deleted {del_res.rowcount} non-admin users.")

        # Reset admin account state
        await session.execute(
            text("""
                UPDATE users 
                SET failed_login_attempts = 0, 
                    locked_until = NULL, 
                    is_active = TRUE, 
                    status = 'APPROVED'
                WHERE id = :admin_id
            """),
            {"admin_id": ADMIN_ID}
        )

        await session.commit()
        print("Database cleanup committed successfully!\n")

        # Verification of counts
        print("=== Final Verification Table Counts ===")
        tables_res = await session.execute(text("""
            SELECT tablename FROM pg_tables WHERE schemaname = 'public'
        """))
        all_tables = [r[0] for r in tables_res.fetchall()]
        for t in sorted(all_tables):
            c_res = await session.execute(text(f'SELECT COUNT(*) FROM "{t}"'))
            count = c_res.scalar()
            print(f"  {t}: {count}")

        # Final check on users
        user_res = await session.execute(text("SELECT id, email, role, status, is_active FROM users"))
        remaining_users = user_res.fetchall()
        print("\n=== Remaining Users ===")
        for u in remaining_users:
            print(dict(u._mapping))

if __name__ == "__main__":
    asyncio.run(clean_database())
