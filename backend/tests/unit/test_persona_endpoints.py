"""
Persona API Endpoints Tests - Phase 3B/4 (RED phase)

Tests for persona CRUD endpoints with OCEAN inference and LLM/image integration.

Endpoints tested:
- POST /personas - Create persona (with OCEAN inference, motto gen, avatar gen)
- GET /personas - List user's personas
- GET /personas/{unique_id} - Get single persona
- DELETE /personas/{unique_id} - Delete persona
- POST /personas/compatibility - Calculate compatibility between personas
- GET /archetypes - List all archetypes
"""

import pytest
from unittest.mock import patch, MagicMock


# ============================================================================
# Shared helpers
# ============================================================================

OCEAN_RETURN = {
    "openness": 0.8,
    "conscientiousness": 0.7,
    "extraversion": 0.4,
    "agreeableness": 0.6,
    "neuroticism": 0.3,
}


def mock_all_ai_services(ocean_cls, llm_cls, img_cls, mod_cls=None):
    """Wire up mocks for all AI services used in persona creation."""
    ocean_svc = MagicMock()
    ocean_svc.infer_ocean_traits.return_value = OCEAN_RETURN
    ocean_cls.return_value = ocean_svc

    llm_svc = MagicMock()
    llm_svc.generate_motto.return_value = "Question everything, trust data."
    llm_cls.return_value = llm_svc

    img_svc = MagicMock()
    img_svc.generate_avatar_for_persona.return_value = "https://example.com/avatar.png"
    img_cls.return_value = img_svc

    if mod_cls is not None:
        mod_svc = MagicMock()
        mod_svc.analyze_toxicity.return_value = 0.01
        mod_svc.is_safe.return_value = True
        mod_cls.return_value = mod_svc
        return ocean_svc, llm_svc, img_svc, mod_svc

    return ocean_svc, llm_svc, img_svc


# ============================================================================
# POST /personas - Create Persona
# ============================================================================

