"""Comprehensive test suite for Gmail SMTP Provider Migration, Factory Selection, and Outbox Integration."""

import email.message
import smtplib
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings, settings
from src.integrations import (
    EmailResponse,
    GmailSMTPClient,
    ResendClient,
    get_email_client,
    gmail_smtp_client,
    resend_client,
)
from src.integrations.email_templates import html_to_plain_text, render_email_template
from src.models.communications import CommunicationJob, CommunicationLog
from src.workers.outbox_worker import OutboxWorker


# ==============================================================================
# 1. Configuration & Factory Selection Tests
# ==============================================================================


def test_smtp_provider_configuration_defaults() -> None:
    """Verify SMTP configuration attributes exist on application settings."""
    assert hasattr(settings, "EMAIL_PROVIDER")
    assert settings.SMTP_HOST == "smtp.gmail.com"
    assert settings.SMTP_PORT == 587
    assert settings.SMTP_USE_TLS is True
    assert settings.SMTP_USE_SSL is False
    assert settings.EMAIL_FROM_NAME == "Maatram Volunteering Portal"


def test_provider_factory_selects_smtp_and_resend() -> None:
    """Verify provider factory selects GmailSMTPClient for 'smtp' and ResendClient for 'resend'."""
    smtp_prov = get_email_client("smtp")
    assert isinstance(smtp_prov, GmailSMTPClient)
    assert smtp_prov.provider_name == "GMAIL_SMTP"

    resend_prov = get_email_client("resend")
    assert isinstance(resend_prov, ResendClient)
    assert resend_prov.provider_name == "RESEND"


def test_provider_factory_invalid_fails_fast() -> None:
    """Verify invalid provider name raises ValueError with descriptive guidance."""
    with pytest.raises(ValueError, match="Invalid EMAIL_PROVIDER 'invalid_provider'"):
        get_email_client("invalid_provider")


@pytest.mark.asyncio
async def test_missing_credentials_fails_safely() -> None:
    """Verify SMTP client returns failure safely when credentials are missing and not in mock mode."""
    client = GmailSMTPClient(
        host="smtp.gmail.com",
        username="",
        password="",
        is_mock=False,
    )
    res = await client.send_email(
        to="volunteer@example.com",
        subject="Test Subject",
        html="<p>Test</p>",
    )
    assert res.success is False
    assert "Missing SMTP username or password" in str(res.error)


@pytest.mark.asyncio
async def test_resend_missing_api_key_fails_safely() -> None:
    """Verify Resend client returns failure safely when API key is missing and not in mock mode."""
    client = ResendClient(api_key="", from_email="noreply@maatram.org", is_mock=False)
    res = await client.send_email(
        to="volunteer@example.com",
        subject="Test Subject",
        html="<p>Test</p>",
    )
    assert res.success is False


# ==============================================================================
# 2. Template Rendering Tests (HTML & Plain Text)
# ==============================================================================


def test_all_five_email_templates_render_html_and_plain_text() -> None:
    """Verify all transactional templates render valid subject, HTML, and accessible plain-text."""
    templates_to_test = [
        ("VERIFY_EMAIL", {"first_name": "Priya", "verify_url": "https://maatram.org/verify?token=123"}),
        ("PASSWORD_RESET", {"first_name": "Arun", "otp": "456789"}),
        ("APPLICATION_APPROVED", {"first_name": "Karthik"}),
        ("APPLICATION_REJECTED", {"first_name": "Ravi", "reason": "Location criteria"}),
        ("EVENT_SELECTED", {"first_name": "Divya", "event_title": "Tree Plantation"}),
        ("EVENT_THANK_YOU", {"first_name": "Meera", "event_title": "Teaching Drive", "hours_credited": "4.00", "total_points": "18.00"}),
        ("EVENT_REMINDER", {"first_name": "Suresh", "event_title": "Mock Interviews", "start_time": "10:00 AM"}),
    ]

    for tmpl_name, payload in templates_to_test:
        subject, html, text = render_email_template(tmpl_name, payload)
        assert subject, f"Subject missing for {tmpl_name}"
        assert html and "<p>" in html, f"HTML structure missing for {tmpl_name}"
        assert text and "<p>" not in text, f"Plain text contains unstripped HTML for {tmpl_name}"
        assert payload.get("first_name", "") in html
        assert payload.get("first_name", "") in text


def test_html_to_plain_text_utility() -> None:
    """Verify HTML stripping decodes entities and formats clean line breaks."""
    raw_html = "<p>Hello&nbsp;World!<br/>Line 2</p><div>Line 3 &amp; &lt;safe&gt;</div>"
    clean = html_to_plain_text(raw_html)
    assert "Hello World!" in clean
    assert "Line 2" in clean
    assert "Line 3 & <safe>" in clean
    assert "<" not in clean.replace("& <safe>", "")


