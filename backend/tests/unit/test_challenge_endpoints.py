"""
Challenge Endpoint Tests - Phase 10

Tests for POST /conversations/challenge
"""

import pytest
from unittest.mock import patch, MagicMock

class TestCreateChallenge:

    @patch("app.services.challenge_service.ChallengeService")
    def test_create_challenge_success(self, mock_svc_cls, client, auth_headers, test_user, test_personas, db_session):
        from app.models.persona import Persona

        # Mock ChallengeService to return some personas
        mock_svc = MagicMock()
        mock_svc.generate_challenge_personas.return_value = test_personas[:3]
        mock_svc_cls.return_value = mock_svc

        response = client.post(
            "/conversations/challenge",
            json={"proposal": "Cycle lanes should be everywhere", "challenge_type": "Public Debate", "n_personas": 3},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_challenge"] is True
        assert data["proposal"] == "Cycle lanes should be everywhere"
        assert len(data["participants"]) == 3
        assert data["participants"][0]["persuaded_score"] == 0.1

    def test_create_challenge_requires_auth(self, client):
        response = client.post(
            "/conversations/challenge",
            json={"proposal": "Test", "n_personas": 3},
        )
        assert response.status_code == 401

    def test_create_challenge_invalid_n(self, client, auth_headers):
        response = client.post(
            "/conversations/challenge",
            json={"proposal": "Test", "n_personas": 0}, # min 1
            headers=auth_headers,
        )
        assert response.status_code == 422

        response = client.post(
            "/conversations/challenge",
            json={"proposal": "Test", "n_personas": 10}, # max 8
            headers=auth_headers,
        )
        assert response.status_code == 422
