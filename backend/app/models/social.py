"""
Social Models

Upvote and PageView tracking for the discovery feed.
"""

from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base


class Upvote(Base):
    """One upvote per user per target (persona or conversation)."""

    __tablename__ = "upvotes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    target_type = Column(
        String(20), nullable=False,
        doc="'persona' or 'conversation'"
    )

    target_id = Column(
        String(6), nullable=False,
        doc="unique_id of the target persona or conversation"
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_upvote_user_target"),
    )

    user = relationship("User")


class PageView(Base):
    """Deduplicated daily page view per (target, user/ip)."""

    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, autoincrement=True)

    target_type = Column(String(20), nullable=False)
    target_id = Column(String(6), nullable=False, index=True)

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    ip_hash = Column(String(64), nullable=True)

    viewed_date = Column(Date, nullable=False, default=date.today)

    __table_args__ = (
        UniqueConstraint(
            "target_type", "target_id", "user_id", "ip_hash", "viewed_date",
            name="uq_pageview_daily"
        ),
    )
