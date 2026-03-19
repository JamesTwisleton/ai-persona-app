"""
Admin Routes - Phase 5

Endpoints for admin users to review and action flagged content.

All endpoints require is_admin=True on the authenticated user.

Endpoints:
- GET /admin/flagged-content - List all moderation audit log entries
- POST /admin/approve/{log_id} - Approve flagged content
- POST /admin/block/{log_id} - Block flagged content
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User
from app.models.moderation import ModerationAuditLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/flagged-content",
    summary="List all flagged moderation log entries",
    responses={
        200: {"description": "List of moderation audit log entries"},
        401: {"description": "Not authenticated"},
        403: {"description": "Admin privileges required"},
    },
)
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


@router.post(
    "/approve/{log_id}",
    summary="Approve flagged content",
    responses={
        200: {"description": "Content approved"},
        401: {"description": "Not authenticated"},
        403: {"description": "Admin privileges required"},
        404: {"description": "Log entry not found"},
    },
)
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


@router.post(
    "/block/{log_id}",
    summary="Block flagged content",
    responses={
        200: {"description": "Content blocked"},
        401: {"description": "Not authenticated"},
        403: {"description": "Admin privileges required"},
        404: {"description": "Log entry not found"},
    },
)
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
