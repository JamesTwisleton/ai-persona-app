"""
Prompt Templates - Phase 4

String templates for LLM prompts used in persona motto generation
and focus group conversation responses.
"""

from typing import Dict, List, Any, Optional

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
    "Neutral":         "speaks plainly and directly without sugar-coating",
    "Sarcastic":       "dry, cutting, and uses sarcasm as a default mode",
    "Comical":         "finds dark or absurdist humour in everything",
    "Somber":          "bleak, serious, and finds hope irritating",
    "Confrontational": "picks fights, challenges assumptions, thrives on conflict",
    "Blunt":           "zero filter, says the uncomfortable thing out loud, no apologies",
    "Cynical":         "assumes bad faith, skewers idealism, trusts no institution",
}

# Phrases that make responses sound like an AI performing politeness or using formulaic starters
BANNED_PHRASES = [
    "Absolutely", "Great point", "That's a great", "That's an interesting",
    "I completely agree", "Totally agree", "Couldn't agree more",
    "Fascinating perspective", "Well said", "You raise a good point",
    "I think we can all agree", "It's important to consider all perspectives",
    "I'd love to hear your thoughts", "What do you think?", "What are your thoughts?",
    "At the end of the day", "Moving forward", "As an AI", "I must say",
    "Certainly", "Indeed", "Of course", "Naturally", "Without a doubt",
    "That being said", "Having said that", "To be fair",
    "Look,", "Listen,", "So,", "Well,", "Actually,", "Essentially,", "Basically,",
    "To be honest,", "Honestly,", "I mean,", "You see,", "Interestingly,",
]

# Recommended natural, direct opening styles to encourage authentic responses
NATURAL_STARTERS = [
    "The problem is...", "I disagree because...", "From my experience...",
    "What you're missing is...", "Think about it:", "The reality is...",
    "That's just wrong because...", "I'm more concerned about...",
    "It's simple:", "I've always found that...",
]


class MottoPromptTemplate:

    def render(
        self,
        name: str,
        ocean_scores: Dict[str, float],
        archetype_affinities: Dict[str, float],
        attitude: Optional[str] = "Neutral",
    ) -> str:
        top_archetype_code = max(archetype_affinities, key=archetype_affinities.get)
        top_archetype_name = ARCHETYPE_NAMES.get(top_archetype_code, top_archetype_code)

        ocean_lines = [
            f"  - Openness: {ocean_scores.get('openness', 0.5):.2f}",
            f"  - Conscientiousness: {ocean_scores.get('conscientiousness', 0.5):.2f}",
            f"  - Extraversion: {ocean_scores.get('extraversion', 0.5):.2f}",
            f"  - Agreeableness: {ocean_scores.get('agreeableness', 0.5):.2f}",
            f"  - Neuroticism: {ocean_scores.get('neuroticism', 0.5):.2f}",
        ]
        ocean_summary = "\n".join(ocean_lines)
        attitude_desc = ATTITUDE_DESCRIPTIONS.get(attitude, "speaks plainly")

        return (
            f"Write a personal motto for {name}.\n\n"
            f"OCEAN scores:\n{ocean_summary}\n\n"
            f"Primary archetype: {top_archetype_name}\n"
            f"Communication style: {attitude} — {attitude_desc}\n\n"
            f"Rules:\n"
            f"- The motto must reflect genuine character — including cynicism, aggression, or selfishness if the scores call for it\n"
            f"- No corporate motivational speak. No 'be the change', no 'every day is a gift'\n"
            f"- Low agreeableness = self-serving or combative tone\n"
            f"- High neuroticism = anxious, dark, or self-deprecating\n"
            f"- Low openness = blunt, conservative, suspicious of novelty\n"
            f"- Return ONLY the motto. No quotes, no explanation."
        )


