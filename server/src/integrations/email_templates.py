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
        name = (
            payload.get("name")
            or payload.get("volunteer_name")
            or f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
            or payload.get("first_name")
            or "Volunteer"
        )
        category_raw = (
            payload.get("category")
            or payload.get("volunteer_category")
            or "Student"
        )
        category = category_raw.replace("_", " ").title() if isinstance(category_raw, str) else "Student"

        subject = "Thank you for registering with Maatram Volunteer Portal"
        html = (
            f"<p>Dear {name},</p>"
            f"<p>Thank you for registering as a {category} volunteer with Maatram Foundation. We have received your application.</p>"
            f"<p><strong>Next steps:</strong><br/>"
            f"Our team will review your details.<br/>"
            f"You will receive an email once your application is approved.<br/>"
            f"After approval, you can browse events and subscribe to the ones that match your interests.</p>"
            f"<p><strong>A message from our team:</strong><br/>"
            f"Your willingness to give your time means the world to our students. We are so happy to welcome you to the Maatram family.</p>"
            f"<p>Warm regards,<br/>"
            f"Maatram Foundation</p>"
        )
        text = (
            f"Dear {name},\n\n"
            f"Thank you for registering as a {category} volunteer with Maatram Foundation. We have received your application.\n\n"
            f"Next steps:\n"
            f"Our team will review your details.\n"
            f"You will receive an email once your application is approved.\n"
            f"After approval, you can browse events and subscribe to the ones that match your interests.\n\n"
            f"A message from our team:\n"
            f"Your willingness to give your time means the world to our students. We are so happy to welcome you to the Maatram family.\n\n"
            f"Warm regards,\n"
            f"Maatram Foundation"
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
        name = (
            payload.get("name")
            or payload.get("volunteer_name")
            or f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
            or payload.get("first_name")
            or "Volunteer"
        )
        subject = "Your application is Approved."
        html = (
            f"<p>Dear {name},</p>"
            f"<p>Your volunteer application has been reviewed and approved by the Maatram team.</p>"
            f"<p>You can now log in to the portal at any time. All events and other portal features are now accessible to you.</p>"
            f"<p><strong>A Message from Our Team:</strong></p>"
            f"<p>Thank you for your patience and your interest in volunteering with us. We truly appreciate your support and look forward to working with you.</p>"
            f"<p>Warm regards,<br/>"
            f"Maatram Foundation</p>"
        )
        text = (
            f"Dear {name},\n\n"
            f"Your volunteer application has been reviewed and approved by the Maatram team.\n\n"
            f"You can now log in to the portal at any time. All events and other portal features are now accessible to you.\n\n"
            f"A Message from Our Team:\n\n"
            f"Thank you for your patience and your interest in volunteering with us. We truly appreciate your support and look forward to working with you.\n\n"
            f"Warm regards,\n"
            f"Maatram Foundation"
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
        event_name = (
            payload.get("event_name")
            or payload.get("event_title")
            or event_title
        )
        name = (
            payload.get("name")
            or payload.get("volunteer_name")
            or f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
            or payload.get("first_name")
            or "Volunteer"
        )
        event_date = payload.get("event_date") or payload.get("date") or "the scheduled date"
        hours = payload.get("hours") or payload.get("hours_credited") or "0"
        points = payload.get("points") or payload.get("points_awarded") or payload.get("total_points") or "0"
        rank = payload.get("rank") or payload.get("current_rank") or "—"

        subject = f"Thank you for volunteering at {event_name}"
        html = (
            f"<p>Dear {name},</p>"
            f"<p>Thank you for volunteering at {event_name} on {event_date}. Your time and effort made a real difference.</p>"
            f"<p><strong>Your contribution:</strong><br/>"
            f"* Verified hours: {hours}<br/>"
            f"* Points earned: {points}<br/>"
            f"* Current rank: {rank}</p>"
            f"<p><strong>A message from our team:</strong></p>"
            f"<p>Your kindness and dedication gave our students the confidence to dream bigger. Thank you for being such a valuable part of the Maatram family.</p>"
            f"<p>We look forward to seeing you at our next event.</p>"
            f"<p>Warm regards,<br/>"
            f"Maatram Foundation</p>"
        )
        text = (
            f"Dear {name},\n\n"
            f"Thank you for volunteering at {event_name} on {event_date}. Your time and effort made a real difference.\n\n"
            f"Your contribution:\n"
            f"* Verified hours: {hours}\n"
            f"* Points earned: {points}\n"
            f"* Current rank: {rank}\n\n"
            f"A message from our team:\n\n"
            f"Your kindness and dedication gave our students the confidence to dream bigger. Thank you for being such a valuable part of the Maatram family.\n\n\n"
            f"We look forward to seeing you at our next event.\n\n"
            f"Warm regards,\n"
            f"Maatram Foundation"
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
