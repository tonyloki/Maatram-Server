# AGENTS.md — Development Guidelines & Operational Directives
**Maatram Volunteering & Gamification Portal**

---

## 1. Core Operating Principles

As an AI engineer or human developer working on the Maatram Volunteering & Gamification Portal backend, you must adhere strictly to these non-negotiable operational principles:

1. **Phase Discipline**: The project is structured across exactly 15 sequential phases (Phase 0 to Phase 14). **Never implement features belonging to future phases** without explicit approval and verification that preceding phases meet all Definition of Done (DoD) criteria.
2. **Database as Single Source of Truth**: Every business metric, leaderboard score, attendance log, and volunteer status must be computed directly from canonical PostgreSQL records. Never hardcode, mock, or fabricate metrics or dashboard figures in production endpoints.
3. **Unified Backend Architecture**: There is exactly one backend powering both the Next.js web application and the Flutter mobile application. Business logic, validation rules, authorization policies, and gamification algorithms must reside exclusively in FastAPI and must never be duplicated or bifurcated across clients.
4. **Architectural Simplicity (Modular Monolith)**: Maintain strict module boundaries within a single FastAPI repository. Do not introduce microservices, distributed queues (e.g., Celery, Redis), or orchestrators (e.g., Kubernetes) without a proven, documented requirement. Asynchronous communications use PostgreSQL-backed transactional outbox tables.
5. **Zero-Trust Security & Explicit Authorization**:
   - Authentication is managed entirely by FastAPI (Argon2id + short-lived tokens + server-tracked sessions).
   - Clients never connect directly to Supabase PostgreSQL.
   - Enforce both Role-Based Access Control (RBAC) and Object-Level Authorization (ownership/tenant checks) on every endpoint.
   - Never commit secrets, API keys, or credentials to git.
6. **Data Integrity & Immutability**:
   - Primary keys must be UUIDv7 (or UUIDv4).
   - Foreign key relationships must be enforced at the database level.
   - Financial/gamification point ledgers and audit logs are strictly append-only (immutable).
   - Soft deletes or state-based deprecations must protect historical volunteering records against accidental destruction.
7. **Traceability & Auditing**:
   - Every administrative action (application review, attendance correction, event cancellation, manual point adjustment) must record an immutable audit log entry including actor ID, previous state, new state, reason, and UTC timestamp.
   - Schema evolutions must be tracked through version-controlled Alembic migrations.

---

## 2. Codebase Organization & Module Boundaries

The backend adheres to a **Layered Modular Monolith** pattern:

```
src/
├── api/                  # API routing, request validation schemas, response formatting
│   ├── v1/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── volunteers.py
│   │   ├── applications.py
│   │   ├── consent.py
│   │   ├── events.py
│   │   ├── registrations.py
│   │   ├── attendance.py
│   │   ├── gamification.py
│   │   ├── notifications.py
│   │   ├── media.py
│   │   ├── communications.py
│   │   ├── reports.py
│   │   └── admin.py
│   └── deps.py           # Dependency injection (db sessions, current user, rbac)
├── core/                 # Cross-cutting foundational modules
│   ├── config.py         # Pydantic Settings (environment variables)
│   ├── security.py       # Argon2id hashing, token signing & verification
│   ├── database.py       # SQLAlchemy engine & async session factories
│   ├── exceptions.py     # Custom domain exceptions & global error handlers
│   └── logging.py        # Structured logging configuration
├── models/               # SQLAlchemy 2.0 declarative database models
├── schemas/              # Pydantic 2.0 request & response DTOs
├── repositories/         # Database persistence abstractions (CRUD & specialized queries)
├── services/             # Core business logic & transactional orchestrations
├── integrations/         # Third-party clients (Resend, Cloudinary, Firebase FCM)
└── workers/              # Transactional outbox background processor
```

### Layer Interaction Rules
- **API Routers** invoke **Services** and handle HTTP serialization/deserialization. Routers **must not** make raw database queries.
- **Services** encapsulate all business logic, invariants, state transitions, and coordination between repositories and external clients.
- **Repositories** interact exclusively with SQLAlchemy models and return domain entities or ORM instances.
- **Integrations** are isolated behind clean client interfaces and are invoked asynchronously via outbox jobs or explicitly guarded service calls.

---

## 3. Coding & Engineering Standards

- **Language & Runtime**: Python 3.13+, strictly typed using Python type hints (`mypy --strict` compliant).
- **ORM**: SQLAlchemy 2.0+ utilizing `select()` style and `AsyncSession`.
- **Validation**: Pydantic 2.0+ `BaseModel` with strict data types, input sanitization, and explicit field constraints.
- **Timezone**: All timestamps must be stored in UTC (`TIMESTAMPTZ`). Event-specific local times must store both UTC start/end times and an explicit IANA timezone identifier (e.g., `Asia/Kolkata`).
- **Formatting & Linting**: `ruff` for linting and formatting. Line length standard: 100 characters.
- **Testing**: `pytest` with `pytest-asyncio`. Every business workflow must have comprehensive unit and integration tests with transactional rollback fixtures. Minimum target test coverage: >85%.

---

## 4. Phase Execution & Handover Protocol

Before beginning work on any phase:
1. Review `AGENTS.md`, `docs/MASTER_PLAN.md`, and the specific phase document in `docs/phases/`.
2. Inspect `docs/PHASE_TRACKER.md` to confirm preceding phases are marked **COMPLETED**.
3. Verify existing tests pass before introducing new code.
4. Execute the phase tasks incrementally: Database models & migrations -> Repositories -> Services -> API Routers -> Unit & Integration Tests.
5. Update `docs/PHASE_TRACKER.md` with status, notes, and blockers.
6. Check all acceptance criteria listed in the phase specification. If any criteria fail, mark the phase **IN_REVIEW** or **BLOCKED** and describe the gap.

