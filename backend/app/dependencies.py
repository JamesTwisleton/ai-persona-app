"""
FastAPI Dependencies

Authentication and authorization dependencies for protected endpoints.

This module was implemented following TDD:
1. RED: Tests written first in tests/unit/test_auth_middleware.py
2. GREEN: This implementation makes those tests pass
3. REFACTOR: Can now improve while keeping tests green

Dependencies:
- get_current_user: Extracts JWT from header, validates, returns User
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.auth import verify_token
from app.models.user import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Authentication dependency for protected endpoints.

    Extracts and validates JWT token from Authorization header,
    then returns the authenticated user.

    Usage in endpoints:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}

    Args:
        request: FastAPI Request object (contains headers)
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: 401 if authentication fails
    """
    # Extract Authorization header
    authorization: Optional[str] = request.headers.get("authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse Bearer token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify and decode JWT token
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Optional: Dependency for optional authentication (user might not be logged in)
def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.

    Returns User if valid token is present, None otherwise.
    Does not raise exceptions for missing/invalid tokens.

    Useful for endpoints that work differently for authenticated users
    but are also accessible to anonymous users.

    Usage:
        @router.get("/public-but-personalized")
        def route(current_user: Optional[User] = Depends(get_current_user_optional)):
            if current_user:
                return {"message": f"Welcome back, {current_user.name}!"}
            return {"message": "Welcome, guest!"}
    """
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None


# ============================================================================
# TDD Status: GREEN Phase
# ============================================================================
#
# This implementation should make all auth middleware tests pass!
#
# Run: pytest tests/unit/test_auth_middleware.py -v
#
# ============================================================================
