"""
Shared pytest fixtures for AI Focus Groups Backend Testing

This module provides common test fixtures used across all tests, including:
- Test database setup/teardown
- Test client for API testing
- Mock authentication
- Sample test data

Following TDD principles:
- All tests should be isolated (no shared state between tests)
- Fixtures should cleanup after themselves
- Use in-memory database where possible for speed
"""

import os
import pytest
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, event as sa_event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Set test environment
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Import FastAPI app (created in Phase 1)
from app.main import app

# Import database components (Phase 2)
from app.database import Base, get_db
from app.models import User, Persona
from app.auth import create_access_token


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db_engine():
    """
    Create a test database engine using SQLite in-memory for speed.
    Each test gets a fresh database.
    """
    # SQLite in-memory database for fast tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign key enforcement in SQLite (disabled by default)
    @sa_event.listens_for(engine, "connect")
    def set_sqlite_fk_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables for testing (Phase 2: User model, Phase 3B: Persona model)
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """
    Create a test database session.
    Automatically rolls back changes after each test for isolation.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ============================================================================
# FastAPI Client Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI test client with test database dependency override.

    Phase 2: Now includes database dependency override for testing endpoints
    that require database access.
    """
    # Override the get_db dependency to use our test database session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """
    Sample user data for testing.
    """
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "password_hash": "$2b$12$TestHashForTesting"  # Placeholder hash
    }


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database (OAuth-based, Phase 2+)."""
    user = User(
        email="test@example.com",
        google_id="google_test_user_123",
        name="Test User",
        picture_url="https://example.com/pic.jpg",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> Dict[str, str]:
    """Generate JWT auth headers for a test user."""
    token = create_access_token(user_id=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(db_session, test_user_data):
    """
    Create a test admin user.
    Will be implemented in Phase 5 when admin features are added.
    """
    pass


@pytest.fixture
def admin_headers(admin_user) -> Dict[str, str]:
    """
    Generate authentication headers for admin testing.
    Will be implemented in Phase 5.
    """
    return {}


# ============================================================================
# Persona Fixtures (Phase 3+)
# ============================================================================

@pytest.fixture
def test_persona_data() -> Dict[str, Any]:
    """
    Sample persona data for testing.
    """
    return {
        "name": "Test Persona",
        "age": 30,
        "gender": "Non-binary",
        "description": "A thoughtful test persona for unit testing",
        "attitude": "Neutral",
        "model_used": "dalle",
        "personality_vector": {"The Skeptic": 0.6, "The Optimist": 0.4},
        "motto": "Test everything",
        "avatar_url": "https://example.com/avatar.png"
    }


@pytest.fixture
def test_persona(db_session, test_user):
    """Create a test persona in the database (Phase 3B)."""
    persona = Persona(
        user_id=test_user.id,
        name="Test Persona",
        age=30,
        gender="Non-binary",
        description="A thoughtful test persona for unit testing",
        attitude="Neutral",
        ocean_openness=0.7,
        ocean_conscientiousness=0.6,
        ocean_extraversion=0.5,
        ocean_agreeableness=0.65,
        ocean_neuroticism=0.35,
        motto="Test everything",
        avatar_url="https://example.com/avatar.png",
    )
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    return persona


@pytest.fixture
def test_personas(db_session, test_user):
    """Create multiple test personas for conversation testing (Phase 3B)."""
    personas = []
    ocean_profiles = [
        (0.9, 0.8, 0.3, 0.4, 0.2),  # Analyst-like
        (0.4, 0.5, 0.9, 0.85, 0.2),  # Socialite-like
        (0.95, 0.6, 0.65, 0.7, 0.3), # Innovator-like
    ]
    names = ["Analyst", "Socialite", "Innovator"]
    for name, (o, c, e, a, n) in zip(names, ocean_profiles):
        p = Persona(
            user_id=test_user.id,
            name=name,
            ocean_openness=o,
            ocean_conscientiousness=c,
            ocean_extraversion=e,
            ocean_agreeableness=a,
            ocean_neuroticism=n,
        )
        db_session.add(p)
        personas.append(p)
    db_session.commit()
    for p in personas:
        db_session.refresh(p)
    return personas


# ============================================================================
# Conversation Fixtures (Phase 7+)
# ============================================================================

@pytest.fixture
def test_conversation_data() -> Dict[str, Any]:
    """
    Sample conversation data for testing.
    """
    return {
        "topic": "Should we colonize Mars?",
        "unique_id": "abc123"
    }


@pytest.fixture
def test_conversation(db_session, test_user, test_personas, test_conversation_data):
    """
    Create a test conversation with messages.
    Will be implemented in Phase 7.
    """
    pass


# ============================================================================
# Mocking Fixtures (Phase 4+)
# ============================================================================

@pytest.fixture
def mock_llm_response():
    """
    Mock LLM API response for testing without hitting external services.
    Will be implemented in Phase 4.
    """
    return {
        "choices": [{
            "message": {
                "content": "This is a test response from the LLM."
            }
        }]
    }


@pytest.fixture
def mock_image_generation_response():
    """
    Mock image generation API response.
    Will be implemented in Phase 4.
    """
    return {
        "data": [{
            "url": "https://example.com/test-image.png"
        }]
    }


@pytest.fixture
def mock_moderation_response():
    """
    Mock content moderation API response.
    Will be implemented in Phase 5.
    """
    return {
        "results": [{
            "category_scores": {
                "hate": 0.001,
                "harassment": 0.001,
                "sexual": 0.001,
                "violence": 0.001
            }
        }]
    }


# ============================================================================
# Helper Functions
# ============================================================================

def assert_valid_uuid(value: str) -> bool:
    """
    Helper function to validate UUID format in tests.
    """
    import re
    uuid_pattern = re.compile(
        r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(value))


def assert_valid_six_char_id(value: str) -> bool:
    """
    Helper function to validate 6-character unique IDs used for personas/conversations.
    """
    import re
    return bool(re.match(r'^[a-z0-9]{6}$', value))
