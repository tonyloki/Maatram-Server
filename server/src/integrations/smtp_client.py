"""Gmail SMTP transactional email client integration.

Delivers transactional emails via authenticated SMTP using TLS certificate
verification, STARTTLS protocol negotiation, and multipart HTML/plain-text bodies.
"""

import asyncio
import email.utils
import smtplib
import ssl
import uuid
from email.message import EmailMessage
from typing import Any

from src.core.config import settings
from src.core.logging import get_logger
from src.integrations.email_provider import EmailResponse
from src.integrations.email_templates import html_to_plain_text, render_email_template

logger = get_logger(__name__)


def mask_email(email_address: str | None) -> str:
    """Mask email address for safe logging without exposing PII."""
    if not email_address or "@" not in email_address:
        return "***"
    local, domain = email_address.split("@", 1)
    if len(local) <= 2:
        masked_local = f"{local[:1]}*"
    else:
        masked_local = f"{local[:1]}***{local[-1:]}"
    return f"{masked_local}@{domain}"


class GmailSMTPClient:
    """Integration client for transactional email dispatch via authenticated Gmail SMTP."""

    provider_name: str = "GMAIL_SMTP"

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool | None = None,
        use_ssl: bool | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        timeout: float | None = None,
        is_mock: bool | None = None,
    ) -> None:
        self.host = host or getattr(settings, "SMTP_HOST", "smtp.gmail.com")
        self.port = port if port is not None else getattr(settings, "SMTP_PORT", 587)
        self.username = username or getattr(settings, "SMTP_USERNAME", None)
        self.password = password or getattr(settings, "SMTP_PASSWORD", None)
        self.use_tls = (
            use_tls if use_tls is not None else getattr(settings, "SMTP_USE_TLS", True)
        )
        self.use_ssl = (
            use_ssl if use_ssl is not None else getattr(settings, "SMTP_USE_SSL", False)
        )
        self.from_email = (
            from_email
            or getattr(settings, "EMAIL_FROM_ADDRESS", None)
            or self.username
            or getattr(settings, "RESEND_FROM_EMAIL", "noreply@maatram.org")
        )
        self.from_name = (
            from_name
            or getattr(settings, "EMAIL_FROM_NAME", "Maatram Volunteering Portal")
        )
        self.timeout = (
            timeout
            if timeout is not None
            else getattr(settings, "SMTP_TIMEOUT_SECONDS", 15.0)
        )

        # In testing or when credentials are intentionally absent/mock, operate in safe mock mode
        self.is_mock = (
            is_mock
            if is_mock is not None
            else (
                not self.username
                or not self.password
                or self.password.startswith("test_")
                or self.password.startswith("mock_")
            )
        )
        self.sent_emails: list[dict[str, Any]] = []

    def render_template(
        self, template_name: str, payload: dict[str, Any]
    ) -> tuple[str, str]:
        """Render subject and HTML body from template name and payload."""
        subject, html, _ = render_email_template(template_name, payload)
        return subject, html

    def render_email(
        self, template_name: str, payload: dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render subject, HTML body, and plain-text body from template name and payload."""
        return render_email_template(template_name, payload)

    def build_message(
        self,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
        idempotency_key: str | None = None,
    ) -> EmailMessage:
        """Construct a standards-compliant MIME multipart/alternative EmailMessage."""
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = email.utils.formataddr((self.from_name, self.from_email))
        msg["To"] = to
        msg["Date"] = email.utils.formatdate(localtime=True)

        domain = self.from_email.split("@")[-1] if "@" in self.from_email else "maatram.org"
        msg["Message-ID"] = email.utils.make_msgid(domain=domain)

        if idempotency_key:
            msg["X-Idempotency-Key"] = idempotency_key

        plain_text = text or html_to_plain_text(html)
        msg.set_content(plain_text)
        msg.add_alternative(html, subtype="html")

        return msg

    def _send_sync(self, to: str, msg: EmailMessage) -> tuple[bool, str | None, str | None]:
        """Synchronous SMTP session execution running inside asyncio.to_thread."""
        if not self.username or not self.password:
            err = "Missing SMTP username or password for authenticated relay"
            logger.error(err)
            return False, None, err

        server: smtplib.SMTP | smtplib.SMTP_SSL | None = None
        context = ssl.create_default_context()
        msg_id = str(msg["Message-ID"])

        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                    context=context,
                )
            else:
                server = smtplib.SMTP(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                )
                if self.use_tls:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()

            if self.username and self.password:
                server.login(self.username, self.password)

            # Send message and ensure full server acceptance
            server.send_message(msg)
            return True, msg_id, None

        except smtplib.SMTPAuthenticationError as exc:
            err = f"SMTP Authentication failed (code {exc.smtp_code})"
            logger.error(
                "SMTP authentication failed for user %s: %s",
                mask_email(self.username),
                err,
            )
            return False, None, err

        except smtplib.SMTPConnectError as exc:
            err = f"SMTP connection error to {self.host}:{self.port}: {exc}"
            logger.error("SMTP connection error: %s", err)
            return False, None, err

        except smtplib.SMTPServerDisconnected as exc:
            err = f"SMTP server disconnected unexpectedly: {exc}"
            logger.error("SMTP disconnection error: %s", err)
            return False, None, err

        except smtplib.SMTPRecipientsRefused as exc:
            err = f"SMTP recipient refused for {mask_email(to)}: {exc}"
            logger.error("SMTP recipient refused: %s", err)
            return False, None, err

        except (smtplib.SMTPException, TimeoutError, OSError) as exc:
            err = f"SMTP transmission error: {exc}"
            logger.error("SMTP transmission error for %s: %s", mask_email(to), err)
            return False, None, err

        finally:
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    try:
                        server.close()
                    except Exception:
                        pass

    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
        idempotency_key: str | None = None,
    ) -> EmailResponse:
        """Deliver transactional email via SMTP with thread-isolated execution."""
        if self.is_mock:
            msg_id = f"<mock_{uuid.uuid4().hex[:16]}@maatram.org>"
            self.sent_emails.append(
                {
                    "to": to,
                    "subject": subject,
                    "html": html,
                    "text": text or html_to_plain_text(html),
                    "idempotency_key": idempotency_key,
                    "message_id": msg_id,
                    "from": email.utils.formataddr((self.from_name, self.from_email)),
                }
            )
            logger.info(
                "Mock SMTP email dispatched to %s, subject: '%s', message_id: %s",
                mask_email(to),
                subject,
                msg_id,
            )
            return EmailResponse(success=True, message_id=msg_id)

        msg = self.build_message(
            to=to,
            subject=subject,
            html=html,
            text=text,
            idempotency_key=idempotency_key,
        )

        success, msg_id, error = await asyncio.to_thread(self._send_sync, to, msg)
        return EmailResponse(success=success, message_id=msg_id, error=error)


gmail_smtp_client = GmailSMTPClient()
