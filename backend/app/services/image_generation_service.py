"""
Image Generation Service - Phase 4 (updated: S3 storage)

Generates avatar images for personas using DALL-E via the OpenAI API.
Images are uploaded to S3 and a presigned URL is returned for display.

The avatar_url stored in the database is an S3 object key ("avatars/{id}.jpg"),
not a URL. Call generate_presigned_url() to get a displayable URL.
"""

import base64
import logging
import uuid
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = {"dalle"}

FALLBACK_AVATAR_URL = "https://api.dicebear.com/7.x/personas/svg?seed=default-avatar"

DALLE_MODEL = "dall-e-3"
DALLE_SIZE = "1024x1024"
DALLE_QUALITY = "hd"

# Presigned URL expiry: 6 hours (DALL-E default was ~1 hour; we give more headroom)
PRESIGNED_URL_EXPIRY_SECONDS = 21600


def get_s3_client():
    """Return a boto3 S3 client. Region from settings."""
    return boto3.client("s3", region_name=settings.AWS_DEFAULT_REGION)


def generate_presigned_url(s3_key: str) -> str:
    """
    Generate a presigned GET URL for an S3 object key.

    Args:
        s3_key: The S3 object key, e.g. "avatars/abc123.jpg"

    Returns:
        str: A presigned HTTPS URL valid for PRESIGNED_URL_EXPIRY_SECONDS seconds,
             or the fallback avatar URL if S3 is not configured or an error occurs.
    """
    if not settings.S3_AVATAR_BUCKET:
        return FALLBACK_AVATAR_URL
    if not s3_key or not s3_key.startswith("avatars/"):
        return FALLBACK_AVATAR_URL
    try:
        client = get_s3_client()
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_AVATAR_BUCKET, "Key": s3_key},
            ExpiresIn=PRESIGNED_URL_EXPIRY_SECONDS,
        )
        return url
    except ClientError as e:
        logger.warning(f"Failed to generate presigned URL for {s3_key}: {e}")
        return FALLBACK_AVATAR_URL


class ImageGenerationService:
    """
    Generates persona avatar images via DALL-E, then stores them in S3.

    Returns an S3 object key ("avatars/{uuid}.jpg") as the stored avatar_url.
    Use generate_presigned_url() to get a displayable URL from that key.
    """

    def __init__(self, client=None, default_model: str = "dalle"):
        if client is not None:
            self.client = client
        else:
            import openai
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        self.default_model = default_model

    def build_avatar_prompt(self, persona_details: Dict[str, Any]) -> str:
        name = persona_details.get("name", "A person")
        age = persona_details.get("age")
        gender = persona_details.get("gender")
        description = persona_details.get("description", "")

        parts = []
        if age:
            parts.append(f"{age}-year-old")
        if gender:
            gender_lower = gender.lower()
            if "female" in gender_lower or "woman" in gender_lower or gender_lower == "f":
                parts.append("woman")
            elif "male" in gender_lower or "man" in gender_lower or gender_lower == "m":
                parts.append("man")
            else:
                parts.append("person")
        else:
            parts.append("person")

        demographic = " ".join(parts)

        prompt = (
            f"Photorealistic portrait photograph of {name}, a {demographic}. "
            f"{description[:200] + '. ' if description else ''}"
            f"Professional headshot, natural skin texture, real camera photo. "
            f"Soft studio lighting, neutral background, sharp focus, 85mm lens. "
            f"Photojournalism style, not illustrated, not digital art."
        )

        return prompt

    def _upload_to_s3(self, image_bytes: bytes) -> Optional[str]:
        """Upload image bytes to S3. Returns the S3 key, or None on failure."""
        if not settings.S3_AVATAR_BUCKET:
            logger.warning("S3_AVATAR_BUCKET not configured — cannot store avatar")
            return None
        try:
            s3_key = f"avatars/{uuid.uuid4().hex}.jpg"
            client = get_s3_client()
            client.put_object(
                Bucket=settings.S3_AVATAR_BUCKET,
                Key=s3_key,
                Body=image_bytes,
                ContentType="image/jpeg",
            )
            return s3_key
        except ClientError as e:
            logger.warning(f"Failed to upload avatar to S3: {e}")
            return None

    def generate_avatar(self, prompt: str, model: str = "dalle") -> str:
        """
        Generate an avatar image from a text prompt, upload to S3.

        Returns:
            str: S3 object key ("avatars/{uuid}.jpg") on success,
                 or fallback avatar URL on failure.
        """
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: '{model}'. Choose from: {sorted(SUPPORTED_MODELS)}")

        try:
            response = self.client.images.generate(
                model=DALLE_MODEL,
                prompt=prompt,
                n=1,
                size=DALLE_SIZE,
                quality=DALLE_QUALITY,
                response_format="b64_json",
            )
            b64_data = response.data[0].b64_json
            image_bytes = base64.b64decode(b64_data)

            s3_key = self._upload_to_s3(image_bytes)
            if s3_key:
                return s3_key

            logger.warning("S3 upload failed — avatar not stored")
            return None

        except Exception as e:
            logger.warning(f"Image generation failed: {e}")
            return None

    def generate_avatar_for_persona(
        self,
        persona_details: Dict[str, Any],
        model: Optional[str] = None,
    ) -> str:
        resolved_model = (
            persona_details.get("model_used")
            or model
            or self.default_model
        )

        if resolved_model not in SUPPORTED_MODELS:
            resolved_model = self.default_model

        prompt = self.build_avatar_prompt(persona_details)
        return self.generate_avatar(prompt, model=resolved_model)
