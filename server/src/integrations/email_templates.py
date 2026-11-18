"""Shared email template rendering engine for transactional notifications.

Renders both rich HTML and accessible plain-text representations across
all supported transactional email workflows.
"""

import re
from typing import Any


def html_to_plain_text(html: str) -> str:
    """Convert HTML string to clean, readable plain text."""
    # Replace paragraph and break tags with newlines
    text = re.sub(r"<\s*br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/div\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/li\s*>", "\n", text, flags=re.IGNORECASE)
    # Strip all remaining tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode common HTML entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # Normalize excessive blank lines and leading/trailing whitespace
    lines = [line.strip() for line in text.splitlines()]
    cleaned: list[str] = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned.append("")
                prev_blank = True
        else:
            cleaned.append(line)
            prev_blank = False
    return "\n".join(cleaned).strip()


def render_email_template(
    template_name: str, payload: dict[str, Any]
) -> tuple[str, str, str]:
    """Render subject, HTML body, and plain-text body from template name and payload.

    Returns:
        tuple[str, str, str]: (subject, html_content, text_content)
    """
    first_name = payload.get("first_name", "Volunteer")
    event_title = payload.get("event_title", "Maatram Event")

    if template_name in ("VOLUNTEER_REGISTRATION", "REGISTRATION_CONFIRMATION"):
        subject = "Maatram Volunteer Registration Confirmation"
        html = (
            f"<p>Dear {first_name},</p>"
            f"<p>We have received your registration. Our team will review your application and approve it within 2 days. Your current application status is Pending.</p>"
        )
        text = (
            f"Dear {first_name},\n\n"
            f"We have received your registration. Our team will review your application and approve it within 2 days. Your current application status is Pending."
        )

    elif template_name == "VERIFY_EMAIL":
        token = payload.get("token", "")
        email_addr = payload.get("email", "")
        verify_url = payload.get("verify_url") or (
            f"http://localhost:3001/verify-email?token={token}&email={email_addr}"
            if token
            else "#"
        )
        subject = "Verify your Maatram Volunteer Portal Email"
        html = (
            f"<p>Hello {first_name},</p>"
            f"<p>Please verify your email address by clicking <a href='{verify_url}'>here</a>.</p>"
            f"<p>If the link above does not work, copy and paste this URL into your browser:<br/>"
            f"<a href='{verify_url}'>{verify_url}</a></p>"
        )
        text = (
            f"Hello {first_name},\n\n"
            f"Please verify your email address by clicking the link below:\n"
            f"{verify_url}\n\n"
            f"If the link above does not work, copy and paste this URL into your browser:\n"
            f"{verify_url}"
        )

    elif template_name == "PASSWORD_RESET":
        otp = payload.get("otp", "")
        subject = "Maatram Volunteer Portal — Password Reset Code"
        html = (
            f"<p>Hello {first_name},</p>"
            f"<p>Your password reset code is: <strong>{otp}</strong>. It expires in 15 minutes.</p>"
        )
        text = (
            f"Hello {first_name},\n\n"
            f"Your password reset code is: {otp}\n\n"
            f"This code expires in 15 minutes."
        )

    elif template_name == "APPLICATION_APPROVED":
        subject = "Welcome to Maatram Foundation — Application Approved!"
        html = (
            f"<p>Dear {first_name},</p>"
            f"<p>Congratulations! Your volunteer onboarding application has been approved.</p>"
        )
        text = (
            f"Dear {first_name},\n\n"
            f"Congratulations! Your volunteer onboarding application has been approved.\n"
            f"Welcome to Maatram Foundation."
        )

    elif template_name == "APPLICATION_REJECTED":
        reason = payload.get("reason", "Eligibility criteria not met.")
        subject = "Update regarding your Maatram Volunteer Application"
        html = (
            f"<p>Dear {first_name},</p>"
            f"<p>Thank you for your interest. Unfortunately, your application was not approved at this time. Reason: {reason}</p>"
        )
        text = (
            f"Dear {first_name},\n\n"
            f"Thank you for your interest. Unfortunately, your application was not approved at this time.\n\n"
            f"Reason: {reason}"
        )

    elif template_name == "EVENT_SELECTED":
        subject = f"You are selected for {event_title}!"
        html = (
            f"<p>Dear {first_name},</p>"
            f"<p>You have been selected to volunteer for <strong>{event_title}</strong>. Please review event details on the portal.</p>"
        )
        text = (
            f"Dear {first_name},\n\n"
            f"You have been selected to volunteer for {event_title}. Please review event details on the portal."
        )

    elif template_name == "EVENT_THANK_YOU":
        hours = payload.get("hours_credited", "0.00")
        points = payload.get("total_points", "0.00")
        subject = f"Thank you for volunteering at {event_title}!"
        html = (
            f"<p>Dear {first_name},</p>"
            f"<p>Thank you for your dedication at <strong>{event_title}</strong>. You have been credited with <strong>{hours} hours</strong> and <strong>{points} points</strong>!</p>"
        )
        text = (
            f"Dear {first_name},\n\n"
            f"Thank you for your dedication at {event_title}.\n\n"
            f"You have been credited with {hours} hours and {points} points!"
        )

    elif template_name == "EVENT_REMINDER":
        start_time = payload.get("start_time", "soon")
        subject = f"Reminder: Upcoming volunteering event {event_title}"
        html = (
            f"<p>Dear {first_name},</p>"
            f"<p>This is a friendly reminder that <strong>{event_title}</strong> begins at {start_time}.</p>"
        )
        text = (
            f"Dear {first_name},\n\n"
            f"This is a friendly reminder that {event_title} begins at {start_time}."
        )

    else:
        subject = payload.get("subject", f"Maatram Foundation Notification: {template_name}")
        html = payload.get(
            "body",
            f"<p>Hello {first_name},</p><p>You have a notification regarding {template_name}.</p>",
        )
        text = payload.get("text") or html_to_plain_text(html)

    return subject, html, text
