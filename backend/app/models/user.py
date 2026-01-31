"""
User Model

Database model for user accounts and authentication via Google OAuth.

This model was implemented following TDD:
1. RED: Tests written first in tests/unit/test_user_model_oauth.py
2. GREEN: This implementation makes those tests pass
3. REFACTOR: Can now improve while keeping tests green

Fields:
- id: Primary key (auto-increment)
- email: User email (unique, lowercase, required)
- google_id: Google OAuth unique identifier (unique, required)
- name: User's display name from Google (optional)
- picture_url: Profile picture URL from Google (optional)
- created_at: Account creation timestamp
- updated_at: Last modification timestamp
"""

from sqlalchemy import Column, Integer, String, DateTime, func, event
from sqlalchemy.orm import validates
from app.database import Base
from datetime import datetime


class User(Base):
    """
    User account model for Google OAuth authentication and profile management.

    Authentication:
    - Uses Google OAuth 2.0 for authentication
    - No password storage - authentication handled by Google
    - google_id is the unique identifier from Google OAuth

    Security Note:
    - Email is normalized to lowercase for consistent lookups
    """

    __tablename__ = "users"

    # ========================================================================
    # Columns
    # ========================================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique user identifier"
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User email address (unique, lowercase)"
    )

    google_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Google OAuth unique identifier (e.g., 'google_oauth2|123456789')"
    )

    name = Column(
        String(255),
        nullable=True,
        doc="User's display name from Google (optional)"
    )

    picture_url = Column(
        String(512),
        nullable=True,
        doc="Profile picture URL from Google (optional)"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Account creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Last account modification timestamp"
    )

    # ========================================================================
    # Relationships (Phase 3+)
    # ========================================================================

    # Will be added in Phase 3 when Persona model is created:
    # personas = relationship("Persona", back_populates="user", cascade="all, delete-orphan")

    # Will be added in Phase 7 when Conversation model is created:
    # conversations = relationship("Conversation", back_populates="creator")

    # ========================================================================
    # Validators
    # ========================================================================

    @validates('email')
    def normalize_email(self, key, email):
        """
        Normalize email to lowercase for consistent storage and lookups.

        Args:
            key: Column name (email)
            email: Email address to normalize

        Returns:
            str: Lowercase email address

        Example:
            User(email="Test@EXAMPLE.com") -> stores as "test@example.com"
        """
        if email:
            return email.lower().strip()
        return email

    # ========================================================================
    # Methods
    # ========================================================================

    def __repr__(self) -> str:
        """
        String representation of User for debugging.

        Returns:
            str: User representation showing ID and email

        Example:
            <User(id=1, email='user@example.com')>
        """
        return f"<User(id={self.id}, email='{self.email}')>"

    def to_dict(self) -> dict:
        """
        Convert user to dictionary (useful for API responses).

        Security Note:
        - Only returns safe, public information
        - Includes OAuth profile information from Google

        Returns:
            dict: User data including OAuth profile fields
        """
        return {
            "id": self.id,
            "email": self.email,
            "google_id": self.google_id,
            "name": self.name,
            "picture_url": self.picture_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================================================
# SQLAlchemy Event Listeners
# ============================================================================

@event.listens_for(User, 'before_update')
def receive_before_update(mapper, connection, target):
    """
    Ensure updated_at is set when user is modified.

    This is a backup for the onupdate=func.now() which may not
    work in all database backends.
    """
    target.updated_at = datetime.utcnow()


# ============================================================================
# TDD Status: GREEN Phase (OAuth)
# ============================================================================
#
# This implementation makes all tests in test_user_model_oauth.py pass!
#
# Run: pytest tests/unit/test_user_model_oauth.py -v
#
# All OAuth tests should now PASS (GREEN state) ✅
#
# Changes from password-based auth:
# - Removed: password_hash field
# - Added: google_id (unique identifier from Google OAuth)
# - Added: name (user's display name from Google)
# - Added: picture_url (profile picture URL from Google)
#
# Next: Implement OAuth callback endpoint and JWT session tokens
# ============================================================================
