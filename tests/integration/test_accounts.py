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


def test_generate_account_statement(client: TestClient, auth_headers: dict):
    """Test generating an account statement."""
    # Create an account
    create_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Statement Test User",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = create_response.json()["id"]

    # Create some transactions
    client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "deposit",
            "amount": 500.0,
            "description": "Salary deposit",
        },
        headers=auth_headers,
    )

    client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "withdrawal",
            "amount": 100.0,
            "description": "ATM withdrawal",
        },
        headers=auth_headers,
    )

    # Generate statement
    response = client.get(
        f"/api/v1/accounts/{account_id}/statement", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify statement structure
    assert data["account_id"] == account_id
    assert data["account_holder"] == "Statement Test User"
    assert data["account_type"] == "checking"
    assert "current_balance" in data
    assert "statement_period" in data
    assert "start_date" in data["statement_period"]
    assert "end_date" in data["statement_period"]
    assert "total_deposits" in data
    assert "total_withdrawals" in data
    assert "total_transfers_in" in data
    assert "total_transfers_out" in data
    assert "transaction_count" in data
    assert "transactions" in data
    assert isinstance(data["transactions"], list)

    # Verify transaction summary (initial balance is a deposit, plus 2 manual transactions)
    assert data["transaction_count"] >= 2
    assert data["total_deposits"] >= 500.0
    assert data["total_withdrawals"] >= 100.0


def test_generate_account_statement_with_date_range(
    client: TestClient, auth_headers: dict
):
    """Test generating an account statement with custom date range."""
    from datetime import datetime, timedelta

    # Create an account
    create_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Date Range Test",
            "account_type": "savings",
            "initial_balance": 2000.0,
        },
        headers=auth_headers,
    )
    account_id = create_response.json()["id"]

    # Add a transaction
    client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "transaction_type": "deposit",
            "amount": 300.0,
            "description": "Test deposit",
        },
        headers=auth_headers,
    )

    # Generate statement with custom date range (last 7 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    response = client.get(
        f"/api/v1/accounts/{account_id}/statement",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == account_id
    assert "statement_period" in data


def test_generate_account_statement_nonexistent_account(
    client: TestClient, auth_headers: dict
):
    """Test generating statement for non-existent account."""
    response = client.get("/api/v1/accounts/99999/statement", headers=auth_headers)
    assert response.status_code == 404


def test_generate_account_statement_no_transactions(
    client: TestClient, auth_headers: dict
):
    """Test generating statement for account with no transactions."""
    # Create an account with zero balance (no initial deposit transaction)
    create_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "No Transactions User",
            "account_type": "checking",
            "initial_balance": 0.0,
        },
        headers=auth_headers,
    )
    account_id = create_response.json()["id"]

    # Generate statement
    response = client.get(
        f"/api/v1/accounts/{account_id}/statement", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == account_id
    assert data["current_balance"] == 0.0
    # Note: transaction_count might be > 0 if initial balance created a transaction
    assert "transactions" in data
    assert isinstance(data["transactions"], list)
