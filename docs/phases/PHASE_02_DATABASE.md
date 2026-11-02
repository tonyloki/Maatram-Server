# PHASE 02 — Database Engineering & Alembic Migrations

## 1. Objective
Implement SQLAlchemy 2.x declarative models for all 29 database tables, configure Alembic for asynchronous migrations with `asyncpg`, implement database-level ledger trigger protections, and generate the baseline database migration.

## 2. Scope
- Base model declarations with UUID primary keys and UTC audit timestamps.
- Implementation of models across Identity, Volunteer Profiles, Applications, Privacy, Events, Registrations, Attendance, Gamification, Notifications, Communications, Media, Admin, and Reports modules.
- Point transactions precision: `NUMERIC(8, 2)` for `event_points`, `hour_points`, `total_points`, and `hours_credited`.
- Trigger implementation: `trg_prevent_point_ledger_mutation` preventing `UPDATE` and `DELETE` on `point_transactions`.
- Age sanity check constraint: `chk_volunteer_age_sanity` (`age > 0 AND age <= 120`), deferring minimum eligibility age to configurable policy.
- Outbox worker tracking columns: `locked_at TIMESTAMPTZ`, `worker_id VARCHAR(100)`, and `DEAD_LETTER` enum status in `communication_jobs`.
- Alembic configuration supporting async engine execution.
- Baseline migration script generation and execution against PostgreSQL.

## 3. Dependencies
- Phase 1 completed.

## 4. Implementation Tasks
1. Configure `alembic.ini` and `src/models/base.py`.
2. Implement declarative models in `src/models/`:
   - `users.py`, `sessions.py`, `tokens.py`
   - `volunteers.py` (base with age sanity check, student, alumni, corporate)
   - `applications.py`
   - `consent.py` (defaults to False for affirmative opt-in)
   - `events.py`
   - `registrations.py`
   - `attendance.py`
   - `gamification.py` (with `NUMERIC(8, 2)` precision for all point columns and related transaction pointers)
   - `notifications.py`
   - `communications.py` (with `locked_at`, `worker_id`, `DEAD_LETTER` state, idempotency key)
   - `media.py`
   - `admin.py`
   - `reports.py`
3. Configure `alembic/env.py` to import all models and support `run_migrations_online` using `asyncio`.
4. Include database-level trigger definition and runtime role privilege restrictions in the migration for `point_transactions`:
   ```sql
   CREATE OR REPLACE FUNCTION prevent_point_ledger_mutation()
   RETURNS TRIGGER AS $$
   BEGIN
       RAISE EXCEPTION 'Point transactions ledger is strictly append-only. UPDATE and DELETE operations are forbidden.';
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER trg_prevent_point_ledger_mutation
   BEFORE UPDATE OR DELETE ON point_transactions
   FOR EACH ROW EXECUTE FUNCTION prevent_point_ledger_mutation();

   -- Restrict application runtime role privileges
   -- (Schema owner remains maatram_migration_admin; application runs as maatram_app_user)
   GRANT SELECT, INSERT ON point_transactions TO maatram_app_user;
   REVOKE UPDATE, DELETE, TRUNCATE, TRIGGER ON point_transactions FROM maatram_app_user;
   ```
5. Generate baseline migration: `alembic revision --autogenerate -m "initial_schema_baseline"`.
6. Verify foreign key constraints, indexes, unique constraints, and check constraints match `DATABASE_DESIGN.md`.

## 5. Database Changes
Creation of all 29 tables via Alembic revision with trigger safeguards and least-privilege role permissions on `point_transactions`.

## 6. APIs
None.

## 7. Security Requirements
- Database connection strings with credentials must not be hardcoded in migration files.
- Foreign keys for historical volunteering records must use `ON DELETE RESTRICT`.
- Database role separation: The application runtime role (`maatram_app_user`) must not own `point_transactions` and must have `UPDATE`, `DELETE`, `TRUNCATE`, and `TRIGGER` revoked.

## 8. Test Requirements
- Test running `alembic upgrade head` on an empty database.
- Test running `alembic downgrade base` and ensuring all tables and triggers drop cleanly.
- Verify constraint violations (e.g., negative duration, invalid enum checks, ledger update attempts) raise database-level integrity errors.
- Verify role isolation test: Executing `UPDATE`, `DELETE`, `TRUNCATE`, or `ALTER TABLE ... DISABLE TRIGGER` under `maatram_app_user` raises permission denied errors.

## 9. Deliverables
- Complete SQLAlchemy 2.x model suite in `src/models/`.
- Alembic migration scripts in `alembic/versions/`.
- Database schema integration tests.

## 10. Acceptance Criteria
- `alembic upgrade head` executes without errors.
- All 29 tables, foreign keys, and indexes exist in PostgreSQL.
- Direct `UPDATE` or `DELETE` on `point_transactions` raises an engine exception.
- `TRUNCATE` or trigger modification attempts by `maatram_app_user` fail with permission denied.
- Downgrade script cleanly reverts schema without orphaned objects.

## 11. Definition of Done (DoD)
Database baseline migration confirmed on Supabase PostgreSQL; models exported and ready for repository consumption.
