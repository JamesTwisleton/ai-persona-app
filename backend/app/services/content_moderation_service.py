"""
Content Moderation Service - Phase 5

Checks text content against the OpenAI Moderation API and returns a
toxicity score. On API failure, fails safe (returns high score = blocked).

TDD Status:
- Tests written first in: tests/unit/test_content_moderation_service.py
- This implementation makes those tests GREEN

Usage:
    from app.services.content_moderation_service import ContentModerationService

    service = ContentModerationService()
    score = service.analyze_toxicity("Some text to check")
    if not service.is_safe(score):
        raise HTTPException(400, "Content failed moderation")
"""

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OPENAI_MODERATION_URL = "https://api.openai.com/v1/moderations"
DEFAULT_THRESHOLD = 0.7
FAIL_SAFE_SCORE = 1.0  # Returned when moderation API is unavailable


class ContentModerationService:
    """
    Wraps the OpenAI Moderation API to check text for harmful content.

    Returns a toxicity score in [0.0, 1.0] (max across all categories).
    On API failure, returns FAIL_SAFE_SCORE (1.0) to block content.

    Args:
        http_client: httpx.Client instance. If None, creates one from env vars.
        threshold: Toxicity score at or above which content is considered unsafe.
    """

    def __init__(
        self,
        http_client: Optional[httpx.Client] = None,
        threshold: Optional[float] = None,
    ):
        if threshold is None:
            threshold = settings.TOXICITY_THRESHOLD
        if http_client is not None:
            self.http_client = http_client
        else:
            self.http_client = httpx.Client(
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                timeout=10.0,
            )
        self.threshold = threshold

    def analyze_toxicity(self, text: str) -> float:
        """
        Send text to OpenAI Moderation API and return max category score.

        Args:
            text: The text content to moderate

        Returns:
            float: Toxicity score in [0.0, 1.0].
                   Returns 1.0 (fail safe) on API error.
        """
        try:
            response = self.http_client.post(
                OPENAI_MODERATION_URL,
                json={"input": text},
            )
            response.raise_for_status()
            data = response.json()
            category_scores = data["results"][0]["category_scores"]
            return float(max(category_scores.values()))

        except Exception as e:
            logger.error(f"Content moderation API failed, failing safe: {e}")
            return FAIL_SAFE_SCORE

    def is_safe(self, toxicity_score: float) -> bool:
        """
        Determine if a toxicity score is below the safety threshold.

        Args:
            toxicity_score: Score from analyze_toxicity()

        Returns:
            bool: True if content is safe, False if it should be blocked
        """
        return toxicity_score < self.threshold
