# PHASE 10 — Notification System & FCM Push Setup

## 1. Objective
Implement the in-app notification subsystem and integrate Firebase Cloud Messaging (FCM) to deliver native push notifications to Flutter mobile clients under explicit at-least-once semantics, distinguishing confirmed token deactivations from payload or system errors, and specifying durable client-side deduplication.

## 2. Scope
- In-app notification inbox (`notifications`) serving as the canonical source of truth for all notifications.
- Push delivery semantics: Explicit at-least-once, best-effort push delivery via FCM; exactly-once delivery is NOT claimed.
- Flutter client-side durable deduplication: Mobile client maintains a persistent SQLite deduplication cache (`processed_push_notifications`) indexed by `notification_id` with a 7-day sliding TTL to prevent duplicate banner presentation upon cellular retransmissions.
- Crash window documentation: Acknowledge the edge window between background push receipt and SQLite persistence where an OS isolate termination could cause duplicate presentation on retry; opening the notification reconciles idempotently with the canonical PostgreSQL backend.
- Flutter device token registration and lifecycle management (`device_tokens`).
- Firebase Admin SDK client adapter with selective error classification (`integrations/fcm_client.py`).
- Token invalidation rules: Deactivate token **only** on confirmed token errors (`UnregisteredError`, `messaging/registration-token-not-registered`, `messaging/invalid-registration-token`). Payload errors (`invalid-argument`) and transient quota/system errors must never deactivate tokens.
- Notification service orchestrating in-app persistence and push dispatch (`services/notification_service.py`).
- Notification API endpoints (`api/v1/notifications.py`).

## 3. Dependencies
- Phase 9 completed.

## 4. Implementation Tasks
1. Implement Pydantic 2 schemas in `schemas/notifications.py`.
2. Implement `FCMClient` in `integrations/fcm_client.py` using `firebase-admin` (with mock fallback for local testing without credentials):
   - Include unique `notification_id` (UUIDv7/v4) in every FCM push `data` payload for client-side deduplication.
   - Catch `UnregisteredError` / `messaging/registration-token-not-registered`: trigger `device_tokens.is_active = FALSE`.
   - Catch payload formatting errors (`messaging/invalid-argument` due to body/data format): log error and flag job as failed without deactivating token.
   - Catch quota/server errors: trigger exponential backoff retry.
3. Implement `NotificationRepository` and `NotificationService`:
   - `create_notification`: Writes record to `notifications` inbox (canonical database source of truth) and dispatches push to active device tokens.
   - `register_device_token`: Upserts FCM token for authenticated user; records device platform (`ANDROID`, `IOS`).
   - `mark_as_read` / `mark_all_read`: Updates notification read status.
4. Integrate notification triggers for event announcements, selection confirmations, event cancellations, and point awards.
5. Implement API routers in `api/v1/notifications.py`.

## 5. Database Changes
Operates on `notifications` and `device_tokens`.

## 6. APIs
- `GET /api/v1/notifications` (List in-app notifications with pagination & unread filter)
- `PATCH /api/v1/notifications/{id}/read` (Mark notification as read)
- `POST /api/v1/notifications/read-all` (Mark all read)
- `POST /api/v1/notifications/devices` (Register FCM device token)
- `DELETE /api/v1/notifications/devices/{token}` (De-register token)

## 7. Security Requirements
- Object-level authorization: Users can only query, read, or dismiss their own notifications.
- Device tokens validated to prevent malicious or malformed string injection.
- Notification payload validation ensures no sensitive authentication credentials or private contact information are broadcast over FCM push.

## 8. Test Requirements
- Unit tests for FCM client with mocked Firebase Admin SDK verifying selective token deactivation vs payload error handling.
- FCM at-least-once delivery test: verify payload includes `notification_id` and test client contract for SQLite deduplication.
- Integration tests for notification creation, unread count queries, and read status transitions.
- Device token upsert and de-registration tests.

## 9. Deliverables
- In-app notification engine, FCM integration client, routers, and test suite.

## 10. Acceptance Criteria
- Volunteers receive real-time notifications in-app, with PostgreSQL `notifications` as the single source of truth.
- Flutter mobile tokens register and receive push messages via FCM with durable deduplication keys.
- Unregistered tokens are deactivated; payload formatting errors do not falsely deactivate tokens.
- Unread notification badges update correctly.

## 11. Definition of Done (DoD)
Notification system functional with mock and live push pathways, ready for email and media integration in Phase 11.
