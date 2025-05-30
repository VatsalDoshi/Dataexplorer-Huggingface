import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import create_db_and_tables, engine
from sqlmodel import Session
from backend.models import User, FollowedDataset, DatasetCombination

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    # Create tables
    create_db_and_tables()
    yield
    # Clean up after test
    with Session(engine) as session:
        session.query(DatasetCombination).delete()
        session.query(FollowedDataset).delete()
        session.query(User).delete()
        session.commit()

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "secure_password123"
    }

@pytest.fixture
def auth_headers(test_db, test_user):
    # Register and login to get token
    client.post("/auth/register", json=test_user)
    login_response = client.post("/auth/login", json=test_user)
    access_token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

def test_get_datasets(auth_headers):
    response = client.get("/auth/datasets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_follow_dataset(auth_headers):
    dataset_id = "test-dataset/example"
    response = client.post(
        "/user/follow",
        json={"dataset_id": dataset_id},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "follow_id" in data

def test_follow_duplicate_dataset(auth_headers):
    dataset_id = "test-dataset/example"
    # First follow
    client.post(
        "/user/follow",
        json={"dataset_id": dataset_id},
        headers=auth_headers
    )
    # Try to follow again
    response = client.post(
        "/user/follow",
        json={"dataset_id": dataset_id},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "already following" in response.json()["detail"].lower()

def test_unfollow_dataset(auth_headers):
    dataset_id = "test-dataset/example"
    # First follow
    client.post(
        "/user/follow",
        json={"dataset_id": dataset_id},
        headers=auth_headers
    )
    # Then unfollow
    response = client.delete(
        f"/user/follow/{dataset_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "message" in response.json()

def test_unfollow_nonexistent_dataset(auth_headers):
    response = client.delete(
        "/user/follow/nonexistent-dataset",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "not following" in response.json()["detail"].lower()

def test_get_followed_datasets(auth_headers):
    # Follow a dataset first
    dataset_id = "test-dataset/example"
    client.post(
        "/user/follow",
        json={"dataset_id": dataset_id},
        headers=auth_headers
    )
    # Get followed datasets
    response = client.get("/user/followed", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(ds["id"] == dataset_id for ds in data)

def test_create_dataset_combination(auth_headers):
    combination_data = {
        "name": "Test Combination",
        "dataset_ids": ["dataset1", "dataset2"],
        "description": "Test description"
    }
    response = client.post(
        "/datasets/combine",
        json=combination_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == combination_data["name"]
    assert data["description"] == combination_data["description"]
    assert "id" in data
    assert "created_at" in data

def test_get_user_combinations(auth_headers):
    # Create a combination first
    combination_data = {
        "name": "Test Combination",
        "dataset_ids": ["dataset1", "dataset2"],
        "description": "Test description"
    }
    client.post(
        "/datasets/combine",
        json=combination_data,
        headers=auth_headers
    )
    # Get user's combinations
    response = client.get("/datasets/combinations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == combination_data["name"]
    assert "datasets" in data[0]

def test_impact_assessment(auth_headers):
    impact_data = {
        "datasets": [
            {"id": "dataset1", "size_mb": 500},
            {"id": "dataset2", "size_mb": 1500}
        ],
        "method": "naive"
    }
    response = client.post(
        "/auth/datasets/impact",
        json=impact_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "method" in data
    assert len(data["results"]) == len(impact_data["datasets"]) 