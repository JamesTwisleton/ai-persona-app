"""
Admin Routes

Endpoints for admin and superuser management.

Admin endpoints (is_admin=True):
- GET  /admin/flagged-content  - List moderation audit log entries
- POST /admin/approve/{log_id} - Approve flagged content
- POST /admin/block/{log_id}   - Block flagged content

Superuser endpoints (is_superuser=True):
- GET   /admin/users               - List all users with counts
- PATCH /admin/users/{id}/superuser - Set/unset superuser flag
- GET   /admin/personas            - All personas with owner info (paginated)
- GET   /admin/conversations       - All conversations with owner info (paginated)
- POST  /admin/repair-avatars      - Regenerate missing avatar images via DALL-E + S3
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


# ============================================================================
# Admin (is_admin) endpoints — moderation review
# ============================================================================

@router.get("/flagged-content")
def get_flagged_content(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Return all moderation audit log entries, newest first."""
    logs = (
        db.query(ModerationAuditLog)
        .order_by(ModerationAuditLog.created_at.desc())
        .all()
    )
    return [log.to_dict() for log in logs]


@router.post("/approve/{log_id}")
def approve_content(
    log_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Mark a moderation log entry as approved."""
    log = db.query(ModerationAuditLog).filter(ModerationAuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Moderation log entry not found")
    log.action_taken = "approved"
    log.reviewed_by = admin.id
    db.commit()
    db.refresh(log)
    return log.to_dict()


@router.post("/block/{log_id}")
def block_content(
    log_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Mark a moderation log entry as blocked."""
    log = db.query(ModerationAuditLog).filter(ModerationAuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Moderation log entry not found")
    log.action_taken = "blocked"
    log.reviewed_by = admin.id
    db.commit()
    db.refresh(log)
    return log.to_dict()


# ============================================================================
# Superuser endpoints — user management + bulk content
# ============================================================================

@router.get("/users")
def list_users(
    superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """List all users with persona/conversation counts."""
    offset = (page - 1) * page_size

    persona_counts = (
        db.query(Persona.user_id, func.count(Persona.id).label("count"))
        .group_by(Persona.user_id)
        .subquery()
    )

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    total = db.query(func.count(User.id)).scalar()

    result = []
    for u in users:
        persona_count = (
            db.query(func.count(Persona.id)).filter(Persona.user_id == u.id).scalar()
        )
        d = u.to_dict()
        d["persona_count"] = persona_count
        result.append(d)

    return {"total": total, "page": page, "page_size": page_size, "items": result}


class SetSuperuserRequest(BaseModel):
    is_superuser: bool


@router.patch("/users/{user_id}/superuser")
def set_superuser(
    user_id: int,
    body: SetSuperuserRequest,
    superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Promote or demote a user's superuser status. Cannot self-demote."""
    if user_id == superuser.id and not body.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own superuser status",
        )
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.is_superuser = body.is_superuser
    db.commit()
    db.refresh(target)
    return target.to_dict()


@router.get("/personas")
def list_all_personas(
    superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """List all personas across all users with owner info."""
    offset = (page - 1) * page_size

    personas = (
        db.query(Persona)
        .options(joinedload(Persona.user))
        .order_by(Persona.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total = db.query(func.count(Persona.id)).scalar()

    items = []
    for p in personas:
        d = p.to_dict()
        d["owner_email"] = p.user.email if p.user else None
        d["owner_name"] = p.user.name if p.user else None
        items.append(d)

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/conversations")
def list_all_conversations(
    superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """List all conversations across all users with owner info."""
    offset = (page - 1) * page_size

    conversations = (
        db.query(Conversation)
        .options(joinedload(Conversation.participants))
        .order_by(Conversation.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total = db.query(func.count(Conversation.id)).scalar()

    items = []
    for c in conversations:
        d = c.to_dict()
        owner = db.query(User).filter(User.id == c.created_by).first() if c.created_by else None
        d["owner_email"] = owner.email if owner else None
        d["owner_name"] = owner.name if owner else None
        items.append(d)

    return {"total": total, "page": page, "page_size": page_size, "items": items}


# ============================================================================
# POST /admin/repair-avatars — regenerate missing avatars
# ============================================================================

@router.post("/repair-avatars")
def repair_avatars(
    superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Max personas to repair per call"),
):
    """
    Regenerate avatar images for personas with no avatar_url.

    Processes up to `limit` personas per call to avoid HTTP timeouts.
    Call repeatedly until remaining == 0.
    """
    from app.services.image_generation_service import ImageGenerationService

    total_pending = db.query(func.count(Persona.id)).filter(Persona.avatar_url == None).scalar()

    pending = (
        db.query(Persona)
        .filter(Persona.avatar_url == None)
        .order_by(Persona.created_at.asc())
        .limit(limit)
        .all()
    )

    repaired = 0
    failed = 0
    img_service = ImageGenerationService()

    for persona in pending:
        try:
            new_avatar = img_service.generate_avatar_for_persona({
                "name": persona.name,
                "age": persona.age,
                "gender": persona.gender,
                "description": persona.description or "",
                "attitude": persona.attitude or "Neutral",
            })
            persona.avatar_url = new_avatar
            db.commit()
            repaired += 1
            logger.info(f"Repaired avatar for persona {persona.unique_id} ({persona.name})")
        except Exception as e:
            failed += 1
            logger.warning(f"Failed to repair avatar for persona {persona.unique_id}: {e}")

    remaining = total_pending - repaired

    if remaining > 0:
        message = f"Repaired {repaired}, failed {failed}. {remaining} still pending — run again."
    elif repaired > 0:
        message = f"Repaired {repaired} avatar(s). All done!"
    else:
        message = "No personas need avatar repair."

    return {"repaired": repaired, "failed": failed, "remaining": remaining, "message": message}
