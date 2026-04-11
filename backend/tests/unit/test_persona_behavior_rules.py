import pytest
from app.services.prompt_templates import (
    ConversationPromptTemplate,
    ChallengeConversationTemplate,
    ChallengePersonaGenerationTemplate,
    ATTITUDE_DESCRIPTIONS
)

def test_conversation_template_ai_defense():
    """Verify that ConversationPromptTemplate includes AI-defense rules."""
    template = ConversationPromptTemplate()
    prompt = template.render(
        persona_name="Alice",
        ocean_scores={"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5},
        attitude="Neutral",
        topic="General",
        history=[]
    )
    assert "If someone suggests you are an AI" in prompt
    assert "respond in-character" in prompt

def test_conversation_template_active_listening():
    """Verify that ConversationPromptTemplate includes active listening instructions."""
    template = ConversationPromptTemplate()
    prompt = template.render(
        persona_name="Alice",
        ocean_scores={"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5},
        attitude="Neutral",
        topic="General",
        history=[{"speaker": "Bob", "message": "I think this is good."}]
    )
    assert "Acknowledge and briefly address the previous speaker's points" in prompt
    assert "Active Listening" in prompt

def test_challenge_conversation_active_listening():
    """Verify that ChallengeConversationTemplate includes active listening instructions."""
    template = ChallengeConversationTemplate()
    prompt = template.render(
        persona_name="Bob",
        ocean_scores={"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5},
        attitude="Neutral",
        proposal="Build a bridge",
        challenge_type="Persuasion",
        history=[{"speaker": "User", "message": "It will help people."}]
    )
    assert "Acknowledge the previous speaker's point" in prompt
    assert "Active Listening" in prompt
    assert "NEVER use personal insults" in prompt

def test_challenge_persona_generation_skeptical_framing():
    """Verify that ChallengePersonaGenerationTemplate uses skeptical rather than combative framing."""
    template = ChallengePersonaGenerationTemplate()
    prompt = template.render(proposal="New tax", challenge_type="Stress Test", n=3)
    assert "skeptical or currently unconvinced" in prompt
    assert "legitimate stake" in prompt
    assert "highly disagreeable" not in prompt.lower()
    assert "opposed to this proposal" not in prompt

def test_attitude_descriptions_respectful():
    """Verify that potentially hostile attitudes now emphasize respect or focus on ideas."""
    assert "never attacks people personally" in ATTITUDE_DESCRIPTIONS["Confrontational"]
    assert "remains professional" in ATTITUDE_DESCRIPTIONS["Blunt"]
    assert "structural flaws rather than personal character" in ATTITUDE_DESCRIPTIONS["Cynical"]

def test_conversation_template_natural_speech():
    """Verify that ConversationPromptTemplate includes natural speech instructions."""
    template = ConversationPromptTemplate()
    prompt = template.render(
        persona_name="Charlie",
        ocean_scores={"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5},
        attitude="Neutral",
        topic="General",
        history=[]
    )
    assert "Use natural speech patterns" in prompt
    assert "hesitations" in prompt
    assert "personal anecdotes" in prompt
