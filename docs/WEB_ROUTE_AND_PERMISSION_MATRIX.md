# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## Web Application — Route & Authorization Matrix

**Document Version:** 1.0.0  
**Status:** Canonical Routing Specification  
**Architecture:** Next.js 15+ App Router with Role-Based Route Groups  
**Backend Security Rule:** Client-side guards provide ergonomic UX; FastAPI endpoints strictly enforce server-side RBAC and Object-Level Authorization (BOLA).

---

## 1. Route Hierarchy & Role Access Matrix

The web application is segregated into three distinct route groups governed by user session state and canonical roles (`VOLUNTEER`, `ADMIN`, `SUPER_ADMIN`) and account statuses (`PENDING`, `APPROVED`, `REJECTED`, `SUSPENDED`).

### 1.1 Public Routes (Unauthenticated & Informational)

| Web Route | Page Purpose | Layout | Allowed Roles / Access State | Redirect Target if Mismatched |
| :--- | :--- | :--- | :--- | :--- |
| `/` | Landing page: Mission, Impact, Core Pillars | Public Header + Footer | All (Unauthenticated & Authenticated) | None |
| `/about` | About Maatram Educational Aid Foundation | Public Header + Footer | All (Unauthenticated & Authenticated) | None |
| `/impact` | Impact stories, community reach, annual reviews | Public Header + Footer | All (Unauthenticated & Authenticated) | None |
| `/login` | Authentication (Email & Password) | Auth Centered Card | Unauthenticated Only | `/volunteer/dashboard` (or `/admin/dashboard`) if logged in |
| `/register` | Multi-step volunteer registration (6 steps) | Multi-step Form Shell | Unauthenticated Only | `/volunteer/dashboard` if logged in |
| `/register/confirmation` | Registration submission receipt | Feedback Centered Card | All (Accessible after registration) | None |
| `/onboarding/pending` | Waiting room for applicants awaiting approval | Status Centered Card | Authenticated with status `PENDING` | `/volunteer/dashboard` if `APPROVED` |
| `/onboarding/rejected` | Notice for rejected applications with reason | Status Centered Card | Authenticated with status `REJECTED` | None |
| `/verify-email` | Email verification token confirmation | Feedback Centered Card | All | None |
| `/forgot-password` | Request password reset OTP | Auth Centered Card | Unauthenticated Only | None |
| `/reset-password` | Submit OTP and new password | Auth Centered Card | Unauthenticated Only | None |

---

### 1.2 Volunteer Portal Routes (`/volunteer/*`)

All routes under `/volunteer/*` require an active user session with `status == "APPROVED"` and role `VOLUNTEER` (or `ADMIN` / `SUPER_ADMIN` in volunteer view).