class TestCreatePersona:
    """Test persona creation with OCEAN inference, motto and avatar generation."""

    @patch("app.routers.personas.ImageGenerationService")
    @patch("app.routers.personas.LLMService")
    @patch("app.routers.personas.OceanInferenceService")
    @patch("app.routers.personas.ContentModerationService")
    def test_create_persona_success(
        self, mock_mod_cls, mock_ocean_cls, mock_llm_cls, mock_img_cls,
        client, auth_headers, db_session,
    ):
        """Creating a persona infers OCEAN traits, generates motto and avatar."""
        ocean_svc, llm_svc, img_svc, mod_svc = mock_all_ai_services(
            mock_ocean_cls, mock_llm_cls, mock_img_cls, mock_mod_cls
        )

        response = client.post(
            "/personas",
            json={
                "name": "Alice",
                "age": 30,
                "gender": "Female",
                "description": "A thoughtful data scientist who loves puzzles",
                "attitude": "Neutral",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice"
        assert data["age"] == 30
        assert data["unique_id"] is not None
        assert len(data["unique_id"]) == 6
        # OCEAN scores from inference
        assert data["ocean_openness"] == pytest.approx(0.8)
        assert data["ocean_conscientiousness"] == pytest.approx(0.7)
        assert data["ocean_extraversion"] == pytest.approx(0.4)
        assert data["ocean_agreeableness"] == pytest.approx(0.6)
        assert data["ocean_neuroticism"] == pytest.approx(0.3)
        # Archetype affinities
        assert data["archetype_affinities"] is not None
        assert isinstance(data["archetype_affinities"], dict)
        assert len(data["archetype_affinities"]) == 8
        # AI-generated fields (Phase 4)
        assert data["motto"] == "Question everything, trust data."
        assert data["avatar_url"] == "https://example.com/avatar.png"
        # All three services called
        ocean_svc.infer_ocean_traits.assert_called_once()
        llm_svc.generate_motto.assert_called_once()
        img_svc.generate_avatar_for_persona.assert_called_once()

    def test_create_persona_requires_auth(self, client):
        """Creating a persona without auth returns 401."""
        response = client.post(
            "/personas",
            json={"name": "Alice", "description": "Test"},
        )
        assert response.status_code == 401

    def test_create_persona_requires_name(self, client, auth_headers):
        """Name is required for persona creation."""
        response = client.post(
            "/personas",
            json={"description": "No name provided"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    @patch("app.routers.personas.ImageGenerationService")
    @patch("app.routers.personas.LLMService")
    @patch("app.routers.personas.OceanInferenceService")
    @patch("app.routers.personas.ContentModerationService")
    def test_create_persona_inference_failure_returns_error(
        self, mock_mod_cls, mock_ocean_cls, mock_llm_cls, mock_img_cls,
        client, auth_headers,
    ):
        """If OCEAN inference fails, return a 502 error."""
        mock_all_ai_services(mock_ocean_cls, mock_llm_cls, mock_img_cls, mock_mod_cls)
        ocean_svc = MagicMock()
        ocean_svc.infer_ocean_traits.side_effect = Exception("API Error")
        mock_ocean_cls.return_value = ocean_svc
        mock_llm_cls.return_value = MagicMock()
        mock_img_cls.return_value = MagicMock()

        response = client.post(
            "/personas",
            json={"name": "Alice", "description": "A data scientist"},
            headers=auth_headers,
        )

        assert response.status_code == 502
        assert "ocean" in response.json()["detail"].lower() or "inference" in response.json()["detail"].lower()

    @patch("app.routers.personas.ImageGenerationService")
    @patch("app.routers.personas.LLMService")
    @patch("app.routers.personas.OceanInferenceService")
    @patch("app.routers.personas.ContentModerationService")
    def test_create_persona_motto_failure_still_saves(
        self, mock_mod_cls, mock_ocean_cls, mock_llm_cls, mock_img_cls,
        client, auth_headers,
    ):
        """If motto generation fails, persona is still saved with None motto."""
        mod_svc = MagicMock()
        mod_svc.analyze_toxicity.return_value = 0.01
        mod_svc.is_safe.return_value = True
        mock_mod_cls.return_value = mod_svc

        ocean_svc = MagicMock()
        ocean_svc.infer_ocean_traits.return_value = OCEAN_RETURN
        mock_ocean_cls.return_value = ocean_svc

        llm_svc = MagicMock()
        llm_svc.generate_motto.side_effect = Exception("LLM unavailable")
        mock_llm_cls.return_value = llm_svc

        img_svc = MagicMock()
        img_svc.generate_avatar_for_persona.return_value = "https://example.com/avatar.png"
        mock_img_cls.return_value = img_svc

        response = client.post(
            "/personas",
            json={"name": "Alice", "description": "A data scientist"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice"
        assert data["motto"] is None  # Failed gracefully

    @patch("app.routers.personas.ImageGenerationService")
    @patch("app.routers.personas.LLMService")
    @patch("app.routers.personas.OceanInferenceService")
    @patch("app.routers.personas.ContentModerationService")
    def test_create_persona_minimal_fields(
        self, mock_mod_cls, mock_ocean_cls, mock_llm_cls, mock_img_cls,
        client, auth_headers,
    ):
        """Persona can be created with just a name (description defaults)."""
        mock_all_ai_services(mock_ocean_cls, mock_llm_cls, mock_img_cls, mock_mod_cls)

        response = client.post(
            "/personas",
            json={"name": "Bob"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Bob"

    @patch("app.routers.personas.ImageGenerationService")
    @patch("app.routers.personas.LLMService")
    @patch("app.routers.personas.OceanInferenceService")
    @patch("app.routers.personas.ContentModerationService")
    def test_create_persona_validates_attitude(
        self, mock_mod_cls, mock_ocean_cls, mock_llm_cls, mock_img_cls,
        client, auth_headers,
    ):
        """Attitude must be one of the valid options."""
        mock_all_ai_services(mock_ocean_cls, mock_llm_cls, mock_img_cls, mock_mod_cls)

        response = client.post(
            "/personas",
            json={"name": "Alice", "attitude": "InvalidAttitude"},
            headers=auth_headers,
        )
        assert response.status_code == 422


# ============================================================================
# GET /personas - List Personas
# ============================================================================

class TestListPersonas:
    """Test listing user's personas."""

    def test_list_personas_empty(self, client, auth_headers):
        """Empty list when user has no personas."""
        response = client.get("/personas", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_personas_returns_user_personas(self, client, auth_headers, test_persona):
        """Returns only the authenticated user's personas."""
        response = client.get("/personas", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Persona"

    def test_list_personas_requires_auth(self, client):
        """Listing personas without auth returns 401."""
        response = client.get("/personas")
        assert response.status_code == 401

    def test_list_multiple_personas(self, client, auth_headers, test_personas):
        """Returns all personas belonging to the user."""
        response = client.get("/personas", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


# ============================================================================
# GET /personas/{unique_id} - Get Single Persona
# ============================================================================

class TestGetPersona:
    """Test retrieving a single persona."""

    def test_get_persona_success(self, client, auth_headers, test_persona):
        """Retrieve persona by unique_id."""
        response = client.get(
            f"/personas/{test_persona.unique_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Persona"
        assert data["unique_id"] == test_persona.unique_id

    def test_get_persona_not_found(self, client, auth_headers):
        """Return 404 for non-existent persona."""
        response = client.get("/personas/xxxxxx", headers=auth_headers)
        assert response.status_code == 404

    def test_get_persona_requires_auth(self, client, test_persona):
        """Getting a persona requires authentication."""
        response = client.get(f"/personas/{test_persona.unique_id}")
        assert response.status_code == 401


# ============================================================================
# DELETE /personas/{unique_id} - Delete Persona
# ============================================================================

class TestDeletePersona:
    """Test persona deletion."""

    def test_delete_persona_success(self, client, auth_headers, test_persona, db_session):
        """Delete persona by unique_id."""
        response = client.delete(
            f"/personas/{test_persona.unique_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify deleted
        from app.models.persona import Persona
        result = db_session.query(Persona).filter_by(unique_id=test_persona.unique_id).first()
        assert result is None

    def test_delete_persona_not_found(self, client, auth_headers):
        """Return 404 when deleting non-existent persona."""
        response = client.delete("/personas/xxxxxx", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_persona_requires_auth(self, client, test_persona):
        """Deleting persona requires authentication."""
        response = client.delete(f"/personas/{test_persona.unique_id}")
        assert response.status_code == 401

    def test_delete_other_users_persona(self, client, db_session, test_persona):
        """Cannot delete another user's persona."""
        from app.models.user import User
        from app.auth import create_access_token

        other_user = User(
            email="other@example.com",
            google_id="google_other_123",
            name="Other User",
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        other_token = create_access_token(user_id=other_user.id)
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = client.delete(
            f"/personas/{test_persona.unique_id}",
            headers=other_headers,
        )
        assert response.status_code == 404


# ============================================================================
# POST /personas/compatibility - Compatibility Analysis
# ============================================================================

class TestCompatibility:
    """Test persona compatibility analysis."""

    def test_compatibility_between_two_personas(self, client, auth_headers, test_personas):
        """Calculate compatibility between two personas."""
        ids = [p.unique_id for p in test_personas[:2]]
        response = client.post(
            "/personas/compatibility",
            json={"persona_ids": ids},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "diversity_score" in data
        assert "pairwise_distances" in data
        assert isinstance(data["diversity_score"], float)
        assert 0 <= data["diversity_score"]

    def test_compatibility_requires_two_personas(self, client, auth_headers, test_persona):
        """Compatibility requires at least 2 personas."""
        response = client.post(
            "/personas/compatibility",
            json={"persona_ids": [test_persona.unique_id]},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_compatibility_nonexistent_persona(self, client, auth_headers, test_persona):
        """Return 404 if any persona doesn't exist."""
        response = client.post(
            "/personas/compatibility",
            json={"persona_ids": [test_persona.unique_id, "xxxxxx"]},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_compatibility_requires_auth(self, client, test_personas):
        """Compatibility requires authentication."""
        ids = [p.unique_id for p in test_personas[:2]]
        response = client.post(
            "/personas/compatibility",
            json={"persona_ids": ids},
        )
        assert response.status_code == 401


# ============================================================================
# GET /archetypes - List Archetypes
# ============================================================================

class TestListArchetypes:
    """Test archetype listing endpoint."""

    def test_list_archetypes(self, client):
        """Returns all 8 archetypes with their details."""
        response = client.get("/archetypes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8
        assert "code" in data[0]
        assert "name" in data[0]
        assert "description" in data[0]
        assert "ocean_vector" in data[0]

    def test_archetypes_no_auth_required(self, client):
        """Archetypes endpoint is public."""
        response = client.get("/archetypes")
        assert response.status_code == 200


# ============================================================================
# POST /personas/generate-backstory - Generate Backstory
# ============================================================================

class TestGenerateBackstoryEndpoint:
    """Test the AI backstory generation endpoint."""

    @patch("app.routers.personas.LLMService")
    def test_generate_backstory_success(self, mock_llm_cls, client, auth_headers):
        """Successfully generate a backstory."""
        mock_llm = MagicMock()
        mock_llm.generate_backstory.return_value = "Generated backstory text."
        mock_llm_cls.return_value = mock_llm

        response = client.post(
            "/personas/generate-backstory",
            json={
                "name": "Elena",
                "age": 28,
                "gender": "Female",
                "attitude": "Sarcastic"
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["backstory"] == "Generated backstory text."
        mock_llm.generate_backstory.assert_called_once_with(
            name="Elena",
            age=28,
            gender="Female",
            description=None,
            attitude="Sarcastic"
        )

    def test_generate_backstory_requires_auth(self, client):
        """Endpoint requires authentication."""
        response = client.post(
            "/personas/generate-backstory",
            json={"name": "Elena"},
        )
        assert response.status_code == 401

    @patch("app.routers.personas.LLMService")
    def test_generate_backstory_failure_returns_502(self, mock_llm_cls, client, auth_headers):
        """If LLM fails, return 502."""
        mock_llm = MagicMock()
        mock_llm.generate_backstory.side_effect = Exception("Claude is down")
        mock_llm_cls.return_value = mock_llm

        response = client.post(
            "/personas/generate-backstory",
            json={"name": "Elena"},
            headers=auth_headers,
        )

        assert response.status_code == 502
        assert "failed" in response.json()["detail"].lower()
