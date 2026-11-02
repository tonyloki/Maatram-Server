# PHASE 08 — Attendance & Hours Management

## 1. Objective
Implement physical and virtual volunteer attendance tracking, individual and bulk check-in/out, exact duration calculation in minutes, incomplete attendance flagging, and an auditable administrative attendance correction mechanism.

## 2. Scope
- Check-in and check-out operations for selected volunteers (`attendance_records`).
- Invariant enforcement: No checkout without check-in; no duplicate check-ins.
- Zero auto-checkout policy: Uncompleted attendances flagged as `INCOMPLETE`.
- Duration calculation in exact minutes: $\text{Duration} = (T_{out} - T_{in})\text{ in minutes}$.
- Administrative attendance correction with mandatory reasoning and audit logging (`attendance_corrections`).

## 3. Dependencies
- Phase 7 completed.

## 4. Implementation Tasks
1. Implement Pydantic 2 schemas in `schemas/attendance.py`.
2. Implement `AttendanceRepository` managing queries for active event rosters.
3. Implement `AttendanceService`:
   - `check_in_volunteers`: Validates event status is `ONGOING`, verifies volunteer is `SELECTED`, inserts record with `status = 'IN_PROGRESS'`.
   - `check_out_volunteers`: Validates $T_{out} \ge T_{in}$, computes duration in minutes, updates status to `COMPLETED`.
   - `correct_attendance`: Admin override of check-in/out; persists original and corrected values with reason into `attendance_corrections`.
4. Implement API routers in `api/v1/attendance.py`.

## 5. Database Changes
Operates on `attendance_records` and `attendance_corrections`.

## 6. APIs
- `POST /api/v1/events/{id}/attendance/check-in`
- `POST /api/v1/events/{id}/attendance/check-out`
- `GET /api/v1/events/{id}/attendance` (Admin list roster)
- `POST /api/v1/attendance/{id}/correct` (Admin correction)
- `GET /api/v1/volunteers/me/attendance` (Volunteer personal log)

## 7. Security Requirements
- Attendance check-in/out and correction endpoints restricted to `ADMIN` and `SUPER_ADMIN`.
- Check-out timestamps cannot precede check-in timestamps.
- All corrections must capture the authenticated admin user ID and a non-empty reason.

## 8. Test Requirements
- Unit tests verifying exact duration calculation in minutes.
- Integration tests preventing check-out without existing check-in.
- Test verifying attendance corrections persist in `attendance_corrections` and update the primary record.

## 9. Deliverables
- Attendance repository, service, routers, and automated test suite.

## 10. Acceptance Criteria
- Bulk and individual check-in/out function reliably.
- Missing checkouts are flagged as `INCOMPLETE` and not auto-completed.
- All modifications are completely auditable.

## 11. Definition of Done (DoD)
Attendance subsystem operational, verified against business rules, and ready for gamification scoring in Phase 9.

