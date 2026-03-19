"""
Moderation Model - Phase 5

Audit log for content that was flagged by the moderation service.
Admin users can review, approve, or block flagged content via the admin endpoints.

TDD Status:
- Tests written first in: tests/unit/test_moderation_model.py
- This implementation makes those tests GREEN

Fields:
- id: Primary key
- content: The flagged text content
- toxicity_score: Score returned by the moderation API [0.0, 1.0]
- source: Where the content came from ("persona_description", "conversation_message")
- source_id: ID/unique_id of the source record (for traceability)
- action_taken: Current status ("pending", "approved", "blocked")
- reviewed_by: ID of the admin user who reviewed (nullable)
- created_at: When the log entry was created
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, func

from app.database import Base


class ModerationAuditLog(Base):
    """
    Audit log entry for content flagged by the moderation service.

    Stores the original content, toxicity score, source, and admin review status.
    Allows admins to review borderline content and approve or block it.
    """

    __tablename__ = "moderation_audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Primary key"
    )

    content = Column(
        String(4096),
        nullable=False,
        doc="The text content that was flagged"
    )

    toxicity_score = Column(
        Float,
        nullable=False,
        doc="Toxicity score from moderation API [0.0, 1.0]"
    )

    source = Column(
        String(100),
        nullable=False,
        doc="Origin of the content: 'persona_description' | 'conversation_message'"
    )

    source_id = Column(
        String(255),
        nullable=False,
        doc="ID or unique_id of the source record"
    )

    action_taken = Column(
        String(50),
        nullable=False,
        default="pending",
        doc="Review status: 'pending' | 'approved' | 'blocked'"
    )

    reviewed_by = Column(
        Integer,
        nullable=True,
        doc="User ID of the admin who reviewed this entry"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When this log entry was created"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "toxicity_score": self.toxicity_score,
            "source": self.source,
            "source_id": self.source_id,
            "action_taken": self.action_taken,
            "reviewed_by": self.reviewed_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<ModerationAuditLog(id={self.id}, score={self.toxicity_score:.2f}, action='{self.action_taken}')>"
