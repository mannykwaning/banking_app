"""
Integration tests for card endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_issue_card(client: TestClient, auth_headers: dict):
    """Test issuing a new card for an account."""
    # First create an account
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "John Doe",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    assert account_response.status_code == 201
    account_id = account_response.json()["id"]

    # Issue a card
    response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "JOHN DOE",
            "card_type": "debit",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["account_id"] == account_id
    assert data["cardholder_name"] == "JOHN DOE"
    assert data["card_type"] == "debit"
    assert data["status"] == "active"
    assert len(data["card_number_last4"]) == 4
    assert "id" in data
    assert "expiry_month" in data
    assert "expiry_year" in data
    assert 1 <= data["expiry_month"] <= 12
    assert data["expiry_year"] >= 2026


def test_issue_card_invalid_account(client: TestClient, auth_headers: dict):
    """Test issuing a card for non-existent account."""
    response = client.post(
        "/api/v1/cards",
        json={
            "account_id": 99999,
            "cardholder_name": "JOHN DOE",
            "card_type": "debit",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_issue_multiple_cards(client: TestClient, auth_headers: dict):
    """Test issuing multiple cards for the same account."""
    # Create an account
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Jane Doe",
            "account_type": "savings",
            "initial_balance": 2000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    # Issue first card (debit)
    response1 = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "JANE DOE",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    assert response1.status_code == 201

    # Issue second card (credit)
    response2 = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "JANE DOE",
            "card_type": "credit",
        },
        headers=auth_headers,
    )
    assert response2.status_code == 201

    # Verify both cards exist
    cards_response = client.get(
        f"/api/v1/cards/account/{account_id}",
        headers=auth_headers,
    )
    assert cards_response.status_code == 200
    cards = cards_response.json()
    assert len(cards) == 2


def test_issue_card_max_limit(client: TestClient, auth_headers: dict):
    """Test that account cannot have more than 5 active cards."""
    # Create an account
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Bob Smith",
            "account_type": "checking",
            "initial_balance": 5000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    # Issue 5 cards (should all succeed)
    for i in range(5):
        response = client.post(
            "/api/v1/cards",
            json={
                "account_id": account_id,
                "cardholder_name": "BOB SMITH",
                "card_type": "debit",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201

    # Try to issue 6th card (should fail)
    response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "BOB SMITH",
            "card_type": "credit",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "maximum" in response.json()["detail"].lower()


def test_get_card(client: TestClient, auth_headers: dict):
    """Test getting a specific card by ID."""
    # Create account and card
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Alice",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    card_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "ALICE",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # Get the card
    response = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == card_id
    assert data["account_id"] == account_id
    assert "encrypted_pan" not in data  # Sensitive data should not be in basic response
    assert "encrypted_cvv" not in data


def test_get_card_not_found(client: TestClient, auth_headers: dict):
    """Test getting non-existent card."""
    response = client.get("/api/v1/cards/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_cards_by_account(client: TestClient, auth_headers: dict):
    """Test getting all cards for an account."""
    # Create account
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Charlie",
            "account_type": "savings",
            "initial_balance": 1500.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    # Issue 3 cards
    for i in range(3):
        client.post(
            "/api/v1/cards",
            json={
                "account_id": account_id,
                "cardholder_name": "CHARLIE",
                "card_type": "debit",
            },
            headers=auth_headers,
        )

    # Get all cards
    response = client.get(f"/api/v1/cards/account/{account_id}", headers=auth_headers)
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) == 3
    for card in cards:
        assert card["account_id"] == account_id


def test_get_masked_card_number(client: TestClient, auth_headers: dict):
    """Test getting masked card number."""
    # Create account and card
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "David",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    card_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "DAVID",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]
    last4 = card_response.json()["card_number_last4"]

    # Get masked card number
    response = client.get(f"/api/v1/cards/{card_id}/masked", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["masked_number"] == f"****-****-****-{last4}"


def test_get_card_details(client: TestClient, auth_headers: dict):
    """Test getting full card details with sensitive data."""
    # Create account and card
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Eve",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    card_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "EVE",
            "card_type": "credit",
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # Get full card details
    response = client.get(f"/api/v1/cards/{card_id}/details", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "card_number" in data
    assert "cvv" in data
    assert len(data["card_number"]) == 16
    assert len(data["cvv"]) == 3
    assert data["card_number"].isdigit()
    assert data["cvv"].isdigit()


def test_update_card_status(client: TestClient, auth_headers: dict):
    """Test updating card status."""
    # Create account and card
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Frank",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    card_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "FRANK",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # Update status to inactive
    response = client.patch(
        f"/api/v1/cards/{card_id}/status",
        json={"status": "inactive"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "inactive"

    # Verify status was updated
    get_response = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
    assert get_response.json()["status"] == "inactive"


def test_block_card(client: TestClient, auth_headers: dict):
    """Test blocking a card."""
    # Create account and card
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Grace",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    card_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "GRACE",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # Block the card
    response = client.post(f"/api/v1/cards/{card_id}/block", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"


def test_activate_card(client: TestClient, auth_headers: dict):
    """Test activating a card."""
    # Create account and card
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Henry",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    card_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "HENRY",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # First block it
    client.post(f"/api/v1/cards/{card_id}/block", headers=auth_headers)

    # Then activate it
    response = client.post(f"/api/v1/cards/{card_id}/activate", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"


def test_list_all_cards(client: TestClient, auth_headers: dict):
    """Test listing all cards with pagination."""
    # Create accounts and cards
    for i in range(3):
        account_response = client.post(
            "/api/v1/accounts",
            json={
                "account_holder": f"User{i}",
                "account_type": "checking",
                "initial_balance": 1000.0,
            },
            headers=auth_headers,
        )
        account_id = account_response.json()["id"]

        client.post(
            "/api/v1/cards",
            json={
                "account_id": account_id,
                "cardholder_name": f"USER{i}",
                "card_type": "debit",
            },
            headers=auth_headers,
        )

    # List all cards
    response = client.get("/api/v1/cards", headers=auth_headers)
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) >= 3


def test_card_encryption(client: TestClient, auth_headers: dict):
    """Test that card data is properly encrypted."""
    # Create account and card
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Iris",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    card_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "IRIS",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # Get card details with decrypted data
    details_response = client.get(
        f"/api/v1/cards/{card_id}/details", headers=auth_headers
    )
    assert details_response.status_code == 200
    details = details_response.json()

    # Verify decrypted data format
    card_number = details["card_number"]
    cvv = details["cvv"]

    assert len(card_number) == 16
    assert card_number.isdigit()
    assert card_number.startswith("400000")  # Test BIN
    assert len(cvv) == 3
    assert cvv.isdigit()

    # Verify last 4 digits match
    assert card_number.endswith(details["card_number_last4"])


def test_issue_card_with_invalid_cardholder_name(
    client: TestClient, auth_headers: dict
):
    """Test issuing card with invalid cardholder name."""
    # Create account
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Jack",
            "account_type": "checking",
            "initial_balance": 1000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    # Try to issue card with empty name
    response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422  # Validation error


def test_issue_different_card_types(client: TestClient, auth_headers: dict):
    """Test issuing different types of cards."""
    # Create account
    account_response = client.post(
        "/api/v1/accounts",
        json={
            "account_holder": "Kate",
            "account_type": "checking",
            "initial_balance": 3000.0,
        },
        headers=auth_headers,
    )
    account_id = account_response.json()["id"]

    # Issue debit card
    debit_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "KATE",
            "card_type": "debit",
        },
        headers=auth_headers,
    )
    assert debit_response.status_code == 201
    assert debit_response.json()["card_type"] == "debit"

    # Issue credit card
    credit_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "KATE",
            "card_type": "credit",
        },
        headers=auth_headers,
    )
    assert credit_response.status_code == 201
    assert credit_response.json()["card_type"] == "credit"

    # Issue prepaid card
    prepaid_response = client.post(
        "/api/v1/cards",
        json={
            "account_id": account_id,
            "cardholder_name": "KATE",
            "card_type": "prepaid",
        },
        headers=auth_headers,
    )
    assert prepaid_response.status_code == 201
    assert prepaid_response.json()["card_type"] == "prepaid"
