"""
Challenge Endpoint Tests - Phase 10

Tests for POST /conversations/challenge
"""

import pytest
from unittest.mock import patch, MagicMock

class TestCreateChallenge:

    def test_create_challenge_success(self, client, auth_headers, test_user, db_session):
        # Endpoint now returns immediately with status="pending"; persona generation
        # happens in a background task, so participants are not present in the response.
        response = client.post(
            "/conversations/challenge",
            json={"proposal": "Cycle lanes should be everywhere", "challenge_type": "Public Debate", "n_personas": 3},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_challenge"] is True
        assert data["proposal"] == "Cycle lanes should be everywhere"
        assert data["challenge_type"] == "Public Debate"
        assert data["status"] == "pending"
        assert data["participants"] == []

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
