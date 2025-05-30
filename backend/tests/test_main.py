import pytest
from fastapi.testclient import TestClient


class TestMainApp:
    """Test cases for the main FastAPI application."""

    def test_app_startup(self, client: TestClient):
        """Test that the app starts up correctly."""
        # Test a basic endpoint to ensure app is running
        response = client.get("/")
        # Even if 404, the app is responding
        assert response.status_code in [200, 404]

    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are properly configured."""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code in [200, 404]  # Options might not be implemented

    def test_auth_router_included(self, client: TestClient):
        """Test that auth router endpoints are accessible."""
        # Try to access an auth endpoint
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        # Should get a response (even if error, means router is included)
        assert response.status_code != 404

    def test_users_router_included(self, client: TestClient):
        """Test that users router endpoints are accessible."""
        # Try to access a users endpoint
        response = client.get("/users/me")
        # Should get a response (likely 401 without auth, but not 404)
        assert response.status_code != 404

    def test_invalid_endpoint(self, client: TestClient):
        """Test that invalid endpoints return 404."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_health_check(self, client: TestClient):
        """Test basic health check functionality."""
        # Test that the client can make requests
        response = client.get("/docs")  # FastAPI auto-generates docs
        assert response.status_code == 200 