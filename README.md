# Maatram Volunteering & Gamification Portal

Monorepo containing the unified backend, Next.js web application, Flutter mobile application, and canonical project engineering documentation for the Maatram Volunteering & Gamification Portal.

## Repository Structure

```text
Maatram-Portal/
├── server/               # FastAPI backend application, PostgreSQL ORM, Alembic migrations, & test suite
├── web/                  # Next.js web application (Phase 13 / Frontend)
├── mobile/               # Flutter mobile application (Phase 13 / Frontend)
├── docs/                 # Canonical specifications, master plans, decision log, & execution reports
│   ├── phases/           # 15 canonical phase specification documents (Phase 00 - Phase 14)
│   └── execution-groups/ # Verified execution group reports (Groups 01 - 07)
├── AGENTS.md             # Development guidelines, architectural standards, & operational directives
├── README.md             # Monorepo root overview & quickstart
└── .gitignore            # Global ignore rules for Python, Node, and Flutter
```

## Backend Quickstart (`server/`)

The backend is built with Python 3.13, FastAPI, SQLAlchemy 2.0 Async, Alembic, and Supabase PostgreSQL.

### 1. Setup Environment

```bash
cd server
cp .env.example .env
# Edit .env with your PostgreSQL credentials, secret keys, etc.
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
alembic upgrade head
alembic current
```

### 4. Start Backend Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Run Verification Suite

```bash
cd server
python -m pytest
ruff check src/ tests/
ruff format --check src/ tests/
mypy --strict src/
```

## Applications Status

| Component | Directory | Stack | Status |
|:---|:---:|:---:|:---|
| **Backend API** | `server/` | FastAPI, SQLAlchemy 2 Async, Alembic, PostgreSQL | **Active & Production Ready** (144 tests passing) |
| **Web Portal** | `web/` | Next.js (TypeScript, TailwindCSS) | **Pending Phase 13** |
| **Mobile App** | `mobile/` | Flutter (Dart) | **Pending Phase 13** |


