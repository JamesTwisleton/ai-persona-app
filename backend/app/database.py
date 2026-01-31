"""
Database Configuration and Session Management

This module provides database connectivity and session management
for the AI Focus Groups application using SQLAlchemy ORM.

Features:
- Database engine creation with connection pooling
- Session factory for database operations
- Dependency injection for FastAPI endpoints
- Environment-based configuration (dev, test, prod)
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# ============================================================================
# Database Configuration
# ============================================================================

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ai_focus_groups_user:dev_password@localhost:5432/ai_focus_groups"
)

# Testing mode uses SQLite in-memory for speed
TESTING = os.getenv("TESTING", "0") == "1"

if TESTING:
    # Use SQLite in-memory for tests (fast, isolated)
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Reuse connection for in-memory DB
    )
else:
    # Production/development PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,  # Connection pool size
        max_overflow=10,  # Additional connections if pool exhausted
        echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL queries in debug mode
    )

# ============================================================================
# Session Factory
# ============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================================
# Base Model Class
# ============================================================================

# All database models will inherit from this Base class
Base = declarative_base()


# ============================================================================
# Database Dependency for FastAPI
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI endpoints.

    Yields a database session and ensures it's closed after use.

    Usage in FastAPI endpoint:
        @app.get("/users/me")
        def get_current_user(db: Session = Depends(get_db)):
            # Use db session here
            pass

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Database Initialization
# ============================================================================

def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined by models that inherit from Base.
    In production, use Alembic migrations instead.

    This is useful for:
    - Testing (create fresh tables for each test)
    - Initial development setup
    """
    # Import all models here to ensure they're registered with Base
    # This will be uncommented as we create models
    # from app.models import user, persona, conversation

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data!
    Only use for testing or development.
    """
    Base.metadata.drop_all(bind=engine)
