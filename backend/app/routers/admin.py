"""
Admin Routes

Endpoints for admin and superuser management.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_admin, get_current_superuser
from app.models.conversation import Conversation
from app.models.moderation import ModerationAuditLog
from app.models.persona import Persona
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/flagged-content")
def get_flagged_content(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    logs = db.query(ModerationAuditLog).order_by(ModerationAuditLog.created_at.desc()).all()
    return [log.to_dict() for log in logs]

@router.post("/approve/{log_id}")
def approve_content(log_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    log = db.query(ModerationAuditLog).filter(ModerationAuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Moderation log entry not found")
    log.action_taken = "approved"
    log.reviewed_by = admin.id
    db.commit()
    db.refresh(log)
    return log.to_dict()

@router.post("/block/{log_id}")
def block_content(log_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    log = db.query(ModerationAuditLog).filter(ModerationAuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Moderation log entry not found")
    log.action_taken = "blocked"
    log.reviewed_by = admin.id
    db.commit()
    db.refresh(log)
    return log.to_dict()

@router.get("/users")
def list_users(superuser: User = Depends(get_current_superuser), db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)):
    offset = (page - 1) * page_size
    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
    total = db.query(func.count(User.id)).scalar()
    result = []
    for u in users:
        persona_count = db.query(func.count(Persona.id)).filter(Persona.user_id == u.id).scalar()
        d = u.to_dict(show_private=True)
        d["persona_count"] = persona_count
        result.append(d)
    return {"total": total, "page": page, "page_size": page_size, "items": result}

class SetSuperuserRequest(BaseModel):
    is_superuser: bool

@router.patch("/users/{user_id}/superuser")
def set_superuser(user_id: int, body: SetSuperuserRequest, superuser: User = Depends(get_current_superuser), db: Session = Depends(get_db)):
    if user_id == superuser.id and not body.is_superuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove your own superuser status")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_superuser = body.is_superuser
    db.commit()
    db.refresh(target)
    return target.to_dict(show_private=True)

@router.get("/personas")
def list_all_personas(superuser: User = Depends(get_current_superuser), db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)):
    offset = (page - 1) * page_size
    personas = db.query(Persona).options(joinedload(Persona.user)).order_by(Persona.created_at.desc()).offset(offset).limit(page_size).all()
    total = db.query(func.count(Persona.id)).scalar()
    items = []
    for p in personas:
        d = p.to_dict()
        d["owner_email"] = p.user.email if p.user else None
        d["owner_name"] = p.user.name if p.user else None
        items.append(d)
    return {"total": total, "page": page, "page_size": page_size, "items": items}

@router.get("/conversations")
def list_all_conversations(superuser: User = Depends(get_current_superuser), db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)):
    offset = (page - 1) * page_size
    conversations = db.query(Conversation).options(joinedload(Conversation.participants)).order_by(Conversation.created_at.desc()).offset(offset).limit(page_size).all()
    total = db.query(func.count(Conversation.id)).scalar()
    items = []
    for c in conversations:
        d = c.to_dict()
        owner = db.query(User).filter(User.id == c.created_by).first() if c.created_by else None
        d["owner_email"] = owner.email if owner else None
        d["owner_name"] = owner.name if owner else None
        items.append(d)
    return {"total": total, "page": page, "page_size": page_size, "items": items}

@router.post("/repair-avatars")
def repair_avatars(superuser: User = Depends(get_current_superuser), db: Session = Depends(get_db), limit: int = Query(10, ge=1, le=50)):
    from sqlalchemy import or_, not_
    from app.services.image_generation_service import ImageGenerationService
    needs_repair = or_(Persona.avatar_url == None, not_(Persona.avatar_url.like("avatars/%")))
    total_pending = db.query(func.count(Persona.id)).filter(needs_repair).scalar()
    pending = db.query(Persona).filter(needs_repair).order_by(Persona.created_at.asc()).limit(limit).all()
    repaired = 0
    failed = 0
    img_service = ImageGenerationService()
    for persona in pending:
        try:
            new_avatar = img_service.generate_avatar_for_persona({"name": persona.name, "age": persona.age, "gender": persona.gender, "description": persona.description or "", "attitude": persona.attitude or "Neutral"})
            persona.avatar_url = new_avatar
            db.commit()
            repaired += 1
        except Exception as e:
            failed += 1
    remaining = total_pending - repaired
    return {"repaired": repaired, "failed": failed, "remaining": remaining}
