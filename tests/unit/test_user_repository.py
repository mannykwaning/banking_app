"""
Unit tests for UserRepository.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def user_repository(db_session):
    """Create a UserRepository instance."""
    return UserRepository(db_session)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123",
        full_name="Test User",
    )


def test_create_user(user_repository, sample_user_data):
    """Test creating a user."""
    hashed_password = "hashed_password_here"
    user = user_repository.create(sample_user_data, hashed_password)

    assert user.id is not None
    assert user.email == sample_user_data.email
    assert user.username == sample_user_data.username
    assert user.hashed_password == hashed_password
    assert user.full_name == sample_user_data.full_name
    assert user.is_active is True
    assert user.is_superuser is False


def test_get_by_id(user_repository, sample_user_data):
    """Test getting user by ID."""
    user = user_repository.create(sample_user_data, "hashed_password")
    retrieved_user = user_repository.get_by_id(user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.username == user.username


def test_get_by_email(user_repository, sample_user_data):
    """Test getting user by email."""
    user = user_repository.create(sample_user_data, "hashed_password")
    retrieved_user = user_repository.get_by_email(sample_user_data.email)

    assert retrieved_user is not None
    assert retrieved_user.email == user.email


def test_get_by_username(user_repository, sample_user_data):
    """Test getting user by username."""
    user = user_repository.create(sample_user_data, "hashed_password")
    retrieved_user = user_repository.get_by_username(sample_user_data.username)

    assert retrieved_user is not None
    assert retrieved_user.username == user.username


def test_exists_by_email(user_repository, sample_user_data):
    """Test checking if user exists by email."""
    assert user_repository.exists_by_email(sample_user_data.email) is False

    user_repository.create(sample_user_data, "hashed_password")

    assert user_repository.exists_by_email(sample_user_data.email) is True


def test_exists_by_username(user_repository, sample_user_data):
    """Test checking if user exists by username."""
    assert user_repository.exists_by_username(sample_user_data.username) is False

    user_repository.create(sample_user_data, "hashed_password")

    assert user_repository.exists_by_username(sample_user_data.username) is True


def test_get_all(user_repository):
    """Test getting all users."""
    # Create multiple users
    for i in range(3):
        user_data = UserCreate(
            email=f"user{i}@example.com",
            username=f"user{i}",
            password="password123",
        )
        user_repository.create(user_data, "hashed_password")

    users = user_repository.get_all()
    assert len(users) == 3


def test_update_user(user_repository, sample_user_data):
    """Test updating user information."""
    user = user_repository.create(sample_user_data, "hashed_password")
    user.full_name = "Updated Name"

    updated_user = user_repository.update(user)

    assert updated_user.full_name == "Updated Name"


def test_delete_user(user_repository, sample_user_data):
    """Test deleting a user."""
    user = user_repository.create(sample_user_data, "hashed_password")
    user_id = user.id

    user_repository.delete(user)

    deleted_user = user_repository.get_by_id(user_id)
    assert deleted_user is None
