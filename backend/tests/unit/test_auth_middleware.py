"""
Test Authentication Middleware

Following TDD: Writing tests FIRST for auth middleware!

TDD Cycle:
🔴 RED: These tests will fail because middleware doesn't exist yet
🟢 GREEN: Implement get_current_user dependency to make tests pass
♻️ REFACTOR: Optimize while keeping tests green

Middleware Purpose:
- Extract JWT token from Authorization header
- Validate token and decode user ID
- Fetch user from database
- Return authenticated user or raise 401 error

Test Coverage:
- Valid JWT token returns user
- Missing Authorization header returns 401
- Invalid token format returns 401
- Expired token returns 401
- Token for non-existent user returns 401
- Token without 'Bearer' prefix returns 401
"""

import pytest
from fastapi import status, HTTPException
from datetime import datetime, timedelta
from jose import jwt


@pytest.mark.unit
class TestAuthMiddleware:
    """Test authentication middleware (get_current_user dependency)"""

    def test_get_current_user_with_valid_token(self, client, db_session):
        """
        RED: This will fail because get_current_user doesn't exist yet.

        Requirement: Valid JWT token should return authenticated user
        """
        from app.models.user import User
        from app.auth import create_access_token
        from app.dependencies import get_current_user
        from fastapi import Request
        from unittest.mock import Mock

        # Create test user
        user = User(
            email="auth@example.com",
            google_id="google_auth_123",
            name="Auth User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Generate valid token
        token = create_access_token(user.id)

        # Mock request with Authorization header
        mock_request = Mock(spec=Request)
        mock_request.headers = {"authorization": f"Bearer {token}"}

        # Get current user should return the user
        current_user = get_current_user(mock_request, db_session)

        assert current_user.id == user.id
        assert current_user.email == "auth@example.com"

    def test_get_current_user_without_authorization_header(self, db_session):
        """
        RED: This will fail.

        Requirement: Request without Authorization header should raise 401
        """
        from app.dependencies import get_current_user
        from fastapi import Request
        from unittest.mock import Mock

        # Mock request without Authorization header
        mock_request = Mock(spec=Request)
        mock_request.headers = {}

        # Should raise HTTPException with 401
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "authorization" in exc_info.value.detail.lower()

    def test_get_current_user_with_invalid_token_format(self, db_session):
        """
        RED: This will fail.

        Requirement: Token without 'Bearer' prefix should raise 401
        """
        from app.dependencies import get_current_user
        from fastapi import Request
        from unittest.mock import Mock

        # Mock request with invalid format (no Bearer prefix)
        mock_request = Mock(spec=Request)
        mock_request.headers = {"authorization": "InvalidToken"}

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_expired_token(self, client, db_session):
        """
        RED: This will fail.

        Requirement: Expired JWT token should raise 401
        """
        from app.models.user import User
        from app.auth import create_access_token
        from app.dependencies import get_current_user
        from fastapi import Request
        from unittest.mock import Mock

        # Create test user
        user = User(
            email="expired@example.com",
            google_id="google_expired_123",
            name="Expired User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Generate expired token (expired 1 hour ago)
        expired_token = create_access_token(
            user.id,
            expires_delta=timedelta(hours=-1)
        )

        # Mock request with expired token
        mock_request = Mock(spec=Request)
        mock_request.headers = {"authorization": f"Bearer {expired_token}"}

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_invalid_signature(self, db_session):
        """
        RED: This will fail.

        Requirement: Token with invalid signature should raise 401
        """
        from app.dependencies import get_current_user
        from app.config import settings
        from fastapi import Request
        from unittest.mock import Mock

        # Create token with wrong secret (invalid signature)
        fake_payload = {"sub": "999", "exp": datetime.utcnow() + timedelta(hours=1)}
        fake_token = jwt.encode(fake_payload, "wrong_secret", algorithm=settings.JWT_ALGORITHM)

        # Mock request with invalid token
        mock_request = Mock(spec=Request)
        mock_request.headers = {"authorization": f"Bearer {fake_token}"}

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_non_existent_user(self, db_session):
        """
        RED: This will fail.

        Requirement: Valid token for non-existent user should raise 401
        """
        from app.auth import create_access_token
        from app.dependencies import get_current_user
        from fastapi import Request
        from unittest.mock import Mock

        # Generate token for non-existent user ID
        token = create_access_token(user_id=99999)

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.headers = {"authorization": f"Bearer {token}"}

        # Should raise HTTPException (user not found)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_malformed_token(self, db_session):
        """
        RED: This will fail.

        Requirement: Malformed JWT token should raise 401
        """
        from app.dependencies import get_current_user
        from fastapi import Request
        from unittest.mock import Mock

        # Mock request with malformed token
        mock_request = Mock(spec=Request)
        mock_request.headers = {"authorization": "Bearer not.a.valid.jwt.token"}

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
class TestProtectedEndpoint:
    """Test that endpoints can use get_current_user dependency"""

    def test_protected_endpoint_requires_authentication(self, client):
        """
        RED: This will fail.

        Requirement: Protected endpoints should return 401 without token
        """
        # Try to access protected endpoint without token
        response = client.get("/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_with_valid_token(self, client, db_session):
        """
        RED: This will fail.

        Requirement: Protected endpoints should work with valid token
        """
        from app.models.user import User
        from app.auth import create_access_token

        # Create test user
        user = User(
            email="protected@example.com",
            google_id="google_protected_123",
            name="Protected User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Generate token
        token = create_access_token(user.id)

        # Access protected endpoint with token
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "protected@example.com"
        assert data["name"] == "Protected User"


# ============================================================================
# TDD Status: RED Phase 🔴
# ============================================================================
#
# These tests will FAIL because:
# - app/dependencies.py doesn't exist yet
# - get_current_user function doesn't exist
# - /users/me endpoint doesn't exist
#
# Next steps (GREEN phase):
# 1. Create app/dependencies.py with get_current_user
# 2. Create /users/me endpoint in auth router
# 3. Run tests and watch them pass!
#
# ============================================================================
