# PHASE 13 — API Stabilization & Web/Flutter Integration

## 1. Objective
Freeze the OpenAPI v1 contract, validate end-to-end user journeys across both Next.js and Flutter clients, ensure unified error handling, and produce comprehensive frontend integration documentation.

## 2. Scope
- OpenAPI specification export and schema validation (`openapi.json`).
- Full lifecycle end-to-end (E2E) integration test simulating complete volunteer and admin journeys.
- Cross-Origin Resource Sharing (CORS) auditing for web client domains.
- Mobile client token refresh and Flutter Secure Storage integration verification.
- Frontend integration handbook (`docs/FRONTEND_INTEGRATION.md`).

## 3. Dependencies
- Phase 12 completed.

## 4. Implementation Tasks
1. Generate and export static `openapi.json` from FastAPI application.
2. Verify all request and response schemas align with Next.js TypeScript definitions and Flutter Dio/Freezed models.
3. Build end-to-end integration test suite (`tests/e2e/`):
   - Journey 1: Volunteer registers -> verifies email -> admin approves -> volunteer logs in -> registers for event -> admin selects -> admin checks in & out -> admin completes event -> verify points awarded -> verify leaderboard rank updated.
   - Journey 2: Admin creates event -> edits -> cancels -> verify cancellation notifications queued.
4. Verify HTTP cookie attributes for web browsers across environments (development vs production).
5. Author `docs/FRONTEND_INTEGRATION.md` detailing token handling, auth headers, and error codes.

## 5. Database Changes
None.

## 6. APIs
All `/api/v1/*` endpoints stabilized and verified.

## 7. Security Requirements
- Verify CORS blocks unauthorized origins.
- Verify CSRF protection on cookie-authenticated web requests.
- Verify mobile Bearer token headers function independently of cookies.

## 8. Test Requirements
- Full-lifecycle automated E2E integration test suite.
- Contract testing verifying all API responses match documented OpenAPI schemas.

## 9. Deliverables
- `openapi.json`.
- E2E test suite in `tests/e2e/`.
- `docs/FRONTEND_INTEGRATION.md`.

## 10. Acceptance Criteria
- Complete end-to-end volunteer journey passes cleanly in automated test.
- Web and mobile authentication models verified without discrepancies.
- Zero undocumented API endpoints or schema mismatches.

## 11. Definition of Done (DoD)
API contract frozen, verified by automated E2E tests, and ready for production deployment in Phase 14.

