"""
User Model

Database model for user accounts and authentication via Google OAuth.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, event
from sqlalchemy.orm import validates, relationship
from app.database import Base
from datetime import datetime


class User(Base):
    """
    User account model for Google OAuth authentication and profile management.
    """

    __tablename__ = "users"

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
        doc="Google OAuth unique identifier"
    )

    name = Column(
        String(255),
        nullable=True,
        doc="User's real name from Google"
    )

    display_name = Column(
        String(255),
        nullable=True,
        doc="User-set name for conversations"
    )

    picture_url = Column(
        String(512),
        nullable=True,
        doc="Profile picture URL from Google"
    )

    is_admin = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        doc="Whether this user has admin privileges"
    )

    is_superuser = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        doc="Whether this user can delete any content"
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

    personas = relationship("Persona", back_populates="user", cascade="all, delete-orphan")

    @validates('email')
    def normalize_email(self, key, email):
        if email:
            return email.lower().strip()
        return email

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"

    def to_dict(self, show_private: bool = False) -> dict:
        """
        Convert user to dictionary.
        Safe for public views by default.
        """
        data = {
            "id": self.id,
            "display_name": self.display_name,
            "picture_url": self.picture_url,
            "is_admin": self.is_admin,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if show_private:
            data.update({
                "email": self.email,
                "name": self.name,
                "google_id": self.google_id,
            })

        return data


@event.listens_for(User, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()
