"""Firebase Cloud Messaging (FCM) client adapter with selective error classification."""

import uuid
from dataclasses import dataclass
from typing import Any

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FCMResponse:
    """Outcome of FCM push delivery with selective token classification."""

    success: bool
    message_id: str | None = None
    token_invalid: bool = False
    error_code: str | None = None
    error_message: str | None = None


# Confirmed invalid registration token error indicators
INVALID_TOKEN_CODES = {
    "UNREGISTERED",
    "REGISTRATION_TOKEN_NOT_REGISTERED",
    "NOT_FOUND",
    "INVALID_REGISTRATION",
    "MESSAGING/REGISTRATION-TOKEN-NOT-REGISTERED",
    "MESSAGING/INVALID-REGISTRATION-TOKEN",
}


class FCMClient:
    """Firebase Cloud Messaging adapter supporting durable client deduplication keys."""

    def __init__(self, is_mock: bool | None = None) -> None:
        self.is_mock = (
            is_mock
            if is_mock is not None
            else (
                settings.ENVIRONMENT in ("development", "staging")
                or settings.FIREBASE_CREDENTIALS_PATH is None
            )
        )
        self.sent_pushes: list[dict[str, Any]] = []

    def classify_error(self, error_code: str | None, error_message: str | None) -> bool:
        """Classify whether an FCM error indicates the device token is permanently invalid.

        Token invalidation rule:
        - TRUE only on confirmed unregistration or missing token errors.
        - FALSE on generic invalid-argument, payload errors, or server quotas.
        """
        if not error_code and not error_message:
            return False

        norm_code = (error_code or "").strip().upper()
        norm_msg = (error_message or "").strip().lower()

        if (
            norm_code in INVALID_TOKEN_CODES
            or "UNREGISTERED" in norm_code
            or "REGISTRATION_TOKEN_NOT_REGISTERED" in norm_code
            or "INVALID_REGISTRATION" in norm_code
        ):
            return True

        if (
            "unregistered" in norm_msg
            or "registration-token-not-registered" in norm_msg
            or "invalid-registration-token" in norm_msg
            or "token not registered" in norm_msg
            or "not registered" in norm_msg
            or "token not found" in norm_msg
        ):
            return True

        return False

    async def send_push_notification(
        self,
        fcm_token: str,
        title: str,
        body: str,
        data: dict[str, str] | None = None,
        notification_id: uuid.UUID | None = None,
    ) -> FCMResponse:
        """Deliver push notification to device token with durable notification_id deduplication."""
        notif_id_str = str(notification_id or uuid.uuid4())
        push_data = dict(data or {})
        push_data["notification_id"] = notif_id_str

        if self.is_mock:
            # Synthetic mock behavior
            if fcm_token.startswith("invalid_token_"):
                return FCMResponse(
                    success=False,
                    token_invalid=True,
                    error_code="REGISTRATION_TOKEN_NOT_REGISTERED",
                    error_message="The registration token is not registered with FCM.",
                )
            elif fcm_token.startswith("payload_error_"):
                return FCMResponse(
                    success=False,
                    token_invalid=False,
                    error_code="INVALID_ARGUMENT",
                    error_message="Payload structure or field exceeds allowed length.",
                )

            msg_id = f"projects/maatram/messages/mock_{uuid.uuid4().hex[:12]}"
            self.sent_pushes.append(
                {
                    "token": fcm_token,
                    "title": title,
                    "body": body,
                    "data": push_data,
                    "notification_id": notif_id_str,
                    "message_id": msg_id,
                }
            )
            logger.info(
                "Mock FCM push delivered: %s, message_id: %s", fcm_token[:15] + "...", msg_id
            )
            return FCMResponse(success=True, message_id=msg_id)

        try:
            # If firebase_admin is installed and configured
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=push_data,
                token=fcm_token,
            )
            response = messaging.send(message)
            return FCMResponse(success=True, message_id=response)
        except Exception as exc:
            error_str = str(exc)
            token_invalid = self.classify_error(type(exc).__name__, error_str)
            logger.warning(
                "FCM push dispatch failed: %s (token_invalid: %s)",
                error_str,
                token_invalid,
            )
            return FCMResponse(
                success=False,
                token_invalid=token_invalid,
                error_code=type(exc).__name__,
                error_message=error_str,
            )


fcm_client = FCMClient()