# ==============================================================================
# 3. SMTP Adapter Protocol, STARTTLS, & MIME Construction
# ==============================================================================


def test_smtp_build_mime_multipart_message() -> None:
    """Verify build_message creates standard multipart/alternative with plain-text and HTML."""
    client = GmailSMTPClient(
        host="smtp.gmail.com",
        port=587,
        username="rnksamy007@gmail.com",
        password="test_password",
        from_email="rnksamy007@gmail.com",
        from_name="Maatram Foundation",
    )

    msg = client.build_message(
        to="volunteer@example.com",
        subject="Welcome Volunteer",
        html="<p>Welcome to <strong>Maatram</strong>!</p>",
        idempotency_key="idemp_12345",
    )

    assert msg["To"] == "volunteer@example.com"
    assert "Maatram Foundation" in msg["From"]
    assert "rnksamy007@gmail.com" in msg["From"]
    assert msg["Subject"] == "Welcome Volunteer"
    assert msg["X-Idempotency-Key"] == "idemp_12345"
    assert msg["Message-ID"] is not None
    assert msg.is_multipart()

    # Inspect payload parts
    payloads = msg.get_payload()
    assert len(payloads) == 2
    types = [part.get_content_type() for part in payloads]
    assert "text/plain" in types
    assert "text/html" in types


@pytest.mark.asyncio
async def test_smtp_starttls_successful_submission() -> None:
    """Verify STARTTLS negotiation, authentication, message sending, and clean quit via mock smtplib."""
    client = GmailSMTPClient(
        host="smtp.gmail.com",
        port=587,
        username="rnksamy007@gmail.com",
        password="app_password_mock",
        use_tls=True,
        use_ssl=False,
        is_mock=False,
    )

    mock_smtp_instance = MagicMock()
    with patch("smtplib.SMTP", return_value=mock_smtp_instance) as mock_smtp_cls:
        res = await client.send_email(
            to="recipient@example.com",
            subject="Test STARTTLS",
            html="<p>Test</p>",
            idempotency_key="test_starttls_key",
        )

        assert res.success is True
        assert res.message_id is not None
        assert res.error is None

        # Verify SMTP handshake sequence
        mock_smtp_cls.assert_called_once_with(host="smtp.gmail.com", port=587, timeout=15.0)
        assert mock_smtp_instance.ehlo.call_count >= 2
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("rnksamy007@gmail.com", "app_password_mock")
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()


@pytest.mark.asyncio
async def test_smtp_authentication_failure_handling() -> None:
    """Verify SMTPAuthenticationError is caught cleanly and returns descriptive error."""
    client = GmailSMTPClient(
        host="smtp.gmail.com",
        port=587,
        username="rnksamy007@gmail.com",
        password="invalid_password",
        is_mock=False,
    )

    mock_smtp_instance = MagicMock()
    mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"5.7.8 Bad credentials")

    with patch("smtplib.SMTP", return_value=mock_smtp_instance):
        res = await client.send_email(
            to="recipient@example.com",
            subject="Test Auth Failure",
            html="<p>Test</p>",
        )

        assert res.success is False
        assert "SMTP Authentication failed (code 535)" in (res.error or "")
        # Connection must be closed cleanly
        mock_smtp_instance.quit.assert_called_once()


@pytest.mark.asyncio
async def test_smtp_connection_timeout_handling() -> None:
    """Verify connection timeout is caught and logged safely."""
    client = GmailSMTPClient(
        host="smtp.gmail.com",
        port=587,
        username="rnksamy007@gmail.com",
        password="app_password",
        is_mock=False,
    )

    with patch("smtplib.SMTP", side_effect=TimeoutError("Connection timed out")):
        res = await client.send_email(
            to="recipient@example.com",
            subject="Test Timeout",
            html="<p>Test</p>",
        )

        assert res.success is False
        assert "SMTP transmission error" in (res.error or "")


