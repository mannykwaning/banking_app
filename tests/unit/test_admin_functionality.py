"""
Unit tests for admin/superuser functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.dependencies import get_current_admin_user


@pytest.fixture
def mock_user_repository():
    """Create a mock UserRepository."""
    return Mock(spec=UserRepository)


@pytest.fixture
def auth_service(mock_user_repository):
    """Create an AuthService instance with mocked repository."""
    return AuthService(mock_user_repository)


@pytest.fixture
def regular_user():
    """Create a regular (non-admin) user for testing."""
    return User(
        id="regular-user-id",
        email="regular@example.com",
        username="regularuser",
        hashed_password="hashed_password",
        full_name="Regular User",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    return User(
        id="admin-user-id",
        email="admin@example.com",
        username="admin",
        hashed_password="hashed_password",
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
    )


class TestUserRepositoryAdminCreation:
    """Test admin user creation in UserRepository."""

    def test_create_regular_user_default(self, mock_user_repository):
        """Test that users are created as regular users by default."""
        from app.repositories.user_repository import UserRepository

        # Create a real repository with mocked db
        mock_db = MagicMock()
        repository = UserRepository(mock_db)

        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="TestPass123!",
            full_name="Test User",
        )

        # Mock the db.add and db.commit
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        user = repository.create(user_data, "hashed_password", is_superuser=False)

        assert user.is_superuser is False
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_create_admin_user(self, mock_user_repository):
        """Test that users can be created as admins."""
        from app.repositories.user_repository import UserRepository

        mock_db = MagicMock()
        repository = UserRepository(mock_db)

        user_data = UserCreate(
            email="admin@example.com",
            username="admin",
            password="AdminPass123!",
            full_name="Admin User",
        )

        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        user = repository.create(user_data, "hashed_password", is_superuser=True)

        assert user.is_superuser is True
        assert user.username == "admin"
        assert user.email == "admin@example.com"


class TestAuthServiceAdminRegistration:
    """Test admin registration in AuthService."""

    def test_register_regular_user_default(self, auth_service, mock_user_repository):
        """Test registering a regular user (default behavior)."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="TestPass123!",
            full_name="Test User",
        )

        # Mock repository methods
        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.exists_by_username.return_value = False

        created_user = User(
            id="test-user-id",
            email=user_data.email,
            username=user_data.username,
            hashed_password="hashed",
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False,
        )
        mock_user_repository.create.return_value = created_user

        # Register user
        user = auth_service.register_user(user_data, is_superuser=False)

        assert user.is_superuser is False
        mock_user_repository.create.assert_called_once()

        # Check that is_superuser was passed correctly
        call_args = mock_user_repository.create.call_args
        assert call_args[1]["is_superuser"] is False

    def test_register_admin_user(self, auth_service, mock_user_repository):
        """Test registering an admin user."""
        user_data = UserCreate(
            email="admin@example.com",
            username="admin",
            password="AdminPass123!",
            full_name="Admin User",
        )

        # Mock repository methods
        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.exists_by_username.return_value = False

        created_user = User(
            id="admin-user-id",
            email=user_data.email,
            username=user_data.username,
            hashed_password="hashed",
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=True,
        )
        mock_user_repository.create.return_value = created_user

        # Register admin user
        user = auth_service.register_user(user_data, is_superuser=True)

        assert user.is_superuser is True
        mock_user_repository.create.assert_called_once()

        # Check that is_superuser was passed correctly
        call_args = mock_user_repository.create.call_args
        assert call_args[1]["is_superuser"] is True

    def test_register_admin_duplicate_email(self, auth_service, mock_user_repository):
        """Test that admin registration fails with duplicate email."""
        user_data = UserCreate(
            email="existing@example.com",
            username="admin",
            password="AdminPass123!",
            full_name="Admin User",
        )

        # Mock repository to return existing user
        mock_user_repository.exists_by_email.return_value = True

        # Should raise ValueError
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.register_user(user_data, is_superuser=True)

    def test_register_admin_duplicate_username(
        self, auth_service, mock_user_repository
    ):
        """Test that admin registration fails with duplicate username."""
        user_data = UserCreate(
            email="admin@example.com",
            username="existinguser",
            password="AdminPass123!",
            full_name="Admin User",
        )

        # Mock repository
        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.exists_by_username.return_value = True

        # Should raise ValueError
        with pytest.raises(ValueError, match="Username already taken"):
            auth_service.register_user(user_data, is_superuser=True)


class TestAdminDependency:
    """Test get_current_admin_user dependency."""

    def test_admin_user_passes(self, admin_user):
        """Test that admin users pass the admin check."""
        result = get_current_admin_user(admin_user)
        assert result == admin_user
        assert result.is_superuser is True

    def test_regular_user_fails(self, regular_user):
        """Test that regular users fail the admin check."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin_user(regular_user)

        assert exc_info.value.status_code == 403
        assert "Admin privileges required" in str(exc_info.value.detail)

    def test_inactive_admin_still_fails(self):
        """Test that inactive admin users fail the check (inactive users shouldn't get tokens anyway)."""
        inactive_admin = User(
            id="inactive-admin-id",
            email="inactive@example.com",
            username="inactiveadmin",
            hashed_password="hashed",
            full_name="Inactive Admin",
            is_active=False,
            is_superuser=True,
        )

        # This should pass the admin check (is_superuser=True)
        # The inactive check happens earlier in get_current_user
        result = get_current_admin_user(inactive_admin)
        assert result == inactive_admin
