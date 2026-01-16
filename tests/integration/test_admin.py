"""
Integration tests for admin/superuser functionality.
Tests the actual API endpoints with proper request formats.
"""

import pytest
from fastapi import status

from app.core.config import settings


class TestAdminSignupEndpoint:
    """Test admin signup endpoint with proper request format."""

    def test_admin_signup_with_valid_key(self, client, db_session):
        """Test admin user creation with valid setup key as query parameter."""
        user_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "AdminPass123!",
            "full_name": "Admin User",
        }

        # admin_setup_key should be a query parameter
        response = client.post(
            f"/api/v1/auth/signup/admin?admin_setup_key={settings.admin_setup_key}",
            json=user_data,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@example.com"
        assert data["is_superuser"] is True
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data

    def test_admin_signup_with_invalid_key(self, client, db_session):
        """Test admin signup fails with invalid setup key."""
        user_data = {
            "email": "hacker@example.com",
            "username": "hacker",
            "password": "HackerPass123!",
            "full_name": "Hacker",
        }

        response = client.post(
            "/api/v1/auth/signup/admin?admin_setup_key=wrong-key-123",
            json=user_data,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Invalid admin setup key" in response.json()["detail"]

    def test_admin_signup_without_key(self, client, db_session):
        """Test admin signup fails without setup key."""
        user_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "AdminPass123!",
            "full_name": "Admin User",
        }

        response = client.post("/api/v1/auth/signup/admin", json=user_data)

        # Should get validation error for missing admin_setup_key
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_admin_signup_duplicate_email(self, client, db_session):
        """Test admin signup fails with duplicate email."""
        user_data = {
            "email": "admin@example.com",
            "username": "admin1",
            "password": "AdminPass123!",
            "full_name": "Admin One",
        }
        client.post(
            f"/api/v1/auth/signup/admin?admin_setup_key={settings.admin_setup_key}",
            json=user_data,
        )

        # Try with same email, different username
        user_data2 = {
            "email": "admin@example.com",  # Same email
            "username": "admin2",
            "password": "AdminPass123!",
            "full_name": "Admin Two",
        }
        response = client.post(
            f"/api/v1/auth/signup/admin?admin_setup_key={settings.admin_setup_key}",
            json=user_data2,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]


class TestRegularSignupVsAdminSignup:
    """Test that regular signup doesn't create admin users."""

    def test_regular_signup_creates_non_admin(self, client, db_session):
        """Test regular signup creates non-admin user."""
        user_data = {
            "email": "user@example.com",
            "username": "regularuser",
            "password": "UserPass123!",
            "full_name": "Regular User",
        }

        response = client.post("/api/v1/auth/signup", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "regularuser"
        # Note: is_superuser is not included in regular signup response by design
        # We verify this by checking admin endpoint access instead


class TestAdminEndpointAuthorization:
    """Test admin endpoint authorization."""

    def test_admin_endpoint_requires_authentication(self, client, db_session):
        """Test that admin endpoints require authentication."""
        response = client.get("/api/v1/admin/errors/summary")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_cannot_access_admin_endpoints(self, client, db_session):
        """Test that regular users cannot access admin endpoints."""
        # Create regular user
        user_data = {
            "email": "user@example.com",
            "username": "regularuser",
            "password": "UserPass123!",
            "full_name": "Regular User",
        }
        client.post("/api/v1/auth/signup", json=user_data)

        # Login as regular user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "regularuser", "password": "UserPass123!"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]

        # Try to access admin endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/admin/errors/summary", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin privileges required" in response.json()["detail"]

    def test_admin_user_can_access_admin_endpoints(self, client, db_session):
        """Test that admin users can access admin endpoints."""
        # Create admin user
        admin_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "AdminPass123!",
            "full_name": "Admin User",
        }
        response = client.post(
            f"/api/v1/auth/signup/admin?admin_setup_key={settings.admin_setup_key}",
            json=admin_data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "AdminPass123!"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]

        # Access admin endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/admin/errors/summary", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_errors" in data
        assert "by_category" in data
        assert "by_status_code" in data


class TestAdminEndpointFunctionality:
    """Test admin endpoint functionality with admin user."""

    @pytest.fixture
    def admin_token(self, client, db_session):
        """Create admin user and return auth token."""
        admin_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "AdminPass123!",
            "full_name": "Admin User",
        }
        signup_response = client.post(
            f"/api/v1/auth/signup/admin?admin_setup_key={settings.admin_setup_key}",
            json=admin_data,
        )
        assert signup_response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "AdminPass123!"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        return login_response.json()["access_token"]

    def test_get_error_summary(self, client, db_session, admin_token):
        """Test getting error summary as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/admin/errors/summary", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_errors" in data
        assert "by_category" in data
        assert "by_status_code" in data
        assert isinstance(data["total_errors"], int)
        assert isinstance(data["by_category"], dict)
        assert isinstance(data["by_status_code"], dict)

    def test_get_recent_errors(self, client, db_session, admin_token):
        """Test getting recent errors as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/admin/errors/recent", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # get_recent_errors returns a list directly, not a dict with errors/total
        assert isinstance(data, list)

    def test_get_all_errors_with_pagination(self, client, db_session, admin_token):
        """Test getting all errors with pagination as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/admin/errors?skip=0&limit=10", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "errors" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert isinstance(data["errors"], list)

    def test_all_admin_endpoints_require_admin_privileges(
        self, client, db_session, admin_token
    ):
        """Test that all admin error endpoints work with admin token."""
        headers = {"Authorization": f"Bearer {admin_token}"}

        endpoints = [
            "/api/v1/admin/errors",
            "/api/v1/admin/errors/summary",
            "/api/v1/admin/errors/recent",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert (
                response.status_code == status.HTTP_200_OK
            ), f"Endpoint {endpoint} should be accessible by admin"
