"""
Discovery Routes

Public feed, upvoting, page view tracking, visibility toggling, and conversation forking.

Endpoints:
- GET  /discover              - Public hot/top/new feed (personas + conversations)
- GET  /p/{unique_id}         - Public persona profile (tracks view)
- GET  /c/{unique_id}         - Public conversation (tracks view)
- POST /p/{unique_id}/upvote  - Toggle upvote on a persona
- POST /c/{unique_id}/upvote  - Toggle upvote on a conversation
- PATCH /personas/{unique_id}/visibility    - Set is_public
- PATCH /conversations/{unique_id}/visibility - Set is_public
- POST /conversations/{unique_id}/fork      - Fork a conversation
- DELETE /personas/{unique_id}/force        - Superuser delete persona
- DELETE /conversations/{unique_id}/force   - Superuser delete conversation
"""

import hashlib
import logging
import math
from datetime import datetime, date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.models.persona import Persona
from app.models.conversation import Conversation, ConversationParticipant, ConversationMessage
from app.models.social import Upvote, PageView

logger = logging.getLogger(__name__)

router = APIRouter(tags=["discovery"])


# ============================================================================
# Helpers
# ============================================================================

def _hot_score(upvotes: int, views: int, created_at: datetime) -> float:
    age_hours = max((datetime.utcnow() - created_at.replace(tzinfo=None)).total_seconds() / 3600, 0)
    return (upvotes + math.log10(views + 1)) / ((age_hours + 2) ** 1.5)


