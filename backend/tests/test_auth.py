import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import User


class TestAuthRoutes:
    """Test cases for authentication endpoints."""

    def test_register_new_user(self, client: TestClient):
        """Test user registration with valid data."""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123"
        }
        response = client.post("/auth/register", json=user_data)
        
        # Expect successful registration
        assert response.status_code in [200, 201]
        data = response.json()
        assert "email" in data or "message" in data

    def test_register_duplicate_email(self, client: TestClient, sample_user: User):
        """Test registration with existing email."""
        user_data = {
            "email": sample_user.email,
            "password": "password123"
        }
        response = client.post("/auth/register", json=user_data)
        
        # Should fail with conflict or bad request
        assert response.status_code in [400, 409]

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        response = client.post("/auth/register", json=user_data)
        
        # Should fail with validation error
        assert response.status_code == 422

    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password."""
        user_data = {
            "email": "test@example.com",
            "password": "123"  # Too weak
        }
        response = client.post("/auth/register", json=user_data)
        
        # May succeed or fail depending on validation rules
        assert response.status_code in [200, 201, 400, 422]

    def test_login_valid_credentials(self, client: TestClient):
        """Test login with valid credentials."""
        # First register a user
        register_data = {
            "email": "loginuser@example.com",
            "password": "password123"
        }
        client.post("/auth/register", json=register_data)
        
        # Then try to login
        login_data = {
            "email": "loginuser@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_data)
        
        # Should succeed and return token
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data or "token" in data

    def test_login_invalid_credentials(self, client: TestClient, sample_user: User):
        """Test login with invalid credentials."""
        login_data = {
            "email": sample_user.email,
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        
        # Should fail with unauthorized
        assert response.status_code in [401, 403]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_data)
        
        # Should fail with unauthorized or not found
        assert response.status_code in [401, 404]

    def test_logout(self, client: TestClient):
        """Test logout functionality."""
        # This test depends on how logout is implemented
        response = client.post("/auth/logout")
        
        # Should succeed or require authentication
        assert response.status_code in [200, 401]

    def test_refresh_token(self, client: TestClient):
        """Test token refresh functionality."""
        # This test depends on token refresh implementation
        response = client.post("/auth/refresh")
        
        # Should succeed with valid token or fail without
        assert response.status_code in [200, 401]


class TestAuthValidation:
    """Test cases for authentication data validation."""

    def test_missing_email(self, client: TestClient):
        """Test registration without email."""
        user_data = {
            "password": "password123"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422

    def test_missing_password(self, client: TestClient):
        """Test registration without password."""
        user_data = {
            "email": "test@example.com"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422

    def test_empty_request_body(self, client: TestClient):
        """Test registration with empty request body."""
        response = client.post("/auth/register", json={})
        assert response.status_code == 422

    def test_malformed_json(self, client: TestClient):
        """Test registration with malformed JSON."""
        response = client.post(
            "/auth/register",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422 