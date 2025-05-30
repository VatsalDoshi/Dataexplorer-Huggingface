import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import create_db_and_tables, engine
from sqlmodel import Session
from backend.models import User

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    # Create tables
    create_db_and_tables()
    yield
    # Clean up after test
    with Session(engine) as session:
        session.query(User).delete()
        session.commit()

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "secure_password123"
    }

def test_register_user(test_db, test_user):
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_user(test_db, test_user):
    # First registration
    client.post("/auth/register", json=test_user)
    # Try to register same user again
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_login_success(test_db, test_user):
    # Register user first
    client.post("/auth/register", json=test_user)
    # Try to login
    response = client.post("/auth/login", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(test_db, test_user):
    # Register user first
    client.post("/auth/register", json=test_user)
    # Try to login with wrong password
    wrong_credentials = test_user.copy()
    wrong_credentials["password"] = "wrong_password"
    response = client.post("/auth/login", json=wrong_credentials)
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_login_nonexistent_user(test_db):
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "any_password"
    })
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_refresh_token(test_db, test_user):
    # Register and login to get tokens
    client.post("/auth/register", json=test_user)
    login_response = client.post("/auth/login", json=test_user)
    refresh_token = login_response.json()["refresh_token"]
    
    # Try to refresh token
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_refresh_token_invalid(test_db):
    response = client.post("/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_protected_route_without_token(test_db):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "bearer" in response.json()["detail"].lower()

def test_protected_route_with_token(test_db, test_user):
    # Register and login to get token
    client.post("/auth/register", json=test_user)
    login_response = client.post("/auth/login", json=test_user)
    access_token = login_response.json()["access_token"]
    
    # Try to access protected route
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"] 