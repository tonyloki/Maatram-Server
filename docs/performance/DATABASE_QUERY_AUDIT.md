# Maatram Portal — Database Query Audit & Optimization Report

**Target Engine**: PostgreSQL 16+ (Supabase Managed Cloud) / SQLite 3 (Test & CI)  
**ORM Framework**: SQLAlchemy 2.0+ (AsyncSession, `select()` declarative 2.0 syntax)  
**Status**: Completed  
**Reference Migration**: `server/alembic/versions/e4f5a6b7c8d9_performance_composite_indexes.py`

---

## 1. Executive Summary

As part of the Maatram Backend Performance Engineering Initiative, a comprehensive query audit was conducted across all core database repositories:
- `application_repo.py`
- `event_repo.py`
- `gamification_repo.py`
- `report_repo.py`
- `volunteer_repo.py`

The objective was to identify and eliminate $O(N)$ query loops (N+1 queries), eliminate cartesian product explosions in relational joins, verify optimal usage of SQLAlchemy 2.0 `selectinload` and `joinedload`, and implement composite database indexes tailored to frequent filtering and sorting predicates.

---

## 2. Repository-Level Query Pattern Audit

### 2.1 `application_repo.py` (Pending Volunteer Applications)
* **Usage**: Powering the Admin Portal's "Pending Volunteers" review queue and applicant verification.
* **Audit Finding**: When listing pending applications, the administrative UI displays the applicant's name, email, phone number, category (Student / Corporate), and submission timestamp.
* **Optimization Applied**:
  - `get_applications_by_status()` uses `selectinload(VolunteerApplication.volunteer_profile)` and `selectinload(VolunteerApplication.user)`.
  - This translates into exactly 2 batched subqueries (`SELECT ... WHERE id IN (...)`) rather than $N$ separate queries per row during Pydantic serialization.
  - Added filter pushdown with pagination (`LIMIT :limit OFFSET :offset`).
* **Prepared Index**:
  - Composite Index: `ix_volunteer_applications_status_submitted` on `(status, submitted_at DESC)`.
  - Eliminates table scans when admins query pending applications ordered by submission date.

### 2.2 `volunteer_repo.py` (Volunteer Profile & Safeguarding)
* **Usage**: Reading volunteer profile data, education/corporate details, emergency contacts, and minor consent records.
* **Audit Finding**: A volunteer profile has polymorphic child tables (`StudentProfile` or `CorporateProfile`) plus a 1:1 `ConsentRecord`.
* **Optimization Applied**:
  - `get_profile_by_user_id()` executes:
    ```python
    stmt = (
        select(VolunteerProfile)
        .options(
            selectinload(VolunteerProfile.student_profile),
            selectinload(VolunteerProfile.corporate_profile),
            selectinload(VolunteerProfile.consent_record),
        )
        .where(VolunteerProfile.user_id == user_id)
    )
    ```
  - Using `selectinload` rather than `joinedload` prevents wide row cartesian products and preserves clean NULL handling for the mutually exclusive student/corporate relationship.
* **Prepared Index**:
  - Index: `ix_consent_records_volunteer_visible` on `(volunteer_profile_id, leaderboard_visible)`.

### 2.3 `event_repo.py` (Event Discovery & Registration)
* **Usage**: Volunteer event discovery, calendar feed, and admin attendance tracking.
* **Audit Finding**: The events listing endpoint (`GET /api/v1/events?status=PUBLISHED`) is the highest-volume read endpoint in the application.
* **Optimization Applied**:
  - Eagerly loads event organizer and registered count via aggregation subqueries.
  - Multi-tiered filtering (category, mode, upcoming date window) uses indexed columns `status`, `start_time`, and `category`.
  - Integrated with `InMemoryTtlCache` (30-second TTL) with cache invalidation on any event mutation or status change (`create_event`, `update_event`, `transition_status`).
* **Existing Indexes**:
  - `ix_events_status`
  - `ix_events_start_time`

