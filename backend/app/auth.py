"""
Authentication Module

Handles JWT token generation and OAuth 2.0 authentication with Google.

This module was implemented following TDD:
1. RED: Tests written first in tests/unit/test_oauth_handler.py
2. GREEN: This implementation makes those tests pass
3. REFACTOR: Can now improve while keeping tests green

Features:
- JWT session token generation and validation
- Google OAuth 2.0 client configuration
- User authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from authlib.integrations.starlette_client import OAuth
from app.config import settings
import secrets


# ============================================================================
# JWT Token Management
# ============================================================================

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for authenticated user sessions.

    Args:
        user_id: User's database ID
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token

    Example:
        token = create_access_token(user_id=123)
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_EXPIRATION_MINUTES
        )

    to_encode = {
        "sub": str(user_id),  # Subject (user ID)
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Optional[Dict]: Token payload if valid, None if invalid/expired

    Example:
        payload = decode_access_token("eyJhbGci...")
        if payload:
            user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[int]:
    """
    Verify JWT token and extract user ID.

    Args:
        token: JWT token string

    Returns:
        Optional[int]: User ID if token is valid, None otherwise
    """
    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        return None

    try:
        return int(user_id)
    except (ValueError, TypeError):
        return None


# ============================================================================
# OAuth 2.0 Client Setup
# ============================================================================

# Initialize OAuth registry
oauth = OAuth()

# Register Google OAuth provider
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url=settings.GOOGLE_DISCOVERY_URL,
    client_kwargs={
        'scope': settings.GOOGLE_SCOPES,
        'prompt': 'select_account',  # Always show account selector
    }
)


# ============================================================================
# OAuth State Management (CSRF Protection)
# ============================================================================

# In production, store OAuth states in Redis/database
# For now, use in-memory dict (will be lost on restart)
_oauth_states: Dict[str, datetime] = {}


def generate_oauth_state() -> str:
    """
    Generate a random state parameter for OAuth CSRF protection.

    Returns:
        str: Random state string
    """
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = datetime.utcnow()
    return state


def verify_oauth_state(state: str, max_age_minutes: int = 10) -> bool:
    """
    Verify OAuth state parameter to prevent CSRF attacks.

    Args:
        state: State parameter from OAuth callback
        max_age_minutes: Maximum age of state in minutes (default 10)

    Returns:
        bool: True if state is valid and not expired
    """
    if state not in _oauth_states:
        return False

    created_at = _oauth_states[state]
    age = datetime.utcnow() - created_at

    # State is valid if not expired
    is_valid = age.total_seconds() < (max_age_minutes * 60)

    # Clean up used state
    if state in _oauth_states:
        del _oauth_states[state]

    return is_valid


def cleanup_expired_states(max_age_minutes: int = 10) -> None:
    """
    Remove expired OAuth states from memory.

    Args:
        max_age_minutes: Maximum age before state is considered expired
    """
    now = datetime.utcnow()
    expired_states = [
        state for state, created_at in _oauth_states.items()
        if (now - created_at).total_seconds() > (max_age_minutes * 60)
    ]

    for state in expired_states:
        del _oauth_states[state]


# ============================================================================
# TDD Status: GREEN Phase (Partial)
# ============================================================================
#
# This implementation provides JWT utilities to make token tests pass.
# OAuth endpoints will be implemented in app/routers/auth.py
#
# ============================================================================
