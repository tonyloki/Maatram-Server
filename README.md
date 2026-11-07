# Maatram Volunteering & Gamification Portal

Monorepo containing the unified backend, Next.js web application, Flutter mobile application, and canonical project engineering documentation for the Maatram Volunteering & Gamification Portal.

## ⚡ Teammate Clone & Quickstart (Under 2 Minutes)

Clone the repository and get running immediately:

```bash
git clone <repo-url>
cd Maatram_Gamification

# 1. Initialize environment files from templates
npm run setup:env

# 2. Setup & run Frontend (Web)
npm run install:web
npm run dev:web       # Boots on http://localhost:3000

# 3. Setup & run Backend (Server in second terminal)
python -m venv .venv
# On Windows: .\.venv\Scripts\Activate.ps1 | On macOS/Linux: source .venv/bin/activate
pip install -r server/requirements.txt
npm run dev:server    # Boots on http://127.0.0.1:8000 (Swagger docs at /docs)
```

## Repository Structure

```text
Maatram_Gamification/
├── package.json          # Root orchestration scripts for full-stack monorepo
├── .env.example          # Root environment reference template
├── server/               # FastAPI backend application, PostgreSQL ORM, Alembic migrations, & test suite
│   ├── src/              # Modular backend architecture
│   ├── alembic/          # Version-controlled database migrations
│   ├── requirements.txt  # Python dependency specifications
│   └── .env.example      # Backend environment template
├── web/                  # Next.js web application (React 19, Tailwind CSS v4, TypeScript)
│   ├── src/              # Next.js App Router, components, and pages
│   ├── package.json      # Frontend dependencies and npm scripts
│   └── .env.example      # Frontend environment template
├── mobile/               # Flutter mobile application
├── docs/                 # Canonical specifications, master plans, audits, & phase specs
├── AGENTS.md             # Development guidelines, architectural standards, & operational directives
├── README.md             # Monorepo root overview & quickstart
├── RUN_GUIDE.md          # Comprehensive step-by-step developer run guide
└── .gitignore            # Global ignore rules for Python, Node, and Flutter
```

## Backend Details (`server/`)

The backend is built with Python 3.13, FastAPI, SQLAlchemy 2.0 Async, Alembic, and PostgreSQL.

### Database Migrations

```bash
cd server
alembic upgrade head
alembic current
```

### Run Verification Suite

```bash
# Run acceptance and unit test suite
pytest server/tests
# Run code quality checks
ruff check server/src server/tests
npm run typecheck:web
```

## Complete Project Run Guide

For full step-by-step instructions on setting up and running both backend and web frontend, see:
👉 **[`RUN_GUIDE.md`](./RUN_GUIDE.md)**

## Applications Status

| Component | Directory | Stack | Status |
|:---|:---:|:---:|:---|
| **Backend API** | `server/` | FastAPI, SQLAlchemy 2 Async, Alembic, PostgreSQL | **Active & Production Ready** (183 tests passing) |
| **Web Portal** | `web/` | Next.js 16, React 19, TypeScript, Tailwind CSS | **Active & Verified** (0 TS errors, 43 routes) |
| **Mobile App** | `mobile/` | Flutter (Dart) | **Pending Phase 13** |
| **Mobile App** | `mobile/` | Flutter (Dart) | **Pending Phase 13** |


