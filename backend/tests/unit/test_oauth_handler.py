"""
Test OAuth Authentication Handler

Following TDD: Writing tests FIRST for Google OAuth authentication!

TDD Cycle:
🔴 RED: These tests will fail because OAuth endpoints don't exist yet
🟢 GREEN: Implement OAuth endpoints to make tests pass
♻️ REFACTOR: Optimize while keeping tests green

OAuth Flow to Test:
1. User clicks "Login with Google" -> Redirect to Google OAuth
2. User authorizes on Google -> Google redirects back with auth code
3. Backend exchanges auth code for user info
4. Backend creates/updates user in database
5. Backend generates JWT session token
6. Frontend receives JWT token for authenticated requests

Test Coverage:
- OAuth login initiation (redirect to Google)
- OAuth callback with valid authorization code
- User creation on first OAuth login
- User login on subsequent OAuth attempts
- JWT token generation after successful OAuth
- Error handling for invalid/expired auth codes
- Error handling for OAuth state mismatch
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import status


@pytest.mark.unit
class TestOAuthLoginInitiation:
    """Test the OAuth login flow initiation (redirect to Google)"""

    def test_oauth_login_endpoint_exists(self, client):
        """
        RED: This will fail because endpoint doesn't exist yet.

        Requirement: GET /auth/login/google should exist
        """
        response = client.get("/auth/login/google", follow_redirects=False)

        # Should not return 404 (endpoint should exist)
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_oauth_login_redirects_to_google(self, client):
        """
        RED: This will fail.

        Requirement: /auth/login/google should redirect to Google OAuth URL
        """
        response = client.get("/auth/login/google", follow_redirects=False)

        # Should redirect (302 or 307)
        assert response.status_code in [
            status.HTTP_302_FOUND,
            status.HTTP_307_TEMPORARY_REDIRECT
        ]

        # Should redirect to Google's OAuth endpoint
        location = response.headers.get("location", "")
        assert "accounts.google.com" in location
        assert "oauth2" in location

    def test_oauth_login_includes_required_parameters(self, client):
        """
        RED: This will fail.

        Requirement: Redirect URL should include required OAuth parameters
        """
        response = client.get("/auth/login/google", follow_redirects=False)
        location = response.headers.get("location", "")

        # OAuth 2.0 required parameters
        assert "client_id=" in location
        assert "redirect_uri=" in location
        assert "response_type=code" in location
        assert "scope=" in location
        assert "state=" in location  # CSRF protection


@pytest.mark.unit
class TestOAuthCallback:
    """Test OAuth callback handling after Google authorization"""

    def test_oauth_callback_endpoint_exists(self, client):
        """
        RED: This will fail.

        Requirement: GET /auth/callback/google should exist
        """
        response = client.get("/auth/callback/google?code=test&state=test")

        # Should not return 404
        assert response.status_code != status.HTTP_404_NOT_FOUND

    @patch('app.routers.auth.verify_oauth_state')
    @patch('app.routers.auth.oauth')
    def test_oauth_callback_with_valid_code_creates_new_user(
        self, mock_oauth, mock_verify_state, client, db_session
    ):
        """
        RED: This will fail.

        Requirement: Valid OAuth code should create new user and return JWT
        """
        # Mock state verification (CSRF protection)
        mock_verify_state.return_value = True

        # Mock OAuth token exchange
        mock_token = {
            "access_token": "mock_access_token",
            "userinfo": {
                "sub": "google_oauth2|123456789",
                "email": "newuser@example.com",
                "name": "New User",
                "picture": "https://lh3.googleusercontent.com/a/test123"
            }
        }
        mock_oauth.google.authorize_access_token = AsyncMock(return_value=mock_token)

        # Simulate OAuth callback with authorization code
        response = client.get(
            "/auth/callback/google",
            params={"code": "valid_auth_code", "state": "valid_state"}
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "access_token" in data  # JWT session token
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

        # User should be created in database
        user_data = data["user"]
        assert user_data["email"] == "newuser@example.com"
        assert user_data["name"] == "New User"

    @patch('app.routers.auth.verify_oauth_state')
    @patch('app.routers.auth.oauth')
    def test_oauth_callback_with_existing_user_returns_user(
        self, mock_oauth, mock_verify_state, client, db_session
    ):
        """
        RED: This will fail.

        Requirement: OAuth with existing user should login (not create duplicate)
        """
        from app.models.user import User

        # Create existing user
        existing_user = User(
            email="existing@example.com",
            google_id="google_oauth2|existing123",
            name="Existing User"
        )
        db_session.add(existing_user)
        db_session.commit()

        # Mock state verification
        mock_verify_state.return_value = True

        # Mock OAuth token exchange with updated user info
        mock_token = {
            "access_token": "mock_access_token",
            "userinfo": {
                "sub": "google_oauth2|existing123",  # Same Google ID
                "email": "existing@example.com",
                "name": "Existing User Updated",  # Name might have changed
                "picture": "https://new-picture.com/photo.jpg"
            }
        }
        mock_oauth.google.authorize_access_token = AsyncMock(return_value=mock_token)

        response = client.get(
            "/auth/callback/google",
            params={"code": "valid_auth_code", "state": "valid_state"}
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "existing@example.com"

        # Should NOT create duplicate user
        from sqlalchemy import select
        result = db_session.execute(
            select(User).where(User.google_id == "google_oauth2|existing123")
        )
        users = result.scalars().all()
        assert len(users) == 1  # Still only one user

    def test_oauth_callback_without_code_returns_error(self, client):
        """
        RED: This will fail.

        Requirement: Callback without auth code should return 400 error
        """
        response = client.get("/auth/callback/google")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()  # FastAPI standard error format

    @patch('app.routers.auth.verify_oauth_state')
    @patch('app.routers.auth.oauth')
    def test_oauth_callback_with_invalid_code_returns_error(
        self, mock_oauth, mock_verify_state, client
    ):
        """
        RED: This will fail.

        Requirement: Invalid auth code should return 401 error
        """
        # Mock state verification to pass
        mock_verify_state.return_value = True

        # Mock failed token exchange (invalid authorization code)
        mock_oauth.google.authorize_access_token = AsyncMock(
            side_effect=Exception("invalid_grant")
        )

        response = client.get(
            "/auth/callback/google",
            params={"code": "invalid_code", "state": "valid_state"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()  # FastAPI standard error format

    def test_oauth_callback_with_state_mismatch_returns_error(self, client):
        """
        RED: This will fail.

        Requirement: State mismatch (CSRF protection) should return 400 error
        """
        response = client.get(
            "/auth/callback/google",
            params={"code": "valid_code", "state": "wrong_state"}
        )

        # Should reject due to CSRF protection
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED
        ]


@pytest.mark.unit
class TestJWTTokenGeneration:
    """Test JWT session token generation after OAuth"""

    def test_jwt_token_contains_user_id(self, client, db_session):
        """
        RED: This will fail.

        Requirement: JWT token should contain user ID in payload
        """
        from app.models.user import User
        from app.auth import create_access_token
        from jose import jwt
        from app.config import settings

        user = User(
            email="jwt@example.com",
            google_id="google_123",
            name="JWT User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Generate JWT token
        token = create_access_token(user.id)

        # Decode and verify
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        assert "sub" in payload  # Subject (user ID)
        assert payload["sub"] == str(user.id)
        assert "exp" in payload  # Expiration

    def test_jwt_token_has_expiration(self, client, db_session):
        """
        RED: This will fail.

        Requirement: JWT tokens should have expiration time
        """
        from app.models.user import User
        from app.auth import create_access_token
        from jose import jwt
        from app.config import settings
        from datetime import datetime

        user = User(
            email="expire@example.com",
            google_id="google_456",
            name="Expire User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = create_access_token(user.id)

        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Should have expiration
        assert "exp" in payload
        exp_timestamp = payload["exp"]

        # Expiration should be in the future
        now = datetime.utcnow().timestamp()
        assert exp_timestamp > now


# ============================================================================
# TDD Status: RED Phase 🔴
# ============================================================================
#
# These tests will FAIL because OAuth endpoints and JWT utilities don't exist yet.
#
# Next steps (GREEN phase):
# 1. Create app/auth.py with OAuth client and JWT utilities
# 2. Create app/routers/auth.py with OAuth endpoints
# 3. Run tests and watch them pass!
#
# ============================================================================
