"""
OCEAN Inference Service Tests - Phase 3B

TDD Phase: RED - Tests written BEFORE the OceanInferenceService exists.

Tests cover:
- Service initialization
- OCEAN trait inference from text description using Claude API (mocked)
- Prompt construction
- Response parsing (valid JSON, edge cases)
- Error handling (API errors, malformed responses)
- Value validation (all scores in [0.0, 1.0])
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestOceanInferenceServiceInit:
    """Test service initialization."""

    def test_service_can_be_instantiated_with_default_client(self):
        """Service can be created without explicitly passing a client."""
        from app.services.ocean_inference import OceanInferenceService

        # When no client is passed, it creates its own (or raises if no API key)
        # We test with an explicit mock to avoid needing a real API key
        mock_client = MagicMock()
        service = OceanInferenceService(client=mock_client)

        assert service is not None

    def test_service_stores_client(self):
        """Service stores the Anthropic client for later use."""
        from app.services.ocean_inference import OceanInferenceService

        mock_client = MagicMock()
        service = OceanInferenceService(client=mock_client)

        assert service.client is mock_client

    def test_service_has_default_model(self):
        """Service has a default Claude model configured."""
        from app.services.ocean_inference import OceanInferenceService

        mock_client = MagicMock()
        service = OceanInferenceService(client=mock_client)

        assert service.model is not None
        assert "claude" in service.model.lower()


class TestOceanPromptConstruction:
    """Test prompt building for OCEAN inference."""

    def test_build_prompt_includes_description(self):
        """The inference prompt contains the persona description."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())
        description = "A methodical engineer who loves spreadsheets and planning"

        prompt = service.build_inference_prompt(description)

        assert description in prompt

    def test_build_prompt_mentions_all_five_ocean_dimensions(self):
        """The prompt references all 5 OCEAN traits."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())
        prompt = service.build_inference_prompt("Test persona description")

        # The prompt should guide Claude on what to measure
        assert "openness" in prompt.lower() or "Openness" in prompt
        assert "conscientiousness" in prompt.lower() or "Conscientiousness" in prompt
        assert "extraversion" in prompt.lower() or "Extraversion" in prompt
        assert "agreeableness" in prompt.lower() or "Agreeableness" in prompt
        assert "neuroticism" in prompt.lower() or "Neuroticism" in prompt

    def test_build_prompt_requests_json_output(self):
        """The prompt instructs Claude to respond with JSON."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())
        prompt = service.build_inference_prompt("Test")

        assert "json" in prompt.lower() or "JSON" in prompt

    def test_build_prompt_specifies_score_range(self):
        """The prompt specifies that scores should be 0.0 to 1.0."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())
        prompt = service.build_inference_prompt("Test")

        assert "0.0" in prompt or "0 to 1" in prompt or "0.0 to 1.0" in prompt


class TestOceanResponseParsing:
    """Test parsing Claude's response into OCEAN scores."""

    def test_parse_valid_json_response(self):
        """Parses a well-formed JSON response into an OCEAN dict."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())

        raw_response = '{"openness": 0.8, "conscientiousness": 0.7, "extraversion": 0.4, "agreeableness": 0.6, "neuroticism": 0.3}'
        result = service.parse_ocean_response(raw_response)

        assert isinstance(result, dict)
        assert result["openness"] == pytest.approx(0.8)
        assert result["conscientiousness"] == pytest.approx(0.7)
        assert result["extraversion"] == pytest.approx(0.4)
        assert result["agreeableness"] == pytest.approx(0.6)
        assert result["neuroticism"] == pytest.approx(0.3)

    def test_parse_response_returns_five_dimensions(self):
        """Parsed result always has exactly 5 OCEAN keys."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())
        raw_response = '{"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5}'

        result = service.parse_ocean_response(raw_response)

        assert set(result.keys()) == {"openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"}

    def test_parse_response_with_markdown_code_block(self):
        """Handles Claude wrapping JSON in markdown code blocks."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())

        raw_response = """```json
{"openness": 0.9, "conscientiousness": 0.8, "extraversion": 0.3, "agreeableness": 0.5, "neuroticism": 0.2}
```"""
        result = service.parse_ocean_response(raw_response)

        assert result["openness"] == pytest.approx(0.9)

    def test_parse_response_clamps_scores_to_valid_range(self):
        """Scores outside [0.0, 1.0] are clamped."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())

        # Malformed scores outside valid range
        raw_response = '{"openness": 1.5, "conscientiousness": -0.1, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5}'
        result = service.parse_ocean_response(raw_response)

        assert 0.0 <= result["openness"] <= 1.0
        assert 0.0 <= result["conscientiousness"] <= 1.0

    def test_parse_invalid_json_raises_value_error(self):
        """Raises ValueError when response is not parseable JSON."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())

        with pytest.raises((ValueError, Exception)):
            service.parse_ocean_response("This is not JSON at all")

    def test_parse_missing_dimensions_raises_value_error(self):
        """Raises ValueError when response is missing required OCEAN keys."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())
        incomplete = '{"openness": 0.5, "conscientiousness": 0.5}'

        with pytest.raises((ValueError, KeyError)):
            service.parse_ocean_response(incomplete)


