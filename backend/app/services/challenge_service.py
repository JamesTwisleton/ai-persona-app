"""
Challenge Service - Phase 10

Handles the logic for Challenge Mode:
1. Generating representative disagreeable personas for a proposal.
2. Evaluating persuasion score changes based on conversational turns.
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from app.services.llm_service import LLMService, DEFAULT_MODEL
from app.services.prompt_templates import (
    ChallengePersonaGenerationTemplate,
    PersuasionEvaluationTemplate
)
from app.services.ocean_inference import OceanInferenceService
from app.services.image_generation_service import ImageGenerationService
from app.models.traits import PersonalityVector
from app.models.affinity import AffinityCalculator
from app.models.archetypes import get_all_archetypes
from app.models.persona import Persona

logger = logging.getLogger(__name__)

class ChallengeService:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.persona_gen_template = ChallengePersonaGenerationTemplate()
        self.evaluation_template = PersuasionEvaluationTemplate()

    def generate_challenge_personas(
        self,
        db: Session,
        user_id: int,
        proposal: str,
        challenge_type: str,
        n: int = 3
    ) -> List[Persona]:
        """
        Brainstorm N personas who would disagree with the proposal and create them.
        """
        prompt = self.persona_gen_template.render(proposal, challenge_type, n)

        response = self.llm_service.client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=2000,
            system="You are an expert in stakeholder analysis and social psychology.",
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = response.content[0].text.strip()
        # Find JSON list
        json_match = re.search(r"\[.*\]", raw_text, re.DOTALL)
        if not json_match:
            logger.error(f"Failed to find JSON in LLM response: {raw_text}")
            return []

        try:
            persona_data_list = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM response: {json_match.group(0)}")
            return []

        created_personas = []
        ocean_service = OceanInferenceService()
        img_service = ImageGenerationService()
        archetypes = get_all_archetypes()
        calculator = AffinityCalculator(archetypes)

        for data in persona_data_list[:n]:
            name = data.get("name", "Unknown")
            description = data.get("description", "")
            age = data.get("age")
            gender = data.get("gender")
            attitude = data.get("attitude", "Neutral")

            # 1. OCEAN Inference
            try:
                ocean_scores = ocean_service.infer_ocean_traits(description)
            except Exception as e:
                logger.warning(f"OCEAN inference failed for {name}: {e}")
                ocean_scores = {"openness": 0.5, "conscientiousness": 0.5, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5}

            # 2. Archetype Affinities
            vector = PersonalityVector({
                "O": ocean_scores["openness"],
                "C": ocean_scores["conscientiousness"],
                "E": ocean_scores["extraversion"],
                "A": ocean_scores["agreeableness"],
                "N": ocean_scores["neuroticism"],
            })
            affinities = calculator.calculate(vector)

            # 3. Motto
            motto = None
            try:
                motto = self.llm_service.generate_motto({
                    "name": name,
                    "ocean_scores": ocean_scores,
                    "archetype_affinities": affinities,
                    "attitude": attitude
                })
            except Exception as e:
                logger.warning(f"Motto generation failed for {name}: {e}")

            # 4. Avatar
            avatar_url = None
            try:
                avatar_url = img_service.generate_avatar_for_persona({
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "description": description,
                    "attitude": attitude
                })
            except Exception as e:
                logger.warning(f"Avatar generation failed for {name}: {e}")

            # 5. Create Persona
            persona = Persona(
                user_id=user_id,
                name=name,
                age=age,
                gender=gender,
                description=description,
                attitude=attitude,
                ocean_openness=ocean_scores["openness"],
                ocean_conscientiousness=ocean_scores["conscientiousness"],
                ocean_extraversion=ocean_scores["extraversion"],
                ocean_agreeableness=ocean_scores["agreeableness"],
                ocean_neuroticism=ocean_scores["neuroticism"],
                archetype_affinities=affinities,
                motto=motto,
                avatar_url=avatar_url,
                is_public=True
            )
            db.add(persona)
            created_personas.append(persona)

        db.flush() # Ensure IDs are populated
        return created_personas

    def evaluate_persuasion(
        self,
        persona_name: str,
        persona_description: str,
        proposal: str,
        current_score: float,
        message_speaker: str,
        message_text: str
    ) -> Dict[str, Any]:
        """
        Evaluate how a message affected a persona's persuasion score.
        """
        prompt = self.evaluation_template.render(
            persona_name=persona_name,
            description=persona_description,
            proposal=proposal,
            current_score=current_score,
            message_speaker=message_speaker,
            message_text=message_text
        )

        response = self.llm_service.client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=512,
            system="You are a social psychologist and debate judge.",
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = response.content[0].text.strip()
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            logger.error(f"Failed to find JSON in persuasion evaluation: {raw_text}")
            return {"new_score": current_score, "reasoning": "Failed to evaluate."}

        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON in persuasion evaluation: {json_match.group(0)}")
            return {"new_score": current_score, "reasoning": "Failed to parse evaluation."}
