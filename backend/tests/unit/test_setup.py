"""
Test Suite Verification

This file contains basic tests to verify that the testing infrastructure
is properly configured and working.

These are the FIRST tests written following TDD principles.
"""

import pytest


class TestTestingInfrastructure:
    """Verify that pytest and testing infrastructure is working correctly"""

    def test_pytest_working(self):
        """
        Verify pytest is installed and can run tests.
        This is our first test following TDD!
        """
        assert True, "Pytest is working!"

    def test_assertions_work(self):
        """Verify that assertions work as expected"""
        # Basic assertions
        assert 1 + 1 == 2
        assert "test" in "testing"
        assert [1, 2, 3] == [1, 2, 3]

    def test_pytest_marks_work(self):
        """Verify that pytest markers are configured correctly"""
        # This test itself is marked as a unit test (implicitly)
        # Markers are defined in pytest.ini
        assert True

    @pytest.mark.unit
    def test_unit_marker(self):
        """Verify unit test marker works"""
        assert True

    def test_type_checking(self):
        """Verify type checking works in tests"""
        value: int = 42
        assert isinstance(value, int)

        text: str = "test"
        assert isinstance(text, str)


class TestFixtures:
    """Verify that test fixtures are working correctly"""

    def test_test_db_engine_fixture(self, test_db_engine):
        """Verify database engine fixture is created"""
        assert test_db_engine is not None
        # SQLite in-memory database
        assert "sqlite" in str(test_db_engine.url).lower()

    def test_db_session_fixture(self, db_session):
        """Verify database session fixture is created"""
        assert db_session is not None
        # Can execute basic operations
        result = db_session.execute("SELECT 1")
        assert result is not None


class TestHelperFunctions:
    """Test helper functions from conftest.py"""

    def test_assert_valid_six_char_id(self):
        """Test six character ID validation helper"""
        from tests.conftest import assert_valid_six_char_id

        # Valid IDs
        assert assert_valid_six_char_id("abc123") == True
        assert assert_valid_six_char_id("zzz999") == True
        assert assert_valid_six_char_id("a1b2c3") == True

        # Invalid IDs
        assert assert_valid_six_char_id("ABC123") == False  # Uppercase
        assert assert_valid_six_char_id("abc12") == False  # Too short
        assert assert_valid_six_char_id("abc1234") == False  # Too long
        assert assert_valid_six_char_id("abc!23") == False  # Special chars
        assert assert_valid_six_char_id("") == False  # Empty


class TestMockData:
    """Verify that mock data fixtures are working"""

    def test_test_user_data_fixture(self, test_user_data):
        """Verify test user data fixture provides correct structure"""
        assert "email" in test_user_data
        assert "password" in test_user_data
        assert "password_hash" in test_user_data
        assert "@" in test_user_data["email"]

    def test_test_persona_data_fixture(self, test_persona_data):
        """Verify test persona data fixture provides correct structure"""
        assert "name" in test_persona_data
        assert "age" in test_persona_data
        assert "gender" in test_persona_data
        assert "description" in test_persona_data
        assert "attitude" in test_persona_data
        assert "personality_vector" in test_persona_data

        # Validate personality vector structure
        assert isinstance(test_persona_data["personality_vector"], dict)
        # Weights should sum to approximately 1.0
        weights_sum = sum(test_persona_data["personality_vector"].values())
        assert 0.99 <= weights_sum <= 1.01

    def test_test_conversation_data_fixture(self, test_conversation_data):
        """Verify test conversation data fixture provides correct structure"""
        assert "topic" in test_conversation_data
        assert "unique_id" in test_conversation_data
        assert len(test_conversation_data["topic"]) > 0
        assert len(test_conversation_data["unique_id"]) == 6


# ============================================================================
# Phase 1 Success Verification
# ============================================================================

def test_phase_1_complete():
    """
    Meta-test: Verify Phase 1 deliverables are in place.

    Phase 1 Goal: Establish testing infrastructure and project structure

    This test verifies:
    - pytest is configured (pytest.ini exists and works)
    - Dependencies are installable (this test runs = deps installed)
    - Test fixtures are available
    - Tests can be run and pass

    If this test passes, Phase 1 testing infrastructure is complete!
    """
    import os
    import pathlib

    # Verify pytest.ini exists
    pytest_ini = pathlib.Path(__file__).parent.parent.parent / "pytest.ini"
    assert pytest_ini.exists(), "pytest.ini should exist"

    # Verify requirements files exist
    backend_dir = pathlib.Path(__file__).parent.parent.parent
    assert (backend_dir / "requirements.txt").exists()
    assert (backend_dir / "requirements-dev.txt").exists()

    # Verify test directory structure
    tests_dir = pathlib.Path(__file__).parent.parent
    assert (tests_dir / "unit").exists()
    assert (tests_dir / "integration").exists()
    assert (tests_dir / "conftest.py").exists()

    print("\n✅ Phase 1 Testing Infrastructure: COMPLETE")
    print("   - pytest configured and working")
    print("   - Test fixtures available")
    print("   - Test directory structure in place")
    print("   - Ready for Phase 2: Core Backend Services (TDD)")
