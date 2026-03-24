"""
Content Moderation Service Tests - Phase 5 (RED phase)

Tests for ContentModerationService using OpenAI Moderation API.
HTTP calls are mocked — tests run without hitting external APIs.

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest
from unittest.mock import MagicMock, patch


def make_mock_http_client(category_scores: dict, flagged: bool = False):
    """Create a mock httpx client that returns a moderation response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "results": [{
            "flagged": flagged,
            "categories": {k: v > 0.5 for k, v in category_scores.items()},
            "category_scores": category_scores,
        }]
    }
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    return mock_client


SAFE_SCORES = {
    "hate": 0.001,
    "hate/threatening": 0.001,
    "harassment": 0.002,
    "harassment/threatening": 0.001,
    "self-harm": 0.001,
    "self-harm/intent": 0.001,
    "self-harm/instructions": 0.001,
    "sexual": 0.002,
    "sexual/minors": 0.001,
    "violence": 0.003,
    "violence/graphic": 0.001,
}

TOXIC_SCORES = {
    "hate": 0.95,
    "hate/threatening": 0.02,
    "harassment": 0.80,
    "harassment/threatening": 0.01,
    "self-harm": 0.001,
    "self-harm/intent": 0.001,
    "self-harm/instructions": 0.001,
    "sexual": 0.002,
    "sexual/minors": 0.001,
    "violence": 0.003,
    "violence/graphic": 0.001,
}


# ============================================================================
# ContentModerationService Initialization
# ============================================================================

class TestContentModerationServiceInit:

    def test_init_with_injected_client(self):
        from app.services.content_moderation_service import ContentModerationService
        mock_client = MagicMock()
        service = ContentModerationService(http_client=mock_client)
        assert service.http_client is mock_client

    def test_default_threshold(self):
        from app.services.content_moderation_service import ContentModerationService
        from app.config import settings
        mock_client = MagicMock()
        service = ContentModerationService(http_client=mock_client)
        assert service.threshold == settings.TOXICITY_THRESHOLD

    def test_custom_threshold(self):
        from app.services.content_moderation_service import ContentModerationService
        mock_client = MagicMock()
        service = ContentModerationService(http_client=mock_client, threshold=0.5)
        assert service.threshold == 0.5


# ============================================================================
# analyze_toxicity Tests
# ============================================================================

class TestAnalyzeToxicity:

    def test_safe_content_returns_low_score(self):
        from app.services.content_moderation_service import ContentModerationService
        mock_client = make_mock_http_client(SAFE_SCORES, flagged=False)
        service = ContentModerationService(http_client=mock_client)
        score = service.analyze_toxicity("I think we should discuss this thoughtfully.")
        assert isinstance(score, float)
        assert score < 0.1

    def test_toxic_content_returns_high_score(self):
        from app.services.content_moderation_service import ContentModerationService
        mock_client = make_mock_http_client(TOXIC_SCORES, flagged=True)
        service = ContentModerationService(http_client=mock_client)
        score = service.analyze_toxicity("Some hateful content here.")
        assert score > 0.7

    def test_score_is_max_of_all_categories(self):
        from app.services.content_moderation_service import ContentModerationService
        mock_client = make_mock_http_client(TOXIC_SCORES, flagged=True)
        service = ContentModerationService(http_client=mock_client)
        score = service.analyze_toxicity("Test")
        assert score == pytest.approx(max(TOXIC_SCORES.values()))

    def test_calls_openai_moderation_endpoint(self):
        from app.services.content_moderation_service import ContentModerationService
        mock_client = make_mock_http_client(SAFE_SCORES)
        service = ContentModerationService(http_client=mock_client)
        service.analyze_toxicity("Hello world")
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "moderation" in str(call_args).lower() or "openai" in str(call_args).lower()

    def test_returns_float_between_0_and_1(self):
        from app.services.content_moderation_service import ContentModerationService
        mock_client = make_mock_http_client(SAFE_SCORES)
        service = ContentModerationService(http_client=mock_client)
        score = service.analyze_toxicity("Neutral text")
        assert 0.0 <= score <= 1.0

    def test_api_failure_returns_high_score_fail_safe(self):
        """On API failure, fail safe by returning a high toxicity score."""
        from app.services.content_moderation_service import ContentModerationService
        mock_client = MagicMock()
        mock_client.post.side_effect = Exception("Connection refused")
        service = ContentModerationService(http_client=mock_client)
        score = service.analyze_toxicity("Test text")
        assert score >= 0.9

    def test_sends_text_in_request(self):
        from app.services.content_moderation_service import ContentModerationService
        mock_client = make_mock_http_client(SAFE_SCORES)
        service = ContentModerationService(http_client=mock_client)
        service.analyze_toxicity("A very specific test phrase")
        call_str = str(mock_client.post.call_args)
        assert "A very specific test phrase" in call_str


# ============================================================================
# is_safe Tests
# ============================================================================

class TestIsSafe:

    def test_low_score_is_safe(self):
        from app.services.content_moderation_service import ContentModerationService
        service = ContentModerationService(http_client=MagicMock(), threshold=0.7)
        assert service.is_safe(0.1) is True

    def test_high_score_is_not_safe(self):
        from app.services.content_moderation_service import ContentModerationService
        service = ContentModerationService(http_client=MagicMock(), threshold=0.7)
        assert service.is_safe(0.8) is False

    def test_score_at_threshold_is_not_safe(self):
        from app.services.content_moderation_service import ContentModerationService
        service = ContentModerationService(http_client=MagicMock(), threshold=0.7)
        assert service.is_safe(0.7) is False

    def test_custom_threshold(self):
        from app.services.content_moderation_service import ContentModerationService
        service = ContentModerationService(http_client=MagicMock(), threshold=0.5)
        assert service.is_safe(0.49) is True
        assert service.is_safe(0.51) is False
