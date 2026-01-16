"""
Tests for account endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_create_account(client: TestClient, auth_headers: dict):
    """Test creating a new account."""
    response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "John Doe",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["account_holder"] == "John Doe"
    assert data["account_type"] == "checking"
    assert data["balance"] == 1000.0
    assert "account_number" in data
    assert "id" in data


def test_list_accounts(client: TestClient, auth_headers: dict):
    """Test listing accounts."""
    # Create a test account first
    client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Jane Doe",
            "account_type": "savings",
            "initial_balance": 500.0,
        },
        headers=auth_headers,
    )

    response = client.get("/api/v1/accounts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_account(client: TestClient, auth_headers: dict):
    """Test getting a specific account."""
    # Create an account
    create_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Bob Smith",
            "account_type": "checking",
            "initial_balance": 750.0,
        },
        headers=auth_headers,
    )
    account_id = create_response.json()["id"]

    # Get the account
    response = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == account_id
    assert data["account_holder"] == "Bob Smith"


def test_get_nonexistent_account(client: TestClient, auth_headers: dict):
    """Test getting a non-existent account."""
    response = client.get("/api/v1/accounts/99999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_account(client: TestClient, auth_headers: dict):
    """Test deleting an account."""
    # Create an account
    create_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Alice Johnson",
            "account_type": "savings",
            "initial_balance": 200.0,
        },
        headers=auth_headers,
    )
    account_id = create_response.json()["id"]

    # Delete the account
    response = client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert get_response.status_code == 404
