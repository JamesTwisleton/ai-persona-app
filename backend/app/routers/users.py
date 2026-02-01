"""
User Routes

User profile and management endpoints.

This module was implemented following TDD:
1. RED: Tests written first in tests/unit/test_auth_middleware.py
2. GREEN: This implementation makes those tests pass
3. REFACTOR: Can now improve while keeping tests green

Endpoints:
- GET /users/me - Get current authenticated user's profile
"""

from fastapi import APIRouter, Depends

from app.models.user import User
from app.dependencies import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


# ============================================================================
# User Profile Endpoint
# ============================================================================

@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.

    Requires authentication via JWT token in Authorization header.

    Headers:
        Authorization: Bearer <jwt_token>

    Returns:
        dict: Current user's profile information

    Raises:
        HTTPException: 401 if not authenticated

    Example:
        GET /users/me
        Authorization: Bearer eyJhbGci...

        Response:
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "google_id": "google_oauth2|123456789",
            "picture_url": "https://...",
            "created_at": "2026-01-31T...",
            "updated_at": "2026-01-31T..."
        }
    """
    return current_user.to_dict()


# ============================================================================
# TDD Status: GREEN Phase
# ============================================================================
#
# This implementation should make user profile tests pass!
#
# Run: pytest tests/unit/test_auth_middleware.py::TestProtectedEndpoint -v
#
# ============================================================================
