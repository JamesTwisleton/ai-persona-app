"""
Authentication Routes

OAuth 2.0 authentication endpoints using Google Sign-In.

This module was implemented following TDD:
1. RED: Tests written first in tests/unit/test_oauth_handler.py
2. GREEN: This implementation makes those tests pass
3. REFACTOR: Can now improve while keeping tests green

Endpoints:
- GET /auth/login/google - Initiate OAuth flow (redirect to Google)
- GET /auth/callback/google - Handle OAuth callback and create session
"""

from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import httpx

from app.database import get_db
from app.models.user import User
from app.auth import (
    oauth,
    create_access_token,
    generate_oauth_state,
    verify_oauth_state,
)
from app.config import settings


router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================================================
# OAuth Login Initiation
# ============================================================================

@router.get("/login/google")
async def google_login(request: Request):
    """
    Initiate Google OAuth 2.0 login flow.

    Redirects user to Google's authorization page where they can
    sign in with their Google account.

    Returns:
        RedirectResponse: Redirect to Google OAuth authorization URL

    Flow:
        1. Generate CSRF protection state
        2. Build authorization URL with required parameters
        3. Redirect user to Google sign-in page
    """
    # Generate state for CSRF protection
    state = generate_oauth_state()

    # Build redirect URI
    redirect_uri = request.url_for('google_callback')

    # Redirect to Google OAuth authorization page
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        state=state
    )


# ============================================================================
# OAuth Callback Handler
# ============================================================================

@router.get("/callback/google")
async def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback after user authorization.

    This endpoint:
    1. Validates the OAuth state (CSRF protection)
    2. Exchanges authorization code for access token
    3. Fetches user info from Google
    4. Creates/updates user in database
    5. Generates JWT session token

    Args:
        request: FastAPI request object
        code: Authorization code from Google
        state: CSRF protection state
        db: Database session

    Returns:
        dict: JWT access token and user information

    Raises:
        HTTPException: If authorization fails or user info cannot be retrieved
    """
    # Validate required parameters
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required"
        )

    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State parameter is required"
        )

    # Verify state for CSRF protection
    if not verify_oauth_state(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter"
        )

    try:
        # Exchange authorization code for access token
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to obtain access token: {str(e)}"
        )

    # Get user info from Google
    try:
        # Parse the ID token (contains user info)
        user_info = token.get('userinfo')

        if not user_info:
            # If userinfo not in token, fetch it from Google's userinfo endpoint
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token['access_token']}"}
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers=headers
                )
                response.raise_for_status()
                user_info = response.json()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to fetch user info: {str(e)}"
        )

    # Extract user data
    google_id = user_info.get('sub')  # Google's unique user ID
    email = user_info.get('email')
    name = user_info.get('name')
    picture_url = user_info.get('picture')

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve required user information from Google"
        )

    # Find or create user in database
    result = db.execute(
        select(User).where(User.google_id == google_id)
    )
    user = result.scalar_one_or_none()

    if user:
        # Update existing user's info (name/picture might have changed)
        user.name = name
        user.picture_url = picture_url
        user.email = email.lower().strip()
    else:
        # Create new user
        user = User(
            google_id=google_id,
            email=email.lower().strip(),
            name=name,
            picture_url=picture_url
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    # Generate JWT session token
    access_token = create_access_token(user.id)

    # Return token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


# ============================================================================
# TDD Status: GREEN Phase
# ============================================================================
#
# This implementation should make OAuth tests pass!
#
# Run: pytest tests/unit/test_oauth_handler.py -v
#
# ============================================================================
