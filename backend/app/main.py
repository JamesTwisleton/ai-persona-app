"""
AI Focus Groups - FastAPI Main Application

This is the entry point for the FastAPI backend application.

Implementation follows Test-Driven Development:
- Tests were written FIRST in tests/integration/test_health_endpoint.py
- This implementation makes those tests pass (GREEN phase)
- Following refactoring will keep tests passing (REFACTOR phase)

Environment Variables Required:
- DATABASE_URL: PostgreSQL connection string
- JWT_SECRET: Secret key for JWT token generation
- TESTING: Set to "1" for test mode
"""

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
import logging
import jwt

# Import version from package
from app import __version__
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI Application Instance
# ============================================================================

app = FastAPI(
    title="AI Focus Groups API",
    description="""
Backend API for AI persona generation and focus group conversations.

## Authentication

This API uses JWT Bearer tokens for authentication:

1. **Get a token**: Sign in via Google OAuth at `/auth/login/google`
2. **Use the token**: Click the 🔒 Authorize button and paste your token
3. **Access protected endpoints**: Endpoints requiring authentication will check your token

The token is valid for 24 hours.
    """,
    version=__version__,
    docs_url="/docs" if os.getenv("TESTING") != "1" else None,  # Disable docs in test
    redoc_url="/redoc" if os.getenv("TESTING") != "1" else None,
    swagger_ui_parameters={
        "persistAuthorization": True,  # Remember authorization between page refreshes
    }
)

# ============================================================================
# CORS Configuration
# ============================================================================

# Allow Next.js frontend to communicate with backend
# In production, this should be restricted to the actual frontend URL
CORS_ORIGINS = [
    "http://localhost:3000",  # Next.js development server
    "http://localhost:3001",  # Alternative port
    "http://frontend:3000",   # Docker internal network
]

# In production, load from environment variable
if os.getenv("FRONTEND_URL"):
    CORS_ORIGINS.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware required for OAuth (stores state)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET
)

# ============================================================================
# OpenAPI Customization for Swagger UI
# ============================================================================

def custom_openapi():
    """Customize OpenAPI schema to add Bearer token authentication"""
    if app.openapi_schema:
        return app.openapi_schema

    # Generate the base OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme for JWT Bearer tokens
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token obtained from /auth/login/google"
        }
    }

    # Mark /users/me endpoint as requiring authentication
    if "/users/me" in openapi_schema["paths"]:
        openapi_schema["paths"]["/users/me"]["get"]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ============================================================================
# Startup/Shutdown Events
# ============================================================================

# Global state for preview mode persistence
PREVIEW_NAMES = {}

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    """
    logger.info(f"Starting AI Focus Groups API v{__version__}")
    logger.info(f"Environment: {settings.ENV}")

    # Preview mode: override auth to return a dummy user without DB lookup.
    if settings.ENV == "preview":
        from app.dependencies import (
            get_current_user, get_current_user_optional,
            get_current_admin, get_current_superuser,
        )
        from app.models.user import User

        async def _dummy_user(request: Request):
            global PREVIEW_NAMES

            # Extract sub from JWT if present
            auth_header = request.headers.get("Authorization")
            sub = "preview-dummy"
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
                    sub = payload.get("sub", sub)
                except:
                    pass

            display_name = PREVIEW_NAMES.get(sub, "Preview Tester")
            if sub.startswith("smoke-test-no-display") and sub not in PREVIEW_NAMES:
                display_name = None

            return User(
                id=abs(hash(sub)) % 1000000,
                email=f"{sub}@preview.local",
                google_id=sub,
                name=f"User {sub}",
                display_name=display_name,
                is_admin=True,
                is_superuser=True,
            )

        app.dependency_overrides[get_current_user] = _dummy_user
        app.dependency_overrides[get_current_user_optional] = _dummy_user
        app.dependency_overrides[get_current_admin] = _dummy_user
        app.dependency_overrides[get_current_superuser] = _dummy_user
        logger.info("Preview mode: auth dependencies overridden with dynamic dummy user")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    """
    logger.info("Shutting down AI Focus Groups API")


# ============================================================================
# Health Check Endpoint (Phase 1)
# ============================================================================

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check endpoint",
    response_description="Returns the health status of the API",
)
async def health_check():
    """
    Health check endpoint for monitoring and container orchestration.

    This endpoint:
    - Returns 200 OK if the service is running
    - Requires no authentication
    - Is used by Kubernetes/ECS health probes
    - Indicates the API version

    Returns:
        dict: Health status information including version
    """
    return {
        "status": "healthy",
        "version": __version__,
        "environment": "test" if os.getenv("TESTING") == "1" else "development"
    }


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get(
    "/",
    tags=["Info"],
    summary="API information",
)
async def root():
    """
    Root endpoint providing basic API information.

    Returns:
        dict: API metadata and links
    """
    return {
        "name": "AI Focus Groups API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
        "message": "Welcome to the AI Focus Groups API. Visit /docs for interactive documentation."
    }


# ============================================================================
# Route Imports (Phase 2+)
# ============================================================================

# Local avatar static file serving (development only)
if settings.LOCAL_AVATAR_DIR:
    os.makedirs(settings.LOCAL_AVATAR_DIR, exist_ok=True)
    app.mount("/avatars", StaticFiles(directory=settings.LOCAL_AVATAR_DIR), name="avatars")
    logger.info(f"Serving local avatars from {settings.LOCAL_AVATAR_DIR} at /avatars")

# Authentication routes (OAuth 2.0)
from app.routers import auth, users, personas, admin, conversations, discovery
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(personas.router)
app.include_router(admin.router)
app.include_router(conversations.router)
app.include_router(discovery.router)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 error handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 error handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Development server configuration
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
