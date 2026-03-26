"""
Challenge Service Tests - Phase 10

Tests for ChallengeService: persona generation and persuasion evaluation.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.services.challenge_service import ChallengeService

def test_evaluate_persuasion():
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"new_score": 0.45, "reasoning": "Good point about safety."}')]
    mock_llm.client.messages.create.return_value = mock_response

    svc = ChallengeService(llm_service=mock_llm)
    res = svc.evaluate_persuasion(
        persona_name="Test Persona",
        persona_description="Test Description",
        proposal="Test Proposal",
        current_score=0.3,
        message_speaker="User",
        message_text="We should do it for safety."
    )

    assert res["new_score"] == 0.45
    assert "safety" in res["reasoning"]

@patch("app.services.challenge_service.OceanInferenceService")
@patch("app.services.challenge_service.ImageGenerationService")
@patch("app.services.challenge_service.AffinityCalculator")
def test_generate_challenge_personas(mock_calc, mock_img, mock_ocean, db_session, test_user):
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='''[
        {"name": " Skeptic Sam", "age": 50, "gender": "Male", "description": "He hates change.", "attitude": "Cynical"}
    ]''')]
    mock_llm.client.messages.create.return_value = mock_response
    mock_llm.generate_motto.return_value = "Change is bad."

    mock_ocean_inst = mock_ocean.return_value
    mock_ocean_inst.infer_ocean_traits.return_value = {
        "openness": 0.1, "conscientiousness": 0.8, "extraversion": 0.4, "agreeableness": 0.2, "neuroticism": 0.5
    }

    mock_img_inst = mock_img.return_value
    mock_img_inst.generate_avatar_for_persona.return_value = "http://avatar.url"

    mock_calc_inst = mock_calc.return_value
    mock_calc_inst.calculate.return_value = {"SKEPTIC": 0.9}

    svc = ChallengeService(llm_service=mock_llm)
    personas = svc.generate_challenge_personas(
        db=db_session,
        user_id=test_user.id,
        proposal="New tech",
        challenge_type="Public Debate",
        n=1
    )

    assert len(personas) == 1
    assert personas[0].name == " Skeptic Sam"
    assert personas[0].ocean_openness == 0.1
    assert personas[0].is_public is False

def test_generate_challenge_personas_invalid_json():
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='Invalid JSON')]
    mock_llm.client.messages.create.return_value = mock_response

    svc = ChallengeService(llm_service=mock_llm)
    personas = svc.generate_challenge_personas(
        db=MagicMock(),
        user_id=1,
        proposal="Test",
        challenge_type="Interview",
        n=1
    )
    assert personas == []

def test_evaluate_persuasion_invalid_json():
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='Invalid JSON')]
    mock_llm.client.messages.create.return_value = mock_response

    svc = ChallengeService(llm_service=mock_llm)
    res = svc.evaluate_persuasion(
        persona_name="Test",
        persona_description="Test",
        proposal="Test",
        current_score=0.5,
        message_speaker="User",
        message_text="Test"
    )
    assert res["new_score"] == 0.5

@patch("app.services.challenge_service.OceanInferenceService")
@patch("app.services.challenge_service.ImageGenerationService")
@patch("app.services.challenge_service.AffinityCalculator")
def test_generate_challenge_personas_services_fail(mock_calc, mock_img, mock_ocean, db_session, test_user):
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='''[
        {"name": "Fail Guy", "age": 30, "gender": "Male", "description": "Broken services.", "attitude": "Somber"}
    ]''')]
    mock_llm.client.messages.create.return_value = mock_response

    # Mock services instances to raise exceptions when methods are called
    mock_ocean_inst = mock_ocean.return_value
    mock_ocean_inst.infer_ocean_traits.side_effect = Exception("OCEAN fail")

    mock_img_inst = mock_img.return_value
    mock_img_inst.generate_avatar_for_persona.side_effect = Exception("Image fail")

    mock_calc_inst = mock_calc.return_value
    mock_calc_inst.calculate.return_value = {"NEUTRAL": 0.5}
    mock_llm.generate_motto.return_value = "Fallback motto"

    svc = ChallengeService(llm_service=mock_llm)
    personas = svc.generate_challenge_personas(
        db=db_session,
        user_id=test_user.id,
        proposal="Fail",
        challenge_type="Interview",
        n=1
    )

    assert len(personas) == 1
    assert personas[0].name == "Fail Guy"
    # Verify fallback OCEAN scores (0.5)
    assert personas[0].ocean_openness == 0.5
