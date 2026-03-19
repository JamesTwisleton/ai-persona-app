# AI Focus Groups - Backend Dockerfile
# Python 3.11+ with FastAPI

# ============================================================================
# Stage 1: Base Image
# ============================================================================
FROM python:3.11-slim as base

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/usr/src/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Stage 2: Development Image
# ============================================================================
FROM base as development

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies (including dev dependencies)
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set entrypoint to initialize database on startup
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Run with hot-reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================================
# Stage 3: Test Image
# ============================================================================
FROM development as test

# Run tests during build (optional, can be disabled)
# Uncomment to run tests as part of Docker build
# RUN pytest tests/ -v --cov=app --cov-report=term-missing

CMD ["pytest", "tests/", "-v", "--cov=app"]

# ============================================================================
# Stage 4: Production Image
# ============================================================================
FROM base as production

# Copy requirements (production only)
COPY requirements.txt ./

# Install Python dependencies (no dev dependencies)
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser

# Copy application code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Change ownership to non-root user
RUN chown -R appuser:appuser /usr/src/app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Set entrypoint to initialize database on startup
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Run with production ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
