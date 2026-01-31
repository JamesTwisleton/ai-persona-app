"""
Test Health Check Endpoint

Following TDD: Tests were written FIRST, implementation came second!

The health check endpoint is critical for:
- Kubernetes/ECS health probes
- Monitoring systems
- Verifying the app is running

Test Requirements:
- Endpoint should be at GET /health
- Should return 200 status code
- Should return JSON with status field
- Should not require authentication (public endpoint)

TDD Cycle Completed:
✅ RED: Tests written and failed initially
✅ GREEN: Implementation in app/main.py makes tests pass
✅ REFACTOR: Can now improve code while keeping tests green
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthEndpoint:
    """Test the /health endpoint for application health checks"""

    def test_health_endpoint_exists(self, client):
        """
        GREEN: This test should now PASS!

        Requirement: GET /health should return 200 OK
        """
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client):
        """
        GREEN: This test should now PASS!

        Requirement: Response should be valid JSON
        """
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

        # Should be able to parse as JSON
        data = response.json()
        assert isinstance(data, dict)

    def test_health_endpoint_contains_status(self, client):
        """
        GREEN: This test should now PASS!

        Requirement: Response should contain 'status' field
        """
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_endpoint_no_auth_required(self, client):
        """
        GREEN: This test should now PASS!

        Requirement: Health check should be public (no auth)
        """
        # Should work without authentication headers
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_includes_version(self, client):
        """
        GREEN: This test should now PASS!

        Requirement: Response should include API version
        """
        response = client.get("/health")
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)
        # Version should match app version
        assert len(data["version"]) > 0

    def test_health_endpoint_includes_environment(self, client):
        """
        Additional test: Should include environment info
        """
        response = client.get("/health")
        data = response.json()

        assert "environment" in data
        # In tests, environment should be "test"
        assert data["environment"] == "test"


# ============================================================================
# Test Root Endpoint
# ============================================================================

@pytest.mark.integration
class TestRootEndpoint:
    """Test the root / endpoint"""

    def test_root_endpoint_exists(self, client):
        """Root endpoint should return 200 OK"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_returns_api_info(self, client):
        """Root endpoint should return API metadata"""
        response = client.get("/")
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data


# ============================================================================
# TDD Success!
# ============================================================================
#
# Run: pytest tests/integration/test_health_endpoint.py -v
#
# All tests should PASS (GREEN state) ✅
#
# This completes the first TDD cycle for Phase 1!
# ============================================================================
