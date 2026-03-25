"""
New Endpoints Tests - Phase 6+ additions

Tests covering new endpoints added to bring coverage back to >=85%:
- GET /admin/users
- PATCH /admin/users/{id}/superuser
- GET /admin/personas
- GET /admin/conversations
- POST /admin/repair-avatars
- DELETE /conversations/{unique_id}
- GET /personas/public
- GET /p/{unique_id}/conversations
- get_current_superuser dependency
"""

import pytest
from unittest.mock import patch, MagicMock


# ============================================================================
# Shared Fixtures
# ============================================================================

@pytest.fixture
def superuser(db_session):
    from app.models.user import User
    user = User(
        email="superuser@example.com",
        google_id="google_super_1",
        name="Super User",
        is_admin=True,
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def superuser_headers(superuser):
    from app.auth import create_access_token
    token = create_access_token(user_id=superuser.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user(db_session):
    from app.models.user import User
    user = User(
        email="other@example.com",
        google_id="google_other_1",
        name="Other User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


OCEAN_DEFAULTS = dict(
    ocean_openness=0.5,
    ocean_conscientiousness=0.5,
    ocean_extraversion=0.5,
    ocean_agreeableness=0.5,
    ocean_neuroticism=0.5,
)


@pytest.fixture
def public_persona(db_session, other_user):
    from app.models.persona import Persona
    p = Persona(
        user_id=other_user.id,
        name="Public Persona",
        description="A public persona by someone else",
        is_public=True,
        **OCEAN_DEFAULTS,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def own_persona(db_session, test_user):
    from app.models.persona import Persona
    p = Persona(
        user_id=test_user.id,
        name="Own Persona",
        description="My own persona",
        is_public=True,
        **OCEAN_DEFAULTS,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def own_conversation(db_session, test_user, own_persona):
    from app.models.conversation import Conversation, ConversationParticipant
    conv = Conversation(topic="Test topic", created_by=test_user.id)
    db_session.add(conv)
    db_session.flush()
    db_session.add(ConversationParticipant(conversation_id=conv.id, persona_id=own_persona.id))
    db_session.commit()
    db_session.refresh(conv)
    return conv


# ============================================================================
# get_current_superuser dependency
# ============================================================================

class TestGetCurrentSuperuser:

    def test_superuser_can_access(self, client, superuser_headers):
        """Superuser can reach a superuser-protected endpoint."""
        response = client.get("/admin/users", headers=superuser_headers)
        assert response.status_code == 200

    def test_non_superuser_gets_403(self, client, auth_headers):
        """Regular user receives 403 on superuser endpoint."""
        response = client.get("/admin/users", headers=auth_headers)
        assert response.status_code == 403

    def test_unauthenticated_gets_401(self, client):
        response = client.get("/admin/users")
        assert response.status_code == 401


# ============================================================================
# GET /admin/users
# ============================================================================

class TestAdminListUsers:

    def test_returns_paginated_response(self, client, superuser_headers, test_user):
        response = client.get("/admin/users", headers=superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_response_includes_persona_count(self, client, superuser_headers, test_user):
        response = client.get("/admin/users", headers=superuser_headers)
        data = response.json()
        assert len(data["items"]) >= 1
        item = next(u for u in data["items"] if u["id"] == test_user.id)
        assert "persona_count" in item

    def test_pagination_params(self, client, superuser_headers):
        response = client.get("/admin/users?page=1&page_size=5", headers=superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5


# ============================================================================
# PATCH /admin/users/{id}/superuser
# ============================================================================

class TestAdminSetSuperuser:

    def test_promote_user(self, client, superuser_headers, test_user, db_session):
        response = client.patch(
            f"/admin/users/{test_user.id}/superuser",
            json={"is_superuser": True},
            headers=superuser_headers,
        )
        assert response.status_code == 200
        db_session.refresh(test_user)
        assert test_user.is_superuser is True

    def test_demote_other_user(self, client, superuser_headers, other_user, db_session):
        # First promote
        other_user.is_superuser = True
        db_session.commit()
        response = client.patch(
            f"/admin/users/{other_user.id}/superuser",
            json={"is_superuser": False},
            headers=superuser_headers,
        )
        assert response.status_code == 200
        db_session.refresh(other_user)
        assert other_user.is_superuser is False

    def test_cannot_demote_self(self, client, superuser_headers, superuser):
        response = client.patch(
            f"/admin/users/{superuser.id}/superuser",
            json={"is_superuser": False},
            headers=superuser_headers,
        )
        assert response.status_code == 400

    def test_nonexistent_user_returns_404(self, client, superuser_headers):
        response = client.patch(
            "/admin/users/99999/superuser",
            json={"is_superuser": True},
            headers=superuser_headers,
        )
        assert response.status_code == 404

    def test_non_superuser_gets_403(self, client, auth_headers, test_user):
        response = client.patch(
            f"/admin/users/{test_user.id}/superuser",
            json={"is_superuser": True},
            headers=auth_headers,
        )
        assert response.status_code == 403


# ============================================================================
# GET /admin/personas
# ============================================================================

class TestAdminListPersonas:

    def test_returns_paginated_response(self, client, superuser_headers, own_persona):
        response = client.get("/admin/personas", headers=superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_includes_owner_info(self, client, superuser_headers, own_persona, test_user):
        response = client.get("/admin/personas", headers=superuser_headers)
        data = response.json()
        item = next((p for p in data["items"] if p["unique_id"] == own_persona.unique_id), None)
        assert item is not None
        assert "owner_email" in item
        assert item["owner_email"] == test_user.email

    def test_non_superuser_gets_403(self, client, auth_headers):
        response = client.get("/admin/personas", headers=auth_headers)
        assert response.status_code == 403


# ============================================================================
# GET /admin/conversations
# ============================================================================

class TestAdminListConversations:

    def test_returns_paginated_response(self, client, superuser_headers, own_conversation):
        response = client.get("/admin/conversations", headers=superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_includes_owner_info(self, client, superuser_headers, own_conversation, test_user):
        response = client.get("/admin/conversations", headers=superuser_headers)
        data = response.json()
        item = next((c for c in data["items"] if c["unique_id"] == own_conversation.unique_id), None)
        assert item is not None
        assert "owner_email" in item
        assert item["owner_email"] == test_user.email

    def test_non_superuser_gets_403(self, client, auth_headers):
        response = client.get("/admin/conversations", headers=auth_headers)
        assert response.status_code == 403


# ============================================================================
# POST /admin/repair-avatars
# ============================================================================

class TestAdminRepairAvatars:

    def test_no_pending_returns_message(self, client, superuser_headers):
        """When no personas need repair, returns a message and 0 repaired."""
        mock_img_svc = MagicMock()
        with patch("app.services.image_generation_service.ImageGenerationService", return_value=mock_img_svc):
            response = client.post("/admin/repair-avatars", headers=superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert "repaired" in data
        assert "message" in data
        assert data["repaired"] == 0

    def test_repairs_personas_with_no_avatar(self, client, superuser_headers, db_session, test_user):
        """Personas with no avatar_url are processed."""
        from app.models.persona import Persona
        p = Persona(user_id=test_user.id, name="NoAvatar", avatar_url=None, **OCEAN_DEFAULTS)
        db_session.add(p)
        db_session.commit()

        mock_img_svc = MagicMock()
        mock_img_svc.generate_avatar_for_persona.return_value = "avatars/new123.jpg"

        with patch("app.services.image_generation_service.ImageGenerationService", return_value=mock_img_svc):
            response = client.post("/admin/repair-avatars?limit=5", headers=superuser_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["repaired"] >= 1

    def test_repair_failure_counted(self, client, superuser_headers, db_session, test_user):
        """When image service fails, failure is counted."""
        from app.models.persona import Persona
        p = Persona(user_id=test_user.id, name="FailAvatar", avatar_url=None, **OCEAN_DEFAULTS)
        db_session.add(p)
        db_session.commit()

        mock_img_svc = MagicMock()
        mock_img_svc.generate_avatar_for_persona.side_effect = Exception("API failure")

        with patch("app.services.image_generation_service.ImageGenerationService", return_value=mock_img_svc):
            response = client.post("/admin/repair-avatars", headers=superuser_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["failed"] >= 1

    def test_repairs_personas_with_legacy_dicebear_url(self, client, superuser_headers, db_session, test_user):
        """Personas with a DiceBear fallback URL (not an S3 key) are detected and repaired."""
        from app.models.persona import Persona
        p = Persona(
            user_id=test_user.id,
            name="LegacyAvatar",
            avatar_url="https://api.dicebear.com/7.x/personas/svg?seed=default-avatar",
            **OCEAN_DEFAULTS,
        )
        db_session.add(p)
        db_session.commit()

        mock_img_svc = MagicMock()
        mock_img_svc.generate_avatar_for_persona.return_value = "avatars/fixed123.jpg"

        with patch("app.services.image_generation_service.ImageGenerationService", return_value=mock_img_svc):
            response = client.post("/admin/repair-avatars?limit=5", headers=superuser_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["repaired"] >= 1

    def test_non_superuser_gets_403(self, client, auth_headers):
        response = client.post("/admin/repair-avatars", headers=auth_headers)
        assert response.status_code == 403


# ============================================================================
# DELETE /conversations/{unique_id}
# ============================================================================

class TestDeleteConversation:

    def test_owner_can_delete(self, client, auth_headers, own_conversation, db_session):
        response = client.delete(
            f"/conversations/{own_conversation.unique_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        from app.models.conversation import Conversation
        conv = db_session.query(Conversation).filter_by(id=own_conversation.id).first()
        assert conv is None

    def test_nonexistent_returns_404(self, client, auth_headers):
        response = client.delete("/conversations/xxxxxx", headers=auth_headers)
        assert response.status_code == 404

    def test_other_user_cannot_delete(self, client, own_conversation, other_user):
        from app.auth import create_access_token
        token = create_access_token(user_id=other_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(
            f"/conversations/{own_conversation.unique_id}",
            headers=headers,
        )
        assert response.status_code == 404

    def test_unauthenticated_gets_401(self, client, own_conversation):
        response = client.delete(f"/conversations/{own_conversation.unique_id}")
        assert response.status_code == 401


# ============================================================================
# GET /personas/public
# ============================================================================

class TestListPublicPersonas:

    def test_returns_list(self, client, auth_headers, public_persona):
        response = client.get("/personas/public", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_excludes_own_personas(self, client, auth_headers, public_persona, own_persona):
        """Own personas should not appear in the public list."""
        response = client.get("/personas/public", headers=auth_headers)
        data = response.json()
        ids = [p["unique_id"] for p in data]
        assert public_persona.unique_id in ids
        assert own_persona.unique_id not in ids

    def test_search_filter(self, client, auth_headers, public_persona):
        response = client.get("/personas/public?q=Public", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert any(p["unique_id"] == public_persona.unique_id for p in data)

    def test_search_no_match(self, client, auth_headers):
        response = client.get("/personas/public?q=zzznomatch", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_unauthenticated_gets_401(self, client):
        response = client.get("/personas/public")
        assert response.status_code == 401


# ============================================================================
# GET /p/{unique_id}/conversations
# ============================================================================

class TestPersonaConversations:

    @pytest.fixture
    def persona_with_convo(self, db_session, test_user):
        from app.models.persona import Persona
        from app.models.conversation import Conversation, ConversationParticipant
        p = Persona(user_id=test_user.id, name="Featured", is_public=True, **OCEAN_DEFAULTS)
        db_session.add(p)
        db_session.flush()

        conv = Conversation(topic="Featured topic", created_by=test_user.id, is_public=True)
        db_session.add(conv)
        db_session.flush()
        db_session.add(ConversationParticipant(conversation_id=conv.id, persona_id=p.id))
        db_session.commit()
        db_session.refresh(p)
        db_session.refresh(conv)
        return p, conv

    def test_returns_list(self, client, persona_with_convo):
        persona, conv = persona_with_convo
        response = client.get(f"/p/{persona.unique_id}/conversations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_contains_conversation(self, client, persona_with_convo):
        persona, conv = persona_with_convo
        response = client.get(f"/p/{persona.unique_id}/conversations")
        data = response.json()
        assert any(c["unique_id"] == conv.unique_id for c in data)

    def test_nonexistent_persona_returns_404(self, client):
        response = client.get("/p/xxxxxx/conversations")
        assert response.status_code == 404

    def test_sort_new(self, client, persona_with_convo):
        persona, conv = persona_with_convo
        response = client.get(f"/p/{persona.unique_id}/conversations?sort=new")
        assert response.status_code == 200

    def test_sort_top(self, client, persona_with_convo):
        persona, conv = persona_with_convo
        response = client.get(f"/p/{persona.unique_id}/conversations?sort=top")
        assert response.status_code == 200

    def test_sort_hot(self, client, persona_with_convo):
        persona, conv = persona_with_convo
        response = client.get(f"/p/{persona.unique_id}/conversations?sort=hot")
        assert response.status_code == 200
