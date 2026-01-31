"""
Test User Model with Google OAuth

Following TDD: Writing tests FIRST for OAuth-based User model!

TDD Cycle:
🔴 RED: These tests will fail because model still has password_hash
🟢 GREEN: Update User model to use Google OAuth instead
♻️ REFACTOR: Optimize while keeping tests green

Changes from password-based auth:
- Removed: password_hash field
- Added: google_id (unique identifier from Google)
- Added: name (user's display name from Google)
- Added: picture_url (profile picture from Google)

Test Coverage:
- User creation with Google OAuth ID
- Google ID uniqueness constraint
- Optional name and picture fields
- Email still required and unique
"""

import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.unit
class TestUserModelOAuth:
    """Test User model with Google OAuth authentication"""

    def test_create_user_with_google_oauth(self, db_session):
        """
        RED: This will fail because model still has password_hash required.

        Requirement: User should be creatable with email and google_id (no password)
        """
        from app.models.user import User

        user = User(
            email="oauth@example.com",
            google_id="google_oauth2|123456789",
            name="Test User",
            picture_url="https://lh3.googleusercontent.com/a/test123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "oauth@example.com"
        assert user.google_id == "google_oauth2|123456789"
        assert user.name == "Test User"
        assert user.picture_url is not None

    def test_user_google_id_is_required(self, db_session):
        """
        RED: Will fail.

        Requirement: google_id must be required (NOT NULL)
        """
        from app.models.user import User

        user = User(email="test@example.com", name="Test")

        db_session.add(user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_google_id_must_be_unique(self, db_session):
        """
        RED: Will fail.

        Requirement: google_id should have UNIQUE constraint
        """
        from app.models.user import User

        # Create first user
        user1 = User(
            email="user1@example.com",
            google_id="duplicate_google_id"
        )
        db_session.add(user1)
        db_session.commit()

        # Attempt to create second user with same google_id
        user2 = User(
            email="user2@example.com",  # Different email
            google_id="duplicate_google_id"  # Same Google ID
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_name_is_optional(self, db_session):
        """
        RED: Will fail.

        Requirement: name field should be optional (can be NULL)
        """
        from app.models.user import User

        user = User(
            email="noname@example.com",
            google_id="google_id_123"
            # name not provided - should be OK
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.name is None  # Should allow NULL

    def test_user_picture_url_is_optional(self, db_session):
        """
        RED: Will fail.

        Requirement: picture_url field should be optional
        """
        from app.models.user import User

        user = User(
            email="nopic@example.com",
            google_id="google_id_456"
            # picture_url not provided - should be OK
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.picture_url is None  # Should allow NULL

    def test_user_model_has_no_password_field(self):
        """
        Requirement: User model should NOT have password or password_hash fields
        when using OAuth.
        """
        from app.models.user import User

        user = User(email="test@example.com", google_id="123")

        # Should not have any password-related fields
        assert not hasattr(user, 'password')
        assert not hasattr(user, 'password_hash')

    def test_user_to_dict_includes_oauth_fields(self, db_session):
        """
        RED: Will fail.

        Requirement: to_dict() should include OAuth fields
        """
        from app.models.user import User

        user = User(
            email="dict@example.com",
            google_id="google_123",
            name="Dictionary User",
            picture_url="https://example.com/pic.jpg"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        user_dict = user.to_dict()

        assert "email" in user_dict
        assert "google_id" in user_dict
        assert "name" in user_dict
        assert "picture_url" in user_dict
        assert user_dict["name"] == "Dictionary User"

        # Should NOT include sensitive data (even though we removed password_hash)
        assert "password" not in user_dict
        assert "password_hash" not in user_dict

    def test_user_repr_with_oauth_data(self, db_session):
        """
        Requirement: User repr should be readable with OAuth data
        """
        from app.models.user import User

        user = User(
            email="repr@example.com",
            google_id="google_repr_123",
            name="Repr User"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        repr_str = repr(user)
        assert "User" in repr_str
        assert "repr@example.com" in repr_str


# ============================================================================
# TDD Status: RED Phase 🔴
# ============================================================================
#
# These tests will FAIL because the User model still has password_hash
# and doesn't have google_id, name, picture_url fields.
#
# Next step: Update app/models/user.py to use Google OAuth (GREEN phase)
# ============================================================================
