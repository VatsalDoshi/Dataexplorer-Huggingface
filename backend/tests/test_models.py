import pytest
from datetime import datetime
from sqlmodel import Session
from models import User, FollowedDataset, DatasetCombination


class TestUserModel:
    """Test cases for the User model."""

    def test_create_user(self, session: Session):
        """Test creating a new user."""
        user = User(
            email="newuser@example.com",
            hashed_password="hashed_password_123",
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)

    def test_user_email_unique(self, session: Session, sample_user: User):
        """Test that user email must be unique."""
        duplicate_user = User(
            email=sample_user.email,  # Same email as existing user
            hashed_password="different_password",
            is_active=True
        )
        session.add(duplicate_user)
        
        with pytest.raises(Exception):  # Should raise integrity error
            session.commit()

    def test_user_defaults(self, session: Session):
        """Test user model defaults."""
        user = User(
            email="defaults@example.com",
            hashed_password="password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.is_active is True  # Default value
        assert isinstance(user.created_at, datetime)


class TestFollowedDatasetModel:
    """Test cases for the FollowedDataset model."""

    def test_create_followed_dataset(self, session: Session, sample_user: User):
        """Test creating a new followed dataset."""
        dataset = FollowedDataset(
            user_id=sample_user.id,
            dataset_id="huggingface/test-dataset"
        )
        session.add(dataset)
        session.commit()
        session.refresh(dataset)

        assert dataset.id is not None
        assert dataset.user_id == sample_user.id
        assert dataset.dataset_id == "huggingface/test-dataset"
        assert isinstance(dataset.created_at, datetime)

    def test_followed_dataset_foreign_key(self, session: Session):
        """Test foreign key constraint for user_id."""
        dataset = FollowedDataset(
            user_id=99999,  # Non-existent user ID
            dataset_id="test-dataset"
        )
        session.add(dataset)
        
        with pytest.raises(Exception):  # Should raise foreign key constraint error
            session.commit()


class TestDatasetCombinationModel:
    """Test cases for the DatasetCombination model."""

    def test_create_dataset_combination(self, session: Session, sample_user: User):
        """Test creating a new dataset combination."""
        combination = DatasetCombination(
            user_id=sample_user.id,
            name="My Combination",
            description="Test combination",
            dataset_ids='["dataset1", "dataset2", "dataset3"]'
        )
        session.add(combination)
        session.commit()
        session.refresh(combination)

        assert combination.id is not None
        assert combination.user_id == sample_user.id
        assert combination.name == "My Combination"
        assert combination.description == "Test combination"
        assert isinstance(combination.created_at, datetime)

    def test_dataset_ids_methods(self, session: Session, sample_user: User):
        """Test the JSON dataset_ids getter and setter methods."""
        combination = DatasetCombination(
            user_id=sample_user.id,
            name="Test Methods",
            dataset_ids='[]'
        )
        
        # Test setter
        test_ids = ["dataset1", "dataset2", "dataset3"]
        combination.set_dataset_ids(test_ids)
        
        session.add(combination)
        session.commit()
        session.refresh(combination)

        # Test getter
        retrieved_ids = combination.get_dataset_ids()
        assert retrieved_ids == test_ids
        assert isinstance(retrieved_ids, list)

    def test_empty_dataset_ids(self, session: Session, sample_user: User):
        """Test combination with empty dataset_ids."""
        combination = DatasetCombination(
            user_id=sample_user.id,
            name="Empty Combination"
        )
        session.add(combination)
        session.commit()
        session.refresh(combination)

        # Should default to empty list
        assert combination.get_dataset_ids() == []

    def test_optional_description(self, session: Session, sample_user: User):
        """Test that description is optional."""
        combination = DatasetCombination(
            user_id=sample_user.id,
            name="No Description",
            dataset_ids='["dataset1"]'
        )
        session.add(combination)
        session.commit()
        session.refresh(combination)

        assert combination.description is None 