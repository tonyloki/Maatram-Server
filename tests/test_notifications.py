"""Comprehensive test suite for Notifications Subsystem, FCM Push, and Outbox Engine (Phase 10)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.integrations.fcm_client import fcm_client
from src.models.communications import CommunicationJob, CommunicationLog
from src.models.notifications import DeviceToken
from src.models.users import User
from src.models.volunteers import VolunteerProfile
from src.services.notification_service import notification_service
from src.workers.outbox_worker import outbox_worker


async def create_test_user(
    async_db: AsyncSession,
    role: str = "VOLUNTEER",
    status: str = "APPROVED",
    email: str | None = None,
) -> tuple[User, VolunteerProfile | None]:
    """Helper to seed user and optional volunteer profile."""
    user_email = email or f"{role.lower()}_{uuid.uuid4().hex[:6]}@example.com"
    user = User(
        email=user_email,
        password_hash=get_password_hash("Password123!"),
        role=role,
        status=status,
        is_active=True,
    )
    async_db.add(user)
    await async_db.flush()

    profile: VolunteerProfile | None = None
    if role == "VOLUNTEER":
        profile = VolunteerProfile(
            user_id=user.id,
            first_name="Test",
            last_name="Volunteer",
            mobile_number=f"+9198{uuid.uuid4().int % 100000000:08d}",
            age=24,
            gender="FEMALE",
            category="STUDENT",
        )
        async_db.add(profile)

    await async_db.commit()
    await async_db.refresh(user)
    if profile:
        await async_db.refresh(profile)
    return user, profile


async def get_token(client: AsyncClient, email: str, password: str = "Password123!") -> str:
    """Helper to obtain access token."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "client_type": "WEB"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]  # type: ignore[no-any-return]


