"""
Unit tests for AuthService.
"""

import pytest
from unittest.mock import Mock
from datetime import timedelta

from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User


@pytest.fixture
def mock_user_repository():
    """Create a mock UserRepository."""
    return Mock(spec=UserRepository)


@pytest.fixture
def auth_service(mock_user_repository):
    """Create an AuthService instance with mocked repository."""
    return AuthService(mock_user_repository)


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = User(
        id="test-user-id",
        email="test@example.com",
        username="testuser",
        hashed_password=AuthService.get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    return user


def test_password_hashing(auth_service):
    """Test password hashing and verification."""
    password = "mySecurePassword123"
    hashed = AuthService.get_password_hash(password)

    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("wrongpassword", hashed) is False


def test_authenticate_user_success(auth_service, mock_user_repository, sample_user):
    """Test successful user authentication."""
    mock_user_repository.get_by_username.return_value = sample_user

    authenticated_user = auth_service.authenticate_user("testuser", "testpassword123")

    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"
    mock_user_repository.get_by_username.assert_called_once_with("testuser")


def test_authenticate_user_wrong_password(
    auth_service, mock_user_repository, sample_user
):
    """Test authentication with wrong password."""
    mock_user_repository.get_by_username.return_value = sample_user

    authenticated_user = auth_service.authenticate_user("testuser", "wrongpassword")

    assert authenticated_user is None


def test_authenticate_user_not_found(auth_service, mock_user_repository):
    """Test authentication with non-existent user."""
    mock_user_repository.get_by_username.return_value = None

    authenticated_user = auth_service.authenticate_user("nonexistent", "password")

    assert authenticated_user is None


def test_create_and_decode_access_token(auth_service):
    """Test creating and decoding JWT access token."""
    data = {"sub": "testuser", "user_id": "test-user-id"}
    token = AuthService.create_access_token(data)

    assert token is not None
    assert isinstance(token, str)

    # Decode token
    token_data = AuthService.decode_access_token(token)

    assert token_data is not None
    assert token_data.username == "testuser"
    assert token_data.user_id == "test-user-id"


def test_decode_invalid_token(auth_service):
    """Test decoding invalid token."""
    token_data = AuthService.decode_access_token("invalid_token_string")
    assert token_data is None


def test_register_user_success(auth_service, mock_user_repository, sample_user):
    """Test successful user registration."""
    user_data = UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="password123",
        full_name="New User",
    )

    mock_user_repository.exists_by_email.return_value = False
    mock_user_repository.exists_by_username.return_value = False
    mock_user_repository.create.return_value = sample_user

    registered_user = auth_service.register_user(user_data)

    assert registered_user is not None
    mock_user_repository.exists_by_email.assert_called_once_with("newuser@example.com")
    mock_user_repository.exists_by_username.assert_called_once_with("newuser")
    mock_user_repository.create.assert_called_once()


def test_register_user_email_exists(auth_service, mock_user_repository):
    """Test registration with existing email."""
    user_data = UserCreate(
        email="existing@example.com",
        username="newuser",
        password="password123",
    )

    mock_user_repository.exists_by_email.return_value = True

    with pytest.raises(ValueError, match="Email already registered"):
        auth_service.register_user(user_data)


def test_register_user_username_exists(auth_service, mock_user_repository):
    """Test registration with existing username."""
    user_data = UserCreate(
        email="newuser@example.com",
        username="existinguser",
        password="password123",
    )

    mock_user_repository.exists_by_email.return_value = False
    mock_user_repository.exists_by_username.return_value = True

    with pytest.raises(ValueError, match="Username already taken"):
        auth_service.register_user(user_data)


def test_login_success(auth_service, mock_user_repository, sample_user):
    """Test successful login."""
    mock_user_repository.get_by_username.return_value = sample_user

    token = auth_service.login("testuser", "testpassword123")

    assert token is not None
    assert token.access_token is not None
    assert token.token_type == "bearer"


def test_login_wrong_credentials(auth_service, mock_user_repository):
    """Test login with wrong credentials."""
    mock_user_repository.get_by_username.return_value = None

    with pytest.raises(ValueError, match="Incorrect username or password"):
        auth_service.login("wronguser", "wrongpassword")


def test_login_inactive_user(auth_service, mock_user_repository, sample_user):
    """Test login with inactive user."""
    sample_user.is_active = False
    mock_user_repository.get_by_username.return_value = sample_user

    with pytest.raises(ValueError, match="User account is inactive"):
        auth_service.login("testuser", "testpassword123")
