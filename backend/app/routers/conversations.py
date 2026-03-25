"""
Conversation Routes - Phase 7

Endpoints for creating and continuing focus group conversations.

Endpoints:
- POST /conversations - Create a new conversation
- GET /conversations - List user's conversations
- GET /conversations/{unique_id} - Get conversation with messages
- POST /conversations/{unique_id}/continue - Generate the next turn
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.persona import Persona
from app.models.conversation import Conversation, ConversationParticipant, ConversationMessage
from app.services.conversation_orchestrator import ConversationOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["conversations"])


# ============================================================================
# Request Schemas
# ============================================================================

class ConversationCreateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=1000)
    persona_ids: List[str] = Field(..., min_length=1)
    is_public: bool = True

class ConversationUpdateRequest(BaseModel):
    is_public: bool | None = None


# ============================================================================
# POST /conversations - Create Conversation
# ============================================================================

@router.post(
    "/conversations",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new focus group conversation",
    responses={
        201: {"description": "Conversation created"},
        401: {"description": "Not authenticated"},
        404: {"description": "One or more personas not found"},
        422: {"description": "Validation error"},
    },
)
def create_conversation(
    request: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Fetch all requested personas — allow own personas OR other users' public personas
    from sqlalchemy import or_
    personas = (
        db.query(Persona)
        .filter(
            Persona.unique_id.in_(request.persona_ids),
            or_(Persona.user_id == current_user.id, Persona.is_public == True),
        )
        .all()
    )
    if len(personas) != len(request.persona_ids):
        found_ids = {p.unique_id for p in personas}
        missing = [pid for pid in request.persona_ids if pid not in found_ids]
        raise HTTPException(
            status_code=404,
            detail=f"Personas not found: {missing}",
        )

    # Create conversation
    conversation = Conversation(
        topic=request.topic,
        created_by=current_user.id,
        is_public=request.is_public,
    )
    db.add(conversation)
    db.flush()  # Get the ID without committing

    # Add participants
    for persona in personas:
        db.add(ConversationParticipant(
            conversation_id=conversation.id,
            persona_id=persona.id,
        ))

    db.commit()
    db.refresh(conversation)
    return conversation.to_dict()


# ============================================================================
# GET /conversations - List User's Conversations
# ============================================================================

@router.get(
    "/conversations",
    summary="List your conversations",
    responses={
        200: {"description": "List of conversations"},
        401: {"description": "Not authenticated"},
    },
)
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.created_by == current_user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    return [c.to_dict() for c in conversations]


# ============================================================================
# GET /conversations/{unique_id} - Get Conversation with Messages
# ============================================================================

@router.get(
    "/conversations/{unique_id}",
    summary="Get a conversation with all messages",
    responses={
        200: {"description": "Conversation details with messages"},
        401: {"description": "Not authenticated"},
        404: {"description": "Conversation not found"},
    },
)
def get_conversation(
    unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.unique_id == unique_id,
            Conversation.created_by == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation.to_dict(include_messages=True)


# ============================================================================
# POST /conversations/{unique_id}/continue - Generate Next Turn
# ============================================================================

@router.post(
    "/conversations/{unique_id}/continue",
    summary="Generate the next turn of the conversation",
    responses={
        200: {"description": "New messages generated"},
        400: {"description": "Conversation is complete"},
        401: {"description": "Not authenticated"},
        404: {"description": "Conversation not found"},
    },
)
def continue_conversation(
    unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.unique_id == unique_id,
            Conversation.created_by == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.is_complete:
        raise HTTPException(
            status_code=400,
            detail=f"Conversation has reached its maximum of {conversation.max_turns} turns.",
        )

    # Load participants and their personas
    participants = (
        db.query(ConversationParticipant)
        .filter(ConversationParticipant.conversation_id == conversation.id)
        .all()
    )
    personas = [p.persona for p in participants]

    # Build conversation history from existing messages
    existing_messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conversation.id)
        .order_by(ConversationMessage.turn_number, ConversationMessage.id)
        .all()
    )
    history = [
        {"speaker": m.persona_name, "message": m.message_text}
        for m in existing_messages
        if m.moderation_status in ("approved", "user")
    ]

    try:
        orchestrator = ConversationOrchestrator()
        new_messages = orchestrator.generate_turn(
            conversation=conversation,
            personas=personas,
            history=history,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "conversation_unique_id": unique_id,
        "turn_number": conversation.turn_count,
        "new_messages": [m.to_dict() for m in new_messages],
        "is_complete": conversation.is_complete,
    }


# ============================================================================
# POST /conversations/{unique_id}/message - User Injects a Message
# ============================================================================

class UserMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


@router.post(
    "/conversations/{unique_id}/message",
    status_code=status.HTTP_201_CREATED,
    summary="Inject a user message into the conversation",
)
def inject_user_message(
    unique_id: str,
    request: UserMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.unique_id == unique_id,
            Conversation.created_by == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    speaker_name = current_user.name or "You"
    msg = ConversationMessage(
        conversation_id=conversation.id,
        persona_id=None,
        persona_name=speaker_name,
        message_text=request.text,
        turn_number=conversation.turn_count,
        toxicity_score=None,
        moderation_status="user",
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg.to_dict()


# ============================================================================
# PATCH /conversations/{unique_id} - Update Conversation
# ============================================================================

@router.patch(
    "/conversations/{unique_id}",
    summary="Update a conversation",
    responses={
        200: {"description": "Conversation updated"},
        401: {"description": "Not authenticated"},
        404: {"description": "Conversation not found"},
    },
)
def update_conversation(
    unique_id: str,
    request: ConversationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.unique_id == unique_id,
            Conversation.created_by == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if request.is_public is not None:
        conversation.is_public = request.is_public

    db.commit()
    db.refresh(conversation)
    return conversation.to_dict(include_messages=True)


# ============================================================================
# DELETE /conversations/{unique_id} - Delete Conversation
# ============================================================================

@router.delete(
    "/conversations/{unique_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
    responses={
        204: {"description": "Conversation deleted"},
        401: {"description": "Not authenticated"},
        404: {"description": "Conversation not found"},
    },
)
def delete_conversation(
    unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.unique_id == unique_id,
            Conversation.created_by == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
