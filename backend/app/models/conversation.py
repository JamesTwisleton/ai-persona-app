"""
Conversation Models - Phase 7

Database models for focus group conversations.

Models:
- Conversation: A focus group discussion with a topic and participating personas
- ConversationParticipant: Junction table linking conversations to personas
- ConversationMessage: An individual message from a persona in a conversation

TDD Status:
- Tests written first in: tests/unit/test_conversation_models.py
- This implementation makes those tests GREEN
"""

import secrets
import string
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, func, event
from sqlalchemy.orm import relationship

from app.database import Base


def _generate_unique_id(length: int = 6) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Conversation(Base):
    """
    A focus group discussion session.

    Tracks the topic, participating personas, turn count, and completion state.
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    unique_id = Column(
        String(6), unique=True, nullable=True, index=True,
        doc="Public 6-char alphanumeric ID"
    )

    topic = Column(Text, nullable=False, doc="Focus group discussion topic")

    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True, doc="ID of the user who created this conversation"
    )

    turn_count = Column(
        Integer, nullable=False, default=0,
        doc="Number of turns that have been generated"
    )

    max_turns = Column(
        Integer, nullable=False, default=20,
        doc="Maximum number of turns allowed before conversation is complete"
    )

    is_public = Column(
        Boolean, nullable=False, default=True, server_default="true",
        doc="Whether this conversation is visible on the public discovery feed"
    )

    forked_from_id = Column(
        String(6), nullable=True,
        doc="unique_id of the conversation this was forked from"
    )

    view_count = Column(
        Integer, nullable=False, default=0, server_default="0",
        doc="Deduplicated page view count"
    )

    upvote_count = Column(
        Integer, nullable=False, default=0, server_default="0",
        doc="Number of upvotes"
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        nullable=False, doc="Creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False, doc="Last update timestamp"
    )

    # Relationships
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.turn_number, ConversationMessage.id",
    )

    participants = relationship(
        "ConversationParticipant",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    @property
    def is_complete(self) -> bool:
        """True when the conversation has reached its maximum turn count."""
        return self.turn_count >= self.max_turns

    def to_dict(self, include_messages: bool = False) -> Dict[str, Any]:
        from app.services.image_generation_service import generate_presigned_url
        d = {
            "id": self.id,
            "unique_id": self.unique_id,
            "topic": self.topic,
            "created_by": self.created_by,
            "turn_count": self.turn_count,
            "max_turns": self.max_turns,
            "is_complete": self.is_complete,
            "is_public": self.is_public,
            "forked_from_id": self.forked_from_id,
            "view_count": self.view_count,
            "upvote_count": self.upvote_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "participants": [
                {
                    "persona_id": p.persona_id,
                    "persona_name": p.persona.name if p.persona else None,
                    "persona_unique_id": p.persona.unique_id if p.persona else None,
                    "avatar_url": (
                        generate_presigned_url(p.persona.avatar_url)
                        if p.persona and p.persona.avatar_url and p.persona.avatar_url.startswith("avatars/")
                        else (p.persona.avatar_url if p.persona else None)
                    ),
                }
                for p in self.participants
            ],
        }
        if include_messages:
            d["messages"] = [m.to_dict() for m in self.messages]
        return d

    def __repr__(self) -> str:
        return f"<Conversation(unique_id='{self.unique_id}', topic='{self.topic[:30]}')>"


class ConversationParticipant(Base):
    """Junction table linking a Conversation to its participating Personas."""

    __tablename__ = "conversation_participants"

    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True, nullable=False
    )

    persona_id = Column(
        Integer, ForeignKey("personas.id", ondelete="CASCADE"),
        primary_key=True, nullable=False
    )

    conversation = relationship("Conversation", back_populates="participants")
    persona = relationship("Persona")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "persona_id": self.persona_id,
            "persona_name": self.persona.name if self.persona else None,
            "persona_unique_id": self.persona.unique_id if self.persona else None,
        }


class ConversationMessage(Base):
    """
    A single message from a persona in a conversation turn.

    Stores the message text, moderation score, and which turn it belongs to.
    """

    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    persona_id = Column(
        Integer, ForeignKey("personas.id", ondelete="SET NULL"),
        nullable=True, index=True
    )

    persona_name = Column(
        String(255), nullable=False,
        doc="Persona name at time of message (denormalized for display)"
    )

    message_text = Column(Text, nullable=False, doc="The generated message content")

    turn_number = Column(
        Integer, nullable=False,
        doc="Which turn this message belongs to (1-indexed)"
    )

    toxicity_score = Column(
        Float, nullable=True,
        doc="Toxicity score from moderation API [0.0, 1.0]"
    )

    moderation_status = Column(
        String(50), nullable=False, default="approved",
        doc="Moderation result: 'approved' | 'flagged' | 'blocked'"
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        nullable=False
    )

    conversation = relationship("Conversation", back_populates="messages")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "message_text": self.message_text,
            "turn_number": self.turn_number,
            "toxicity_score": self.toxicity_score,
            "moderation_status": self.moderation_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<ConversationMessage(persona='{self.persona_name}', turn={self.turn_number})>"


# ============================================================================
# SQLAlchemy Event Listeners
# ============================================================================

@event.listens_for(Conversation, "before_insert")
def generate_conversation_unique_id(mapper, connection, target):
    """Auto-generate unique_id before insert if not set."""
    if target.unique_id is None:
        target.unique_id = _generate_unique_id()


@event.listens_for(Conversation, "before_update")
def update_conversation_timestamp(mapper, connection, target):
    target.updated_at = datetime.utcnow()
