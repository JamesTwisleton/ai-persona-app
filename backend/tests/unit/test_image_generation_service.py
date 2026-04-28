"""
Image Generation Service Tests

Tests for ImageGenerationService: avatar creation via DALL-E + local/S3 storage.
HTTP calls and storage are mocked — tests run fast without hitting external APIs.
"""

import base64
import pytest
from unittest.mock import MagicMock, patch

from app.services.image_generation_service import generate_presigned_url, FALLBACK_AVATAR_URL

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

# Minimal valid base64-encoded bytes (simulates a DALL-E b64_json response)
SAMPLE_B64 = base64.b64encode(b"fake_image_data").decode()
SAMPLE_AVATAR_KEY = "avatars/abc123def456.jpg"


def _mock_dalle_response(b64=SAMPLE_B64):
    """Return a MagicMock that looks like a DALL-E b64_json response."""
    return MagicMock(data=[MagicMock(b64_json=b64)])


# ============================================================================
# generate_presigned_url Tests
# ============================================================================

class TestGeneratePresignedUrl:

    def test_returns_fallback_on_none(self):
        assert generate_presigned_url(None) == FALLBACK_AVATAR_URL

    def test_returns_fallback_on_empty(self):
        assert generate_presigned_url("") == FALLBACK_AVATAR_URL

    def test_returns_original_if_full_url(self):
        url = "https://example.com/avatar.jpg"
        assert generate_presigned_url(url) == url

    def test_returns_fallback_on_invalid_key_format(self):
        assert generate_presigned_url("not-an-avatar-key") == FALLBACK_AVATAR_URL

    @patch("app.services.image_generation_service.settings")
    def test_local_mode_returns_backend_url(self, mock_settings):
        mock_settings.LOCAL_AVATAR_DIR = "local_avatars"
        mock_settings.BACKEND_URL = "http://localhost:8000"
        key = "avatars/test.jpg"
        expected = "http://localhost:8000/avatars/test.jpg"
        assert generate_presigned_url(key) == expected


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
        assert service.default_model == "nano-banana"


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
        """Avatar prompts should request portrait-style photo."""
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        prompt = service.build_avatar_prompt(SAMPLE_PERSONA)
        assert any(word in prompt.lower() for word in ["portrait", "avatar", "illustration", "profile", "display picture"])

    def test_build_prompt_includes_social_media_requirement(self):
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        prompt = service.build_avatar_prompt(SAMPLE_PERSONA)
        assert "social media website" in prompt.lower()


# ============================================================================
# generate_avatar Tests
# ============================================================================

class TestGenerateAvatar:

    def test_generate_avatar_returns_avatar_key(self):
        """Successful generation returns an avatar storage key."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        # Force model to dalle for this test as nano-banana is now default
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            result = service.generate_avatar("A professional portrait of a data scientist", model="dalle")
        assert result == SAMPLE_AVATAR_KEY

    def test_generate_avatar_calls_api(self):
        """DALL-E API is called once per generate_avatar invocation."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            service.generate_avatar("A portrait of a scientist", model="dalle")
        mock_client.images.generate.assert_called_once()

    def test_generate_avatar_uses_b64_json_format(self):
        """API is called with response_format=b64_json."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            service.generate_avatar("A portrait", model="dalle")
        call_kwargs = mock_client.images.generate.call_args[1]
        assert call_kwargs.get("response_format") == "b64_json"

    def test_generate_avatar_invalid_model_raises(self):
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        with pytest.raises(ValueError, match="Unsupported model"):
            service.generate_avatar("A portrait", model="invalid_model")

    def test_generate_avatar_dalle_model(self):
        """Explicit 'dalle' model works and returns avatar key."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            result = service.generate_avatar("A portrait", model="dalle")
        assert result == SAMPLE_AVATAR_KEY

    def test_generate_avatar_on_api_failure_returns_none(self):
        """API failure returns None — caller handles the missing avatar gracefully."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.side_effect = Exception("API Error")
        service = ImageGenerationService(client=mock_client)
        result = service.generate_avatar("A portrait", model="dalle")
        assert result is None

    def test_generate_avatar_on_storage_failure_returns_none(self):
        """Storage failure returns None — image was generated but not stored."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        with patch.object(service, "_store_avatar", return_value=None):
            result = service.generate_avatar("A portrait", model="dalle")
        assert result is None

    @patch("google.genai.Client")
    @patch("app.services.image_generation_service.settings")
    def test_generate_avatar_banana_success(self, mock_settings, mock_genai_client_class):
        mock_settings.GEMINI_API_KEY = "test-api-key"
        mock_settings.GEMINI_MODEL_ID = "gemini-2.5-flash-image"

        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = base64.b64decode(SAMPLE_B64)
        mock_part.inline_data.mime_type = "image/png"
        mock_part.text = None

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_client_class.return_value = mock_client

        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            result = service.generate_avatar("A portrait", model="nano-banana")

        assert result == SAMPLE_AVATAR_KEY
        mock_client.models.generate_content.assert_called_once()

    @patch("app.services.image_generation_service.settings")
    def test_generate_avatar_banana_missing_config(self, mock_settings):
        mock_settings.GEMINI_API_KEY = None

        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        result = service.generate_avatar("A portrait", model="nano-banana")
        assert result is None


# ============================================================================
# generate_avatar_for_persona Tests
# ============================================================================

class TestGenerateAvatarForPersona:
    """Integration test of build_avatar_prompt + generate_avatar."""

    @patch("google.genai.Client")
    @patch("app.services.image_generation_service.settings")
    def test_generate_avatar_for_persona(self, mock_settings, mock_genai_client_class):
        mock_settings.GEMINI_API_KEY = "test-api-key"
        mock_settings.GEMINI_MODEL_ID = "gemini-2.5-flash-image"

        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = base64.b64decode(SAMPLE_B64)
        mock_part.inline_data.mime_type = "image/png"
        mock_part.text = None

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_client_class.return_value = mock_client

        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            result = service.generate_avatar_for_persona(SAMPLE_PERSONA)
        assert result == SAMPLE_AVATAR_KEY

    def test_generate_avatar_for_persona_uses_model_field(self):
        """model_used field from persona dict is passed to generate_avatar."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        persona_with_model = {**SAMPLE_PERSONA, "model_used": "dalle"}
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            result = service.generate_avatar_for_persona(persona_with_model)
        assert result is not None

    def test_generate_avatar_for_persona_defaults_to_banana(self):
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        with patch.object(service, "generate_avatar", return_value=SAMPLE_AVATAR_KEY) as mock_gen:
            service.generate_avatar_for_persona(SAMPLE_PERSONA)
            mock_gen.assert_called_once()
            assert mock_gen.call_args[1]["model"] == "nano-banana"
