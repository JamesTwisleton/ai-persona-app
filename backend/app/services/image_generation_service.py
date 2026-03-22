"""
Image Generation Service - Phase 4

Generates avatar images for personas using DALL-E via the OpenAI API.

Uses injectable client pattern for testability. Falls back to a placeholder
URL if the API call fails, so persona creation is not blocked by image gen.

TDD Status:
- Tests written first in: tests/unit/test_image_generation_service.py
- This implementation makes those tests GREEN

Usage:
    from app.services.image_generation_service import ImageGenerationService

    service = ImageGenerationService()
    url = service.generate_avatar_for_persona(persona_details)
"""

import logging
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = {"dalle"}

# Placeholder avatar served when image generation fails or is unavailable
FALLBACK_AVATAR_URL = "https://api.dicebear.com/7.x/personas/svg?seed=default-avatar"

# DALL-E model to use
DALLE_MODEL = "dall-e-3"
DALLE_SIZE = "1024x1024"
DALLE_QUALITY = "hd"


class ImageGenerationService:
    """
    Generates persona avatar images via DALL-E.

    On API failure, returns a deterministic fallback placeholder URL
    so that persona creation can continue without interruption.

    Args:
        client: OpenAI client instance. If None, creates one from env vars.
        default_model: Default image generation model ("dalle").
    """

    def __init__(self, client=None, default_model: str = "dalle"):
        if client is not None:
            self.client = client
        else:
            import openai
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        self.default_model = default_model

    def build_avatar_prompt(self, persona_details: Dict[str, Any]) -> str:
        """
        Construct a DALL-E prompt for a persona's avatar.

        Args:
            persona_details: Dict with name, age, gender, description, etc.

        Returns:
            str: Image generation prompt
        """
        name = persona_details.get("name", "A person")
        age = persona_details.get("age")
        gender = persona_details.get("gender")
        description = persona_details.get("description", "")

        # Build demographic descriptor
        parts = []
        if age:
            parts.append(f"{age}-year-old")
        if gender:
            # Map gender to a more descriptive term for the prompt
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

        # Keep prompt focused and safe for DALL-E
        prompt = (
            f"Photorealistic portrait photograph of {name}, a {demographic}. "
            f"{description[:200] + '. ' if description else ''}"
            f"Professional headshot, natural skin texture, real camera photo. "
            f"Soft studio lighting, neutral background, sharp focus, 85mm lens. "
            f"Photojournalism style, not illustrated, not digital art."
        )

        return prompt

    def generate_avatar(self, prompt: str, model: str = "dalle") -> str:
        """
        Generate an avatar image from a text prompt.

        Args:
            prompt: Text description for image generation
            model: Image model to use (currently only "dalle" is supported)

        Returns:
            str: URL of the generated image, or fallback URL on failure

        Raises:
            ValueError: If model is not supported
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
            )
            return response.data[0].url

        except Exception as e:
            logger.warning(f"Image generation failed, using fallback avatar: {e}")
            return FALLBACK_AVATAR_URL

    def generate_avatar_for_persona(
        self,
        persona_details: Dict[str, Any],
        model: Optional[str] = None,
    ) -> str:
        """
        Build prompt from persona details and generate avatar.

        Convenience method combining build_avatar_prompt + generate_avatar.

        Args:
            persona_details: Dict with persona fields
            model: Override model (uses persona's model_used field or default)

        Returns:
            str: Avatar image URL
        """
        # Use model from persona, then caller override, then default
        resolved_model = (
            persona_details.get("model_used")
            or model
            or self.default_model
        )

        # If model_used isn't a supported image model, fall back to default
        if resolved_model not in SUPPORTED_MODELS:
            resolved_model = self.default_model

        prompt = self.build_avatar_prompt(persona_details)
        return self.generate_avatar(prompt, model=resolved_model)
