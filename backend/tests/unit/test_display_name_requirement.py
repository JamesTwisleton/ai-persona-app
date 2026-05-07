import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User

@pytest.fixture
def user_without_display_name(db_session):
    user = User(
        email="nodisplay@example.com",
        google_id="google_no_display",
        name="No Display Name",
        display_name=None
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers_no_display(user_without_display_name):
    from app.auth import create_access_token
    token = create_access_token(user_id=user_without_display_name.id)
    return {"Authorization": f"Bearer {token}"}

def test_create_persona_without_display_name_fails(client, auth_headers_no_display):
    response = client.post(
        "/personas",
        json={"name": "Test Persona", "description": "Some description"},
        headers=auth_headers_no_display
    )
    assert response.status_code == 403
    assert "display name" in response.json()["detail"].lower()

def test_create_conversation_without_display_name_fails(client, auth_headers_no_display):
    response = client.post(
        "/conversations",
        json={"topic": "Test Topic", "persona_ids": ["dummy1", "dummy2"]},
        headers=auth_headers_no_display
    )
    assert response.status_code == 403
    assert "display name" in response.json()["detail"].lower()

def test_create_challenge_without_display_name_fails(client, auth_headers_no_display):
    response = client.post(
        "/conversations/challenge",
        json={"proposal": "Test Proposal", "n_personas": 3},
        headers=auth_headers_no_display
    )
    assert response.status_code == 403
    assert "display name" in response.json()["detail"].lower()

def test_user_message_uses_display_name(client, auth_headers, test_user, test_conversation_data, db_session):
    # Setup: Create a conversation first
    from app.models.conversation import Conversation
    import secrets
    conv = Conversation(
        topic="Test Conversation",
        created_by=test_user.id,
        status="active",
        unique_id=secrets.token_hex(3)
    )
    db_session.add(conv)
    db_session.commit()
    db_session.refresh(conv)

    response = client.post(
        f"/conversations/{conv.unique_id}/message",
        json={"text": "Hello world"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["persona_name"] == "TestUser"
