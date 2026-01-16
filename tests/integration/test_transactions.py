"""
Tests for transaction endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_create_deposit_transaction(client: TestClient, auth_headers: dict):
    """Test creating a deposit transaction."""
    # Create an account first
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "John Doe",
            "account_type": "checking",
            "initial_balance": 100.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    # Create a deposit transaction
    response = client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "deposit",
            "amount": 50.0,
            "description": "Test deposit",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["account_id"] == account_id
    assert data["transaction_type"] == "deposit"
    assert data["amount"] == 50.0
    assert data["description"] == "Test deposit"

    # Verify account balance increased
    account = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers).json()
    assert account["balance"] == 150.0


def test_create_withdrawal_transaction(client: TestClient, auth_headers: dict):
    """Test creating a withdrawal transaction."""
    # Create an account
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Jane Doe",
            "account_type": "savings",
            "initial_balance": 200.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    # Create a withdrawal transaction
    response = client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "withdrawal",
            "amount": 75.0,
            "description": "Test withdrawal",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["transaction_type"] == "withdrawal"
    assert data["amount"] == 75.0

    # Verify account balance decreased
    account = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers).json()
    assert account["balance"] == 125.0


def test_insufficient_balance_withdrawal(client: TestClient, auth_headers: dict):
    """Test withdrawal with insufficient balance."""
    # Create an account with low balance
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Poor User",
            "account_type": "checking",
            "initial_balance": 10.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    # Try to withdraw more than available
    response = client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "withdrawal",
            "amount": 100.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "Insufficient balance" in response.json()["detail"]


def test_list_transactions(client: TestClient, auth_headers: dict):
    """Test listing all transactions."""
    # Create account and transaction
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Test User",
            "account_type": "checking",
            "initial_balance": 500.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "deposit",
            "amount": 100.0,
        },
        headers=auth_headers,
    )

    # List transactions
    response = client.get("/api/v1/transactions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_transaction(client: TestClient, auth_headers: dict):
    """Test getting a specific transaction."""
    # Create account and transaction
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Test User",
            "account_type": "savings",
            "initial_balance": 300.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    transaction_response = client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "deposit",
            "amount": 25.0,
        },
        headers=auth_headers,
    )
    transaction_id = transaction_response.json()["id"]

    # Get the transaction
    response = client.get(
        f"/api/v1/transactions/{transaction_id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction_id
    assert data["amount"] == 25.0
