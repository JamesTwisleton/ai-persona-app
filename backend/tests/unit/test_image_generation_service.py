"""
Image Generation Service Tests

Tests for ImageGenerationService: avatar creation via DALL-E + local/S3 storage.
HTTP calls and storage are mocked — tests run fast without hitting external APIs.
"""

import base64
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

# Minimal valid base64-encoded bytes (simulates a DALL-E b64_json response)
SAMPLE_B64 = base64.b64encode(b"fake_image_data").decode()
SAMPLE_AVATAR_KEY = "avatars/abc123def456.jpg"


def _mock_dalle_response(b64=SAMPLE_B64):
    """Return a MagicMock that looks like a DALL-E b64_json response."""
    return MagicMock(data=[MagicMock(b64_json=b64)])


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
        """Avatar prompts should request portrait-style photo."""
        from app.services.image_generation_service import ImageGenerationService
        service = ImageGenerationService(client=MagicMock())
        prompt = service.build_avatar_prompt(SAMPLE_PERSONA)
        assert any(word in prompt.lower() for word in ["portrait", "avatar", "illustration", "profile"])


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
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            result = service.generate_avatar("A professional portrait of a data scientist")
        assert result == SAMPLE_AVATAR_KEY

    def test_generate_avatar_calls_api(self):
        """DALL-E API is called once per generate_avatar invocation."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            service.generate_avatar("A portrait of a scientist")
        mock_client.images.generate.assert_called_once()

    def test_generate_avatar_uses_b64_json_format(self):
        """API is called with response_format=b64_json."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        with patch.object(service, "_store_avatar", return_value=SAMPLE_AVATAR_KEY):
            service.generate_avatar("A portrait")
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
        result = service.generate_avatar("A portrait")
        assert result is None

    def test_generate_avatar_on_storage_failure_returns_none(self):
        """Storage failure returns None — image was generated but not stored."""
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
        with patch.object(service, "_store_avatar", return_value=None):
            result = service.generate_avatar("A portrait")
        assert result is None


# ============================================================================
# generate_avatar_for_persona Tests
# ============================================================================

class TestGenerateAvatarForPersona:
    """Integration test of build_avatar_prompt + generate_avatar."""

    def test_generate_avatar_for_persona(self):
        from app.services.image_generation_service import ImageGenerationService
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_dalle_response()
        service = ImageGenerationService(client=mock_client)
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

# ============================================================================
# upload_image Tests
# ============================================================================

class TestUploadImage:

    def test_upload_image_local(self, tmp_path):
        from app.services.image_generation_service import ImageGenerationService
        from app.config import settings

        # Mock settings for local storage
        with patch.object(settings, "LOCAL_AVATAR_DIR", str(tmp_path)):
            service = ImageGenerationService(client=MagicMock())
            image_bytes = b"test_image_data"

            key = service.upload_image(image_bytes, prefix="test_uploads")

            assert key.startswith("test_uploads/")
            assert key.endswith(".jpg")

            # Verify file exists
            file_path = tmp_path / "test_uploads" / key.split("/")[-1]
            assert file_path.exists()
            assert file_path.read_bytes() == image_bytes

    @patch("app.services.image_generation_service.get_s3_client")
    def test_upload_image_s3(self, mock_get_s3, tmp_path):
        from app.services.image_generation_service import ImageGenerationService
        from app.config import settings

        mock_s3 = MagicMock()
        mock_get_s3.return_value = mock_s3

        with patch.object(settings, "LOCAL_AVATAR_DIR", None), \
             patch.object(settings, "S3_AVATAR_BUCKET", "test-bucket"):
            service = ImageGenerationService(client=MagicMock())
            image_bytes = b"test_image_data"

            key = service.upload_image(image_bytes, prefix="uploads")

            assert key.startswith("uploads/")
            mock_s3.put_object.assert_called_once()
            call_kwargs = mock_s3.put_object.call_args[1]
            assert call_kwargs["Bucket"] == "test-bucket"
            assert call_kwargs["Key"] == key
            assert call_kwargs["Body"] == image_bytes

# ============================================================================
# get_image_bytes Tests
# ============================================================================

class TestGetImageBytes:

    def test_get_image_bytes_local(self, tmp_path):
        from app.services.image_generation_service import ImageGenerationService
        from app.config import settings

        image_dir = tmp_path / "uploads"
        image_dir.mkdir()
        image_file = image_dir / "test.jpg"
        image_bytes = b"image_content"
        image_file.write_bytes(image_bytes)

        with patch.object(settings, "LOCAL_AVATAR_DIR", str(tmp_path)):
            service = ImageGenerationService(client=MagicMock())
            result = service.get_image_bytes("uploads/test.jpg")
            assert result == image_bytes

    def test_get_image_bytes_local_fallback(self, tmp_path):
        from app.services.image_generation_service import ImageGenerationService
        from app.config import settings

        image_bytes = b"avatar_content"
        image_file = tmp_path / "avatar.jpg"
        image_file.write_bytes(image_bytes)

        with patch.object(settings, "LOCAL_AVATAR_DIR", str(tmp_path)):
            service = ImageGenerationService(client=MagicMock())
            # Test looking for "avatars/avatar.jpg" but it's directly in LOCAL_AVATAR_DIR
            result = service.get_image_bytes("avatars/avatar.jpg")
            assert result == image_bytes

    @patch("app.services.image_generation_service.get_s3_client")
    def test_get_image_bytes_s3(self, mock_get_s3):
        from app.services.image_generation_service import ImageGenerationService
        from app.config import settings

        mock_s3 = MagicMock()
        mock_response = {"Body": MagicMock()}
        mock_response["Body"].read.return_value = b"s3_content"
        mock_s3.get_object.return_value = mock_response
        mock_get_s3.return_value = mock_s3

        with patch.object(settings, "LOCAL_AVATAR_DIR", None), \
             patch.object(settings, "S3_AVATAR_BUCKET", "test-bucket"):
            service = ImageGenerationService(client=MagicMock())
            result = service.get_image_bytes("uploads/test.jpg")
            assert result == b"s3_content"
            mock_s3.get_object.assert_called_with(Bucket="test-bucket", Key="uploads/test.jpg")

# ============================================================================
# generate_presigned_url Tests
# ============================================================================

class TestGeneratePresignedUrl:

    def test_generate_presigned_url_local_uploads(self):
        from app.services.image_generation_service import generate_presigned_url
        from app.config import settings

        with patch.object(settings, "LOCAL_AVATAR_DIR", "/tmp"), \
             patch.object(settings, "BACKEND_URL", "http://backend"):
            url = generate_presigned_url("uploads/test.jpg")
            assert url == "http://backend/uploads/test.jpg"

    def test_generate_presigned_url_http(self):
        from app.services.image_generation_service import generate_presigned_url
        url = generate_presigned_url("http://example.com/img.jpg")
        assert url == "http://example.com/img.jpg"

    def test_generate_presigned_url_none(self):
        from app.services.image_generation_service import generate_presigned_url, FALLBACK_AVATAR_URL
        assert generate_presigned_url(None) == FALLBACK_AVATAR_URL