@pytest.mark.asyncio
async def test_device_token_registration_and_deactivation(
    client: AsyncClient, async_db: AsyncSession
) -> None:
    """Test device token registration, lookup, and deactivation lifecycle."""
    user, _ = await create_test_user(async_db, role="VOLUNTEER")
    token_str = await get_token(client, user.email)
    headers = {"Authorization": f"Bearer {token_str}"}

    fcm_tok = f"fcm_token_valid_{uuid.uuid4().hex[:16]}"
    res = await client.post(
        "/api/v1/notifications/device-token",
        json={"fcm_token": fcm_tok, "device_platform": "ANDROID"},
        headers=headers,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["fcm_token"] == fcm_tok
    assert data["device_platform"] == "ANDROID"
    assert data["is_active"] is True

    # Verify in DB
    db_stmt = select(DeviceToken).where(DeviceToken.fcm_token == fcm_tok)
    token_db = (await async_db.execute(db_stmt)).scalar_one_or_none()
    assert token_db is not None
    assert token_db.is_active is True

    # Deactivate token
    del_res = await client.delete(
        f"/api/v1/notifications/devices/{fcm_tok}",
        headers=headers,
    )
    assert del_res.status_code == 200

    await async_db.refresh(token_db)
    assert token_db.is_active is False


@pytest.mark.asyncio
async def test_device_token_ownership_check(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify BOLA protection: user cannot deactivate another user's device token."""
    user_a, _ = await create_test_user(async_db, role="VOLUNTEER")
    user_b, _ = await create_test_user(async_db, role="VOLUNTEER")

    token_b_str = await get_token(client, user_b.email)
    headers_b = {"Authorization": f"Bearer {token_b_str}"}

    # Register token for User A
    tok_a = f"fcm_token_a_{uuid.uuid4().hex[:12]}"
    await notification_service.register_device_token(
        db=async_db,
        user=user_a,
        fcm_token=tok_a,
        device_platform="IOS",
    )

    # User B attempts to delete User A's token
    del_res = await client.delete(
        f"/api/v1/notifications/devices/{tok_a}",
        headers=headers_b,
    )
    assert del_res.status_code == 403


@pytest.mark.asyncio
async def test_fcm_selective_error_classification() -> None:
    """Test FCM token error classification: confirmed unregistration vs generic payload errors."""
    # Confirmed token errors deactivate
    assert fcm_client.classify_error("UNREGISTERED", None) is True
    assert fcm_client.classify_error("REGISTRATION_TOKEN_NOT_REGISTERED", None) is True
    assert fcm_client.classify_error("UnregisteredError", "Token not registered") is True
    assert (
        fcm_client.classify_error("FirebaseError", "messaging/registration-token-not-registered")
        is True
    )

    # Payload and quota errors DO NOT deactivate
    assert fcm_client.classify_error("INVALID_ARGUMENT", "Body too large") is False
    assert fcm_client.classify_error("QUOTA_EXCEEDED", "Too many messages") is False
    assert fcm_client.classify_error("UNAVAILABLE", "Server temporarily down") is False


@pytest.mark.asyncio
async def test_fcm_invalid_token_deactivates_in_db(async_db: AsyncSession) -> None:
    """Verify notification dispatch selectively deactivates confirmed invalid tokens but retains valid ones."""
    user, _ = await create_test_user(async_db, role="VOLUNTEER")

    # 1. Confirmed invalid token
    invalid_token = f"invalid_token_{uuid.uuid4().hex[:10]}"
    dt_invalid = await notification_service.register_device_token(
        db=async_db,
        user=user,
        fcm_token=invalid_token,
        device_platform="ANDROID",
    )
    assert dt_invalid.is_active is True

    # 2. Payload error token
    payload_err_token = f"payload_error_{uuid.uuid4().hex[:10]}"
    dt_payload_err = await notification_service.register_device_token(
        db=async_db,
        user=user,
        fcm_token=payload_err_token,
        device_platform="IOS",
    )
    assert dt_payload_err.is_active is True

    # Create notification with push
    await notification_service.create_in_app_notification(
        db=async_db,
        user_id=user.id,
        title="Event Alert",
        message="Your event starts tomorrow.",
        type="EVENT_REMINDER",
        dispatch_push=True,
    )

    await async_db.refresh(dt_invalid)
    await async_db.refresh(dt_payload_err)

    # Invalid token MUST be deactivated
    assert dt_invalid.is_active is False
    # Payload error token MUST remain active
    assert dt_payload_err.is_active is True


@pytest.mark.asyncio
async def test_in_app_notifications_lifecycle(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify in-app notification creation, unread count badge, mark read, and mark all read."""
    user, _ = await create_test_user(async_db, role="VOLUNTEER")
    token_str = await get_token(client, user.email)
    headers = {"Authorization": f"Bearer {token_str}"}

    # 1. Initially unread count is 0
    res = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert res.status_code == 200
    assert res.json()["unread_count"] == 0

    # 2. Create 2 notifications
    n1 = await notification_service.create_in_app_notification(
        db=async_db,
        user_id=user.id,
        title="Points Awarded",
        message="You earned 12.00 points!",
        type="POINTS_AWARDED",
        dispatch_push=False,
    )
    await notification_service.create_in_app_notification(
        db=async_db,
        user_id=user.id,
        title="Application Status",
        message="Your onboarding application is approved.",
        type="APPLICATION_APPROVED",
        dispatch_push=False,
    )
    await async_db.commit()

    # 3. Unread count is now 2
    res = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert res.json()["unread_count"] == 2

    # 4. List notifications
    list_res = await client.get("/api/v1/notifications/me", headers=headers)
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["unread_count"] == 2

    # Verify both body and message aliases exist
    assert data["items"][0]["message"] is not None
    assert data["items"][0]["body"] is not None

    # 5. Mark single notification as read
    patch_res = await client.patch(f"/api/v1/notifications/{n1.id}/read", headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["is_read"] is True

    res = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert res.json()["unread_count"] == 1

    # 6. Mark all read
    all_read_res = await client.post("/api/v1/notifications/read-all", headers=headers)
    assert all_read_res.status_code == 200
    assert all_read_res.json()["marked_count"] == 1

    res = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert res.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_outbox_worker_state_machine_and_dead_letter(
    async_db: AsyncSession,
) -> None:
    """Verify outbox worker state machine: 4 attempts max under max_retries=3, exponential backoff, and DEAD_LETTER transition."""
    now = datetime.now(UTC)
    job = CommunicationJob(
        id=uuid.uuid4(),
        channel="EMAIL",
        recipient="nonexistent@domain.invalid",
        template_name="EVENT_SELECTED",
        payload={"first_name": "Test", "event_title": "Beach Cleanup"},
        status="PENDING",
        attempts=0,
        max_retries=3,
        idempotency_key=f"idemp_{uuid.uuid4().hex}",
        scheduled_at=now - timedelta(minutes=1),
        created_at=now,
    )
    async_db.add(job)
    await async_db.commit()
    await async_db.refresh(job)

    # Force fail the email client for testing retries
    original_send = outbox_worker.email_client.send_email

    async def mock_fail_send(*args: object, **kwargs: object) -> object:
        from src.integrations.resend_client import ResendResponse

        return ResendResponse(success=False, error="Simulated provider connection timeout")

    outbox_worker.email_client.send_email = mock_fail_send  # type: ignore[method-assign]

    try:
        # Attempt 1: PENDING -> claimed (attempts=1) -> fails -> FAILED
        processed = await outbox_worker.process_batch(async_db, batch_size=10)
        assert processed == 1
        await async_db.refresh(job)
        assert job.attempts == 1
        assert job.status == "FAILED"
        sched_dt = (
            job.scheduled_at if job.scheduled_at.tzinfo else job.scheduled_at.replace(tzinfo=UTC)
        )
        assert sched_dt > now

        # Prepare for Attempt 2
        job.scheduled_at = now - timedelta(seconds=1)
        await async_db.commit()

        # Attempt 2: FAILED -> claimed (attempts=2) -> fails -> FAILED
        await outbox_worker.process_batch(async_db, batch_size=10)
        await async_db.refresh(job)
        assert job.attempts == 2
        assert job.status == "FAILED"

        # Prepare for Attempt 3
        job.scheduled_at = now - timedelta(seconds=1)
        await async_db.commit()

        # Attempt 3: FAILED -> claimed (attempts=3) -> fails -> FAILED
        await outbox_worker.process_batch(async_db, batch_size=10)
        await async_db.refresh(job)
        assert job.attempts == 3
        assert job.status == "FAILED"

        # Prepare for Attempt 4
        job.scheduled_at = now - timedelta(seconds=1)
        await async_db.commit()

        # Attempt 4: FAILED -> claimed (attempts=4) -> fails on 4th attempt -> DEAD_LETTER
        await outbox_worker.process_batch(async_db, batch_size=10)
        await async_db.refresh(job)
        assert job.attempts == 4
        assert job.status == "DEAD_LETTER"

        # Verify audit logs in communication_logs
        log_stmt = select(CommunicationLog).where(CommunicationLog.job_id == job.id)
        logs = list((await async_db.execute(log_stmt)).scalars().all())
        assert len(logs) == 4
        assert all(log_rec.status == "FAILED" for log_rec in logs)

    finally:
        outbox_worker.email_client.send_email = original_send  # type: ignore[method-assign]


@pytest.mark.asyncio
async def test_outbox_lease_crash_recovery(async_db: AsyncSession) -> None:
    """Verify expired PROCESSING lease recovery resets job to PENDING."""
    now = datetime.now(UTC)
    job = CommunicationJob(
        id=uuid.uuid4(),
        channel="EMAIL",
        recipient="volunteer@example.com",
        template_name="VERIFY_EMAIL",
        payload={"first_name": "Test", "verify_url": "https://maatram.org"},
        status="PROCESSING",
        attempts=1,
        max_retries=3,
        idempotency_key=f"idemp_{uuid.uuid4().hex}",
        scheduled_at=now,
        locked_at=now - timedelta(minutes=10),  # Lease expired (>5m)
        worker_id="crashed_worker_1",
        created_at=now,
    )
    async_db.add(job)
    await async_db.commit()

    recovered_count = await outbox_worker.recover_expired_leases(
        async_db, lease_timeout_seconds=300
    )
    assert recovered_count >= 1

    await async_db.refresh(job)
    assert job.status == "PENDING"
    assert job.locked_at is None
    assert job.worker_id is None


@pytest.mark.asyncio
async def test_admin_outbox_endpoints(client: AsyncClient, async_db: AsyncSession) -> None:
    """Verify admin outbox job listing, dead-letter filtering, and manual retry."""
    admin, _ = await create_test_user(async_db, role="ADMIN")
    super_admin, _ = await create_test_user(async_db, role="SUPER_ADMIN")

    admin_token = await get_token(client, admin.email)
    super_token = await get_token(client, super_admin.email)

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    super_headers = {"Authorization": f"Bearer {super_token}"}

    # Seed a DEAD_LETTER job
    now = datetime.now(UTC)
    dl_job = CommunicationJob(
        id=uuid.uuid4(),
        channel="EMAIL",
        recipient="failed_recipient@example.com",
        template_name="EVENT_THANK_YOU",
        payload={"first_name": "DeadLetterUser"},
        status="DEAD_LETTER",
        attempts=4,
        max_retries=3,
        idempotency_key=f"dl_idemp_{uuid.uuid4().hex}",
        scheduled_at=now,
        created_at=now,
    )
    async_db.add(dl_job)
    await async_db.commit()

    # 1. Admin lists outbox jobs
    list_res = await client.get("/api/v1/admin/outbox/jobs", headers=admin_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 2. Super admin inspects dead-letter queue
    dl_res = await client.get("/api/v1/admin/outbox/dead-letter", headers=super_headers)
    assert dl_res.status_code == 200
    assert dl_res.json()["total"] >= 1

    # 3. Requeue job
    retry_res = await client.post(
        f"/api/v1/admin/outbox/jobs/{dl_job.id}/retry", headers=admin_headers
    )
    assert retry_res.status_code == 200
    data = retry_res.json()
    assert data["status"] == "PENDING"

    await async_db.refresh(dl_job)
    assert dl_job.status == "PENDING"
    assert dl_job.attempts == 0
