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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Set test environment
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Import FastAPI app (created in Phase 1)
from app.main import app

# Note: These imports will be created in Phase 2
# from app.database import Base, get_db
# from app.models import User, Persona, Conversation
# from app.auth import create_access_token


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

    # Note: Will uncomment in Phase 2 when models are created
    # Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    # Base.metadata.drop_all(bind=engine)
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
    """
    # Phase 1: Basic client without database dependency override
    # Database override will be added in Phase 2 when database models are created

    # def override_get_db():
    #     try:
    #         yield db_session
    #     finally:
    #         pass
    #
    # app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # app.dependency_overrides.clear()  # Will uncomment in Phase 2


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
def test_user(db_session, test_user_data):
    """
    Create a test user in the database.
    Will be implemented in Phase 2 when User model exists.
    """
    # user = User(
    #     email=test_user_data["email"],
    #     password_hash=test_user_data["password_hash"]
    # )
    # db_session.add(user)
    # db_session.commit()
    # db_session.refresh(user)
    # return user
    pass


@pytest.fixture
def auth_headers(test_user) -> Dict[str, str]:
    """
    Generate authentication headers for testing protected endpoints.
    Will be implemented in Phase 2 when auth is built.
    """
    # token = create_access_token(data={"sub": test_user.email})
    # return {"Authorization": f"Bearer {token}"}
    return {}


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
def test_persona(db_session, test_user, test_persona_data):
    """
    Create a test persona in the database.
    Will be implemented in Phase 3.
    """
    pass


@pytest.fixture
def test_personas(db_session, test_user, test_persona_data):
    """
    Create multiple test personas for conversation testing.
    Will be implemented in Phase 3.
    """
    pass


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
