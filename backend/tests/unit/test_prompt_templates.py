"""
Prompt Templates Tests - Phase 4 (RED phase)

Tests for MottoPromptTemplate and ConversationPromptTemplate.

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest
from app.services.prompt_templates import MottoPromptTemplate, ConversationPromptTemplate


SAMPLE_OCEAN = {
    "openness": 0.8,
    "conscientiousness": 0.7,
    "extraversion": 0.4,
    "agreeableness": 0.6,
    "neuroticism": 0.3,
}

SAMPLE_AFFINITIES = {
    "ANA": 0.35,
    "SOC": 0.10,
    "INN": 0.25,
    "PRA": 0.10,
    "REB": 0.08,
    "CUS": 0.05,
    "EMP": 0.05,
    "CAT": 0.02,
}


# ============================================================================
# MottoPromptTemplate Tests
# ============================================================================

class TestMottoPromptTemplate:
    """Tests for motto generation prompt construction."""

    def test_render_includes_persona_name(self):
        template = MottoPromptTemplate()
        prompt = template.render(
            name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            archetype_affinities=SAMPLE_AFFINITIES,
        )
        assert "Alice" in prompt

    def test_render_includes_ocean_scores(self):
        template = MottoPromptTemplate()
        prompt = template.render(
            name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            archetype_affinities=SAMPLE_AFFINITIES,
        )
        # Should mention OCEAN traits in some form
        assert "openness" in prompt.lower() or "0.8" in prompt

    def test_render_includes_attitude(self):
        template = MottoPromptTemplate()
        prompt = template.render(
            name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            archetype_affinities=SAMPLE_AFFINITIES,
            attitude="Sarcastic",
        )
        assert "Sarcastic" in prompt or "sarcastic" in prompt.lower()

    def test_render_includes_top_archetype(self):
        template = MottoPromptTemplate()
        prompt = template.render(
            name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            archetype_affinities=SAMPLE_AFFINITIES,
        )
        # Top archetype is "ANA" (Analyst) with 0.35
        assert "ANA" in prompt or "Analyst" in prompt or "analyst" in prompt.lower()

    def test_render_returns_string(self):
        template = MottoPromptTemplate()
        prompt = template.render(
            name="Bob",
            ocean_scores=SAMPLE_OCEAN,
            archetype_affinities=SAMPLE_AFFINITIES,
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 50

    def test_render_neutral_attitude_default(self):
        """Neutral is the default attitude."""
        template = MottoPromptTemplate()
        prompt = template.render(
            name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            archetype_affinities=SAMPLE_AFFINITIES,
        )
        assert isinstance(prompt, str)

    def test_render_instructions_request_short_motto(self):
        """Prompt should instruct Claude to return a short motto."""
        template = MottoPromptTemplate()
        prompt = template.render(
            name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            archetype_affinities=SAMPLE_AFFINITIES,
        )
        # Prompt should ask for something concise
        assert any(word in prompt.lower() for word in ["short", "concise", "brief", "motto", "single"])


# ============================================================================
# ConversationPromptTemplate Tests
# ============================================================================

class TestConversationPromptTemplate:
    """Tests for conversation response prompt construction."""

    def test_render_includes_persona_name(self):
        template = ConversationPromptTemplate()
        prompt = template.render(
            persona_name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            attitude="Neutral",
            topic="Should we colonize Mars?",
            history=[],
        )
        assert "Alice" in prompt

    def test_render_includes_topic(self):
        template = ConversationPromptTemplate()
        prompt = template.render(
            persona_name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            attitude="Neutral",
            topic="Should we colonize Mars?",
            history=[],
        )
        assert "Mars" in prompt or "colonize" in prompt.lower()

    def test_render_includes_conversation_history(self):
        template = ConversationPromptTemplate()
        history = [
            {"speaker": "Bob", "message": "I think Mars colonization is dangerous."},
            {"speaker": "Carol", "message": "But the long-term benefits are enormous."},
        ]
        prompt = template.render(
            persona_name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            attitude="Neutral",
            topic="Should we colonize Mars?",
            history=history,
        )
        assert "Bob" in prompt
        assert "dangerous" in prompt
        assert "Carol" in prompt

    def test_render_empty_history_works(self):
        """Empty history produces valid prompt."""
        template = ConversationPromptTemplate()
        prompt = template.render(
            persona_name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            attitude="Neutral",
            topic="Climate change",
            history=[],
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 50

    def test_render_includes_attitude(self):
        template = ConversationPromptTemplate()
        prompt = template.render(
            persona_name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            attitude="Comical",
            topic="Climate change",
            history=[],
        )
        assert "Comical" in prompt or "comical" in prompt.lower() or "humor" in prompt.lower()

    def test_render_includes_ocean_personality(self):
        """Prompt should encode personality characteristics."""
        template = ConversationPromptTemplate()
        prompt = template.render(
            persona_name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            attitude="Neutral",
            topic="Climate change",
            history=[],
        )
        # Should reference personality/traits in some form
        assert any(word in prompt.lower() for word in ["personality", "trait", "open", "conscientious", "character"])

    def test_render_includes_reddit_flair(self):
        template = ConversationPromptTemplate()
        prompt = template.render(
            persona_name="Alice",
            ocean_scores=SAMPLE_OCEAN,
            attitude="Neutral",
            topic="Climate change",
            history=[],
            reddit_flair="Logic > Emotions"
        )
        assert "Reddit flair" in prompt
        assert "Logic > Emotions" in prompt

    def test_render_returns_string(self):
        template = ConversationPromptTemplate()
        prompt = template.render(
            persona_name="Dave",
            ocean_scores=SAMPLE_OCEAN,
            attitude="Somber",
            topic="AI ethics",
            history=[],
        )
        assert isinstance(prompt, str)
