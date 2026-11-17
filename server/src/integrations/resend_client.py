"""Resend transactional email client integration."""

import uuid
from typing import Any

import httpx

from src.core.config import settings
from src.core.logging import get_logger
from src.integrations.email_provider import EmailResponse
from src.integrations.email_templates import render_email_template

logger = get_logger(__name__)

# Backward-compatible alias for existing test suites
ResendResponse = EmailResponse


class ResendClient:
    """Integration client for transactional email dispatch via Resend API."""

    provider_name: str = "RESEND"

    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        is_mock: bool | None = None,
    ) -> None:
        self.api_key = api_key or getattr(settings, "RESEND_API_KEY", "re_test_key")
        self.from_email = (
            from_email
            or getattr(settings, "EMAIL_FROM_ADDRESS", None)
            or getattr(settings, "RESEND_FROM_EMAIL", "noreply@maatram.org")
        )
        self.is_mock = (
            is_mock
            if is_mock is not None
            else (not self.api_key or self.api_key.startswith("re_test"))
        )
        self.sent_emails: list[dict[str, Any]] = []

    def render_template(self, template_name: str, payload: dict[str, Any]) -> tuple[str, str]:
        """Render subject and HTML body from template name and payload."""
        subject, html, _ = render_email_template(template_name, payload)
        return subject, html

    def render_email(
        self, template_name: str, payload: dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render subject, HTML body, and plain-text body from template name and payload."""
        return render_email_template(template_name, payload)

    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
        idempotency_key: str | None = None,
    ) -> ResendResponse:
        """Send an email via Resend API or mock in-memory for testing."""
        if self.is_mock:
            msg_id = f"re_msg_{uuid.uuid4().hex[:16]}"
            self.sent_emails.append(
                {
                    "to": to,
                    "subject": subject,
                    "html": html,
                    "text": text,
                    "idempotency_key": idempotency_key,
                    "message_id": msg_id,
                }
            )
            logger.info(
                "Mock email sent to %s, subject: %s, idempotency_key: %s, message_id: %s",
                to,
                subject,
                idempotency_key,
                msg_id,
            )
            return ResendResponse(success=True, message_id=msg_id)

        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        payload: dict[str, Any] = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if text:
            payload["text"] = text

        try:
            timeout_sec = getattr(settings, "RESEND_TIMEOUT_SECONDS", 15.0)
            async with httpx.AsyncClient(timeout=timeout_sec) as client:
                res = await client.post(
                    "https://api.resend.com/emails",
                    json=payload,
                    headers=headers,
                )
                if res.status_code in (200, 201):
                    data = res.json()
                    return ResendResponse(success=True, message_id=data.get("id"))
                else:
                    err_msg = f"Resend API error {res.status_code}: {res.text}"
                    logger.error("Resend API failure: %s for recipient: %s", err_msg, to)
                    return ResendResponse(success=False, error=err_msg)
        except Exception as exc:
            err_msg = f"Network or HTTP error communicating with Resend: {exc}"
            logger.error("Resend dispatch exception: %s for recipient: %s", err_msg, to)
            return ResendResponse(success=False, error=err_msg)


resend_client = ResendClient()
