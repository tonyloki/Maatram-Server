# PHASE 12 — Administration, Dashboard & Reporting APIs

## 1. Objective
Implement high-performance administrative reporting endpoints, real-time SQL-driven analytics aggregations, inactive volunteer detection, asynchronous CSV/Excel report exports, and outbox dead-letter queue management.

## 2. Scope
- Aggregate volunteer statistics across categories, genders, colleges, and employers.
- Real-time contribution hours queries partitioned by date ranges and event categories.
- Alumni participation consistency and employer contribution analytics.
- Inactive volunteer detection based on attendance recency (`INACTIVE_VOLUNTEER_DAYS_THRESHOLD` [POLICY: PENDING_APPROVAL]).
- Asynchronous CSV/Excel report export engine (`report_exports`).
- Outbox dead-letter queue inspection and administrative requeue (`communication_jobs`).
- Security and administrative audit log inspection (`audit_logs`).

## 3. Dependencies
- Phase 11 completed.

## 4. Implementation Tasks
1. Implement Pydantic 2 schemas in `schemas/reports.py` and `schemas/admin.py`.
2. Implement `ReportRepository` executing optimized SQL aggregations with indexes.
3. Implement `ReportService`:
   - `get_volunteer_stats`: Aggregates active/pending counts, category distribution, top colleges, top corporate employers.
   - `get_contribution_hours`: Calculates verified hours grouped by event category and month.
   - `get_inactive_volunteers`: Identifies volunteers with zero attendances in past $N$ days.
   - `trigger_report_export`: Enqueues CSV generation task into `report_exports`.
4. Build asynchronous CSV exporter writing formatted data files.
5. Implement Outbox Dead-Letter Admin Service:
   - `list_dead_letter_jobs`: Queries jobs with `status = 'DEAD_LETTER'` for Super Admin inspection.
   - `requeue_dead_letter_job`: Resets `status = 'PENDING'`, `attempts = 0`, `locked_at = NULL`, `scheduled_at = NOW()`.
6. Implement administrative audit log query endpoints.
7. Implement API routers in `api/v1/reports.py` and `api/v1/admin.py`.

## 5. Database Changes
Operates on `report_exports`, `audit_logs`, and `communication_jobs`.

## 6. APIs
- `GET /api/v1/reports/volunteer-stats`
- `GET /api/v1/reports/contribution-hours`
- `GET /api/v1/reports/inactive-volunteers`
- `POST /api/v1/reports/export`
- `GET /api/v1/reports/exports/{export_id}`
- `GET /api/v1/admin/audit-logs`
- `GET /api/v1/admin/outbox/dead-letter` (Super Admin inspection)
- `POST /api/v1/admin/outbox/{job_id}/requeue` (Super Admin requeue)

## 7. Security Requirements
- All reporting and admin endpoints restricted to `ADMIN` and `SUPER_ADMIN`.
- System audit log inspection and dead-letter requeue restricted strictly to `SUPER_ADMIN`.
- Rate limiting on export endpoints to prevent resource exhaustion.
- Input parameters validated to prevent SQL injection.

## 8. Test Requirements
- Unit tests verifying aggregation calculations against controlled test datasets.
- Integration tests for CSV export generation.
- Dead-letter requeue integration test: verify job status transitions from `DEAD_LETTER` to `PENDING` and executes cleanly.
- Security tests verifying non-super admins cannot access audit logs or requeue dead-letter jobs.

## 9. Deliverables
- Reporting engine, CSV export generator, admin routers, dead-letter tools, and test suite.

## 10. Acceptance Criteria
- All metrics are calculated dynamically from real database records (zero hardcoded numbers).
- CSV export generates valid downloadable reports.
- Dead-lettered jobs can be inspected and requeued by Super Admins.
- Audit logs capture all administrative decisions.

## 11. Definition of Done (DoD)
Reporting and administrative subsystems operational, tested, and ready for client stabilization in Phase 13.
