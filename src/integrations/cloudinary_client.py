"""Cloudinary media signed upload authorization and asset management."""

import hashlib
import time
from typing import Any

from src.core.config import settings
from src.core.exceptions import DomainException
from src.core.logging import get_logger

logger = get_logger(__name__)

ALLOWED_IMAGE_FORMATS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_DOCUMENT_FORMATS = {"pdf", "jpg", "jpeg", "png"}


class CloudinaryClient:
    """Direct-to-Cloudinary upload signer and asset management client."""

    def __init__(
        self,
        cloud_name: str | None = None,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        self.cloud_name = cloud_name or settings.CLOUDINARY_CLOUD_NAME
        self.api_key = api_key or settings.CLOUDINARY_API_KEY
        self.api_secret = api_secret or settings.CLOUDINARY_API_SECRET
        self.max_bytes = settings.CLOUDINARY_MAX_FILE_SIZE_BYTES

    def validate_file_format(self, asset_type: str, file_format: str) -> None:
        """Validate requested file format against allowed MIME extensions for the asset type."""
        fmt = file_format.strip().lower().replace(".", "")
        if asset_type in ("PARENTAL_CONSENT", "DOCUMENT"):
            allowed = ALLOWED_DOCUMENT_FORMATS
        else:
            allowed = ALLOWED_IMAGE_FORMATS

        if fmt not in allowed:
            raise DomainException(
                f"Unsupported format '{file_format}' for {asset_type}. Allowed: {sorted(allowed)}",
                status_code=400,
                code="INVALID_FILE_FORMAT",
            )

    def validate_byte_size(self, byte_size: int) -> None:
        """Validate media byte size does not exceed maximum configured ceiling."""
        if byte_size <= 0:
            raise DomainException(
                "File size must be strictly positive.",
                status_code=400,
                code="INVALID_FILE_SIZE",
            )
        if byte_size > self.max_bytes:
            raise DomainException(
                f"File size {byte_size} bytes exceeds maximum limit of {self.max_bytes} bytes (10MB).",
                status_code=400,
                code="FILE_SIZE_EXCEEDED",
            )

    def verify_uploaded_asset(
        self,
        public_id: str,
        secure_url: str,
        asset_type: str,
        file_format: str,
        byte_size: int,
        user_id: str,
        is_admin: bool = False,
    ) -> None:
        """Server-side verification of uploaded asset metadata, user folder boundary, and Cloudinary URL integrity."""
        # 1. Format validation
        self.validate_file_format(asset_type, file_format)

        # 2. Byte size validation
        self.validate_byte_size(byte_size)

        # 3. Canonical Cloudinary URL check
        expected_url_prefix = f"https://res.cloudinary.com/{self.cloud_name}/"
        if not secure_url.startswith(expected_url_prefix):
            raise DomainException(
                f"Invalid secure_url. Must be hosted on Cloudinary cloud '{self.cloud_name}'.",
                status_code=400,
                code="INVALID_MEDIA_URL",
            )

        # 4. Folder / ownership check (non-admins must upload only to their assigned folder)
        norm_type = asset_type.lower()
        if not norm_type.endswith("s"):
            norm_type = f"{norm_type}s"
        expected_user_prefix = f"maatram/{norm_type}/{user_id}/"

        if not is_admin and not public_id.startswith(expected_user_prefix):
            raise DomainException(
                f"Unauthorized public_id path. Non-admin assets must reside within '{expected_user_prefix}'.",
                status_code=403,
                code="UNAUTHORIZED_MEDIA_FOLDER",
            )

        # 5. Public ID correspondence in secure_url
        clean_public_id = public_id.strip("/")
        if clean_public_id not in secure_url:
            raise DomainException(
                "secure_url does not correspond to the provided public_id.",
                status_code=400,
                code="MEDIA_URL_MISMATCH",
            )

    def generate_signature(self, params_to_sign: dict[str, Any], algorithm: str = "sha256") -> str:
        """Generate Cloudinary cryptographic signature for direct client uploads.

        Parameters are sorted alphabetically, joined as key=value pairs, concatenated
        with the API secret, and hashed with SHA-256 (or SHA-1).
        """
        sorted_keys = sorted(params_to_sign.keys())
        query_parts: list[str] = []
        for k in sorted_keys:
            v = params_to_sign[k]
            if v is not None and v != "":
                query_parts.append(f"{k}={v}")

        raw_query = "&".join(query_parts)
        string_to_sign = f"{raw_query}{self.api_secret}"

        if algorithm.lower() == "sha1":
            return hashlib.sha1(string_to_sign.encode("utf-8")).hexdigest()
        return hashlib.sha256(string_to_sign.encode("utf-8")).hexdigest()

    def generate_signed_upload_params(
        self,
        asset_type: str,
        file_format: str,
        user_id: str,
        custom_folder: str | None = None,
    ) -> dict[str, Any]:
        """Generate authorized signed upload payload for client direct upload."""
        self.validate_file_format(asset_type, file_format)

        timestamp = int(time.time())
        folder = custom_folder or f"maatram/{asset_type.lower()}s/{user_id}"

        params_to_sign = {
            "folder": folder,
            "timestamp": timestamp,
        }

        signature = self.generate_signature(params_to_sign, algorithm="sha256")
        upload_url = f"https://api.cloudinary.com/v1_1/{self.cloud_name}/image/upload"
        if asset_type in ("PARENTAL_CONSENT", "DOCUMENT") and file_format.lower() == "pdf":
            upload_url = f"https://api.cloudinary.com/v1_1/{self.cloud_name}/raw/upload"

        return {
            "upload_url": upload_url,
            "api_key": self.api_key,
            "cloud_name": self.cloud_name,
            "timestamp": timestamp,
            "signature": signature,
            "folder": folder,
        }

    async def destroy_asset(self, public_id: str) -> bool:
        """Call Cloudinary destroy API or mock removal."""
        logger.info("Cloudinary asset destroy requested: %s", public_id)
        return True


cloudinary_client = CloudinaryClient()
