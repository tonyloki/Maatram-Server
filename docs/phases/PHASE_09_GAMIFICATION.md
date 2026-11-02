# PHASE 09 — Gamification, Points & Leaderboards

## 1. Objective
Implement the official scoring formula $P = (E \times 10) + (H \times 2)$ with exact decimal precision (`NUMERIC(8, 2)`), trigger-protected append-only point ledgers, compensating transactions for adjustments, atomic event completion preview and finalization, multi-tier leaderboards, and anonymity preferences.

## 2. Scope
- Implementation of scoring formula:
  $$P = (E \times 10) + (H \times 2)$$
  with exact decimal precision (`NUMERIC(8, 2)` / Python `Decimal` strictly, never mixing with `float`), supporting fractional points (e.g., 45 minutes = 0.75 hours = 1.50 points). Raw attendance duration is tracked in integer minutes (`duration_minutes INTEGER`); credited hours (`hours_credited NUMERIC(8, 2)`) and points use Python `Decimal`. Acknowledges precision limitation of `NUMERIC(8, 2)` for repeating fractions ($20\text{ mins} = 0.333...\text{ hrs}$); formal rounding policy remains pending Maatram approval.
- Immutable point ledger persistence in `point_transactions` protected by database trigger `trg_prevent_point_ledger_mutation` and database role privilege isolation (application runtime role has only `SELECT, INSERT`; `UPDATE, DELETE, TRUNCATE, TRIGGER` revoked).
- Compensating transactions (`transaction_type = 'COMPENSATION_REVERSAL'`) for point adjustments and reversals.
- Two-phase event completion:
  1. Preview (`GET /api/v1/events/{id}/completion-preview`).
  2. Atomic Finalization (`POST /api/v1/events/{id}/complete`).
- Multi-tier leaderboards: Overall, Student, Alumni, Corporate Panelist.
- Cycle year partitioning and historical point preservation.
- Volunteer anonymity enforcement (`consent_records.leaderboard_visible`).
- System achievements catalog (`achievement_definitions`, `volunteer_achievements`).

## 3. Dependencies
- Phase 8 completed.

## 4. Implementation Tasks
1. Implement Pydantic 2 schemas in `schemas/gamification.py` using Python `Decimal` exclusively for all point and credited hour fields (no `float` types).
2. Implement `GamificationRepository` for ledger queries, aggregations (`SUM(total_points)`), and leaderboard rankings with window functions.
3. Implement `GamificationService`:
   - Compute points: $P = (E \times 10.00) + (H \times 2.00)$ as exact decimal values.
   - Generate completion preview: evaluate selected vs attended, hours credited, incomplete flags, point totals, thank-you email recipients, and draft LinkedIn celebration copy.
   - Atomic event finalization: execute database transaction locking the event, finalizing attendance, writing point ledger records, and enqueuing outbox communication jobs.
   - Compensating transactions: execute Super Admin point adjustments via compensating rows with negative values and pointers to `related_transaction_id`.
   - Leaderboard generation: aggregate decimal points per cycle year; mask names of anonymous volunteers.
   - Achievement evaluation engine.
4. Implement API routers in `api/v1/gamification.py` and `api/v1/leaderboards.py`.

## 5. Database Changes
Operates on `point_transactions`, `achievement_definitions`, and `volunteer_achievements`.

## 6. APIs
- `GET /api/v1/events/{id}/completion-preview`
- `POST /api/v1/events/{id}/complete`
- `GET /api/v1/gamification/summary`
- `GET /api/v1/gamification/ledger`
- `GET /api/v1/leaderboards`
- `GET /api/v1/achievements`

## 7. Security Requirements
- Points can only be awarded via atomic event completion or audited Super Admin compensating adjustment.
- Duplicate point prevention enforced by unique constraint (`volunteer_profile_id`, `event_id`).
- Ledger protected against `UPDATE` and `DELETE` at the engine level via triggers.
- Application runtime DB role (`maatram_app_user`) restricted to `SELECT, INSERT`; table owned by migration admin to prevent `TRUNCATE` or trigger disabling.
- Leaderboards must strictly mask volunteers who have not consented to public visibility (`leaderboard_visible = FALSE`).

## 8. Test Requirements
- Unit tests validating formula calculations across edge cases using Python `Decimal` strictly (e.g., partial hours like 45 minutes yielding exactly 1.50 points; 20 minutes repeating fraction behavior).
- Integration test for atomic event completion transaction verifying that rollback preserves zero state if any ledger insert fails.
- Idempotency test: calling event completion twice on the same event returns error and awards zero additional points.
- Immutability test: verify direct SQL `UPDATE` or `DELETE` on `point_transactions` raises database trigger exception.
- Ledger privilege isolation test: verify application database role cannot execute `TRUNCATE` or `ALTER TABLE ... DISABLE TRIGGER`.
- Compensating transaction test: verify point adjustments preserve historical records while updating net sums.
- Leaderboard ranking and anonymity masking integration tests.

## 9. Deliverables
- Gamification repository, service, routers, and test suite.

## 10. Acceptance Criteria
- $P = (E \times 10) + (H \times 2)$ computed with exact decimal precision (`NUMERIC(8, 2)`) using Python `Decimal` strictly.
- Points awarded exactly once per completed event attendance.
- Direct ledger updates and deletes are rejected by database triggers.
- Application role is blocked from executing `TRUNCATE` or trigger alteration.
- Leaderboards render rankings across Overall, Student, Alumni, and Corporate tiers with anonymity respected.

## 11. Definition of Done (DoD)
Gamification engine verified, points ledger immutable, and ready for notification engine integration in Phase 10.
