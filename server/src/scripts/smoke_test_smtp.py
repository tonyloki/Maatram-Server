"""Opt-in manual smoke test for Gmail SMTP delivery.

CRITICAL SAFETY PROTOCOL:
This script WILL NOT send an email unless the '--authorized' CLI flag is explicitly passed.
Automated test suites MUST NOT invoke this script with '--authorized'.
"""

import argparse
import asyncio
import sys

from src.core.config import settings
from src.integrations.smtp_client import GmailSMTPClient, mask_email


async def run_smoke_test(recipient: str, authorized: bool) -> int:
    """Execute opt-in manual smoke test against Gmail SMTP."""
    print("=" * 70)
    print("MAATRAM FOUNDATION — GMAIL SMTP MANUAL SMOKE TEST")
    print("=" * 70)
    print(f"Target Recipient: {recipient}")
    print(f"Configured Host:  {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"Configured User:  {mask_email(settings.SMTP_USERNAME)}")
    print(f"Sender Address:   {settings.EMAIL_FROM_ADDRESS}")
    print(f"Sender Name:      {settings.EMAIL_FROM_NAME}")
    print(f"STARTTLS Enabled: {settings.SMTP_USE_TLS}")
    print("=" * 70)

    if not authorized:
        print("\n[SAFETY HALT] The '--authorized' flag was NOT provided.")
        print("To protect against accidental email dispatches during development or testing,")
        print("real email delivery is blocked by default.")
        print("\nTo authorize sending exactly ONE test email after verifying your credentials, run:")
        print(f"  python -m src.scripts.smoke_test_smtp --recipient {recipient} --authorized\n")
        return 1

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print("\n[ERROR] SMTP_USERNAME or SMTP_PASSWORD is not configured in server/.env.")
        print("Please configure Gmail credentials before attempting a live smoke test.")
        return 1

    print("\nInitiating live SMTP handshake, STARTTLS negotiation, and message dispatch...")
    # Initialize live client (is_mock=False)
    client = GmailSMTPClient(is_mock=False)

    subject = "Maatram Volunteer Portal — Gmail SMTP Integration Verification"
    html = (
        "<h2>Maatram Volunteer Portal</h2>"
        "<p>This is a manual verification email confirming that the <strong>Gmail SMTP</strong> "
        "provider has been successfully configured and is operational for transactional email delivery.</p>"
        "<p>Timestamp: Automated delivery check</p>"
    )
    text = (
        "Maatram Volunteer Portal\n\n"
        "This is a manual verification email confirming that the Gmail SMTP provider "
        "has been successfully configured and is operational for transactional email delivery."
    )

    result = await client.send_email(
        to=recipient,
        subject=subject,
        html=html,
        text=text,
        idempotency_key="manual_smoke_test_001",
    )

    if result.success:
        print("\n[SUCCESS] Test email successfully accepted by Gmail SMTP server!")
        print(f"Message ID: {result.message_id}")
        return 0
    else:
        print(f"\n[FAILURE] Gmail SMTP dispatch failed: {result.error}")
        return 2


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Opt-in manual smoke test for Gmail SMTP transactional delivery."
    )
    parser.add_argument(
        "--recipient",
        type=str,
        default="rnksamy007@gmail.com",
        help="Email address of the test recipient.",
    )
    parser.add_argument(
        "--authorized",
        action="store_true",
        default=False,
        help="Explicit authorization flag required to perform actual SMTP delivery.",
    )

    args = parser.parse_args()
    code = asyncio.run(run_smoke_test(recipient=args.recipient, authorized=args.authorized))
    sys.exit(code)


if __name__ == "__main__":
    main()
