# Maatram Portal — Backend Server

FastAPI backend application powering the Maatram Volunteering & Gamification Portal.

## Architecture

- **Language & Runtime**: Python 3.13+
- **Framework**: FastAPI (REST APIs, Dependency Injection, OpenAPI docs)
- **Database**: PostgreSQL (Supabase) via SQLAlchemy 2.0 Async (`asyncpg`)
- **Migrations**: Alembic with safety rollback guards
- **Authentication**: Argon2id password hashing, rotating JWT tokens, PostgreSQL session tracking
- **Asynchronous Processing**: Transactional outbox engine (`communication_jobs`)

## Directory Layout

```text
server/
├── alembic/              # Database schema migrations
├── src/
│   ├── api/              # API routers and dependency injection
│   │   ├── deps.py       # Current user, database session, RBAC dependencies
│   │   └── v1/           # Modular API endpoints (auth, events, attendance, gamification, etc.)
│   ├── core/             # Foundational config, database, logging, security, rate limiting
│   ├── integrations/     # Cloudinary, Firebase Cloud Messaging (FCM), Resend adapters
│   ├── models/           # SQLAlchemy 2.0 declarative database models (29 tables)
│   ├── repositories/     # Database persistence abstractions
│   ├── schemas/          # Pydantic 2 request and response DTOs
│   ├── services/         # Domain business logic & transactions
│   ├── workers/          # Transactional outbox background processor
│   └── main.py           # FastAPI application entry point
├── tests/                # Comprehensive unit, integration, and migration test suites
├── alembic.ini           # Alembic migration configuration
├── pyproject.toml        # Build configuration, linting, typing, and pytest settings
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## Getting Started

### 1. Environment Setup

```bash
cd server
cp .env.example .env
# Edit .env with your PostgreSQL credentials, secret key, etc.
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Migrations

```bash
alembic upgrade head
alembic current
```

### 4. Running the Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Running the Outbox Worker

```bash
python -c "import asyncio; from src.workers.outbox_worker import outbox_worker; from src.core.database import async_session_factory; asyncio.run(outbox_worker.process_batch(async_session_factory()))"
```

### 6. Testing & Quality Verification

```bash
# Run pytest suite
python -m pytest

# Run Ruff linter and formatter checks
ruff check src/ tests/
ruff format --check src/ tests/

# Run Mypy static type checking
mypy --strict src/
```

