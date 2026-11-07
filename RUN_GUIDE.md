# Maatram Volunteering & Gamification Portal — Complete Run Guide

This step-by-step guide walks you through setting up and running both the **FastAPI Backend Server** and the **Next.js Web Frontend** locally on your machine.

---

## 📋 System Prerequisites

Before starting, ensure you have the following installed:

1. **Python**: `3.11`, `3.12`, or `3.13+` ([Download Python](https://www.python.org/downloads/))
2. **Node.js**: `v20.x` or `v22.x` (LTS recommended) and `npm` ([Download Node.js](https://nodejs.org/))
3. **Git**: Installed and available in terminal
4. **PostgreSQL Database**: A running Supabase PostgreSQL project or a local PostgreSQL 15+ database.

---

## 📁 Repository Structure Overview

```text
Maatram_Gamification/
├── package.json          # Root scripts for monorepo orchestration
├── .env.example          # Root template reference
├── server/               # FastAPI backend (Port 8000)
│   ├── src/              # API routes, business logic, SQLAlchemy models
│   ├── alembic/          # Database migrations
│   ├── requirements.txt  # Python backend dependencies
│   └── .env.example      # Backend environment template
├── web/                  # Next.js 16 Web Application (Port 3000 or 3001)
│   ├── src/              # React 19 pages, UI components, Tailwind CSS
│   ├── package.json      # Frontend dependencies & scripts
│   └── .env.example      # Frontend environment template
└── RUN_GUIDE.md          # This guide
```

---

## ⚡ Superfast Teammate Quickstart

From the cloned repository root `Maatram_Gamification/`:

```bash
# 1. Initialize environment files for server and web automatically
npm run setup:env

# 2. Install web packages and start frontend
npm run install:web
npm run dev:web

# 3. In a second terminal, activate Python virtual environment and run backend
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1 | macOS/Linux: source .venv/bin/activate
pip install -r server/requirements.txt
npm run dev:server
```

---

## 🚀 Step-by-Step Setup & Execution

### STEP 1: Backend Setup (`server/`)

Open a terminal in the root repository directory `Maatram_Gamification/`.

#### 1.1 Navigate to server directory
```bash
cd server
```

#### 1.2 Create and activate a Python virtual environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If you see an execution policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once).*

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 1.3 Install backend dependencies
```bash
pip install -r requirements.txt
```

#### 1.4 Configure environment variables
Create a `.env` file in the `server/` directory:
```bash
cp .env.example .env
```

Open `server/.env` in your text editor and ensure the following are configured:
```ini
ENVIRONMENT=development
DEBUG=True
SECRET_KEY="generate-a-random-string-at-least-32-chars-long"

# Database connection (use asyncpg driver)
DATABASE_URL="postgresql+asyncpg://postgres:YOUR_PASSWORD@YOUR_DB_HOST:6543/postgres"
DIRECT_URL="postgresql+asyncpg://postgres:YOUR_PASSWORD@YOUR_DB_HOST:5432/postgres"

# CORS origins (allow Next.js frontend ports)
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://127.0.0.1:3000","http://127.0.0.1:3001"]
```

#### 1.5 Run database schema migrations
Ensure your database tables and indexes are fully up-to-date:
```bash
alembic upgrade head
```

#### 1.6 Start the FastAPI backend server
```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

✅ **Verification**:
- Open `http://127.0.0.1:8000/api/v1/health` in your browser. It should return:
  ```json
  {"status":"healthy","database":"connected"}
  ```
- Interactive Swagger API documentation is available at:
  👉 **`http://127.0.0.1:8000/docs`**

---

### STEP 2: Frontend Setup (`web/`)

Keep the backend terminal running. Open a **second terminal window** in the root directory `Maatram_Gamification/`.

#### 2.1 Navigate to web directory
```bash
cd web
```

#### 2.2 Install frontend dependencies
```bash
npm install
```

#### 2.3 Configure environment variables (Optional)
By default, the web client communicates with `http://localhost:8000/api/v1`. If your backend is hosted on a different URL or port, create a `web/.env.local` file:
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### 2.4 Start the development server
```bash
npm run dev
```

The web application will boot up at:
👉 **`http://localhost:3000`**

*(Note: If port 3000 is occupied, Next.js will offer to run on port 3001).*

---

### STEP 3: Production Build & Run (Alternative to `dev`)

If you want to test the optimized production build with Turbopack:

```bash
cd web
npm run build
npm run start
```
*(Runs the production server on `http://localhost:3000` or specify `-p 3001`)*

---

## 🌐 Navigating the Application

Once both servers are running:

| Page | URL | Description |
|:---|:---|:---|
| **Public Landing Page** | `http://localhost:3000` | Organization mission, hero photography, volunteering tracks |
| **Volunteer Registration** | `http://localhost:3000/register` | Multi-step registration wizard (Student / Alumni / Corporate) |
| **Volunteer Login** | `http://localhost:3000/login` | Secure login with email and password |
| **Volunteer Dashboard** | `http://localhost:3000/volunteer/dashboard` | Contribution stats, hours, points, quick actions |
| **Discover Events** | `http://localhost:3000/volunteer/events` | Browse and register for upcoming volunteering drives |
| **My Activity** | `http://localhost:3000/volunteer/activity` | Track upcoming registrations, attendance, and points ledger |
| **Leaderboard** | `http://localhost:3000/volunteer/leaderboard` | Gamified ranking podium, categories, and yearly filters |
| **Profile & Privacy** | `http://localhost:3000/volunteer/profile` | Manage contact details, preferences, and 6 DPDP consent toggles |
| **Admin Portal** | `http://localhost:3000/admin/dashboard` | Administrative overview, attendance verification, reports |
| **Component Showcase** | `http://localhost:3000/showcase` | Interactive design system tokens and component showcase |

---

## 🧪 Running Automated Tests

### Backend Test Suite (Pytest)
From the repository root or inside `server/`:
```bash
# From repository root:
npm run test:server

# Or inside server directory:
cd server
pytest tests/
```
*Expected: 183+ passed tests (including comprehensive security and acceptance suites).*

### Frontend Checks
From the repository root or inside `web/`:
```bash
# From repository root:
npm run typecheck:web
npm run lint:web

# Or inside web directory:
cd web
npm run typecheck   # TypeScript strict type-check (tsc --noEmit)
npm run lint        # Code linting
```

---

## 🛠️ Common Troubleshooting & FAQs

### 1. `DATABASE_URL` connection failure
- Make sure your PostgreSQL server is active.
- If using Supabase, ensure you use the **Transaction Pooler** URL (Port 6543) with the `postgresql+asyncpg://` protocol prefix.
- If passwords contain special characters (like `@`, `#`, or `/`), make sure they are properly URL-encoded.

### 2. CORS Error in browser console
- If the browser console shows `Access-Control-Allow-Origin blocked`, verify that your frontend port (e.g. `http://localhost:3000` or `http://localhost:3001`) is included in `BACKEND_CORS_ORIGINS` inside `server/.env`.
- Restart the FastAPI server after changing `server/.env`.

### 3. Missing packages or module errors in Python
- Verify that your virtual environment is activated. The terminal prompt should show `(.venv)`.
- Re-run `pip install -r requirements.txt`.

### 4. Port 8000 or 3000 already in use
- On Windows: Run `netstat -ano | findstr :8000` and `taskkill /PID <PID> /F` to stop hanging processes.
- Alternatively, launch FastAPI on another port: `uvicorn src.main:app --port 8001` and update `NEXT_PUBLIC_API_URL` in `web/.env.local`.