def _ip_hash(request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    return hashlib.sha256(ip.encode()).hexdigest()[:32]


def _record_view(db: Session, target_type: str, target_id: str, user_id: Optional[int], ip: str) -> bool:
    """Insert a page view. Returns True if it was a new (deduplicated) view."""
    today = date.today()
    uid = user_id if user_id else None
    ih = ip if not user_id else None  # prefer user_id dedup over ip

    existing = db.query(PageView).filter(
        PageView.target_type == target_type,
        PageView.target_id == target_id,
        PageView.viewed_date == today,
        PageView.user_id == uid if uid else PageView.ip_hash == ih,
    ).first()

    if existing:
        return False

    db.add(PageView(
        target_type=target_type,
        target_id=target_id,
        user_id=uid,
        ip_hash=ih,
        viewed_date=today,
    ))
    # Increment counter on the target
    if target_type == "persona":
        db.execute(
            text("UPDATE personas SET view_count = view_count + 1 WHERE unique_id = :uid"),
            {"uid": target_id}
        )
    else:
        db.execute(
            text("UPDATE conversations SET view_count = view_count + 1 WHERE unique_id = :uid"),
            {"uid": target_id}
        )
    db.commit()
    return True


# ============================================================================
# GET /discover
# ============================================================================

class DiscoverRequest(BaseModel):
    sort: str = "hot"   # hot | top | new
    cursor: Optional[int] = None
    limit: int = 20


@router.get("/discover", summary="Public discovery feed")
def discover(
    sort: str = "hot",
    cursor: Optional[int] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    limit = min(limit, 50)

    def base_persona_q():
        return db.query(Persona).filter(Persona.is_public == True)

    def base_conv_q():
        return db.query(Conversation).filter(Conversation.is_public == True)

    if sort == "new":
        personas = base_persona_q().order_by(Persona.created_at.desc()).limit(limit).all()
        convos = base_conv_q().order_by(Conversation.created_at.desc()).limit(limit).all()
    elif sort == "top":
        personas = base_persona_q().order_by(Persona.upvote_count.desc(), Persona.view_count.desc()).limit(limit).all()
        convos = base_conv_q().order_by(Conversation.upvote_count.desc(), Conversation.view_count.desc()).limit(limit).all()
    else:  # hot
        personas = base_persona_q().all()
        convos = base_conv_q().all()
        personas = sorted(personas, key=lambda p: _hot_score(p.upvote_count, p.view_count, p.created_at), reverse=True)[:limit]
        convos = sorted(convos, key=lambda c: _hot_score(c.upvote_count, c.view_count, c.created_at), reverse=True)[:limit]

    return {
        "personas": [p.to_dict() for p in personas],
        "conversations": [c.to_dict() for c in convos],
    }


# ============================================================================
# GET /p/{unique_id} - Public persona
# ============================================================================

@router.get("/p/{unique_id}", summary="Public persona profile")
def public_persona(
    unique_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    persona = db.query(Persona).filter(Persona.unique_id == unique_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    if not persona.is_public and (not current_user or current_user.id != persona.user_id):
        raise HTTPException(status_code=404, detail="Persona not found")

    _record_view(db, "persona", unique_id, current_user.id if current_user else None, _ip_hash(request))

    result = persona.to_dict()
    result["is_owner"] = bool(current_user and current_user.id == persona.user_id)
    return result


# ============================================================================
# GET /p/{unique_id}/conversations - Conversations featuring a persona
# ============================================================================

@router.get("/p/{unique_id}/conversations", summary="Public conversations featuring this persona")
def persona_conversations(
    unique_id: str,
    sort: str = "hot",
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    persona = db.query(Persona).filter(Persona.unique_id == unique_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Conversations that have this persona as a participant
    convos_q = (
        db.query(Conversation)
        .join(ConversationParticipant, ConversationParticipant.conversation_id == Conversation.id)
        .filter(
            ConversationParticipant.persona_id == persona.id,
            Conversation.is_public == True,
        )
    )

    limit = min(limit, 50)
    if sort == "new":
        convos = convos_q.order_by(Conversation.created_at.desc()).limit(limit).all()
    elif sort == "top":
        convos = convos_q.order_by(Conversation.upvote_count.desc(), Conversation.view_count.desc()).limit(limit).all()
    else:  # hot
        convos = convos_q.all()
        convos = sorted(convos, key=lambda c: _hot_score(c.upvote_count, c.view_count, c.created_at), reverse=True)[:limit]

    return [c.to_dict() for c in convos]


# ============================================================================
# GET /c/{unique_id} - Public conversation
# ============================================================================

@router.get("/c/{unique_id}", summary="Public conversation")
def public_conversation(
    unique_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    conv = db.query(Conversation).filter(Conversation.unique_id == unique_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not conv.is_public and (not current_user or current_user.id != conv.created_by):
        raise HTTPException(status_code=404, detail="Conversation not found")

    _record_view(db, "conversation", unique_id, current_user.id if current_user else None, _ip_hash(request))

    result = conv.to_dict(include_messages=True)
    result["is_owner"] = bool(current_user and current_user.id == conv.created_by)
    return result


# ============================================================================
# POST /p/{unique_id}/upvote - Toggle persona upvote
# ============================================================================

@router.post("/p/{unique_id}/upvote", summary="Toggle upvote on a persona")
def upvote_persona(
    unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    persona = db.query(Persona).filter(Persona.unique_id == unique_id).first()
    if not persona or not persona.is_public:
        raise HTTPException(status_code=404, detail="Persona not found")

    existing = db.query(Upvote).filter(
        Upvote.user_id == current_user.id,
        Upvote.target_type == "persona",
        Upvote.target_id == unique_id,
    ).first()

    if existing:
        db.delete(existing)
        db.execute(text("UPDATE personas SET upvote_count = CASE WHEN upvote_count > 0 THEN upvote_count - 1 ELSE 0 END WHERE unique_id = :uid"), {"uid": unique_id})
        db.commit()
        db.refresh(persona)
        return {"upvoted": False, "upvote_count": persona.upvote_count}
    else:
        db.add(Upvote(user_id=current_user.id, target_type="persona", target_id=unique_id))
        db.execute(text("UPDATE personas SET upvote_count = upvote_count + 1 WHERE unique_id = :uid"), {"uid": unique_id})
        db.commit()
        db.refresh(persona)
        return {"upvoted": True, "upvote_count": persona.upvote_count}


# ============================================================================
# POST /c/{unique_id}/upvote - Toggle conversation upvote
# ============================================================================

@router.post("/c/{unique_id}/upvote", summary="Toggle upvote on a conversation")
def upvote_conversation(
    unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(Conversation.unique_id == unique_id).first()
    if not conv or not conv.is_public:
        raise HTTPException(status_code=404, detail="Conversation not found")

    existing = db.query(Upvote).filter(
        Upvote.user_id == current_user.id,
        Upvote.target_type == "conversation",
        Upvote.target_id == unique_id,
    ).first()

    if existing:
        db.delete(existing)
        db.execute(text("UPDATE conversations SET upvote_count = CASE WHEN upvote_count > 0 THEN upvote_count - 1 ELSE 0 END WHERE unique_id = :uid"), {"uid": unique_id})
        db.commit()
        db.refresh(conv)
        return {"upvoted": False, "upvote_count": conv.upvote_count}
    else:
        db.add(Upvote(user_id=current_user.id, target_type="conversation", target_id=unique_id))
        db.execute(text("UPDATE conversations SET upvote_count = upvote_count + 1 WHERE unique_id = :uid"), {"uid": unique_id})
        db.commit()
        db.refresh(conv)
        return {"upvoted": True, "upvote_count": conv.upvote_count}


# ============================================================================
# PATCH /personas/{unique_id}/visibility
# ============================================================================

class VisibilityRequest(BaseModel):
    is_public: bool


@router.patch("/personas/{unique_id}/visibility", summary="Set persona visibility")
def set_persona_visibility(
    unique_id: str,
    body: VisibilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    persona = db.query(Persona).filter(
        Persona.unique_id == unique_id,
        Persona.user_id == current_user.id,
    ).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    persona.is_public = body.is_public
    db.commit()
    return {"unique_id": unique_id, "is_public": persona.is_public}


@router.patch("/conversations/{unique_id}/visibility", summary="Set conversation visibility")
def set_conversation_visibility(
    unique_id: str,
    body: VisibilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(
        Conversation.unique_id == unique_id,
        Conversation.created_by == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.is_public = body.is_public
    db.commit()
    return {"unique_id": unique_id, "is_public": conv.is_public}


# ============================================================================
# POST /conversations/{unique_id}/fork
# ============================================================================

class ForkRequest(BaseModel):
    topic: Optional[str] = None
    persona_ids: Optional[List[str]] = None  # if provided, swap participants


@router.post("/conversations/{unique_id}/fork", status_code=status.HTTP_201_CREATED, summary="Fork a conversation")
def fork_conversation(
    unique_id: str,
    body: ForkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source = db.query(Conversation).filter(Conversation.unique_id == unique_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not source.is_public and source.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Determine participants for the fork
    if body.persona_ids:
        # Caller provided new personas — must own them
        personas = (
            db.query(Persona)
            .filter(Persona.unique_id.in_(body.persona_ids), Persona.user_id == current_user.id)
            .all()
        )
        if len(personas) != len(body.persona_ids):
            raise HTTPException(status_code=404, detail="One or more personas not found")
    else:
        # Inherit the original participants
        participants = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == source.id
        ).all()
        personas = [p.persona for p in participants if p.persona]

    # Create the forked conversation
    fork = Conversation(
        topic=body.topic or source.topic,
        created_by=current_user.id,
        forked_from_id=source.unique_id,
    )
    db.add(fork)
    db.flush()

    # Copy participants
    for persona in personas:
        db.add(ConversationParticipant(conversation_id=fork.id, persona_id=persona.id))

    # Copy full message history from source
    source_messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == source.id)
        .order_by(ConversationMessage.turn_number, ConversationMessage.id)
        .all()
    )
    for msg in source_messages:
        db.add(ConversationMessage(
            conversation_id=fork.id,
            persona_id=msg.persona_id,
            persona_name=msg.persona_name,
            message_text=msg.message_text,
            turn_number=msg.turn_number,
            toxicity_score=msg.toxicity_score,
            moderation_status=msg.moderation_status,
        ))

    fork.turn_count = source.turn_count
    db.commit()
    db.refresh(fork)
    return fork.to_dict(include_messages=True)


# ============================================================================
# Superuser force-delete endpoints
# ============================================================================

@router.delete("/personas/{unique_id}/force", status_code=status.HTTP_204_NO_CONTENT, summary="Superuser delete persona")
def force_delete_persona(
    unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")
    persona = db.query(Persona).filter(Persona.unique_id == unique_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    db.delete(persona)
    db.commit()


@router.delete("/conversations/{unique_id}/force", status_code=status.HTTP_204_NO_CONTENT, summary="Superuser delete conversation")
def force_delete_conversation(
    unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")
    conv = db.query(Conversation).filter(Conversation.unique_id == unique_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
