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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import os
import logging

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
    description="Backend API for AI persona generation and focus group conversations",
    version=__version__,
    docs_url="/docs" if os.getenv("TESTING") != "1" else None,  # Disable docs in test
    redoc_url="/redoc" if os.getenv("TESTING") != "1" else None,
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
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    Future: Initialize database connection pool, load AI models, etc.
    """
    logger.info(f"Starting AI Focus Groups API v{__version__}")
    logger.info("Environment: " + ("TEST" if os.getenv("TESTING") == "1" else "DEVELOPMENT"))


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    Future: Close database connections, cleanup resources, etc.
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

# Authentication routes (OAuth 2.0)
from app.routers import auth, users
app.include_router(auth.router)
app.include_router(users.router)

# Future routers (Phase 3+):
# from app.routers import personas, conversations, admin
# app.include_router(personas.router)
# app.include_router(conversations.router)
# app.include_router(admin.router)


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
