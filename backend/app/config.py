"""
Application Configuration

Manages environment variables and application settings using Pydantic Settings.

Settings are loaded from:
1. Environment variables
2. .env file (if present)
3. Default values (for development)

Usage:
    from app.config import settings

    client_id = settings.GOOGLE_CLIENT_ID
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are typed and validated using Pydantic.
    """

    # ========================================================================
    # Application Settings
    # ========================================================================

    ENV: str = "development"
    DEBUG: bool = True
    TESTING: bool = False

    # ========================================================================
    # Database Configuration
    # ========================================================================

    DATABASE_URL: str = "postgresql://ai_focus_groups_user:dev_password@localhost:5432/ai_focus_groups"

    # ========================================================================
    # JWT Configuration (Session Tokens)
    # ========================================================================

    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    # ========================================================================
    # Google OAuth 2.0 Configuration
    # ========================================================================

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback/google"
    GOOGLE_SCOPES: str = "openid email profile"

    # Discovery endpoint for Google OAuth
    GOOGLE_DISCOVERY_URL: str = "https://accounts.google.com/.well-known/openid-configuration"

    # ========================================================================
    # CORS Settings
    # ========================================================================

    FRONTEND_URL: str = "http://localhost:3000"

    # ========================================================================
    # Logging
    # ========================================================================

    LOG_LEVEL: str = "INFO"

    # ========================================================================
    # Pydantic Settings Configuration
    # ========================================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars
    )

    # ========================================================================
    # Computed Properties
    # ========================================================================

    @property
    def google_scopes_list(self) -> List[str]:
        """Convert GOOGLE_SCOPES string to list."""
        return self.GOOGLE_SCOPES.split()

    @property
    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.TESTING or os.getenv("TESTING", "0") == "1"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENV == "production"


# ============================================================================
# Global Settings Instance
# ============================================================================

# Create a single instance of settings that can be imported throughout the app
settings = Settings()


# ============================================================================
# Configuration Validation
# ============================================================================

def validate_oauth_config() -> bool:
    """
    Validate that OAuth configuration is set up correctly.

    Returns:
        bool: True if OAuth is properly configured, False otherwise
    """
    if settings.is_testing:
        # Test environment doesn't need real OAuth credentials
        return True

    required_settings = [
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        settings.GOOGLE_REDIRECT_URI,
    ]

    return all(required_settings)


def get_oauth_missing_vars() -> List[str]:
    """
    Get list of missing OAuth configuration variables.

    Returns:
        List[str]: List of missing environment variable names
    """
    missing = []

    if not settings.GOOGLE_CLIENT_ID:
        missing.append("GOOGLE_CLIENT_ID")
    if not settings.GOOGLE_CLIENT_SECRET:
        missing.append("GOOGLE_CLIENT_SECRET")
    if not settings.GOOGLE_REDIRECT_URI:
        missing.append("GOOGLE_REDIRECT_URI")

    return missing
