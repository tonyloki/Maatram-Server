# Maatram Volunteering & Gamification Portal — Backend

Centralized FastAPI backend and PostgreSQL database powering the Maatram Volunteering & Gamification Portal.

## Architecture

- **Runtime**: Python 3.13+
- **Framework**: FastAPI
- **Validation**: Pydantic 2.0+
- **Database ORM**: SQLAlchemy 2.0+ (asyncpg)
- **Migrations**: Alembic
- **Database**: Supabase PostgreSQL

## Local Development Setup

1. **Create Virtual Environment**:
   ```powershell
   uv venv --python 3.13 .venv
   .venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```powershell
   uv pip install -e ".[dev]"
   ```

3. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in required connection strings.

4. **Run Database Migrations**:
   ```powershell
   alembic upgrade head
   ```

5. **Start Development Server**:
   ```powershell
   uvicorn src.main:app --reload --port 8000
   ```