| Web Route | Page Purpose | Layout | Required Role | Required Status | Redirect if Unauthorized |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/volunteer/dashboard` | Volunteer personal home: Key metrics, quick actions | Volunteer Light Sidebar | `VOLUNTEER`, `ADMIN`, `SUPER_ADMIN` | `APPROVED` | `/login` (if guest) or `/onboarding/pending` (if pending) |
| `/volunteer/events` | Discover upcoming events with search & category filters | Volunteer Light Sidebar | `VOLUNTEER`, `ADMIN`, `SUPER_ADMIN` | `APPROVED` | `/login` or `/onboarding/pending` |
| `/volunteer/events/[id]` | Event details, agenda, venue, and registration CTA | Volunteer Light Sidebar | `VOLUNTEER`, `ADMIN`, `SUPER_ADMIN` | `APPROVED` | `/login` or `/onboarding/pending` |
| `/volunteer/activity` | My registrations (`Upcoming`, `Ongoing`, `Past`) | Volunteer Light Sidebar | `VOLUNTEER`, `ADMIN`, `SUPER_ADMIN` | `APPROVED` | `/login` or `/onboarding/pending` |
| `/volunteer/leaderboard` | Annual Leaderboard with Top 3 Podium and sticky user row | Volunteer Light Sidebar | `VOLUNTEER`, `ADMIN`, `SUPER_ADMIN` | `APPROVED` | `/login` or `/onboarding/pending` |
| `/volunteer/profile` | Polymorphic profile, attendance history, and 6-switch consent | Volunteer Light Sidebar | `VOLUNTEER`, `ADMIN`, `SUPER_ADMIN` | `APPROVED` | `/login` or `/onboarding/pending` |
| `/volunteer/notifications` | In-app notification center & announcement inbox | Volunteer Light Sidebar | `VOLUNTEER`, `ADMIN`, `SUPER_ADMIN` | `APPROVED` | `/login` or `/onboarding/pending` |

---

### 1.3 Admin Command Portal Routes (`/admin/*`)

All routes under `/admin/*` require an active user session with role `ADMIN` or `SUPER_ADMIN`.

| Web Route | Page Purpose | Layout | Required Role | Backend API Equivalent |
| :--- | :--- | :--- | :--- | :--- |
| `/admin/dashboard` | Command center: 4 KPI cards, Category Donut, Action Required, Recent Activity | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/admin/dashboard` |
| `/admin/applications` | Review onboarding volunteer applications with filters | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/applications` |
| `/admin/applications/[id]` | Detailed application inspection, parental consent verification, approve/reject | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/applications/{id}` |
| `/admin/volunteers` | Searchable volunteer directory (Student, Alumni, Corporate) | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/volunteers` |
| `/admin/volunteers/[id]` | Volunteer profile, verified hours, attendance logs, and contact | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/volunteers/{id}` |
| `/admin/events` | Event management: Create, list, filter, publish, cancel, duplicate | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET, POST /api/v1/events` |
| `/admin/events/[id]` | Event roster tabs: `Subscribed`, `Selected`, `Attendance`, `Completion` | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/events/{id}/registrations` |
| `/admin/attendance/correction` | Audited attendance time override dialog / view | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `POST /api/v1/attendance/{id}/correct` |
| `/admin/reports` | 6 production reports with date filters and streaming Excel export | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/admin/reports/...` |
| `/admin/notifications` | Outbox Dead-Letter Queue (DLQ) inspection and manual retry | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/admin/outbox/dead-letter` |
| `/admin/audit-logs` | Immutable security and business audit logs | Admin Dark Sidebar | `SUPER_ADMIN` only | `GET /api/v1/admin/audit-logs` |
| `/admin/settings` | Operational system settings and session management | Admin Dark Sidebar | `ADMIN`, `SUPER_ADMIN` | `GET /api/v1/users/me/sessions` |

---

## 2. Next.js Middleware & Client-Side Navigation Flow

### 2.1 Next.js Edge Middleware (`middleware.ts`)
The edge middleware inspects incoming HTTP requests before page rendering:
1. **Token Detection**:
   - Inspects the `refresh_token` or `access_token` cookie.
2. **Path Matching**:
   - If path matches `/volunteer/*`:
     - If no auth tokens: Redirect to `/login?redirect=${encodeURIComponent(path)}`.
   - If path matches `/admin/*`:
     - If no auth tokens: Redirect to `/login?redirect=${encodeURIComponent(path)}`.
3. **Session Verification via In-Memory State**:
   - The React client layer (`AuthContext`) reads current user status from `/api/v1/users/me`.
   - If user `status == "PENDING"`, accessing `/volunteer/*` redirects to `/onboarding/pending`.
   - If user `status == "REJECTED"`, accessing `/volunteer/*` redirects to `/onboarding/rejected`.
   - If user `role == "VOLUNTEER"`, accessing `/admin/*` redirects to `/volunteer/dashboard` with an *"Unauthorized"* notification.

### 2.2 Security Principle
Client-side middleware and routing guards are strictly for **user experience and navigation guidance**. Under no circumstances does the frontend assume security responsibility:
- All sensitive database records, rosters, and operational metrics are protected by FastAPI dependencies (`require_role("ADMIN", "SUPER_ADMIN")`, `get_current_user`, and BOLA checks in `registration_service`).
- Tampering with client state or bypassing middleware will only result in `401 Unauthorized` or `403 Forbidden` responses from the backend.