class TestOceanInference:
    """Test the main infer_ocean_traits method with mocked Claude API."""

    def test_infer_ocean_traits_calls_claude_api(self):
        """infer_ocean_traits calls the Anthropic client."""
        from app.services.ocean_inference import OceanInferenceService

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='{"openness": 0.7, "conscientiousness": 0.6, "extraversion": 0.5, "agreeableness": 0.65, "neuroticism": 0.35}')]
        mock_client.messages.create.return_value = mock_message

        service = OceanInferenceService(client=mock_client)
        result = service.infer_ocean_traits("A thoughtful engineer who plans everything")

        mock_client.messages.create.assert_called_once()

    def test_infer_ocean_traits_returns_valid_scores(self):
        """Returns dict with 5 OCEAN scores in [0.0, 1.0]."""
        from app.services.ocean_inference import OceanInferenceService

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='{"openness": 0.8, "conscientiousness": 0.9, "extraversion": 0.25, "agreeableness": 0.35, "neuroticism": 0.2}')]
        mock_client.messages.create.return_value = mock_message

        service = OceanInferenceService(client=mock_client)
        result = service.infer_ocean_traits("A meticulous data scientist who prefers working alone")

        assert isinstance(result, dict)
        assert len(result) == 5
        for key, val in result.items():
            assert 0.0 <= val <= 1.0, f"{key} = {val} out of range"

    def test_infer_ocean_traits_passes_description_in_prompt(self):
        """The description is included in the API call."""
        from app.services.ocean_inference import OceanInferenceService

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='{"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5}')]
        mock_client.messages.create.return_value = mock_message

        service = OceanInferenceService(client=mock_client)
        description = "A unique description that should appear in the prompt"
        service.infer_ocean_traits(description)

        call_args = mock_client.messages.create.call_args
        # The description should appear in messages or system prompt
        call_str = str(call_args)
        assert description in call_str

    def test_infer_ocean_traits_on_api_error_raises_exception(self):
        """API failure propagates as a clear exception."""
        from app.services.ocean_inference import OceanInferenceService

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API rate limit exceeded")

        service = OceanInferenceService(client=mock_client)

        with pytest.raises(Exception, match="API rate limit exceeded"):
            service.infer_ocean_traits("Test description")

    def test_infer_empty_description_still_calls_api(self):
        """Empty description still calls the API (Claude handles it)."""
        from app.services.ocean_inference import OceanInferenceService

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='{"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5}')]
        mock_client.messages.create.return_value = mock_message

        service = OceanInferenceService(client=mock_client)
        result = service.infer_ocean_traits("")

        mock_client.messages.create.assert_called_once()
        assert isinstance(result, dict)

    def test_infer_ocean_correct_model_used(self):
        """The configured model is passed to the API call."""
        from app.services.ocean_inference import OceanInferenceService

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='{"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5}')]
        mock_client.messages.create.return_value = mock_message

        service = OceanInferenceService(client=mock_client, model="claude-haiku-4-5-20251001")
        service.infer_ocean_traits("Test")

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs.get("model") == "claude-haiku-4-5-20251001"


class TestOceanScoreNormalization:
    """Test that OCEAN scores are properly normalized after inference."""

    def test_scores_converted_to_floats(self):
        """Integer scores from Claude are converted to floats."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())
        # Claude might return integers
        raw_response = '{"openness": 1, "conscientiousness": 0, "extraversion": 1, "agreeableness": 0, "neuroticism": 1}'
        result = service.parse_ocean_response(raw_response)

        for val in result.values():
            assert isinstance(val, float)

    def test_scores_at_boundary_values_accepted(self):
        """Boundary values 0.0 and 1.0 are valid."""
        from app.services.ocean_inference import OceanInferenceService

        service = OceanInferenceService(client=MagicMock())
        raw_response = '{"openness": 0.0, "conscientiousness": 1.0, "extraversion": 0.5, "agreeableness": 0.0, "neuroticism": 1.0}'
        result = service.parse_ocean_response(raw_response)

        assert result["openness"] == pytest.approx(0.0)
        assert result["conscientiousness"] == pytest.approx(1.0)
