"""
LLM Service - Phase 4

Uses Claude API to generate persona mottos and conversation responses.

Follows the same injectable-client pattern as OceanInferenceService so
that tests can pass a mock client without hitting the real API.

TDD Status:
- Tests written first in: tests/unit/test_llm_service.py
- This implementation makes those tests GREEN

Usage:
    from app.services.llm_service import LLMService

    service = LLMService()  # Uses ANTHROPIC_API_KEY from env
    motto = service.generate_motto(persona_details)
    response = service.generate_response(persona_details, history, topic)
"""

from typing import Dict, List, Any, Optional

from app.config import settings
from app.services.prompt_templates import MottoPromptTemplate, ConversationPromptTemplate

# Use a capable but cost-effective model for generation tasks
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

MOTTO_SYSTEM_PROMPT = (
    "You are a creative writer specializing in personal branding and self-expression. "
    "When given a personality profile, you craft authentic, memorable personal mottos. "
    "You respond with only the motto text — no explanations, no quotation marks, no punctuation beyond the motto itself."
)

CONVERSATION_SYSTEM_PROMPT = (
    "You are roleplaying as a specific persona in a focus group discussion. "
    "Stay completely in character. Respond naturally and authentically based on the personality traits provided. "
    "Keep responses concise (2-4 sentences) and conversational."
)


class LLMService:
    """
    Generates persona mottos and conversation responses via Claude.

    All Claude API calls are made synchronously. For production async use,
    run in a thread pool executor.

    Args:
        client: Anthropic client instance. If None, creates one from env vars.
        model: Claude model ID to use.
    """

    def __init__(self, client=None, model: str = DEFAULT_MODEL):
        if client is not None:
            self.client = client
        else:
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        self.model = model
        self._motto_template = MottoPromptTemplate()
        self._conversation_template = ConversationPromptTemplate()

    def generate_motto(self, persona_details: Dict[str, Any]) -> str:
        """
        Generate a short personal motto for a persona.

        Args:
            persona_details: Dict with keys:
                - name (str)
                - ocean_scores (dict)
                - archetype_affinities (dict)
                - attitude (str, optional)

        Returns:
            str: Generated motto, stripped of surrounding whitespace and quotes

        Raises:
            Exception: Re-raises any Anthropic API errors
        """
        user_message = self._motto_template.render(
            name=persona_details.get("name", "Unknown"),
            ocean_scores=persona_details.get("ocean_scores", {}),
            archetype_affinities=persona_details.get("archetype_affinities", {}),
            attitude=persona_details.get("attitude", "Neutral"),
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=128,
            system=MOTTO_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = message.content[0].text.strip()
        # Strip surrounding quotation marks if Claude added them
        return raw.strip('"').strip("'").strip()

    def generate_response(
        self,
        persona_details: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        topic: str,
    ) -> str:
        """
        Generate a conversation response for a persona in a focus group.

        Args:
            persona_details: Dict with name, ocean_scores, attitude, etc.
            conversation_history: List of {"speaker": ..., "message": ...} dicts
            topic: The focus group discussion topic

        Returns:
            str: Generated response text, stripped of whitespace

        Raises:
            Exception: Re-raises any Anthropic API errors
        """
        user_message = self._conversation_template.render(
            persona_name=persona_details.get("name", "Participant"),
            ocean_scores=persona_details.get("ocean_scores", {}),
            attitude=persona_details.get("attitude", "Neutral"),
            topic=topic,
            history=conversation_history,
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=CONVERSATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        return message.content[0].text.strip()
