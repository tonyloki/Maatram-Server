"""Email provider interface and response abstractions."""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class EmailResponse:
    """Outcome of email dispatch through an email provider."""

    success: bool
    message_id: str | None = None
    error: str | None = None


@runtime_checkable
class EmailProvider(Protocol):
    """Protocol defining the interface for transactional email delivery providers."""

    provider_name: str

    def render_template(
        self, template_name: str, payload: dict[str, Any]
    ) -> tuple[str, str]:
        """Render subject and HTML body from template name and payload."""
        ...

    def render_email(
        self, template_name: str, payload: dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render subject, HTML body, and plain-text body from template name and payload."""
        ...

    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
        idempotency_key: str | None = None,
    ) -> EmailResponse:
        """Deliver email to recipient with optional plain-text body and idempotency key."""
        ...
