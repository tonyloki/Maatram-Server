# PHASE 14 — Security Hardening, Performance Testing & Production Deployment

## 1. Objective
Execute security penetration audits, conduct browser integration testing across topologies, run Locust load and stress testing, containerize the FastAPI backend with multi-stage Docker builds, and deploy the production service to Render connected to Supabase PostgreSQL.

## 2. Scope
- Production multi-stage `Dockerfile` and `docker-compose.yml`.
- OWASP API Security Top 10 penetration checklist verification.
- Browser integration testing across deployment topologies (Production `SameSite=Lax` on `.maatram.org`, Staging `SameSite=None; Secure` on cross-SaaS domains, Local development over HTTP).
- Performance load testing with Locust simulating 1,000+ concurrent volunteers.
- Database connection pool tuning, timeout configuration, and index analysis on Supabase PostgreSQL.
- Render web service configuration, health check checks, and deployment blueprints.
- Production operations runbook and monitoring.

## 3. Dependencies
- Phase 13 completed.

## 4. Implementation Tasks
1. Build hardened production `Dockerfile`:
   - Non-root user execution (`appuser`).
   - Multi-stage build minimizing image footprint.
   - Uvicorn runner with production worker configuration (`gunicorn -k uvicorn.workers.UvicornWorker`).
2. Implement automated browser integration test suite across cookie topologies:
   - Verify `SameSite=Lax; Domain=.maatram.org; Secure` sends cookies on cross-subdomain asynchronous fetch and external link landings.
   - Verify `SameSite=None; Secure` functions across distinct public suffixes (`*.vercel.app` <-> `*.onrender.com`).
   - Verify `X-CSRF-Token` validation blocks cross-site request forgery attempts.
3. Implement Locust load testing scenarios in `tests/load/`:
   - Event discovery browsing.
   - High-concurrency event registration bursts.
   - Leaderboard queries.
4. Execute load testing against staging environment:
   - Target $P_{95} < 200\text{ ms}$ under 1,000 concurrent simulated users.
   - Verify database connection pool behaves properly without exhausting Supabase connections.
5. Execute OWASP API Security checklist audit.
6. Verify production database least privilege role provisioning:
   - Runtime web and worker services connect strictly as `maatram_app_user`.
   - Verify `maatram_app_user` permissions: `SELECT, INSERT` on `point_transactions`; `UPDATE, DELETE, TRUNCATE, TRIGGER` revoked; table owned by `maatram_migration_admin`.
7. Create Render blueprint (`render.yaml`) and deployment runbook.
7. Run production database migrations on Supabase PostgreSQL: `alembic upgrade head`.

## 5. Database Changes
Production execution of Alembic baseline migrations on Supabase PostgreSQL.

## 6. APIs
All production `/api/v1` endpoints live on Render.

## 7. Security Requirements
- All secrets (JWT keys, Supabase DB URL, Resend API key, Cloudinary secrets, FCM credentials) injected exclusively via Render environment variables.
- HTTPS enforced; HSTS headers enabled; TLS 1.3.
- Database connections enforce SSL (`sslmode=require`).
- Non-root container execution.

## 8. Test Requirements
- Automated browser integration test verifying cookie behavior across topologies.
- Locust load test verifying latency targets under load.
- Security scan with zero high or critical vulnerabilities.
- Production smoke test verifying `/api/v1/health` and basic auth flows.

## 9. Deliverables
- `Dockerfile` and `docker-compose.yml`.
- `render.yaml` deployment configuration.
- Browser topology test suite in `tests/browser/`.
- Load test report in `docs/LOAD_TEST_REPORT.md`.
- Production operations runbook in `docs/OPERATIONS_RUNBOOK.md`.

## 10. Acceptance Criteria
- Application deployed successfully on Render web service.
- Production database migrated on Supabase PostgreSQL with trigger protections and role privilege isolation active.
- Runtime application role (`maatram_app_user`) blocked from mutating, truncating, or altering triggers on `point_transactions`.
- Health check returns `200 OK` on production domain.
- Browser tests verify cookie transport without credential leakage across topologies.
- Load testing meets latency thresholds ($P_{95} < 200\text{ ms}$).

## 11. Definition of Done (DoD)
Backend live in production, securely configured, monitored, and operational.
