"""
Reddit Flair generation tests.
"""

import pytest
from unittest.mock import MagicMock
from app.services.llm_service import LLMService

def make_mock_client(response_text: str):
    mock_content = MagicMock()
    mock_content.text = response_text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client

class TestRedditFlair:

    def test_generate_reddit_flair_returns_string(self):
        mock_client = make_mock_client("Logic Scientist")
        service = LLMService(client=mock_client)
        flair = service.generate_reddit_flair("A logic-driven data scientist")
        assert isinstance(flair, str)
        assert flair == "Logic Scientist"

    def test_generate_reddit_flair_calls_claude_api(self):
        mock_client = make_mock_client("Chaos Architect")
        service = LLMService(client=mock_client)
        service.generate_reddit_flair("An edgy street artist")
        mock_client.messages.create.assert_called_once()

    def test_generate_reddit_flair_strips_quotes(self):
        mock_client = make_mock_client('"The Realist"')
        service = LLMService(client=mock_client)
        flair = service.generate_reddit_flair("A pragmatic person")
        assert flair == "The Realist"

    def test_generate_reddit_flair_handles_empty_description(self):
        mock_client = make_mock_client("Mysterious User")
        service = LLMService(client=mock_client)
        flair = service.generate_reddit_flair("")
        assert flair == "Mysterious User"

        call_kwargs = mock_client.messages.create.call_args
        assert "mysterious" in str(call_kwargs).lower()
