"""
Admin Endpoints Tests - Phase 5 (RED phase)

Tests for admin-only endpoints for content moderation review.

Endpoints tested:
- GET /admin/flagged-content - List flagged moderation logs
- POST /admin/approve/{log_id} - Approve flagged content
- POST /admin/block/{log_id} - Block flagged content

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def admin_user(db_session):
    """Create an admin user in the database."""
    from app.models.user import User
    user = User(
        email="admin@example.com",
        google_id="google_admin_123",
        name="Admin User",
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_auth_headers(admin_user):
    """Generate JWT auth headers for an admin user."""
    from app.auth import create_access_token
    token = create_access_token(user_id=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def flagged_log(db_session):
    """Create a flagged moderation log entry."""
    from app.models.moderation import ModerationAuditLog
    log = ModerationAuditLog(
        content="Some flagged content that was blocked",
        toxicity_score=0.87,
        source="persona_description",
        source_id="abc123",
        action_taken="blocked",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log


@pytest.fixture
def pending_log(db_session):
    """Create a pending moderation log entry."""
    from app.models.moderation import ModerationAuditLog
    log = ModerationAuditLog(
        content="Borderline content awaiting review",
        toxicity_score=0.72,
        source="persona_description",
        source_id="def456",
        action_taken="pending",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log


# ============================================================================
# GET /admin/flagged-content
# ============================================================================

class TestGetFlaggedContent:

    def test_admin_can_access(self, client, admin_auth_headers, flagged_log):
        response = client.get("/admin/flagged-content", headers=admin_auth_headers)
        assert response.status_code == 200

    def test_returns_list(self, client, admin_auth_headers, flagged_log):
        response = client.get("/admin/flagged-content", headers=admin_auth_headers)
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_response_includes_required_fields(self, client, admin_auth_headers, flagged_log):
        response = client.get("/admin/flagged-content", headers=admin_auth_headers)
        item = response.json()[0]
        assert "id" in item
        assert "content" in item
        assert "toxicity_score" in item
        assert "source" in item
        assert "action_taken" in item

    def test_regular_user_gets_403(self, client, auth_headers):
        response = client.get("/admin/flagged-content", headers=auth_headers)
        assert response.status_code == 403

    def test_unauthenticated_gets_401(self, client):
        response = client.get("/admin/flagged-content")
        assert response.status_code == 401

    def test_empty_list_when_no_flagged_content(self, client, admin_auth_headers):
        response = client.get("/admin/flagged-content", headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.json() == []


# ============================================================================
# POST /admin/approve/{log_id}
# ============================================================================

class TestApproveContent:

    def test_admin_can_approve(self, client, admin_auth_headers, pending_log, db_session):
        response = client.post(
            f"/admin/approve/{pending_log.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action_taken"] == "approved"

    def test_approve_updates_reviewed_by(self, client, admin_auth_headers, pending_log, db_session, admin_user):
        client.post(f"/admin/approve/{pending_log.id}", headers=admin_auth_headers)
        db_session.refresh(pending_log)
        assert pending_log.reviewed_by == admin_user.id

    def test_approve_nonexistent_log_returns_404(self, client, admin_auth_headers):
        response = client.post("/admin/approve/99999", headers=admin_auth_headers)
        assert response.status_code == 404

    def test_regular_user_cannot_approve(self, client, auth_headers, pending_log):
        response = client.post(f"/admin/approve/{pending_log.id}", headers=auth_headers)
        assert response.status_code == 403


# ============================================================================
# POST /admin/block/{log_id}
# ============================================================================

class TestBlockContent:

    def test_admin_can_block(self, client, admin_auth_headers, pending_log):
        response = client.post(
            f"/admin/block/{pending_log.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action_taken"] == "blocked"

    def test_block_nonexistent_log_returns_404(self, client, admin_auth_headers):
        response = client.post("/admin/block/99999", headers=admin_auth_headers)
        assert response.status_code == 404

    def test_regular_user_cannot_block(self, client, auth_headers, pending_log):
        response = client.post(f"/admin/block/{pending_log.id}", headers=auth_headers)
        assert response.status_code == 403


# ============================================================================
# POST /personas moderation integration
# ============================================================================

class TestPersonaModerationIntegration:
    """Test that persona creation checks content moderation."""

    @patch("app.routers.personas.ImageGenerationService")
    @patch("app.routers.personas.LLMService")
    @patch("app.routers.personas.OceanInferenceService")
    @patch("app.routers.personas.ContentModerationService")
    def test_toxic_description_returns_400(
        self, mock_mod_cls, mock_ocean_cls, mock_llm_cls, mock_img_cls,
        client, auth_headers,
    ):
        """Persona creation with toxic description returns 400."""
        mod_svc = MagicMock()
        mod_svc.analyze_toxicity.return_value = 0.95
        mod_svc.is_safe.return_value = False
        mock_mod_cls.return_value = mod_svc

        mock_ocean_cls.return_value = MagicMock()
        mock_llm_cls.return_value = MagicMock()
        mock_img_cls.return_value = MagicMock()

        response = client.post(
            "/personas",
            json={"name": "BadActor", "description": "Toxic content here"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "moderation" in response.json()["detail"].lower() or "content" in response.json()["detail"].lower()

    @patch("app.routers.personas.ImageGenerationService")
    @patch("app.routers.personas.LLMService")
    @patch("app.routers.personas.OceanInferenceService")
    @patch("app.routers.personas.ContentModerationService")
    def test_safe_description_proceeds_normally(
        self, mock_mod_cls, mock_ocean_cls, mock_llm_cls, mock_img_cls,
        client, auth_headers,
    ):
        """Safe description passes moderation and persona is created."""
        mod_svc = MagicMock()
        mod_svc.analyze_toxicity.return_value = 0.01
        mod_svc.is_safe.return_value = True
        mock_mod_cls.return_value = mod_svc

        ocean_svc = MagicMock()
        ocean_svc.infer_ocean_traits.return_value = {
            "openness": 0.7, "conscientiousness": 0.6,
            "extraversion": 0.5, "agreeableness": 0.65, "neuroticism": 0.35,
        }
        mock_ocean_cls.return_value = ocean_svc

        llm_svc = MagicMock()
        llm_svc.generate_motto.return_value = "Stay curious."
        mock_llm_cls.return_value = llm_svc

        img_svc = MagicMock()
        img_svc.generate_avatar_for_persona.return_value = "https://example.com/avatar.png"
        mock_img_cls.return_value = img_svc

        response = client.post(
            "/personas",
            json={"name": "Alice", "description": "A kind researcher"},
            headers=auth_headers,
        )
        assert response.status_code == 201

    @patch("app.routers.personas.ImageGenerationService")
    @patch("app.routers.personas.LLMService")
    @patch("app.routers.personas.OceanInferenceService")
    @patch("app.routers.personas.ContentModerationService")
    def test_moderation_failure_allows_creation(
        self, mock_mod_cls, mock_ocean_cls, mock_llm_cls, mock_img_cls,
        client, auth_headers,
    ):
        """If moderation API fails, persona creation proceeds (fail open)."""
        mod_svc = MagicMock()
        mod_svc.analyze_toxicity.side_effect = Exception("Moderation API down")
        mock_mod_cls.return_value = mod_svc

        ocean_svc = MagicMock()
        ocean_svc.infer_ocean_traits.return_value = {
            "openness": 0.7, "conscientiousness": 0.6,
            "extraversion": 0.5, "agreeableness": 0.65, "neuroticism": 0.35,
        }
        mock_ocean_cls.return_value = ocean_svc

        llm_svc = MagicMock()
        llm_svc.generate_motto.return_value = "Be bold."
        mock_llm_cls.return_value = llm_svc

        img_svc = MagicMock()
        img_svc.generate_avatar_for_persona.return_value = "https://example.com/avatar.png"
        mock_img_cls.return_value = img_svc

        response = client.post(
            "/personas",
            json={"name": "Alice", "description": "A thoughtful researcher"},
            headers=auth_headers,
        )
        assert response.status_code == 201
