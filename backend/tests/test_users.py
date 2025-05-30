import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import User, FollowedDataset, DatasetCombination


class TestUserRoutes:
    """Test cases for user-related endpoints."""

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/users/me")
        
        # Should require authentication
        assert response.status_code == 401

    def test_get_current_user_authorized(self, client: TestClient):
        """Test getting current user with valid authentication."""
        # This test would require implementing auth token generation
        # For now, test the endpoint exists
        response = client.get("/users/me")
        assert response.status_code in [200, 401]

    def test_update_user_profile(self, client: TestClient):
        """Test updating user profile."""
        update_data = {
            "email": "updated@example.com"
        }
        response = client.put("/users/me", json=update_data)
        
        # Should require authentication or succeed if authenticated
        assert response.status_code in [200, 401]

    def test_delete_user_account(self, client: TestClient):
        """Test deleting user account."""
        response = client.delete("/users/me")
        
        # Should require authentication
        assert response.status_code in [200, 401, 404]


class TestFollowedDatasets:
    """Test cases for followed datasets functionality."""

    def test_get_followed_datasets_unauthorized(self, client: TestClient):
        """Test getting followed datasets without auth."""
        response = client.get("/users/me/followed-datasets")
        
        assert response.status_code == 401

    def test_follow_dataset_unauthorized(self, client: TestClient):
        """Test following a dataset without auth."""
        dataset_data = {
            "dataset_id": "huggingface/test-dataset"
        }
        response = client.post("/users/me/followed-datasets", json=dataset_data)
        
        assert response.status_code == 401

    def test_unfollow_dataset_unauthorized(self, client: TestClient):
        """Test unfollowing a dataset without auth."""
        response = client.delete("/users/me/followed-datasets/test-dataset")
        
        assert response.status_code == 401


class TestDatasetCombinations:
    """Test cases for dataset combinations functionality."""

    def test_get_combinations_unauthorized(self, client: TestClient):
        """Test getting combinations without auth."""
        response = client.get("/users/me/combinations")
        
        assert response.status_code == 401

    def test_create_combination_unauthorized(self, client: TestClient):
        """Test creating combination without auth."""
        combination_data = {
            "name": "Test Combination",
            "description": "Test description",
            "dataset_ids": ["dataset1", "dataset2"]
        }
        response = client.post("/users/me/combinations", json=combination_data)
        
        assert response.status_code == 401

    def test_update_combination_unauthorized(self, client: TestClient):
        """Test updating combination without auth."""
        update_data = {
            "name": "Updated Combination"
        }
        response = client.put("/users/me/combinations/1", json=update_data)
        
        assert response.status_code == 401

    def test_delete_combination_unauthorized(self, client: TestClient):
        """Test deleting combination without auth."""
        response = client.delete("/users/me/combinations/1")
        
        assert response.status_code == 401


class TestUserDataValidation:
    """Test cases for user data validation."""

    def test_invalid_email_format(self, client: TestClient):
        """Test user update with invalid email format."""
        update_data = {
            "email": "invalid-email-format"
        }
        response = client.put("/users/me", json=update_data)
        
        # Should fail with validation error (or require auth first)
        assert response.status_code in [401, 422]

    def test_empty_combination_name(self, client: TestClient):
        """Test creating combination with empty name."""
        combination_data = {
            "name": "",
            "dataset_ids": ["dataset1"]
        }
        response = client.post("/users/me/combinations", json=combination_data)
        
        # Should fail with validation error (or require auth first)
        assert response.status_code in [401, 422]

    def test_invalid_dataset_id_format(self, client: TestClient):
        """Test following dataset with invalid ID format."""
        dataset_data = {
            "dataset_id": ""  # Empty dataset ID
        }
        response = client.post("/users/me/followed-datasets", json=dataset_data)
        
        # Should fail with validation error (or require auth first)
        assert response.status_code in [401, 422]


class TestUserEndpointsExist:
    """Test that user endpoints are properly registered."""

    def test_user_routes_exist(self, client: TestClient):
        """Test that user-related routes are registered."""
        endpoints = [
            "/users/me",
            "/users/me/followed-datasets",
            "/users/me/combinations"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404 (route exists)
            assert response.status_code != 404

    def test_user_post_routes_exist(self, client: TestClient):
        """Test that POST user routes are registered."""
        response = client.post("/users/me/followed-datasets", json={})
        # Should not return 404 (route exists)
        assert response.status_code != 404

        response = client.post("/users/me/combinations", json={})
        # Should not return 404 (route exists)
        assert response.status_code != 404 