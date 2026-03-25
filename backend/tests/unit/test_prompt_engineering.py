import pytest
from app.services.prompt_templates import ConversationPromptTemplate, BANNED_PHRASES, NATURAL_STARTERS

def test_conversation_prompt_includes_banned_phrases():
    template = ConversationPromptTemplate()
    persona_details = {
        "name": "Alice",
        "ocean_scores": {"openness": 0.8, "conscientiousness": 0.7, "extraversion": 0.4, "agreeableness": 0.6, "neuroticism": 0.3},
        "attitude": "Neutral",
        "description": "A thoughtful scientist"
    }

    prompt = template.render(
        persona_name=persona_details["name"],
        ocean_scores=persona_details["ocean_scores"],
        attitude=persona_details["attitude"],
        topic="Climate Change",
        history=[],
        description=persona_details["description"]
    )

    # Check if "Look," is in the prompt (it's in the expanded BANNED_PHRASES)
    assert '"Look,"' in prompt

    # Check if more than just the first 12 are included
    for phrase in BANNED_PHRASES:
        assert f'"{phrase}"' in prompt

def test_conversation_prompt_includes_natural_starters():
    template = ConversationPromptTemplate()
    persona_details = {
        "name": "Alice",
        "ocean_scores": {"openness": 0.8, "conscientiousness": 0.7, "extraversion": 0.4, "agreeableness": 0.6, "neuroticism": 0.3},
        "attitude": "Neutral",
        "description": "A thoughtful scientist"
    }

    prompt = template.render(
        persona_name=persona_details["name"],
        ocean_scores=persona_details["ocean_scores"],
        attitude=persona_details["attitude"],
        topic="Climate Change",
        history=[],
        description=persona_details["description"]
    )

    # Check if NATURAL_STARTERS examples are in the prompt
    for starter in NATURAL_STARTERS:
        assert f'"{starter}"' in prompt

    # Check for the rule about natural opening
    assert "Aim for a direct, authentic opening" in prompt

def test_conversation_prompt_rules_updated():
    template = ConversationPromptTemplate()
    persona_details = {
        "name": "Alice",
        "ocean_scores": {"openness": 0.8, "conscientiousness": 0.7, "extraversion": 0.4, "agreeableness": 0.6, "neuroticism": 0.3},
        "attitude": "Neutral",
        "description": "A thoughtful scientist"
    }

    prompt = template.render(
        persona_name=persona_details["name"],
        ocean_scores=persona_details["ocean_scores"],
        attitude=persona_details["attitude"],
        topic="Climate Change",
        history=[],
        description=persona_details["description"]
    )

    # Verify the specific rule number for authentic opening exists
    assert "4. Aim for a direct, authentic opening." in prompt
    # Verify the no filler phrases rule
    assert "No filler phrases." in prompt
