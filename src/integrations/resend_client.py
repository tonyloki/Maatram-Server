"""Resend transactional email client integration."""

import uuid
from dataclasses import dataclass
from typing import Any

import httpx

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ResendResponse:
    """Outcome of Resend email dispatch."""

    success: bool
    message_id: str | None = None
    error: str | None = None


class ResendClient:
    """Integration client for transactional email dispatch via Resend API."""

    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        is_mock: bool | None = None,
    ) -> None:
        self.api_key = api_key or settings.RESEND_API_KEY
        self.from_email = from_email or settings.RESEND_FROM_EMAIL
        self.is_mock = (
            is_mock
            if is_mock is not None
            else (
                settings.ENVIRONMENT in ("development", "staging")
                or not self.api_key
                or self.api_key.startswith("re_test")
            )
        )
        self.sent_emails: list[dict[str, Any]] = []

    def render_template(self, template_name: str, payload: dict[str, Any]) -> tuple[str, str]:
        """Render subject and HTML body from template name and payload."""
        first_name = payload.get("first_name", "Volunteer")
        event_title = payload.get("event_title", "Maatram Event")

        if template_name == "VERIFY_EMAIL":
            verify_url = payload.get("verify_url", "#")
            subject = "Verify your Maatram Volunteer Portal Email"
            html = f"<p>Hello {first_name},</p><p>Please verify your email address by clicking <a href='{verify_url}'>here</a>.</p>"
        elif template_name == "PASSWORD_RESET":
            otp = payload.get("otp", "")
            subject = "Maatram Volunteer Portal — Password Reset Code"
            html = f"<p>Hello {first_name},</p><p>Your password reset code is: <strong>{otp}</strong>. It expires in 15 minutes.</p>"
        elif template_name == "APPLICATION_APPROVED":
            subject = "Welcome to Maatram Foundation — Application Approved!"
            html = f"<p>Dear {first_name},</p><p>Congratulations! Your volunteer onboarding application has been approved.</p>"
        elif template_name == "APPLICATION_REJECTED":
            reason = payload.get("reason", "Eligibility criteria not met.")
            subject = "Update regarding your Maatram Volunteer Application"
            html = f"<p>Dear {first_name},</p><p>Thank you for your interest. Unfortunately, your application was not approved at this time. Reason: {reason}</p>"
        elif template_name == "EVENT_SELECTED":
            subject = f"You are selected for {event_title}!"
            html = f"<p>Dear {first_name},</p><p>You have been selected to volunteer for <strong>{event_title}</strong>. Please review event details on the portal.</p>"
        elif template_name == "EVENT_THANK_YOU":
            hours = payload.get("hours_credited", "0.00")
            points = payload.get("total_points", "0.00")
            subject = f"Thank you for volunteering at {event_title}!"
            html = f"<p>Dear {first_name},</p><p>Thank you for your dedication at <strong>{event_title}</strong>. You have been credited with <strong>{hours} hours</strong> and <strong>{points} points</strong>!</p>"
        elif template_name == "EVENT_REMINDER":
            start_time = payload.get("start_time", "soon")
            subject = f"Reminder: Upcoming volunteering event {event_title}"
            html = f"<p>Dear {first_name},</p><p>This is a friendly reminder that <strong>{event_title}</strong> begins at {start_time}.</p>"
        else:
            subject = payload.get("subject", f"Maatram Foundation Notification: {template_name}")
            html = payload.get(
                "body",
                f"<p>Hello {first_name},</p><p>You have a notification regarding {template_name}.</p>",
            )

        return subject, html

    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
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

        payload = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
            "html": html,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
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
