"""
Integration tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient

# Using fixtures from conftest.py


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
    }


def test_signup_success(client, test_user_data):
    """Test successful user signup."""
    response = client.post("/api/v1/auth/signup", json=test_user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert data["full_name"] == test_user_data["full_name"]
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_signup_duplicate_email(client, test_user_data):
    """Test signup with duplicate email."""
    # Create first user
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Try to create another user with same email
    duplicate_data = test_user_data.copy()
    duplicate_data["username"] = "anotheruser"
    response = client.post("/api/v1/auth/signup", json=duplicate_data)

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_signup_duplicate_username(client, test_user_data):
    """Test signup with duplicate username."""
    # Create first user
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Try to create another user with same username
    duplicate_data = test_user_data.copy()
    duplicate_data["email"] = "another@example.com"
    response = client.post("/api/v1/auth/signup", json=duplicate_data)

    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


def test_signup_invalid_email(client):
    """Test signup with invalid email."""
    invalid_data = {
        "email": "not-an-email",
        "username": "testuser",
        "password": "password123",
    }
    response = client.post("/api/v1/auth/signup", json=invalid_data)

    assert response.status_code == 422


def test_signup_short_password(client):
    """Test signup with too short password."""
    invalid_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "short",
    }
    response = client.post("/api/v1/auth/signup", json=invalid_data)

    assert response.status_code == 422


def test_login_success(client, test_user_data):
    """Test successful login."""
    # First, signup
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Then login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_json_success(client, test_user_data):
    """Test successful login with JSON body."""
    # First, signup
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Then login with JSON
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    response = client.post("/api/v1/auth/login/json", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password."""
    # First, signup
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Try to login with wrong password
    login_data = {
        "username": test_user_data["username"],
        "password": "wrongpassword",
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    login_data = {"username": "nonexistent", "password": "password123"}
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401


def test_get_current_user_info(client, test_user_data):
    """Test getting current user information."""
    # Signup
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Login to get token
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    login_response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]

    # Get current user info
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]


def test_get_current_user_info_without_token(client):
    """Test getting current user info without token."""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_get_current_user_info_invalid_token(client):
    """Test getting current user info with invalid token."""
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_protected_endpoint_without_auth(client):
    """Test accessing protected endpoint without authentication."""
    response = client.get("/api/v1/accounts")

    assert response.status_code == 401


def test_protected_endpoint_with_auth(client, test_user_data):
    """Test accessing protected endpoint with authentication."""
    # Signup
    client.post("/api/v1/auth/signup", json=test_user_data)

    # Login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    login_response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/v1/accounts", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_create_account_with_auth(client, test_user_data):
    """Test creating an account with authentication."""
    # Signup and login
    client.post("/api/v1/auth/signup", json=test_user_data)
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    login_response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]

    # Create account
    account_data = {
        "account_holder": "John Doe",
        "account_type": "savings",
        "initial_balance": 1000.0,
    }
    response = client.post(
        "/api/v1/accounts",
        json=account_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["account_holder"] == "John Doe"
    assert data["balance"] == 1000.0


def test_create_transaction_with_auth(client, test_user_data):
    """Test creating a transaction with authentication."""
    # Signup and login
    client.post("/api/v1/auth/signup", json=test_user_data)
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    login_response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]

    # Create account first
    account_data = {
        "account_holder": "Jane Doe",
        "account_type": "checking",
        "initial_balance": 500.0,
    }
    account_response = client.post(
        "/api/v1/accounts",
        json=account_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    account_id = account_response.json()["id"]

    # Create transaction
    transaction_data = {
        "account_id": account_id,
        "transaction_type": "deposit",
        "amount": 100.0,
        "description": "Test deposit",
    }
    response = client.post(
        "/api/v1/transactions",
        json=transaction_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 100.0
    assert data["transaction_type"] == "deposit"
