"""
Conversation Routes - Phase 7

Endpoints for creating and continuing focus group conversations.
"""

import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.dependencies import get_current_user
from app.models.user import User
from app.models.persona import Persona
from app.models.conversation import Conversation, ConversationParticipant, ConversationMessage
from app.services.conversation_orchestrator import ConversationOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["conversations"])

class ConversationCreateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=1000)
    persona_ids: List[str] = Field(..., min_length=1)
    is_public: bool = True

class ChallengeCreateRequest(BaseModel):
    proposal: str = Field(..., min_length=1, max_length=2000)
    challenge_type: str = "Public Debate"
    n_personas: int = Field(3, ge=1, le=8)

class ConversationUpdateRequest(BaseModel):
    is_public: bool | None = None

def _build_challenge_background(conversation_unique_id: str, user_id: int, proposal: str, challenge_type: str, n_personas: int) -> None:
    from app.services.challenge_service import ChallengeService
    db = SessionLocal()
    try:
        challenge_svc = ChallengeService()
        personas = challenge_svc.generate_challenge_personas(db=db, user_id=user_id, proposal=proposal, challenge_type=challenge_type, n=n_personas)
        conversation = db.query(Conversation).filter(Conversation.unique_id == conversation_unique_id).first()
        if conversation:
            for persona in personas:
                db.add(ConversationParticipant(conversation_id=conversation.id, persona_id=persona.id, persuaded_score=0.1))
            conversation.status = "active"
            db.commit()
    except Exception as e:
        logger.error(f"Background challenge build failed: {e}")
        db.rollback()
    finally:
        db.close()

@router.post("/conversations/challenge", status_code=status.HTTP_201_CREATED)
def create_challenge(request: ChallengeCreateRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.display_name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You must set a display name before creating a challenge.")
    conversation = Conversation(topic=f"Challenge: {request.proposal[:100]}", proposal=request.proposal, challenge_type=request.challenge_type, is_challenge=True, status="pending", created_by=current_user.id, is_public=False)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    background_tasks.add_task(_build_challenge_background, conversation.unique_id, current_user.id, request.proposal, request.challenge_type, request.n_personas)
    return conversation.to_dict()

@router.post("/conversations", status_code=status.HTTP_201_CREATED)
def create_conversation(request: ConversationCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.display_name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You must set a display name before creating a conversation.")
    from sqlalchemy import or_
    personas = db.query(Persona).filter(Persona.unique_id.in_(request.persona_ids), or_(Persona.user_id == current_user.id, Persona.is_public == True)).all()
    if len(personas) != len(request.persona_ids):
        raise HTTPException(status_code=404, detail="One or more personas not found")
    conversation = Conversation(topic=request.topic, created_by=current_user.id, is_public=request.is_public)
    db.add(conversation)
    db.flush()
    for persona in personas:
        db.add(ConversationParticipant(conversation_id=conversation.id, persona_id=persona.id))
    db.commit()
    db.refresh(conversation)
    return conversation.to_dict()

@router.get("/conversations")
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.created_by == current_user.id).order_by(Conversation.created_at.desc()).all()
    return [c.to_dict() for c in conversations]

@router.get("/conversations/{unique_id}")
def get_conversation(unique_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.unique_id == unique_id, Conversation.created_by == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation.to_dict(include_messages=True)

@router.post("/conversations/{unique_id}/continue")
def continue_conversation(unique_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.unique_id == unique_id, Conversation.created_by == current_user.id).first()
    if not conversation or conversation.is_complete:
        raise HTTPException(status_code=400, detail="Conversation not found or complete")
    participants = db.query(ConversationParticipant).filter(ConversationParticipant.conversation_id == conversation.id).all()
    personas = [p.persona for p in participants]
    existing_messages = db.query(ConversationMessage).filter(ConversationMessage.conversation_id == conversation.id).order_by(ConversationMessage.turn_number, ConversationMessage.id).all()
    history = [{"speaker": m.persona_name, "message": m.message_text} for m in existing_messages if m.moderation_status in ("approved", "user")]
    orchestrator = ConversationOrchestrator()
    new_messages = orchestrator.generate_turn(conversation=conversation, personas=personas, history=history, db=db)
    return {"conversation_unique_id": unique_id, "turn_number": conversation.turn_count, "new_messages": [m.to_dict() for m in new_messages], "is_complete": conversation.is_complete}

class UserMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

@router.post("/conversations/{unique_id}/message", status_code=status.HTTP_201_CREATED)
def inject_user_message(unique_id: str, request: UserMessageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.unique_id == unique_id, Conversation.created_by == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    speaker_name = current_user.display_name or "You"
    msg = ConversationMessage(conversation_id=conversation.id, persona_id=None, persona_name=speaker_name, message_text=request.text, turn_number=conversation.turn_count, moderation_status="user")
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg.to_dict()

@router.patch("/conversations/{unique_id}")
def update_conversation(unique_id: str, request: ConversationUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.unique_id == unique_id, Conversation.created_by == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if request.is_public is not None:
        conversation.is_public = request.is_public
    db.commit()
    db.refresh(conversation)
    return conversation.to_dict(include_messages=True)

@router.delete("/conversations/{unique_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(unique_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.unique_id == unique_id, Conversation.created_by == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
