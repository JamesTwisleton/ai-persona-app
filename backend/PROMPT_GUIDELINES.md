# Prompt Guidelines for Authentic Persona Responses

To ensure that persona responses in focus groups feel authentic and non-formulaic (avoiding "AI-generated" vibes), we follow these guidelines in our prompt engineering.

## 1. Banned Phrases and Starters

We explicitly ban phrases that are hallmarks of LLM-generated text, especially those that perform unnecessary politeness or use common "filler" starters.

**Banned Hallmarks:**
- **Polite Affirmations:** "Absolutely", "Great point", "I completely agree", "Fascinating perspective".
- **AI-isms:** "As an AI", "It's important to consider all perspectives", "Moving forward".
- **Formulaic Starters:** "Look,", "Listen,", "So,", "Well,", "Actually,", "Honestly,", "I mean,".

The full list is maintained in `backend/app/services/prompt_templates.py` as `BANNED_PHRASES`.

## 2. Encouraging Natural Starters

Instead of formulaic openings, we guide the LLM towards direct and opinionated starts. We provide examples of natural openings to set the tone.

**Examples of Natural Openings:**
- "The problem is..."
- "I disagree because..."
- "From my experience..."
- "What you're missing is..."
- "The reality is..."

These are defined in `NATURAL_STARTERS` within `backend/app/services/prompt_templates.py`.

## 3. System Prompt Constraints

The `CONVERSATION_SYSTEM_PROMPT` in `backend/app/services/llm_service.py` enforces:
- Roleplaying as a specific person with real, sometimes non-diplomatic opinions.
- Avoiding the role of a moderator.
- Sounding like a real human being, not an AI performing balance.
- Explicitly avoiding the formulaic fillers and affirmations mentioned above.

## 4. Response Structure

- **Directness:** Personas must state their own position first, without asking others for their thoughts initially.
- **Brevity:** Responses are kept to 2-3 sentences to ensure they remain dense and impactful.
- **Character-Driven:** Low agreeableness leads to pushing back; high neuroticism leads to anxious or dark tones.

## 5. Testing and Verification

Any changes to prompt templates or system prompts should be verified by:
1. Unit tests in `backend/tests/unit/test_prompt_engineering.py` which check if the generated prompts contain the necessary constraints.
2. Manual review of generated responses in the development environment to ensure the tone remains authentic.
