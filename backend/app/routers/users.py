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

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/users", tags=["users"])


# ============================================================================
# Request Schemas
# ============================================================================

class UserUpdate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)


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
    return current_user.to_dict(show_private=True)


# ============================================================================
# Update User Profile
# ============================================================================

@router.patch(
    "/me",
    summary="Update current user profile",
    responses={
        200: {"description": "User profile updated successfully"},
        401: {"description": "Not authenticated"},
        400: {"description": "Invalid data"}
    }
)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's display name."""
    current_user.display_name = update_data.display_name

    # Handle preview mode state persistence
    if settings.ENV == "preview":
        import app.main
        # Use google_id as sub key
        app.main.PREVIEW_NAMES[current_user.google_id] = update_data.display_name

    try:
        state = inspect(current_user)
        if state and state.session:
            db.commit()
            db.refresh(current_user)
    except:
        # If not a real DB object, just proceed
        pass

    return current_user.to_dict(show_private=True)
