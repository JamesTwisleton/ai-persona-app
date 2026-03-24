"""
Image Generation Service Tests - Phase 4 (RED phase)

Tests for ImageGenerationService: avatar creation via DALL-E.
HTTP calls are mocked - tests run fast without hitting external APIs.

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest
from unittest.mock import MagicMock, patch


SAMPLE_PERSONA = {
    "name": "Alice",
    "age": 30,
    "gender": "Female",
    "description": "A thoughtful data scientist who loves puzzles",
    "attitude": "Neutral",
    "ocean_scores": {
        "openness": 0.8,
        "conscientiousness": 0.7,
        "extraversion": 0.4,
        "agreeableness": 0.6,
        "neuroticism": 0.3,
    },
}

DALLE_SUCCESS_RESPONSE = {
    "data": [{"url": "https://oaidalleapiprodscus.blob.core.windows.net/test/image.png"}]
}


# ============================================================================
# ImageGenerationService Initialization
# ============================================================================

class TestImageGenerationServiceInit:

    def test_init_with_injected_client(self):
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        service = ImageGenerationService(client=mock_client)
        assert service.client is mock_client

    def test_init_default_model(self):
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        service = ImageGenerationService(client=mock_client)
        assert service.default_model == "dalle"


# ============================================================================
# build_avatar_prompt Tests
# ============================================================================

class TestBuildAvatarPrompt:

    def test_build_prompt_includes_name(self):
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        prompt = service.build_avatar_prompt(SAMPLE_PERSONA)
        assert "Alice" in prompt

    def test_build_prompt_includes_gender(self):
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        prompt = service.build_avatar_prompt(SAMPLE_PERSONA)
        assert "Female" in prompt or "female" in prompt.lower() or "woman" in prompt.lower()

    def test_build_prompt_includes_age(self):
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        prompt = service.build_avatar_prompt(SAMPLE_PERSONA)
        assert "30" in prompt

    def test_build_prompt_returns_string(self):
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        prompt = service.build_avatar_prompt(SAMPLE_PERSONA)
        assert isinstance(prompt, str)
        assert len(prompt) > 20

    def test_build_prompt_handles_missing_optional_fields(self):
        """Prompt builds fine even without age/gender."""
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        minimal = {"name": "Bob", "description": "A quiet thinker"}
        prompt = service.build_avatar_prompt(minimal)
        assert "Bob" in prompt

    def test_build_prompt_includes_portrait_style(self):
        """Avatar prompts should request portrait-style illustrations."""
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        prompt = service.build_avatar_prompt(SAMPLE_PERSONA)
        assert any(word in prompt.lower() for word in ["portrait", "avatar", "illustration", "profile"])


# ============================================================================
# generate_avatar Tests
# ============================================================================

class TestGenerateAvatar:

    def test_generate_avatar_returns_url(self):
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/avatar.png")]
        )
        service = ImageGenerationService(client=mock_client)
        url = service.generate_avatar("A professional portrait of a data scientist")
        assert url == "https://example.com/avatar.png"

    def test_generate_avatar_calls_api(self):
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/avatar.png")]
        )
        service = ImageGenerationService(client=mock_client)
        service.generate_avatar("A portrait of a scientist")
        mock_client.images.generate.assert_called_once()

    def test_generate_avatar_invalid_model_raises(self):
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        with pytest.raises(ValueError, match="Unsupported model"):
            service.generate_avatar("A portrait", model="invalid_model")

    def test_generate_avatar_dalle_model(self):
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/avatar.png")]
        )
        service = ImageGenerationService(client=mock_client)
        url = service.generate_avatar("A portrait", model="dalle")
        assert url.startswith("https://")

    def test_generate_avatar_on_api_failure_returns_fallback(self):
        """API failure should return a fallback placeholder URL, not raise."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.side_effect = Exception("API Error")
        service = ImageGenerationService(client=mock_client)
        url = service.generate_avatar("A portrait")
        assert url is not None
        assert isinstance(url, str)
        assert len(url) > 0

    def test_fallback_url_is_placeholder(self):
        """Fallback URL should indicate it's a placeholder."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.side_effect = Exception("API Error")
        service = ImageGenerationService(client=mock_client)
        url = service.generate_avatar("A portrait")
        assert "placeholder" in url.lower() or "default" in url.lower() or "avatar" in url.lower()


# ============================================================================
# generate_avatar_for_persona Tests
# ============================================================================

class TestGenerateAvatarForPersona:
    """Integration test of build_avatar_prompt + generate_avatar."""

    def test_generate_avatar_for_persona(self):
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/alice.png")]
        )
        service = ImageGenerationService(client=mock_client)
        url = service.generate_avatar_for_persona(SAMPLE_PERSONA)
        assert url == "https://example.com/alice.png"

    def test_generate_avatar_for_persona_uses_model_field(self):
        """model_used field from persona dict is passed to generate_avatar."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/alice.png")]
        )
        service = ImageGenerationService(client=mock_client)
        persona_with_model = {**SAMPLE_PERSONA, "model_used": "dalle"}
        url = service.generate_avatar_for_persona(persona_with_model)
        assert url is not None
