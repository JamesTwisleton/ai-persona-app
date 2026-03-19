"""
Prompt Templates - Phase 4

String templates for LLM prompts used in persona motto generation
and focus group conversation responses.

TDD Status:
- Tests written first in: tests/unit/test_prompt_templates.py
- This implementation makes those tests GREEN

Classes:
- MottoPromptTemplate: Generates a prompt to create a personal motto
- ConversationPromptTemplate: Generates a prompt for a conversation turn
"""

from typing import Dict, List, Any, Optional

# Archetype code → display name mapping
ARCHETYPE_NAMES = {
    "ANALYST": "The Analyst",
    "SOCIALITE": "The Socialite",
    "INNOVATOR": "The Innovator",
    "ACTIVIST": "The Activist",
    "PRAGMATIST": "The Pragmatist",
    "TRADITIONALIST": "The Traditionalist",
    "SKEPTIC": "The Skeptic",
    "OPTIMIST": "The Optimist",
}

ATTITUDE_DESCRIPTIONS = {
    "Neutral": "thoughtful and balanced",
    "Sarcastic": "witty and sarcastic",
    "Comical": "humorous and lighthearted",
    "Somber": "serious and reflective",
}


class MottoPromptTemplate:
    """
    Builds a prompt asking Claude to generate a short personal motto
    for a given persona based on their OCEAN traits and archetype affinities.

    Usage:
        template = MottoPromptTemplate()
        prompt = template.render(
            name="Alice",
            ocean_scores={"openness": 0.8, ...},
            archetype_affinities={"ANA": 0.35, ...},
            attitude="Neutral",
        )
        # prompt is a string ready to be sent to Claude
    """

    def render(
        self,
        name: str,
        ocean_scores: Dict[str, float],
        archetype_affinities: Dict[str, float],
        attitude: Optional[str] = "Neutral",
    ) -> str:
        """
        Build the user message for motto generation.

        Args:
            name: Persona's name
            ocean_scores: Dict of OCEAN trait scores (0.0–1.0)
            archetype_affinities: Dict of archetype code → affinity score
            attitude: Response style (Neutral, Sarcastic, Comical, Somber)

        Returns:
            str: Formatted prompt for Claude
        """
        # Find top archetype
        top_archetype_code = max(archetype_affinities, key=archetype_affinities.get)
        top_archetype_name = ARCHETYPE_NAMES.get(top_archetype_code, top_archetype_code)
        top_affinity = archetype_affinities[top_archetype_code]

        # Build OCEAN summary
        ocean_lines = [
            f"  - Openness: {ocean_scores.get('openness', 0.5):.2f}",
            f"  - Conscientiousness: {ocean_scores.get('conscientiousness', 0.5):.2f}",
            f"  - Extraversion: {ocean_scores.get('extraversion', 0.5):.2f}",
            f"  - Agreeableness: {ocean_scores.get('agreeableness', 0.5):.2f}",
            f"  - Neuroticism: {ocean_scores.get('neuroticism', 0.5):.2f}",
        ]
        ocean_summary = "\n".join(ocean_lines)

        attitude_desc = ATTITUDE_DESCRIPTIONS.get(attitude, "thoughtful and balanced")

        return (
            f"Create a short personal motto for a persona named {name}.\n\n"
            f"Their personality profile:\n"
            f"OCEAN trait scores (0.0 = low, 1.0 = high):\n"
            f"{ocean_summary}\n\n"
            f"Primary archetype: {top_archetype_name} ({top_archetype_code}, affinity={top_affinity:.2f})\n"
            f"Communication style: {attitude} ({attitude_desc})\n\n"
            f"Write a concise, single-sentence motto that reflects this persona's character. "
            f"The motto should sound authentic to someone who is {attitude_desc}. "
            f"Return only the motto text itself, with no explanation or quotation marks."
        )


class ConversationPromptTemplate:
    """
    Builds a system + user prompt for a persona's response in a focus group.

    The system prompt establishes the persona's identity and personality.
    The user prompt provides the conversation context and asks for a response.

    Usage:
        template = ConversationPromptTemplate()
        system, user = template.render(
            persona_name="Alice",
            ocean_scores={"openness": 0.8, ...},
            attitude="Neutral",
            topic="Should we colonize Mars?",
            history=[{"speaker": "Bob", "message": "I think..."}],
        )
    """

    def render(
        self,
        persona_name: str,
        ocean_scores: Dict[str, float],
        attitude: str,
        topic: str,
        history: List[Dict[str, str]],
    ) -> str:
        """
        Build the full conversation prompt.

        Args:
            persona_name: Name of the persona responding
            ocean_scores: OCEAN trait scores for this persona
            attitude: Response style (Neutral, Sarcastic, Comical, Somber)
            topic: Focus group discussion topic
            history: List of prior messages [{"speaker": ..., "message": ...}]

        Returns:
            str: Combined prompt string (system + conversation context)
        """
        attitude_desc = ATTITUDE_DESCRIPTIONS.get(attitude, "thoughtful and balanced")

        # Personality characterization based on OCEAN scores
        personality_traits = self._describe_personality(ocean_scores)

        # Format conversation history
        history_text = ""
        if history:
            lines = [
                f"{msg['speaker']}: {msg['message']}"
                for msg in history
            ]
            history_text = "\n".join(lines)
            history_section = f"Conversation so far:\n{history_text}\n\n"
        else:
            history_section = "This is the start of the discussion.\n\n"

        return (
            f"You are {persona_name}, a participant in a focus group.\n\n"
            f"Your personality traits:\n{personality_traits}\n"
            f"Your communication style is {attitude} ({attitude_desc}).\n\n"
            f"Discussion topic: {topic}\n\n"
            f"{history_section}"
            f"Respond as {persona_name} in 2-4 sentences. Stay in character."
        )

    def _describe_personality(self, ocean_scores: Dict[str, float]) -> str:
        """
        Convert OCEAN scores into human-readable personality descriptors.

        Args:
            ocean_scores: Dict of trait name → float score

        Returns:
            str: Bulleted personality description
        """
        traits = []

        o = ocean_scores.get("openness", 0.5)
        c = ocean_scores.get("conscientiousness", 0.5)
        e = ocean_scores.get("extraversion", 0.5)
        a = ocean_scores.get("agreeableness", 0.5)
        n = ocean_scores.get("neuroticism", 0.5)

        if o > 0.6:
            traits.append("open to new ideas and intellectually curious")
        elif o < 0.4:
            traits.append("practical and conventional in thinking")

        if c > 0.6:
            traits.append("organized, disciplined, and goal-oriented")
        elif c < 0.4:
            traits.append("flexible and spontaneous")

        if e > 0.6:
            traits.append("outgoing and energetic in social situations")
        elif e < 0.4:
            traits.append("reserved and thoughtful before speaking")

        if a > 0.6:
            traits.append("cooperative and considerate of others' feelings")
        elif a < 0.4:
            traits.append("direct and competitive")

        if n > 0.6:
            traits.append("emotionally sensitive and prone to anxiety")
        elif n < 0.4:
            traits.append("emotionally stable and resilient")

        if not traits:
            traits.append("balanced across all personality dimensions")

        return "\n".join(f"- {t}" for t in traits)
