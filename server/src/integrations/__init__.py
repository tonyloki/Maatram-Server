"""Third-party external service integration clients."""

from src.core.config import settings
from src.integrations.cloudinary_client import CloudinaryClient, cloudinary_client
from src.integrations.email_provider import EmailProvider, EmailResponse
from src.integrations.fcm_client import FCMClient, fcm_client
from src.integrations.resend_client import ResendClient, ResendResponse, resend_client
from src.integrations.smtp_client import GmailSMTPClient, gmail_smtp_client


def get_email_client(provider: str | None = None) -> EmailProvider:
    """Factory function for selecting the configured transactional email provider.

    Args:
        provider: Explicit provider override ('smtp' or 'resend'). If None, reads from settings.EMAIL_PROVIDER.

    Returns:
        EmailProvider: Active email client instance (GmailSMTPClient or ResendClient).

    Raises:
        ValueError: If an unknown or invalid provider name is specified.
    """
    prov = (provider or getattr(settings, "EMAIL_PROVIDER", "smtp")).strip().lower()
    if prov in ("smtp", "gmail"):
        return gmail_smtp_client
    elif prov == "resend":
        return resend_client
    else:
        raise ValueError(
            f"Invalid EMAIL_PROVIDER '{prov}'. Supported providers are: 'smtp', 'resend'."
        )


__all__ = [
    "CloudinaryClient",
    "EmailProvider",
    "EmailResponse",
    "FCMClient",
    "GmailSMTPClient",
    "ResendClient",
    "ResendResponse",
    "cloudinary_client",
    "fcm_client",
    "get_email_client",
    "gmail_smtp_client",
    "resend_client",
]
