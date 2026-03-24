"""
OCEAN Inference Service - Phase 3B

Uses Claude API to infer OCEAN personality trait scores from a persona description.

The service sends the description to Claude with a structured prompt that asks
for all five OCEAN dimensions scored between 0.0 and 1.0, returned as JSON.

TDD Status:
- Tests written first in: tests/unit/test_ocean_inference_service.py
- This implementation makes those tests GREEN

Usage:
    from app.services.ocean_inference import OceanInferenceService

    service = OceanInferenceService()  # Uses ANTHROPIC_API_KEY from env
    scores = service.infer_ocean_traits("A meticulous planner who loves data")
    # Returns: {"openness": 0.6, "conscientiousness": 0.9, ...}
"""

import json
import re
from typing import Optional, Dict

from app.config import settings

# Default model for OCEAN inference - Haiku is fast and cheap for structured extraction
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

OCEAN_KEYS = {"openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"}

INFERENCE_SYSTEM_PROMPT = """You are a psychologist specializing in the Big Five (OCEAN) personality model.
Given a description of a person, infer their personality trait scores on all five OCEAN dimensions.

Score each dimension from 0.0 (extremely low) to 1.0 (extremely high):
- openness: Curiosity, creativity, preference for novelty and variety
- conscientiousness: Organization, dependability, self-discipline, goal-directed behavior
- extraversion: Sociability, assertiveness, positive emotionality, energy from social interaction
- agreeableness: Cooperation, trust, empathy, concern for others' well-being
- neuroticism: Emotional instability, anxiety, moodiness, tendency toward negative emotions

Respond ONLY with a JSON object containing exactly these five keys with float values between 0.0 and 1.0.
Do not include any explanation or commentary - only the JSON object.

Example response format:
{"openness": 0.7, "conscientiousness": 0.8, "extraversion": 0.4, "agreeableness": 0.6, "neuroticism": 0.3}"""


class OceanInferenceService:
    """
    Infers OCEAN personality scores from a text description using Claude.

    All five OCEAN dimensions (Openness, Conscientiousness, Extraversion,
    Agreeableness, Neuroticism) are returned as floats in [0.0, 1.0].

    External API calls are made to Anthropic's Messages API. In tests,
    pass a mock client to avoid real API calls.

    Args:
        client: Anthropic client instance. If None, creates one from env vars.
        model: Claude model ID to use for inference.
    """

    def __init__(self, client=None, model: str = DEFAULT_MODEL):
        if client is not None:
            self.client = client
        else:
            # Lazy import to avoid requiring anthropic package unless needed
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        self.model = model

    def build_inference_prompt(self, description: str) -> str:
        """
        Build the user message for OCEAN inference.

        The system prompt contains the full task instructions.
        This method returns the user-facing content.

        Args:
            description: Persona description/backstory text

        Returns:
            str: Formatted user message for Claude
        """
        if not description:
            description = "No description provided. Use neutral/average scores."

        return (
            f"Please analyze the following persona description and provide OCEAN personality scores "
            f"as a JSON object with scores from 0.0 to 1.0:\n\n"
            f'"{description}"\n\n'
            f"Respond with only the JSON object containing: openness, conscientiousness, "
            f"extraversion, agreeableness, neuroticism"
        )

    def parse_ocean_response(self, response_text: str) -> Dict[str, float]:
        """
        Parse Claude's response text into an OCEAN scores dict.

        Handles:
        - Plain JSON responses
        - JSON wrapped in markdown code blocks (```json ... ```)
        - Integer values (converts to float)
        - Out-of-range values (clamps to [0.0, 1.0])

        Args:
            response_text: Raw text from Claude's response

        Returns:
            dict: {"openness": float, "conscientiousness": float, ...}

        Raises:
            ValueError: If response cannot be parsed or is missing required keys
        """
        # Strip markdown code blocks if present
        cleaned = response_text.strip()
        # Match ```json ... ``` or ``` ... ```
        code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if code_block_match:
            cleaned = code_block_match.group(1)
        else:
            # Find first JSON object in the response
            json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse OCEAN response as JSON: {e}\nResponse: {response_text!r}")

        # Validate all required keys are present
        missing = OCEAN_KEYS - set(data.keys())
        if missing:
            raise KeyError(f"OCEAN response missing required keys: {missing}")

        # Convert to floats and clamp to [0.0, 1.0]
        result = {}
        for key in OCEAN_KEYS:
            try:
                val = float(data[key])
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid value for {key}: {data[key]!r}") from e
            result[key] = max(0.0, min(1.0, val))

        return result

    def infer_ocean_traits(self, description: str) -> Dict[str, float]:
        """
        Infer OCEAN personality scores from a persona description.

        Makes a synchronous call to the Claude API. For production use in
        async FastAPI endpoints, run in a thread pool executor.

        Args:
            description: Persona backstory or description text

        Returns:
            dict: {"openness": float, "conscientiousness": float,
                   "extraversion": float, "agreeableness": float,
                   "neuroticism": float}

        Raises:
            Exception: Re-raises any API errors from Anthropic client
            ValueError: If response cannot be parsed into valid OCEAN scores
        """
        user_message = self.build_inference_prompt(description)

        # Call the Anthropic Messages API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            system=INFERENCE_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ],
        )

        # Extract text from response
        response_text = message.content[0].text

        return self.parse_ocean_response(response_text)
