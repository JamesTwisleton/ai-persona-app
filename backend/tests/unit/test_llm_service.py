"""
LLM Service Tests - Phase 4 (RED phase)

Tests for LLMService: motto generation and conversation response generation.
External API calls are mocked - tests run fast without hitting Claude.

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest
from unittest.mock import MagicMock, patch


SAMPLE_PERSONA = {
    "name": "Alice",
    "description": "A thoughtful data scientist who loves puzzles",
    "attitude": "Neutral",
    "ocean_scores": {
        "openness": 0.8,
        "conscientiousness": 0.7,
        "extraversion": 0.4,
        "agreeableness": 0.6,
        "neuroticism": 0.3,
    },
    "archetype_affinities": {
        "ANA": 0.35,
        "SOC": 0.10,
        "INN": 0.25,
        "PRA": 0.10,
        "REB": 0.08,
        "CUS": 0.05,
        "EMP": 0.05,
        "CAT": 0.02,
    },
}


def make_mock_client(response_text: str):
    """Helper to create a mock Anthropic client returning given text."""
    mock_content = MagicMock()
    mock_content.text = response_text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


# ============================================================================
# LLMService Initialization
# ============================================================================

class TestLLMServiceInit:

    def test_init_with_injected_client(self):
        from app.services.llm_service import LLMService
        mock_client = MagicMock()
        service = LLMService(client=mock_client)
        assert service.client is mock_client

    def test_init_uses_default_model(self):
        from app.services.llm_service import LLMService, DEFAULT_MODEL
        mock_client = MagicMock()
        service = LLMService(client=mock_client)
        assert service.model == DEFAULT_MODEL

    def test_init_accepts_custom_model(self):
        from app.services.llm_service import LLMService
        mock_client = MagicMock()
        service = LLMService(client=mock_client, model="claude-opus-4-6")
        assert service.model == "claude-opus-4-6"


# ============================================================================
# generate_motto Tests
# ============================================================================

class TestGenerateMotto:

    def test_generate_motto_returns_string(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("Question everything, trust data.")
        service = LLMService(client=mock_client)
        motto = service.generate_motto(SAMPLE_PERSONA)
        assert isinstance(motto, str)
        assert len(motto) > 0

    def test_generate_motto_calls_claude_api(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("Data reveals truth.")
        service = LLMService(client=mock_client)
        service.generate_motto(SAMPLE_PERSONA)
        mock_client.messages.create.assert_called_once()

    def test_generate_motto_strips_whitespace(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("  Question everything.  \n")
        service = LLMService(client=mock_client)
        motto = service.generate_motto(SAMPLE_PERSONA)
        assert motto == motto.strip()

    def test_generate_motto_removes_quotes(self):
        """If Claude returns the motto in quotes, they should be stripped."""
        from app.services.llm_service import LLMService
        mock_client = make_mock_client('"Question everything."')
        service = LLMService(client=mock_client)
        motto = service.generate_motto(SAMPLE_PERSONA)
        assert not motto.startswith('"')
        assert not motto.endswith('"')

    def test_generate_motto_includes_persona_name_in_prompt(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("Live boldly.")
        service = LLMService(client=mock_client)
        service.generate_motto(SAMPLE_PERSONA)

        call_kwargs = mock_client.messages.create.call_args
        # Check persona name appears somewhere in the API call
        call_str = str(call_kwargs)
        assert "Alice" in call_str

    def test_generate_motto_on_api_failure_raises(self):
        from app.services.llm_service import LLMService
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API unavailable")
        service = LLMService(client=mock_client)
        with pytest.raises(Exception, match="API unavailable"):
            service.generate_motto(SAMPLE_PERSONA)

    def test_generate_motto_uses_attitude_in_prompt(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("Always look on the bright side.")
        service = LLMService(client=mock_client)

        persona_comical = {**SAMPLE_PERSONA, "attitude": "Comical"}
        service.generate_motto(persona_comical)

        call_str = str(mock_client.messages.create.call_args)
        assert "Comical" in call_str or "comical" in call_str.lower()


# ============================================================================
# generate_response Tests
# ============================================================================

class TestGenerateResponse:

    def test_generate_response_returns_string(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("I believe we should colonize Mars for humanity's survival.")
        service = LLMService(client=mock_client)
        response = service.generate_response(
            persona_details=SAMPLE_PERSONA,
            conversation_history=[],
            topic="Should we colonize Mars?",
        )
        assert isinstance(response, str)
        assert len(response) > 0

    def test_generate_response_calls_claude_api(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("Mars is worth exploring.")
        service = LLMService(client=mock_client)
        service.generate_response(
            persona_details=SAMPLE_PERSONA,
            conversation_history=[],
            topic="Mars",
        )
        mock_client.messages.create.assert_called_once()

    def test_generate_response_includes_topic_in_prompt(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("I think so.")
        service = LLMService(client=mock_client)
        service.generate_response(
            persona_details=SAMPLE_PERSONA,
            conversation_history=[],
            topic="Climate change policy",
        )
        call_str = str(mock_client.messages.create.call_args)
        assert "Climate change" in call_str or "climate" in call_str.lower()

    def test_generate_response_includes_history_in_prompt(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("I agree with Bob.")
        service = LLMService(client=mock_client)
        history = [{"speaker": "Bob", "message": "We need renewable energy now."}]
        service.generate_response(
            persona_details=SAMPLE_PERSONA,
            conversation_history=history,
            topic="Energy policy",
        )
        call_str = str(mock_client.messages.create.call_args)
        assert "Bob" in call_str or "renewable" in call_str.lower()

    def test_generate_response_strips_whitespace(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("  I agree.  \n")
        service = LLMService(client=mock_client)
        response = service.generate_response(
            persona_details=SAMPLE_PERSONA,
            conversation_history=[],
            topic="Test",
        )
        assert response == response.strip()

    def test_generate_response_with_image_calls_claude_with_vision_payload(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("The design looks good.")

        # Mock ImageGenerationService
        with patch("app.services.image_generation_service.ImageGenerationService") as mock_img_service_cls:
            mock_img_service = mock_img_service_cls.return_value
            mock_img_service.get_image_bytes.return_value = b"fake_bytes"

            service = LLMService(client=mock_client)
            service.generate_response(
                persona_details=SAMPLE_PERSONA,
                conversation_history=[],
                topic="Test",
                image_url="uploads/test.jpg"
            )

            call_args = mock_client.messages.create.call_args[1]
            messages = call_args["messages"]
            content = messages[0]["content"]

            # Should have image and text
            assert any(item["type"] == "image" for item in content)
            assert any(item["type"] == "text" for item in content)

    def test_generate_response_with_image_fetch_failure_continues_with_text_only(self):
        from app.services.llm_service import LLMService
        mock_client = make_mock_client("Text only response.")

        with patch("app.services.image_generation_service.ImageGenerationService") as mock_img_service_cls:
            mock_img_service = mock_img_service_cls.return_value
            mock_img_service.get_image_bytes.side_effect = Exception("Fetch failed")

            service = LLMService(client=mock_client)
            service.generate_response(
                persona_details=SAMPLE_PERSONA,
                conversation_history=[],
                topic="Test",
                image_url="uploads/test.jpg"
            )

            call_args = mock_client.messages.create.call_args[1]
            content = call_args["messages"][0]["content"]

            # Content should only have text if image fetch failed
            assert len(content) == 1
            assert content[0]["type"] == "text"