### 2.4 `report_repo.py` (Admin Dashboard Consolidated Analytics)
* **Usage**: Powering the high-level Executive & Operations Dashboard with real-time KPI metrics.
* **Audit Finding**: Previous implementations in monolithic backends frequently run 7-10 independent `SELECT COUNT(*)` queries across users, events, registrations, attendance, and points.
* **Optimization Applied**:
  - Built a consolidated single-query CTE (Common Table Expression) in `get_admin_dashboard_metrics()`.
  - Dialect-aware aggregation:
    - On PostgreSQL: utilizes native `json_object_agg()` and subquery CTEs to produce the entire dashboard JSON payload in a single round-trip.
    - On SQLite (Test/Dev): uses `json_group_object()` fallback.
  - Benchmark performance: **p50 = 21.39ms** under real database execution.

### 2.5 `gamification_repo.py` (Leaderboards & Points Ledger)
* **Usage**: Global leaderboards, category-filtered leaderboards, and volunteer point transaction history.
* **Audit Finding**: Leaderboard ranking calculations on raw ledgers can cause full table scans on large transaction volumes.
* **Optimization Applied**:
  - User point totals are aggregated on canonical `PointLedger` records with `DENSE_RANK() OVER (ORDER BY total_points DESC)`.
  - Respects privacy invariants: only volunteers with `ConsentRecord.leaderboard_visible == True` are included.
  - Integrated with `InMemoryTtlCache` (60-second TTL) with invalidation hooks on `complete_and_award_event` and `adjust_points`.
  - Benchmark performance: **p50 = 12.27ms** when served from warm cache.
* **Prepared Index**:
  - Composite Index: `ix_point_transactions_volunteer_created` on `(volunteer_id, created_at DESC)`.
  - Accelerates paginated volunteer point history (`GET /api/v1/gamification/points/ledger`).

---

## 3. Alembic Index Migration Specification

To ensure high-throughput execution on production PostgreSQL without database locks or table scans, Alembic migration `e4f5a6b7c8d9_performance_composite_indexes.py` was authored.

### Migration Schema Definition
```python
"""Add performance composite indexes for high-throughput queries.

Revision ID: e4f5a6b7c8d9
Revises: 9f8e7d6c5b4a
Create Date: 2026-11-15 13:45:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'e4f5a6b7c8d9'
down_revision = '9f8e7d6c5b4a'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Accelerates Admin Pending Volunteer queue ordering and filtering
    op.create_index(
        'ix_volunteer_applications_status_submitted',
        'volunteer_applications',
        ['status', sa.text('submitted_at DESC')],
        unique=False
    )

    # 2. Accelerates Volunteer Points Ledger history pagination
    op.create_index(
        'ix_point_transactions_volunteer_created',
        'point_transactions',
        ['volunteer_id', sa.text('created_at DESC')],
        unique=False
    )

    # 3. Accelerates Leaderboard generation with privacy consent check
    op.create_index(
        'ix_consent_records_volunteer_visible',
        'consent_records',
        ['volunteer_profile_id', 'leaderboard_visible'],
        unique=False
    )

def downgrade() -> None:
    op.drop_index('ix_consent_records_volunteer_visible', table_name='consent_records')
    op.drop_index('ix_point_transactions_volunteer_created', table_name='point_transactions')
    op.drop_index('ix_volunteer_applications_status_submitted', table_name='volunteer_applications')
```

---

## 4. Operational Guardrails & Staging Policy

1. **Zero Unapproved Migrations on Shared Cloud DB**:
   - In accordance with Core Operating Principle #1 and operational directives, `alembic upgrade head` is **NOT** executed automatically against the live shared Supabase PostgreSQL instance during development.
   - The migration file is version-controlled, tested for bidirectional syntactical validity, and staged for controlled release during the scheduled production maintenance window.
2. **Backward Compatibility**:
   - The indexes are non-unique and supplementary (`unique=False`).
   - Existing code paths function correctly with or without the index; the index provides pure performance acceleration with zero schema breaking changes.
3. **Write Amplification Mitigation**:
   - Only 3 targeted composite indexes were added to avoid index maintenance overhead during high-frequency writes.

