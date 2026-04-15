"""
Conversation Orchestrator Tests - Phase 7 (RED phase)

Tests for ConversationOrchestrator: multi-persona response generation,
moderation, and regeneration logic.

All LLM and moderation calls are mocked — tests run fast.

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest
from unittest.mock import MagicMock, patch, call


def make_mock_llm(response="I think this is a great idea."):
    svc = MagicMock()
    svc.generate_response.return_value = response
    return svc


def make_mock_moderator(score=0.01, safe=True):
    svc = MagicMock()
    svc.analyze_toxicity.return_value = score
    svc.is_safe.return_value = safe
    return svc


# ============================================================================
# ConversationOrchestrator Initialization
# ============================================================================

class TestOrchestratorInit:

    def test_init_with_injected_services(self):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        llm = MagicMock()
        mod = MagicMock()
        orchestrator = ConversationOrchestrator(llm_service=llm, moderation_service=mod)
        assert orchestrator.llm_service is llm
        assert orchestrator.moderation_service is mod

    def test_default_max_regeneration_attempts(self):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        orchestrator = ConversationOrchestrator(
            llm_service=MagicMock(), moderation_service=MagicMock()
        )
        assert orchestrator.max_regeneration_attempts == 2


# ============================================================================
# generate_turn Tests
# ============================================================================

class TestGenerateTurn:

    def test_generates_one_message_per_persona(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation, ConversationParticipant

        conv = Conversation(topic="Should we colonize Mars?", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        orchestrator = ConversationOrchestrator(
            llm_service=make_mock_llm(),
            moderation_service=make_mock_moderator(),
        )
        messages = orchestrator.generate_turn(
            conversation=conv,
            personas=test_personas,
            history=[],
            db=db_session,
        )

        assert len(messages) == len(test_personas)

    def test_messages_saved_to_database(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation, ConversationMessage

        conv = Conversation(topic="Climate change", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        orchestrator = ConversationOrchestrator(
            llm_service=make_mock_llm(),
            moderation_service=make_mock_moderator(),
        )
        orchestrator.generate_turn(
            conversation=conv, personas=test_personas, history=[], db=db_session
        )

        count = db_session.query(ConversationMessage).filter_by(
            conversation_id=conv.id
        ).count()
        assert count == len(test_personas)

    def test_turn_count_incremented(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation

        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        assert conv.turn_count == 0

        orchestrator = ConversationOrchestrator(
            llm_service=make_mock_llm(),
            moderation_service=make_mock_moderator(),
        )
        orchestrator.generate_turn(
            conversation=conv, personas=test_personas, history=[], db=db_session
        )

        db_session.refresh(conv)
        assert conv.turn_count == 1

    def test_calls_llm_for_each_persona(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation

        conv = Conversation(topic="Test topic", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        llm = make_mock_llm()
        orchestrator = ConversationOrchestrator(
            llm_service=llm, moderation_service=make_mock_moderator()
        )
        orchestrator.generate_turn(
            conversation=conv, personas=test_personas, history=[], db=db_session
        )

        assert llm.generate_response.call_count == len(test_personas)

    def test_checks_moderation_for_each_message(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation

        conv = Conversation(topic="Test topic", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        mod = make_mock_moderator()
        orchestrator = ConversationOrchestrator(
            llm_service=make_mock_llm(), moderation_service=mod
        )
        orchestrator.generate_turn(
            conversation=conv, personas=test_personas, history=[], db=db_session
        )

        assert mod.analyze_toxicity.call_count == len(test_personas)

    def test_messages_have_correct_turn_number(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation, ConversationMessage

        conv = Conversation(topic="Test", created_by=test_user.id, turn_count=2)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        orchestrator = ConversationOrchestrator(
            llm_service=make_mock_llm(), moderation_service=make_mock_moderator()
        )
        orchestrator.generate_turn(
            conversation=conv, personas=test_personas, history=[], db=db_session
        )

        messages = db_session.query(ConversationMessage).filter_by(
            conversation_id=conv.id
        ).all()
        assert all(m.turn_number == 3 for m in messages)

    def test_includes_history_in_llm_call(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation

        conv = Conversation(topic="AI ethics", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        llm = make_mock_llm()
        orchestrator = ConversationOrchestrator(
            llm_service=llm, moderation_service=make_mock_moderator()
        )
        history = [{"speaker": "Bob", "message": "I think AI is dangerous."}]
        orchestrator.generate_turn(
            conversation=conv, personas=[test_personas[0]], history=history, db=db_session
        )

        # History should be passed as a keyword argument
        call_kwargs = llm.generate_response.call_args.kwargs
        assert call_kwargs.get("conversation_history") == history

    def test_toxic_message_triggers_regeneration(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation

        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        llm = MagicMock()
        llm.generate_response.side_effect = ["Toxic content!", "Safe content this time."]

        mod = MagicMock()
        mod.analyze_toxicity.side_effect = [0.95, 0.05]
        mod.is_safe.side_effect = [False, True]

        orchestrator = ConversationOrchestrator(
            llm_service=llm, moderation_service=mod, max_regeneration_attempts=2
        )
        messages = orchestrator.generate_turn(
            conversation=conv, personas=[test_personas[0]], history=[], db=db_session
        )

        assert len(messages) == 1
        assert messages[0].message_text == "Safe content this time."
        assert messages[0].moderation_status == "approved"
        assert llm.generate_response.call_count == 2

    def test_still_toxic_after_max_attempts_marked_flagged(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation

        conv = Conversation(topic="Test", created_by=test_user.id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        llm = MagicMock()
        llm.generate_response.return_value = "Toxic content!"

        mod = MagicMock()
        mod.analyze_toxicity.return_value = 0.95
        mod.is_safe.return_value = False

        orchestrator = ConversationOrchestrator(
            llm_service=llm, moderation_service=mod, max_regeneration_attempts=2
        )
        messages = orchestrator.generate_turn(
            conversation=conv, personas=[test_personas[0]], history=[], db=db_session
        )

        assert len(messages) == 1
        assert messages[0].moderation_status == "flagged"

    def test_raises_if_conversation_is_complete(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation

        conv = Conversation(topic="Test", created_by=test_user.id, max_turns=3, turn_count=3)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        orchestrator = ConversationOrchestrator(
            llm_service=MagicMock(), moderation_service=MagicMock()
        )
        with pytest.raises(ValueError, match="maximum"):
            orchestrator.generate_turn(
                conversation=conv, personas=test_personas, history=[], db=db_session
            )

    def test_generate_turn_challenge_mode(self, db_session, test_user, test_personas):
        from app.services.conversation_orchestrator import ConversationOrchestrator
        from app.models.conversation import Conversation, ConversationParticipant

        conv = Conversation(
            topic="Challenge",
            proposal="Test",
            is_challenge=True,
            created_by=test_user.id
        )
        db_session.add(conv)
        db_session.flush()

        for p in test_personas[:1]:
            db_session.add(ConversationParticipant(
                conversation_id=conv.id,
                persona_id=p.id,
                persuaded_score=0.2
            ))
        db_session.commit()
        db_session.refresh(conv)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='Response')]
        mock_llm.client.messages.create.return_value = mock_response
        mock_llm.model = "test-model"

        # Mock challenge service for persuasion evaluation
        with patch("app.services.challenge_service.ChallengeService") as mock_challenge_svc_cls:
            mock_challenge_svc = mock_challenge_svc_cls.return_value
            mock_challenge_svc.evaluate_persuasion.return_value = {"new_score": 0.3, "reasoning": "Progress."}

            orchestrator = ConversationOrchestrator(
                llm_service=mock_llm,
                moderation_service=make_mock_moderator(),
            )

            history = [{"speaker": "User", "message": "I have proof."}]
            messages = orchestrator.generate_turn(
                conversation=conv,
                personas=[test_personas[0]],
                history=history,
                db=db_session,
            )

            assert len(messages) == 1
            # Verify score updated
            assert conv.participants[0].persuaded_score == 0.3
