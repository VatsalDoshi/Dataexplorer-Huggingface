import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_session
from models import User, FollowedDataset, DatasetCombination

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite://"

@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user(session: Session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_123",
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def sample_dataset(session: Session, sample_user: User):
    """Create a sample followed dataset for testing."""
    dataset = FollowedDataset(
        user_id=sample_user.id,
        dataset_id="test-dataset-id"
    )
    session.add(dataset)
    session.commit()
    session.refresh(dataset)
    return dataset

@pytest.fixture
def sample_combination(session: Session, sample_user: User):
    """Create a sample dataset combination for testing."""
    combination = DatasetCombination(
        user_id=sample_user.id,
        name="Test Combination",
        description="A test dataset combination",
        dataset_ids='["dataset1", "dataset2"]'
    )
    session.add(combination)
    session.commit()
    session.refresh(combination)
    return combination 