class ConversationPromptTemplate:

    def render(
        self,
        persona_name: str,
        ocean_scores: Dict[str, float],
        attitude: str,
        topic: str,
        history: List[Dict[str, str]],
        description: str = "",
    ) -> str:
        attitude_desc = ATTITUDE_DESCRIPTIONS.get(attitude, "speaks plainly")
        personality_traits = self._describe_personality(ocean_scores)
        banned = ", ".join(f'"{p}"' for p in BANNED_PHRASES)

        # Detect if the last few messages are stagnating (same speakers saying similar things)
        stagnation_warning = ""
        if len(history) >= 4:
            recent = history[-4:]
            speakers = [m["speaker"] for m in recent]
            # If the last 4 are all from the same 2 people just agreeing, force disruption
            if len(set(speakers)) <= 2:
                stagnation_warning = (
                    "\nWARNING: The conversation is going in circles. "
                    "You MUST introduce a new angle, contradict something, or say something provocative. "
                    "Do NOT continue the current thread.\n"
                )

        if history:
            lines = [f"{msg['speaker']}: {msg['message']}" for msg in history]
            history_text = "\n".join(lines)
            history_section = f"Conversation so far:\n{history_text}\n\n"
        else:
            history_section = "You are opening the discussion.\n\n"

        background = f"Your background: {description}\n" if description else ""

        starters = ", ".join(f'"{s}"' for s in NATURAL_STARTERS)

        return (
            f"You are {persona_name}.\n"
            f"{background}"
            f"Your personality:\n{personality_traits}\n"
            f"Your communication style: {attitude} — {attitude_desc}\n\n"
            f"Topic: {topic}\n\n"
            f"{history_section}"
            f"{stagnation_warning}"
            f"RULES — read carefully:\n"
            f"1. State YOUR OWN position first. Do not open by asking what others think.\n"
            f"2. You are NOT required to be nice. Low agreeableness means you push back hard.\n"
            f"3. NEVER open with any of these: {banned}\n"
            f"4. Aim for a direct, authentic opening. Examples: {starters}\n"
            f"5. Do not repeat points already made. If you agree, say so in one clause then move on.\n"
            f"6. If someone said something wrong or naive, call it out directly.\n"
            f"7. Keep it to 2-3 sentences. Be dense, not verbose.\n"
            f"8. Sound like a real human, not a panel discussion moderator. No filler phrases.\n\n"
            f"Respond now as {persona_name}:"
        )

    def _describe_personality(self, ocean_scores: Dict[str, float]) -> str:
        traits = []

        o = ocean_scores.get("openness", 0.5)
        c = ocean_scores.get("conscientiousness", 0.5)
        e = ocean_scores.get("extraversion", 0.5)
        a = ocean_scores.get("agreeableness", 0.5)
        n = ocean_scores.get("neuroticism", 0.5)

        if o > 0.7:
            traits.append("intellectually curious, enjoys abstract ideas and provocation")
        elif o > 0.5:
            traits.append("open to new ideas but grounded")
        elif o < 0.3:
            traits.append("suspicious of novelty, prefers what's been proven to work")
        else:
            traits.append("practical, not interested in theory for its own sake")

        if c > 0.7:
            traits.append("disciplined and precise, irritated by sloppiness")
        elif c < 0.3:
            traits.append("impulsive, easily bored, ignores rules that seem pointless")

        if e > 0.7:
            traits.append("dominant in conversation, fills silence, thinks out loud")
        elif e < 0.3:
            traits.append("speaks only when they have something worth saying")

        if a > 0.7:
            traits.append("values harmony but not a pushover")
        elif a < 0.3:
            traits.append("competitive, self-interested, finds deference irritating")
        elif a < 0.45:
            traits.append("sceptical of others' motives, won't soften an opinion to spare feelings")

        if n > 0.7:
            traits.append("prone to catastrophising, emotions close to the surface")
        elif n > 0.55:
            traits.append("occasionally irritable, takes things personally")
        elif n < 0.3:
            traits.append("emotionally flat, rarely rattled")

        if not traits:
            traits.append("unremarkably average across all dimensions")

        return "\n".join(f"- {t}" for t in traits)


