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

@router.get(
    "/me",
    summary="Get current user profile",
    description="Get the authenticated user's profile information. Requires a valid JWT token.",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Not authenticated - missing or invalid token"}
    }
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.

    Requires authentication via JWT token in Authorization header.

    **How to authenticate:**
    1. Get a JWT token by signing in at `/auth/login/google`
    2. Click the 🔒 Authorize button at the top of this page
    3. Enter: `Bearer YOUR_JWT_TOKEN`
    4. Click "Authorize"
    5. Try this endpoint!

    **Response includes:**
    - User ID
    - Email address
    - Full name
    - Google ID
    - Profile picture URL
    - Account creation timestamp

    **Example Response:**
    ```json
    {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name",
        "google_id": "108423082868902273239",
        "picture_url": "https://lh3.googleusercontent.com/...",
        "created_at": "2026-02-01T19:36:26",
        "updated_at": "2026-02-01T19:36:26"
    }
    ```
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
