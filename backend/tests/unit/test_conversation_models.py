"""
Conversation Model Tests - Phase 7 (RED phase)

Tests for Conversation, ConversationParticipant, and ConversationMessage models.

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest


# ============================================================================
# Conversation Model
# ============================================================================

class TestConversationModel:

    def test_create_conversation(self, db_session, test_user):
        from app.models.conversation import Conversation
        conv = Conversation(
            topic="Should we colonize Mars?",
            created_by=test_user.id,
        )
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        assert conv.id is not None
        assert conv.topic == "Should we colonize Mars?"
        assert conv.created_by == test_user.id

    def test_unique_id_auto_generated(self, db_session, test_user):
        from app.models.conversation import Conversation
        conv = Conversation(topic="Test topic", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        assert conv.unique_id is not None
        assert len(conv.unique_id) == 6
        assert conv.unique_id.isalnum()

    def test_unique_ids_are_unique(self, db_session, test_user):
        from app.models.conversation import Conversation
        c1 = Conversation(topic="Topic 1", created_by=test_user.id)
        c2 = Conversation(topic="Topic 2", created_by=test_user.id)
        db_session.add_all([c1, c2])
        db_session.commit()
        assert c1.unique_id != c2.unique_id

    def test_default_max_turns(self, db_session, test_user):
        from app.models.conversation import Conversation
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)
        assert conv.max_turns == 20

    def test_default_turn_count_zero(self, db_session, test_user):
        from app.models.conversation import Conversation
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)
        assert conv.turn_count == 0

    def test_created_at_auto_set(self, db_session, test_user):
        from app.models.conversation import Conversation
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)
        assert conv.created_at is not None

    def test_is_complete_when_at_max_turns(self, db_session, test_user):
        from app.models.conversation import Conversation
        conv = Conversation(topic="Test", created_by=test_user.id, max_turns=5, turn_count=5)
        db_session.add(conv)
        db_session.commit()
        assert conv.is_complete is True

    def test_is_not_complete_when_below_max_turns(self, db_session, test_user):
        from app.models.conversation import Conversation
        conv = Conversation(topic="Test", created_by=test_user.id, max_turns=20, turn_count=3)
        db_session.add(conv)
        db_session.commit()
        assert conv.is_complete is False

    def test_to_dict(self, db_session, test_user):
        from app.models.conversation import Conversation
        conv = Conversation(topic="Test topic", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)
        d = conv.to_dict()
        assert d["topic"] == "Test topic"
        assert d["unique_id"] is not None
        assert d["turn_count"] == 0
        assert d["max_turns"] == 20
        assert d["is_complete"] is False


# ============================================================================
# ConversationParticipant Model
# ============================================================================

class TestConversationParticipant:

    def test_add_participant(self, db_session, test_user, test_persona):
        from app.models.conversation import Conversation, ConversationParticipant
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        participant = ConversationParticipant(
            conversation_id=conv.id,
            persona_id=test_persona.id,
        )
        db_session.add(participant)
        db_session.commit()

        result = db_session.query(ConversationParticipant).filter_by(
            conversation_id=conv.id
        ).first()
        assert result is not None
        assert result.persona_id == test_persona.id

    def test_multiple_participants(self, db_session, test_user, test_personas):
        from app.models.conversation import Conversation, ConversationParticipant
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        for persona in test_personas:
            db_session.add(ConversationParticipant(
                conversation_id=conv.id,
                persona_id=persona.id,
            ))
        db_session.commit()

        count = db_session.query(ConversationParticipant).filter_by(
            conversation_id=conv.id
        ).count()
        assert count == 3


# ============================================================================
# ConversationMessage Model
# ============================================================================

class TestConversationMessage:

    def test_create_message(self, db_session, test_user, test_persona):
        from app.models.conversation import Conversation, ConversationMessage
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        msg = ConversationMessage(
            conversation_id=conv.id,
            persona_id=test_persona.id,
            persona_name=test_persona.name,
            message_text="I believe we should colonize Mars.",
            turn_number=1,
        )
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)

        assert msg.id is not None
        assert msg.message_text == "I believe we should colonize Mars."
        assert msg.turn_number == 1

    def test_default_moderation_status_approved(self, db_session, test_user, test_persona):
        from app.models.conversation import Conversation, ConversationMessage
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()

        msg = ConversationMessage(
            conversation_id=conv.id,
            persona_id=test_persona.id,
            persona_name=test_persona.name,
            message_text="Hello world",
            turn_number=1,
        )
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)

        assert msg.moderation_status == "approved"

    def test_toxicity_score_nullable(self, db_session, test_user, test_persona):
        from app.models.conversation import Conversation, ConversationMessage
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()

        msg = ConversationMessage(
            conversation_id=conv.id,
            persona_id=test_persona.id,
            persona_name=test_persona.name,
            message_text="Hello",
            turn_number=1,
        )
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)
        assert msg.toxicity_score is None

    def test_to_dict(self, db_session, test_user, test_persona):
        from app.models.conversation import Conversation, ConversationMessage
        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()

        msg = ConversationMessage(
            conversation_id=conv.id,
            persona_id=test_persona.id,
            persona_name=test_persona.name,
            message_text="Mars is worth exploring.",
            turn_number=1,
            toxicity_score=0.02,
        )
        db_session.add(msg)
        db_session.commit()
        db_session.refresh(msg)

        d = msg.to_dict()
        assert d["message_text"] == "Mars is worth exploring."
        assert d["persona_name"] == test_persona.name
        assert d["turn_number"] == 1
        assert d["toxicity_score"] == pytest.approx(0.02)
