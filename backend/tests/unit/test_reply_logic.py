import pytest
from unittest.mock import MagicMock
from app.services.conversation_orchestrator import ConversationOrchestrator
from app.models.conversation import Conversation, ConversationMessage

def make_mock_llm(responses):
    svc = MagicMock()
    svc.generate_response.side_effect = responses
    return svc

def make_mock_moderator():
    svc = MagicMock()
    svc.analyze_toxicity.return_value = 0.01
    svc.is_safe.return_value = True
    return svc

def test_reply_to_parsing_and_linking(db_session, test_user, test_personas):
    conv = Conversation(topic="Test topic", created_by=test_user.id)
    db_session.add(conv)
    db_session.commit()
    db_session.refresh(conv)

    # First turn: Persona 1 speaks
    orchestrator = ConversationOrchestrator(
        llm_service=make_mock_llm(["Hello world"]),
        moderation_service=make_mock_moderator(),
    )
    msg1 = orchestrator.generate_turn(
        conversation=conv, personas=[test_personas[0]], history=[], db=db_session
    )[0]

    db_session.refresh(conv)
    assert conv.turn_count == 1
    assert msg1.id is not None

    # Second turn: Persona 2 replies to Persona 1
    # Note: history will contain msg1
    orchestrator2 = ConversationOrchestrator(
        llm_service=make_mock_llm(["REPLY_TO: [1] I agree with you!"]),
        moderation_service=make_mock_moderator(),
    )

    # We need to pass the actual history as it would be from the DB
    history = [{"speaker": msg1.persona_name, "message": msg1.message_text}]

    msg2 = orchestrator2.generate_turn(
        conversation=conv, personas=[test_personas[1]], history=history, db=db_session
    )[0]

    assert msg2.reply_to_id == msg1.id
    assert msg2.message_text == "I agree with you!"

def test_dynamic_history_within_turn(db_session, test_user, test_personas):
    conv = Conversation(topic="Test topic", created_by=test_user.id)
    db_session.add(conv)
    db_session.commit()
    db_session.refresh(conv)

    # Persona 1 and Persona 2 in the same turn
    # Persona 2 should be able to reply to Persona 1 because history is updated dynamically
    llm = make_mock_llm(["Message from P1", "REPLY_TO: [1] P2 replying to P1"])
    orchestrator = ConversationOrchestrator(
        llm_service=llm,
        moderation_service=make_mock_moderator(),
    )

    messages = orchestrator.generate_turn(
        conversation=conv, personas=[test_personas[0], test_personas[1]], history=[], db=db_session
    )

    assert len(messages) == 2
    assert messages[1].reply_to_id == messages[0].id
    assert messages[1].message_text == "P2 replying to P1"

    # Verify that Persona 2's generation call actually saw Persona 1's message in history
    # 1st call: personas[0], history=[]
    # 2nd call: personas[1], history=[{"speaker": P1, "message": "Message from P1"}]
    assert llm.generate_response.call_count == 2
    second_call_history = llm.generate_response.call_args_list[1].kwargs['conversation_history']
    assert len(second_call_history) == 1
    assert second_call_history[0]['message'] == "Message from P1"
