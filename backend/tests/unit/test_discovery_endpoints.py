"""
Discovery Endpoints Tests

Tests for public feed, upvoting, visibility, fork, and force-delete endpoints.
"""

import pytest


OCEAN_DEFAULTS = dict(
    ocean_openness=0.5,
    ocean_conscientiousness=0.5,
    ocean_extraversion=0.5,
    ocean_agreeableness=0.5,
    ocean_neuroticism=0.5,
)


@pytest.fixture
def public_persona(db_session, test_user):
    from app.models.persona import Persona
    p = Persona(user_id=test_user.id, name="Public Hero", is_public=True, **OCEAN_DEFAULTS)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def private_persona(db_session, test_user):
    from app.models.persona import Persona
    p = Persona(user_id=test_user.id, name="Private One", is_public=False, **OCEAN_DEFAULTS)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def public_conversation(db_session, test_user, public_persona):
    from app.models.conversation import Conversation, ConversationParticipant
    conv = Conversation(topic="Public topic", created_by=test_user.id, is_public=True)
    db_session.add(conv)
    db_session.flush()
    db_session.add(ConversationParticipant(conversation_id=conv.id, persona_id=public_persona.id))
    db_session.commit()
    db_session.refresh(conv)
    return conv


@pytest.fixture
def superuser(db_session):
    from app.models.user import User
    user = User(
        email="superuser@example.com",
        google_id="google_super_disc_1",
        name="Super User",
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


# ============================================================================
# GET /discover
# ============================================================================

class TestDiscover:

    def test_returns_personas_and_conversations(self, client, public_persona, public_conversation):
        response = client.get("/discover")
        assert response.status_code == 200
        data = response.json()
        assert "personas" in data
        assert "conversations" in data

    def test_sort_new(self, client, public_persona):
        response = client.get("/discover?sort=new")
        assert response.status_code == 200

    def test_sort_top(self, client, public_persona):
        response = client.get("/discover?sort=top")
        assert response.status_code == 200

    def test_sort_hot_default(self, client, public_persona):
        response = client.get("/discover?sort=hot")
        assert response.status_code == 200

    def test_private_items_excluded(self, client, private_persona):
        response = client.get("/discover")
        data = response.json()
        ids = [p["unique_id"] for p in data["personas"]]
        assert private_persona.unique_id not in ids


# ============================================================================
# GET /p/{unique_id} - Public persona
# ============================================================================

class TestPublicPersona:

    def test_returns_public_persona(self, client, public_persona):
        response = client.get(f"/p/{public_persona.unique_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["unique_id"] == public_persona.unique_id

    def test_private_persona_returns_404_for_anonymous(self, client, private_persona):
        response = client.get(f"/p/{private_persona.unique_id}")
        assert response.status_code == 404

    def test_owner_can_see_private_persona(self, client, auth_headers, private_persona):
        response = client.get(f"/p/{private_persona.unique_id}", headers=auth_headers)
        assert response.status_code == 200

    def test_nonexistent_returns_404(self, client):
        response = client.get("/p/xxxxxx")
        assert response.status_code == 404

    def test_response_includes_is_owner_for_owner(self, client, auth_headers, public_persona):
        response = client.get(f"/p/{public_persona.unique_id}", headers=auth_headers)
        data = response.json()
        assert data["is_owner"] is True

    def test_response_includes_is_owner_false_for_anon(self, client, public_persona):
        response = client.get(f"/p/{public_persona.unique_id}")
        data = response.json()
        assert data["is_owner"] is False


# ============================================================================
# GET /c/{unique_id} - Public conversation
# ============================================================================

class TestPublicConversation:

    def test_returns_public_conversation(self, client, public_conversation):
        response = client.get(f"/c/{public_conversation.unique_id}")
        assert response.status_code == 200

    def test_nonexistent_returns_404(self, client):
        response = client.get("/c/xxxxxx")
        assert response.status_code == 404

    def test_owner_field_true_for_owner(self, client, auth_headers, public_conversation):
        response = client.get(f"/c/{public_conversation.unique_id}", headers=auth_headers)
        data = response.json()
        assert data["is_owner"] is True


# ============================================================================
# POST /p/{unique_id}/upvote
# ============================================================================

class TestUpvotePersona:

    def test_upvote_adds(self, client, auth_headers, public_persona):
        response = client.post(f"/p/{public_persona.unique_id}/upvote", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["upvoted"] is True

    def test_nonexistent_returns_404(self, client, auth_headers):
        response = client.post("/p/xxxxxx/upvote", headers=auth_headers)
        assert response.status_code == 404

    def test_unauthenticated_gets_401(self, client, public_persona):
        response = client.post(f"/p/{public_persona.unique_id}/upvote")
        assert response.status_code == 401


# ============================================================================
# POST /c/{unique_id}/upvote
# ============================================================================

class TestUpvoteConversation:

    def test_upvote_adds(self, client, auth_headers, public_conversation):
        response = client.post(f"/c/{public_conversation.unique_id}/upvote", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["upvoted"] is True

    def test_nonexistent_returns_404(self, client, auth_headers):
        response = client.post("/c/xxxxxx/upvote", headers=auth_headers)
        assert response.status_code == 404


# ============================================================================
# PATCH /personas/{unique_id}/visibility
# ============================================================================

class TestPersonaVisibility:

    def test_set_private(self, client, auth_headers, public_persona, db_session):
        response = client.patch(
            f"/personas/{public_persona.unique_id}/visibility",
            json={"is_public": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_public"] is False

    def test_nonexistent_returns_404(self, client, auth_headers):
        response = client.patch(
            "/personas/xxxxxx/visibility",
            json={"is_public": False},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_unauthenticated_gets_401(self, client, public_persona):
        response = client.patch(
            f"/personas/{public_persona.unique_id}/visibility",
            json={"is_public": False},
        )
        assert response.status_code == 401


# ============================================================================
# PATCH /conversations/{unique_id}/visibility
# ============================================================================

class TestConversationVisibility:

    def test_set_private(self, client, auth_headers, public_conversation, db_session):
        response = client.patch(
            f"/conversations/{public_conversation.unique_id}/visibility",
            json={"is_public": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_public"] is False

    def test_nonexistent_returns_404(self, client, auth_headers):
        response = client.patch(
            "/conversations/xxxxxx/visibility",
            json={"is_public": False},
            headers=auth_headers,
        )
        assert response.status_code == 404


# ============================================================================
# POST /conversations/{unique_id}/fork
# ============================================================================

class TestForkConversation:

    def test_fork_creates_new_conversation(self, client, auth_headers, public_conversation):
        response = client.post(
            f"/conversations/{public_conversation.unique_id}/fork",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["unique_id"] != public_conversation.unique_id
        assert data["forked_from_id"] == public_conversation.unique_id

    def test_fork_with_custom_topic(self, client, auth_headers, public_conversation):
        response = client.post(
            f"/conversations/{public_conversation.unique_id}/fork",
            json={"topic": "My custom topic"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["topic"] == "My custom topic"

    def test_fork_nonexistent_returns_404(self, client, auth_headers):
        response = client.post(
            "/conversations/xxxxxx/fork",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_fork_unauthenticated_gets_401(self, client, public_conversation):
        response = client.post(
            f"/conversations/{public_conversation.unique_id}/fork",
            json={},
        )
        assert response.status_code == 401


# ============================================================================
# Force-delete endpoints (superuser)
# ============================================================================

class TestForceDelete:

    def test_force_delete_persona(self, client, superuser_headers, public_persona, db_session):
        response = client.delete(
            f"/personas/{public_persona.unique_id}/force",
            headers=superuser_headers,
        )
        assert response.status_code == 204

    def test_force_delete_persona_non_superuser(self, client, auth_headers, public_persona):
        response = client.delete(
            f"/personas/{public_persona.unique_id}/force",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_force_delete_persona_nonexistent(self, client, superuser_headers):
        response = client.delete("/personas/xxxxxx/force", headers=superuser_headers)
        assert response.status_code == 404

    def test_force_delete_conversation(self, client, superuser_headers, public_conversation, db_session):
        response = client.delete(
            f"/conversations/{public_conversation.unique_id}/force",
            headers=superuser_headers,
        )
        assert response.status_code == 204

    def test_force_delete_conversation_non_superuser(self, client, auth_headers, public_conversation):
        response = client.delete(
            f"/conversations/{public_conversation.unique_id}/force",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_force_delete_conversation_nonexistent(self, client, superuser_headers):
        response = client.delete("/conversations/xxxxxx/force", headers=superuser_headers)
        assert response.status_code == 404