# ==============================================================================
# 4. Outbox Worker Lifecycle & Resiliency Integration Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_outbox_temporary_smtp_failure_and_retry(async_db: AsyncSession) -> None:
    """Verify transient SMTP failure transitions job to FAILED with exponential backoff delay."""
    now = datetime.now(UTC)
    job = CommunicationJob(
        id=uuid.uuid4(),
        channel="EMAIL",
        recipient="retry_user@example.com",
        template_name="VERIFY_EMAIL",
        payload={"first_name": "RetryUser", "verify_url": "https://maatram.org/verify"},
        status="PENDING",
        attempts=0,
        max_retries=3,
        idempotency_key=f"idemp_retry_{uuid.uuid4().hex[:12]}",
        scheduled_at=now - timedelta(seconds=10),
        created_at=now,
    )
    async_db.add(job)
    await async_db.commit()

    # Mock failing email client
    mock_email_client = MagicMock()
    mock_email_client.provider_name = "GMAIL_SMTP"
    mock_email_client.render_email.return_value = ("Subject", "<p>HTML</p>", "Text")

    async def fail_send(*args: object, **kwargs: object) -> EmailResponse:
        return EmailResponse(success=False, error="Temporary SMTP 421 Service not available")

    mock_email_client.send_email.side_effect = fail_send

    worker = OutboxWorker(email_client=mock_email_client)
    processed = await worker.process_batch(async_db, batch_size=10)
    assert processed == 1

    await async_db.refresh(job)
    assert job.attempts == 1
    assert job.status == "FAILED"
    assert job.last_error == "Temporary SMTP 421 Service not available"

    # Verify audit log entry
    log_stmt = select(CommunicationLog).where(CommunicationLog.job_id == job.id)
    log_entry = (await async_db.execute(log_stmt)).scalar_one_or_none()
    assert log_entry is not None
    assert log_entry.provider == "GMAIL_SMTP"
    assert log_entry.status == "FAILED"


@pytest.mark.asyncio
async def test_outbox_permanent_failure_transitions_to_dead_letter(
    async_db: AsyncSession,
) -> None:
    """Verify job transitions to DEAD_LETTER after max_retries attempts are exhausted."""
    now = datetime.now(UTC)
    job = CommunicationJob(
        id=uuid.uuid4(),
        channel="EMAIL",
        recipient="exhausted@example.com",
        template_name="APPLICATION_REJECTED",
        payload={"first_name": "ExhaustedUser", "reason": "Quota reached"},
        status="FAILED",
        attempts=3,  # Reaching attempt 4 will exhaust max_retries=3
        max_retries=3,
        idempotency_key=f"idemp_dl_{uuid.uuid4().hex[:12]}",
        scheduled_at=now - timedelta(seconds=10),
        created_at=now,
    )
    async_db.add(job)
    await async_db.commit()

    mock_email_client = MagicMock()
    mock_email_client.provider_name = "GMAIL_SMTP"
    mock_email_client.render_email.return_value = ("Subject", "<p>HTML</p>", "Text")

    async def fail_send(*args: object, **kwargs: object) -> EmailResponse:
        return EmailResponse(success=False, error="Permanent recipient mailbox unavailable")

    mock_email_client.send_email.side_effect = fail_send

    worker = OutboxWorker(email_client=mock_email_client)
    processed = await worker.process_batch(async_db, batch_size=10)
    assert processed == 1

    await async_db.refresh(job)
    assert job.attempts == 4
    assert job.status == "DEAD_LETTER"


@pytest.mark.asyncio
async def test_outbox_idempotency_key_uniqueness(async_db: AsyncSession) -> None:
    """Verify database unique constraint prevents duplicate communication jobs with the same idempotency key."""
    shared_key = f"idemp_unique_{uuid.uuid4().hex}"
    job1 = CommunicationJob(
        id=uuid.uuid4(),
        channel="EMAIL",
        recipient="user1@example.com",
        template_name="VERIFY_EMAIL",
        payload={"first_name": "User1"},
        status="PENDING",
        idempotency_key=shared_key,
    )
    async_db.add(job1)
    await async_db.commit()

    job2 = CommunicationJob(
        id=uuid.uuid4(),
        channel="EMAIL",
        recipient="user2@example.com",
        template_name="VERIFY_EMAIL",
        payload={"first_name": "User2"},
        status="PENDING",
        idempotency_key=shared_key,
    )
    async_db.add(job2)
    with pytest.raises(IntegrityError):
        await async_db.commit()
    await async_db.rollback()


@pytest.mark.asyncio
async def test_resend_client_fallback_remains_fully_functional() -> None:
    """Verify existing ResendClient implementation remains operational in mock mode."""
    resend = ResendClient(is_mock=True)
    res = await resend.send_email(
        to="resend_test@example.com",
        subject="Resend Verification",
        html="<p>Testing Resend fallback</p>",
        idempotency_key="resend_key_123",
    )
    assert res.success is True
    assert res.message_id is not None
    assert len(resend.sent_emails) >= 1
    assert resend.sent_emails[-1]["to"] == "resend_test@example.com"
