"""
Conversation Orchestrator - Phase 7

Drives a single turn of a focus group conversation:
1. Validates the conversation isn't complete
2. For each persona, generates a response via LLM
3. Checks moderation; regenerates if toxic (up to max_regeneration_attempts)
4. Saves all messages and increments the turn counter

TDD Status:
- Tests written first in: tests/unit/test_conversation_orchestrator.py
- This implementation makes those tests GREEN

Usage:
    orchestrator = ConversationOrchestrator()
    messages = orchestrator.generate_turn(
        conversation=conv,
        personas=personas,
        history=[{"speaker": "Alice", "message": "I think..."}],
        db=db_session,
    )
"""

import logging
from typing import List, Dict, Any

from app.services.llm_service import LLMService
from app.services.content_moderation_service import ContentModerationService

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """
    Generates one turn of a focus group conversation.

    For each participating persona, calls the LLM to generate a response,
    checks moderation, and regenerates if the content is toxic.

    Args:
        llm_service: LLMService instance. If None, creates one from env vars.
        moderation_service: ContentModerationService instance.
        max_regeneration_attempts: Max retries when content is toxic.
    """

    def __init__(
        self,
        llm_service=None,
        moderation_service=None,
        max_regeneration_attempts: int = 2,
    ):
        self.llm_service = llm_service or LLMService()
        self.moderation_service = moderation_service or ContentModerationService()
        self.max_regeneration_attempts = max_regeneration_attempts

    def generate_turn(
        self,
        conversation,
        personas: list,
        history: List[Dict[str, str]],
        db,
    ) -> list:
        """
        Generate one full turn — one message from each persona.

        Args:
            conversation: Conversation model instance
            personas: List of Persona model instances
            history: Prior messages as [{"speaker": name, "message": text}]
            db: SQLAlchemy session

        Returns:
            List[ConversationMessage]: The newly created messages

        Raises:
            ValueError: If conversation.is_complete is True
        """
        from app.models.conversation import ConversationMessage

        if conversation.is_complete:
            raise ValueError(
                f"Conversation has reached its maximum of {conversation.max_turns} turns."
            )

        next_turn = conversation.turn_count + 1
        new_messages = []

        # For challenge mode, evaluate persuasion from previous turn's messages (especially user message)
        if conversation.is_challenge and history:
            from app.services.challenge_service import ChallengeService
            challenge_svc = ChallengeService(llm_service=self.llm_service)

            # Find the last message in history
            last_msg = history[-1]

            for participant in conversation.participants:
                # Evaluate how this last message affected this participant
                eval_res = challenge_svc.evaluate_persuasion(
                    persona_name=participant.persona.name,
                    persona_description=participant.persona.description,
                    proposal=conversation.proposal,
                    current_score=participant.persuaded_score,
                    message_speaker=last_msg["speaker"],
                    message_text=last_msg["message"]
                )
                participant.persuaded_score = eval_res.get("new_score", participant.persuaded_score)

        for persona in personas:
            # Get current persuaded score for this persona in this conversation
            persuaded_score = 0.0
            participant = next((p for p in conversation.participants if p.persona_id == persona.id), None)
            if participant:
                persuaded_score = participant.persuaded_score

            persona_details = self._build_persona_details(persona)
            message_text, toxicity_score, moderation_status = self._generate_safe_message(
                persona_details=persona_details,
                history=history,
                topic=conversation.topic,
                image_url=conversation.image_url,
                is_challenge=conversation.is_challenge,
                proposal=conversation.proposal,
                challenge_type=conversation.challenge_type,
                persuaded_score=persuaded_score,
            )

            msg = ConversationMessage(
                conversation_id=conversation.id,
                persona_id=persona.id,
                persona_name=persona.name,
                message_text=message_text,
                turn_number=next_turn,
                toxicity_score=toxicity_score,
                moderation_status=moderation_status,
            )
            db.add(msg)
            new_messages.append(msg)

            if moderation_status == "flagged":
                from app.models.moderation import ModerationAuditLog
                db.add(ModerationAuditLog(
                    content=message_text[:4096],
                    toxicity_score=toxicity_score,
                    source="conversation_turn",
                    source_id=str(conversation.unique_id),
                    action_taken="flagged",
                ))

        conversation.turn_count = next_turn
        db.commit()

        for msg in new_messages:
            db.refresh(msg)

        return new_messages

    def _generate_safe_message(
        self,
        persona_details: Dict[str, Any],
        history: List[Dict[str, str]],
        topic: str,
        image_url: str = None,
        is_challenge: bool = False,
        proposal: str = None,
        challenge_type: str = None,
        persuaded_score: float = 0.0,
    ):
        """
        Generate a message, regenerating up to max_regeneration_attempts if toxic.

        Returns:
            tuple: (message_text, toxicity_score, moderation_status)
        """
        from app.services.prompt_templates import ChallengeConversationTemplate
        last_text = ""
        last_score = 0.0

        for attempt in range(self.max_regeneration_attempts):
            if is_challenge:
                template = ChallengeConversationTemplate()
                user_message_text = template.render(
                    persona_name=persona_details.get("name", "Participant"),
                    ocean_scores=persona_details.get("ocean_scores", {}),
                    attitude=persona_details.get("attitude", "Neutral"),
                    proposal=proposal,
                    challenge_type=challenge_type,
                    history=history,
                    description=persona_details.get("description", ""),
                    persuaded_score=persuaded_score,
                    has_image=bool(image_url),
                )

                content = []
                if image_url:
                    try:
                        from app.services.image_generation_service import ImageGenerationService
                        import base64
                        img_service = ImageGenerationService()
                        image_bytes = img_service.get_image_bytes(image_url)
                        base64_image = base64.b64encode(image_bytes).decode("utf-8")

                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image,
                            },
                        })
                    except Exception as e:
                        logger.warning(f"Failed to fetch image for LLM vision: {e}")

                content.append({
                    "type": "text",
                    "text": user_message_text,
                })

                text = self.llm_service.client.messages.create(
                    model=self.llm_service.model,
                    max_tokens=512,
                    system="You are roleplaying as a specific person in a challenge conversation.",
                    messages=[{"role": "user", "content": content}],
                ).content[0].text.strip()
            else:
                text = self.llm_service.generate_response(
                    persona_details=persona_details,
                    conversation_history=history,
                    topic=topic,
                    image_url=image_url,
                )
            score = self.moderation_service.analyze_toxicity(text)
            last_text = text
            last_score = score

            if self.moderation_service.is_safe(score):
                return text, score, "approved"

            logger.warning(
                f"Toxic content (score={score:.2f}) for '{persona_details.get('name')}', "
                f"attempt {attempt + 1}/{self.max_regeneration_attempts}"
            )

        # Exhausted attempts — save as flagged
        logger.error(
            f"Content still toxic after {self.max_regeneration_attempts} attempts "
            f"for '{persona_details.get('name')}'. Saving as flagged."
        )
        return last_text, last_score, "flagged"

    def _build_persona_details(self, persona) -> Dict[str, Any]:
        """Convert a Persona model instance to a details dict for the LLM."""
        return {
            "name": persona.name,
            "description": persona.description or "",
            "attitude": persona.attitude or "Neutral",
            "ocean_scores": {
                "openness": persona.ocean_openness,
                "conscientiousness": persona.ocean_conscientiousness,
                "extraversion": persona.ocean_extraversion,
                "agreeableness": persona.ocean_agreeableness,
                "neuroticism": persona.ocean_neuroticism,
            },
            "archetype_affinities": persona.archetype_affinities or {},
        }
