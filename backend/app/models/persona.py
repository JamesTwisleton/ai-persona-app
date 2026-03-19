"""
Persona Model - Phase 3B

Database model for AI personas with OCEAN personality scores.

The OCEAN scores are inferred by Claude API from the user-provided description.
Archetype affinities are calculated using the AffinityCalculator from Phase 3A.

TDD Status:
- Tests written first in: tests/unit/test_persona_model.py
- This implementation makes those tests GREEN

Fields:
- id: Primary key (auto-increment)
- unique_id: 6-character alphanumeric public identifier
- user_id: Foreign key to users table
- name: Persona display name
- age: Optional age
- gender: Optional gender
- description: User-provided backstory (used for OCEAN inference)
- attitude: Response style ("Neutral", "Sarcastic", "Comical", "Somber")
- ocean_openness: OCEAN O score [0.0, 1.0]
- ocean_conscientiousness: OCEAN C score [0.0, 1.0]
- ocean_extraversion: OCEAN E score [0.0, 1.0]
- ocean_agreeableness: OCEAN A score [0.0, 1.0]
- ocean_neuroticism: OCEAN N score [0.0, 1.0]
- archetype_affinities: JSON dict of archetype affinity scores
- motto: AI-generated personal motto
- avatar_url: Generated avatar image URL
- created_at / updated_at: Timestamps
"""

import secrets
import string
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func, event
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.database import Base


def _generate_unique_id(length: int = 6) -> str:
    """
    Generate a random alphanumeric unique ID for a persona.

    Uses lowercase letters and digits for readability.
    Collision probability is negligible for reasonable persona counts
    (62^6 ≈ 56 billion combinations).

    Args:
        length: Length of ID (default 6)

    Returns:
        str: Random alphanumeric string, e.g. "a3k9z2"
    """
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Persona(Base):
    """
    AI Persona with OCEAN-based personality.

    OCEAN scores are inferred from the user's description by Claude API.
    Archetype affinities are then calculated using cosine similarity
    against the 8 predefined archetypes from Phase 3A.

    Usage:
        persona = Persona(
            user_id=1,
            name="Alice",
            description="A thoughtful data scientist...",
            ocean_openness=0.8,
            ocean_conscientiousness=0.7,
            ocean_extraversion=0.4,
            ocean_agreeableness=0.6,
            ocean_neuroticism=0.3,
        )
    """

    __tablename__ = "personas"

    # =========================================================================
    # Primary Key & Identity
    # =========================================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Internal database ID"
    )

    unique_id = Column(
        String(6),
        unique=True,
        nullable=True,
        index=True,
        doc="Public 6-char alphanumeric ID (e.g. 'a3k9z2')"
    )

    # =========================================================================
    # Foreign Keys
    # =========================================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Owner user ID"
    )

    # =========================================================================
    # Basic Info
    # =========================================================================

    name = Column(
        String(255),
        nullable=False,
        doc="Persona display name"
    )

    age = Column(
        Integer,
        nullable=True,
        doc="Optional age"
    )

    gender = Column(
        String(50),
        nullable=True,
        doc="Optional gender identity"
    )

    description = Column(
        Text,
        nullable=True,
        doc="User-provided backstory used for OCEAN inference"
    )

    attitude = Column(
        String(50),
        nullable=True,
        doc="Response style: Neutral | Sarcastic | Comical | Somber"
    )

    model_used = Column(
        String(50),
        nullable=True,
        doc="Image generation model used for avatar: dalle | openjourney"
    )

    # =========================================================================
    # OCEAN Personality Scores (inferred by Claude)
    # =========================================================================

    ocean_openness = Column(
        Float,
        nullable=False,
        doc="Openness to Experience [0.0, 1.0]"
    )

    ocean_conscientiousness = Column(
        Float,
        nullable=False,
        doc="Conscientiousness [0.0, 1.0]"
    )

    ocean_extraversion = Column(
        Float,
        nullable=False,
        doc="Extraversion [0.0, 1.0]"
    )

    ocean_agreeableness = Column(
        Float,
        nullable=False,
        doc="Agreeableness [0.0, 1.0]"
    )

    ocean_neuroticism = Column(
        Float,
        nullable=False,
        doc="Neuroticism [0.0, 1.0]"
    )

    # =========================================================================
    # Derived Fields
    # =========================================================================

    archetype_affinities = Column(
        JSON,
        nullable=True,
        doc="Archetype affinity scores {archetype_code: score} from AffinityCalculator"
    )

    motto = Column(
        String(512),
        nullable=True,
        doc="AI-generated personal motto"
    )

    avatar_url = Column(
        String(512),
        nullable=True,
        doc="URL of generated avatar image"
    )

    # =========================================================================
    # Timestamps
    # =========================================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Persona creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Last modification timestamp"
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    user = relationship(
        "User",
        back_populates="personas",
        doc="Owner user"
    )

    # =========================================================================
    # Methods
    # =========================================================================

    def get_ocean_vector(self) -> Dict[str, float]:
        """
        Return OCEAN scores as a dict keyed by trait codes.

        Returns:
            dict: {"O": float, "C": float, "E": float, "A": float, "N": float}

        Example:
            {"O": 0.8, "C": 0.6, "E": 0.5, "A": 0.7, "N": 0.3}
        """
        return {
            "O": float(self.ocean_openness),
            "C": float(self.ocean_conscientiousness),
            "E": float(self.ocean_extraversion),
            "A": float(self.ocean_agreeableness),
            "N": float(self.ocean_neuroticism),
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize persona to a dictionary for API responses.

        Returns:
            dict: All persona fields with JSON-serializable types
        """
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "description": self.description,
            "attitude": self.attitude,
            "model_used": self.model_used,
            "ocean_openness": float(self.ocean_openness) if self.ocean_openness is not None else None,
            "ocean_conscientiousness": float(self.ocean_conscientiousness) if self.ocean_conscientiousness is not None else None,
            "ocean_extraversion": float(self.ocean_extraversion) if self.ocean_extraversion is not None else None,
            "ocean_agreeableness": float(self.ocean_agreeableness) if self.ocean_agreeableness is not None else None,
            "ocean_neuroticism": float(self.ocean_neuroticism) if self.ocean_neuroticism is not None else None,
            "archetype_affinities": self.archetype_affinities,
            "motto": self.motto,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Persona(name='{self.name}', unique_id='{self.unique_id}')>"


# =============================================================================
# SQLAlchemy Event Listeners
# =============================================================================

@event.listens_for(Persona, "before_insert")
def generate_unique_id(mapper, connection, target):
    """Auto-generate unique_id before insert if not set."""
    if target.unique_id is None:
        target.unique_id = _generate_unique_id()


@event.listens_for(Persona, "before_update")
def update_timestamp(mapper, connection, target):
    """Ensure updated_at is refreshed on update."""
    target.updated_at = datetime.utcnow()