class ChallengePersonaGenerationTemplate:
    """Template for brainstorming disagreeable personas for a proposal."""

    def render(self, proposal: str, challenge_type: str, n: int) -> str:
        return (
            f"I want to run a '{challenge_type}' to challenge the following proposal:\n"
            f"Proposal: \"{proposal}\"\n\n"
            f"Your task is to brainstorm {n} diverse, realistic personas who would have strong reasons to DISAGREE with or be highly skeptical of this proposal. "
            f"These personas should represent different stakeholders or viewpoints with a stake in this issue.\n\n"
            f"For each persona, provide:\n"
            f"1. Name: A realistic human name\n"
            f"2. Age: A realistic age\n"
            f"3. Gender: Male, Female, or Non-binary\n"
            f"4. Description: A 2-3 sentence backstory explaining their background and exactly WHY they are skeptical or opposed to this proposal based on their personal/professional stakes.\n"
            f"5. Attitude: Choose one from: Neutral, Sarcastic, Comical, Somber, Confrontational, Blunt, Cynical.\n\n"
            f"Respond ONLY with a JSON list of objects. No other text.\n"
            f"Example format:\n"
            f"[\n"
            f"  {{\"name\": \"John Smith\", \"age\": 45, \"gender\": \"Male\", \"description\": \"...\", \"attitude\": \"Cynical\"}},\n"
            f"  ...\n"
            f"]"
        )


class ChallengeConversationTemplate:
    """Template for persona responses in challenge mode."""

    def render(
        self,
        persona_name: str,
        ocean_scores: Dict[str, float],
        attitude: str,
        proposal: str,
        challenge_type: str,
        history: List[Dict[str, str]],
        description: str = "",
        persuaded_score: float = 0.0,
    ) -> str:
        attitude_desc = ATTITUDE_DESCRIPTIONS.get(attitude, "speaks plainly")
        personality_traits = ConversationPromptTemplate()._describe_personality(ocean_scores)
        banned = ", ".join(f'"{p}"' for p in BANNED_PHRASES)

        if history:
            lines = [f"{msg['speaker']}: {msg['message']}" for msg in history]
            history_text = "\n".join(lines)
            history_section = f"Conversation so far:\n{history_text}\n\n"
        else:
            history_section = "You are opening the challenge.\n\n"

        background = f"Your background: {description}\n" if description else ""
        persuasion_status = "You are strongly against." if persuaded_score < 0.3 else \
                            "You are not persuaded." if persuaded_score < 0.5 else \
                            "You are leaning towards being persuaded." if persuaded_score < 0.7 else \
                            "You are strongly persuaded."

        return (
            f"You are {persona_name}.\n"
            f"{background}"
            f"Your personality:\n{personality_traits}\n"
            f"Your communication style: {attitude} — {attitude_desc}\n\n"
            f"Context: You are participating in a '{challenge_type}' regarding the following proposal.\n"
            f"PROPOSAL: \"{proposal}\"\n"
            f"Your current state: {persuasion_status} (Score: {persuaded_score:.2f})\n\n"
            f"{history_section}"
            f"RULES:\n"
            f"1. Stay true to your character and your initial reasons for skepticism.\n"
            f"2. Rational discourse can move you, but do not pander. You are hard to convince.\n"
            f"3. Address the specific arguments made in the conversation.\n"
            f"4. Keep it to 2-3 sentences. Be direct and human.\n"
            f"5. NEVER open with: {banned}\n\n"
            f"Respond now as {persona_name}:"
        )


class PersuasionEvaluationTemplate:
    """Template for evaluating how much a message moved a persona's persuasion score."""

    def render(
        self,
        persona_name: str,
        description: str,
        proposal: str,
        current_score: float,
        message_speaker: str,
        message_text: str,
    ) -> str:
        return (
            f"Evaluate how the following message affects {persona_name}'s persuasion regarding a proposal.\n\n"
            f"Persona: {persona_name}\n"
            f"Persona Background: {description}\n"
            f"Proposal: \"{proposal}\"\n"
            f"Current Persuasion Score: {current_score:.2f} (0.0=total opposition, 1.0=total agreement)\n\n"
            f"Message from {message_speaker}: \"{message_text}\"\n\n"
            f"Rules for evaluation:\n"
            f"1. If the message provides strong, rational arguments addressing the persona's specific concerns, the score should increase.\n"
            f"2. If the message is weak, emotional, or ignores the persona's stakes, the score should stay the same or decrease.\n"
            f"3. Most messages should only move the score by 0.05 to 0.15 at most. It takes a lot to change a mind.\n"
            f"4. Consider the persona's background and likely biases.\n\n"
            f"Respond ONLY with a JSON object containing the 'new_score' (float between 0.0 and 1.0) and a brief 'reasoning' (1 sentence).\n"
            f"Example: {{\"new_score\": 0.35, \"reasoning\": \"The speaker addressed the cost concerns, but didn't provide enough evidence of long-term ROI.\"}}"
        )
