"""
Conversation Endpoints Tests - Phase 7 (RED phase)

Tests for conversation CRUD and continuation endpoints.

Endpoints tested:
- POST /conversations - Create conversation
- GET /conversations - List user's conversations
- GET /conversations/{unique_id} - Get conversation with messages
- POST /conversations/{unique_id}/continue - Generate next turn

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def test_conversation(db_session, test_user, test_personas):
    """Create a test conversation with participants."""
    from app.models.conversation import Conversation, ConversationParticipant
    conv = Conversation(topic="Should we colonize Mars?", created_by=test_user.id)
    db_session.add(conv)
    db_session.commit()
    db_session.refresh(conv)

    for persona in test_personas[:2]:
        db_session.add(ConversationParticipant(
            conversation_id=conv.id,
            persona_id=persona.id,
        ))
    db_session.commit()
    return conv


@pytest.fixture
def test_conversation_with_messages(db_session, test_user, test_personas, test_conversation):
    """Conversation with some messages already added."""
    from app.models.conversation import ConversationMessage
    for i, persona in enumerate(test_personas[:2]):
        db_session.add(ConversationMessage(
            conversation_id=test_conversation.id,
            persona_id=persona.id,
            persona_name=persona.name,
            message_text=f"Response from {persona.name}",
            turn_number=1,
        ))
    test_conversation.turn_count = 1
    db_session.commit()
    db_session.refresh(test_conversation)
    return test_conversation


# ============================================================================
# POST /conversations - Create Conversation
# ============================================================================

class TestCreateConversation:

    def test_create_conversation_success(self, client, auth_headers, test_personas):
        persona_ids = [p.unique_id for p in test_personas[:2]]
        response = client.post(
            "/conversations",
            json={"topic": "Should we colonize Mars?", "persona_ids": persona_ids},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["topic"] == "Should we colonize Mars?"
        assert data["unique_id"] is not None
        assert len(data["unique_id"]) == 6
        assert data["turn_count"] == 0
        assert data["is_complete"] is False

    def test_create_conversation_requires_auth(self, client, test_personas):
        persona_ids = [p.unique_id for p in test_personas[:2]]
        response = client.post(
            "/conversations",
            json={"topic": "Test", "persona_ids": persona_ids},
        )
        assert response.status_code == 401

    def test_create_conversation_requires_topic(self, client, auth_headers, test_personas):
        persona_ids = [p.unique_id for p in test_personas[:2]]
        response = client.post(
            "/conversations",
            json={"persona_ids": persona_ids},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_conversation_requires_at_least_one_persona(self, client, auth_headers):
        response = client.post(
            "/conversations",
            json={"topic": "Test topic", "persona_ids": []},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_conversation_nonexistent_persona_returns_404(self, client, auth_headers):
        response = client.post(
            "/conversations",
            json={"topic": "Test topic", "persona_ids": ["xxxxxx"]},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_create_stores_participants(self, client, auth_headers, test_personas, db_session):
        from app.models.conversation import Conversation, ConversationParticipant
        persona_ids = [p.unique_id for p in test_personas[:2]]
        response = client.post(
            "/conversations",
            json={"topic": "Test", "persona_ids": persona_ids},
            headers=auth_headers,
        )
        assert response.status_code == 201
        unique_id = response.json()["unique_id"]
        conv = db_session.query(Conversation).filter_by(unique_id=unique_id).first()
        participants = db_session.query(ConversationParticipant).filter_by(
            conversation_id=conv.id
        ).all()
        assert len(participants) == 2


# ============================================================================
# GET /conversations - List Conversations
# ============================================================================

class TestListConversations:

    def test_list_conversations_empty(self, client, auth_headers):
        response = client.get("/conversations", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_conversations_returns_users_conversations(
        self, client, auth_headers, test_conversation
    ):
        response = client.get("/conversations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["topic"] == "Should we colonize Mars?"

    def test_list_conversations_requires_auth(self, client):
        response = client.get("/conversations")
        assert response.status_code == 401


# ============================================================================
# GET /conversations/{unique_id} - Get Conversation
# ============================================================================

class TestGetConversation:

    def test_get_conversation_success(self, client, auth_headers, test_conversation):
        response = client.get(
            f"/conversations/{test_conversation.unique_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "Should we colonize Mars?"
        assert data["unique_id"] == test_conversation.unique_id
        assert "messages" in data
        assert "participants" in data

    def test_get_conversation_includes_messages(
        self, client, auth_headers, test_conversation_with_messages
    ):
        response = client.get(
            f"/conversations/{test_conversation_with_messages.unique_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2

    def test_get_conversation_not_found(self, client, auth_headers):
        response = client.get("/conversations/xxxxxx", headers=auth_headers)
        assert response.status_code == 404

    def test_get_conversation_requires_auth(self, client, test_conversation):
        response = client.get(f"/conversations/{test_conversation.unique_id}")
        assert response.status_code == 401

    def test_get_other_users_conversation_returns_404(
        self, client, db_session, test_conversation
    ):
        from app.models.user import User
        from app.auth import create_access_token
        other_user = User(email="other@test.com", google_id="other_g", name="Other")
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        token = create_access_token(user_id=other_user.id)
        other_headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            f"/conversations/{test_conversation.unique_id}",
            headers=other_headers,
        )
        assert response.status_code == 404


# ============================================================================
# PATCH /conversations/{unique_id} - Update Conversation
# ============================================================================

class TestUpdateConversation:
    def test_update_conversation_visibility(self, client, auth_headers, test_conversation):
        response = client.patch(
            f"/conversations/{test_conversation.unique_id}",
            json={"is_public": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_public"] is False

        response = client.patch(
            f"/conversations/{test_conversation.unique_id}",
            json={"is_public": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_public"] is True

    def test_update_conversation_not_found(self, client, auth_headers):
        response = client.patch(
            "/conversations/xxxxxx",
            json={"is_public": False},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_update_conversation_requires_auth(self, client, test_conversation):
        response = client.patch(
            f"/conversations/{test_conversation.unique_id}",
            json={"is_public": False},
        )
        assert response.status_code == 401


# ============================================================================
# POST /conversations/{unique_id}/continue - Continue Conversation
# ============================================================================

class TestContinueConversation:

    @patch("app.routers.conversations.ConversationOrchestrator")
    def test_continue_conversation_success(
        self, mock_orch_cls, client, auth_headers, test_conversation, test_personas, db_session
    ):
        from app.models.conversation import ConversationMessage

        # Mock orchestrator to create real messages
        def fake_generate_turn(conversation, personas, history, db):
            msgs = []
            for p in personas:
                msg = ConversationMessage(
                    conversation_id=conversation.id,
                    persona_id=p.id,
                    persona_name=p.name,
                    message_text=f"Response from {p.name}",
                    turn_number=conversation.turn_count + 1,
                )
                db.add(msg)
                msgs.append(msg)
            conversation.turn_count += 1
            db.commit()
            for m in msgs:
                db.refresh(m)
            return msgs

        mock_orch = MagicMock()
        mock_orch.generate_turn.side_effect = fake_generate_turn
        mock_orch_cls.return_value = mock_orch

        response = client.post(
            f"/conversations/{test_conversation.unique_id}/continue",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "new_messages" in data
        assert len(data["new_messages"]) == 2

    @patch("app.routers.conversations.ConversationOrchestrator")
    def test_continue_complete_conversation_returns_400(
        self, mock_orch_cls, client, auth_headers, db_session, test_user, test_personas
    ):
        from app.models.conversation import Conversation, ConversationParticipant
        conv = Conversation(
            topic="Done", created_by=test_user.id, max_turns=3, turn_count=3
        )
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)
        for p in test_personas[:2]:
            db_session.add(ConversationParticipant(
                conversation_id=conv.id, persona_id=p.id
            ))
        db_session.commit()

        response = client.post(
            f"/conversations/{conv.unique_id}/continue",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "maximum" in response.json()["detail"].lower() or "complete" in response.json()["detail"].lower()

    def test_continue_nonexistent_conversation_returns_404(self, client, auth_headers):
        response = client.post("/conversations/xxxxxx/continue", headers=auth_headers)
        assert response.status_code == 404

    def test_continue_requires_auth(self, client, test_conversation):
        response = client.post(f"/conversations/{test_conversation.unique_id}/continue")
        assert response.status_code == 401
