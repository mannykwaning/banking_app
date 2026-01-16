"""
Integration tests for transfer functionality.
Tests the secure money transfer system with ACID compliance.
"""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import Account, Transaction, User
from app.services.transfer_service import TransferService
from app.core.config import settings


class TestInternalTransfers:
    """Test internal transfer functionality."""

    def test_successful_internal_transfer(
        self, db: Session, sample_accounts: tuple[Account, Account]
    ):
        """Test a successful internal transfer between two accounts."""
        source_account, dest_account = sample_accounts
        transfer_service = TransferService(db)

        initial_source_balance = source_account.balance
        initial_dest_balance = dest_account.balance
        transfer_amount = 100.0

        # Execute transfer
        result = transfer_service.create_internal_transfer(
            source_account_id=source_account.id,
            destination_account_id=dest_account.id,
            amount=transfer_amount,
            description="Test transfer",
        )

        # Verify result structure
        assert result["transfer_type"] == "internal"
        assert result["status"] == "completed"
        assert result["amount"] == transfer_amount
        assert result["source_account_id"] == source_account.id
        assert result["destination_account_id"] == dest_account.id
        assert "transfer_id" in result
        assert result["transfer_id"].startswith("TXN-")

        # Refresh accounts and verify balances
        db.refresh(source_account)
        db.refresh(dest_account)

        assert source_account.balance == initial_source_balance - transfer_amount
        assert dest_account.balance == initial_dest_balance + transfer_amount

        # Verify transactions were created
        source_txn = (
            db.query(Transaction)
            .filter(Transaction.id == result["source_transaction_id"])
            .first()
        )
        dest_txn = (
            db.query(Transaction)
            .filter(Transaction.id == result["destination_transaction_id"])
            .first()
        )

        assert source_txn is not None
        assert source_txn.transaction_type == "transfer_out"
        assert source_txn.amount == transfer_amount
        assert source_txn.status == "completed"
        assert source_txn.reference_id == result["transfer_id"]

        assert dest_txn is not None
        assert dest_txn.transaction_type == "transfer_in"
        assert dest_txn.amount == transfer_amount
        assert dest_txn.status == "completed"
        assert dest_txn.reference_id == result["transfer_id"]

    def test_insufficient_balance(
        self, db: Session, sample_accounts: tuple[Account, Account]
    ):
        """Test transfer fails with insufficient balance."""
        source_account, dest_account = sample_accounts
        transfer_service = TransferService(db)

        # Try to transfer more than available
        with pytest.raises(Exception) as exc_info:
            transfer_service.create_internal_transfer(
                source_account_id=source_account.id,
                destination_account_id=dest_account.id,
                amount=source_account.balance + 1000.0,
                description="Should fail",
            )

        assert "Insufficient balance" in str(exc_info.value)

    def test_same_account_transfer_fails(
        self, db: Session, sample_accounts: tuple[Account, Account]
    ):
        """Test transfer to same account is rejected."""
        source_account, _ = sample_accounts
        transfer_service = TransferService(db)

        with pytest.raises(Exception) as exc_info:
            transfer_service.create_internal_transfer(
                source_account_id=source_account.id,
                destination_account_id=source_account.id,
                amount=100.0,
            )

        assert "must be different" in str(exc_info.value).lower()

    def test_transfer_exceeds_single_limit(
        self, db: Session, sample_accounts: tuple[Account, Account]
    ):
        """Test transfer exceeding single transaction limit is rejected."""
        source_account, dest_account = sample_accounts
        transfer_service = TransferService(db)

        # Try to transfer more than max_transfer_amount
        with pytest.raises(Exception) as exc_info:
            transfer_service.create_internal_transfer(
                source_account_id=source_account.id,
                destination_account_id=dest_account.id,
                amount=settings.max_transfer_amount + 1000.0,
            )

        assert "exceeds maximum limit" in str(exc_info.value)

    def test_transfer_below_minimum(
        self, db: Session, sample_accounts: tuple[Account, Account]
    ):
        """Test transfer below minimum amount is rejected."""
        source_account, dest_account = sample_accounts
        transfer_service = TransferService(db)

        with pytest.raises(Exception) as exc_info:
            transfer_service.create_internal_transfer(
                source_account_id=source_account.id,
                destination_account_id=dest_account.id,
                amount=settings.min_transfer_amount - 0.001,
            )

        assert "at least" in str(exc_info.value)

    def test_account_not_found(self, db: Session):
        """Test transfer fails when account doesn't exist."""
        transfer_service = TransferService(db)

        with pytest.raises(Exception) as exc_info:
            transfer_service.create_internal_transfer(
                source_account_id=99999, destination_account_id=99998, amount=100.0
            )

        assert "not found" in str(exc_info.value).lower()


class TestExternalTransfers:
    """Test external transfer functionality."""

    def test_successful_external_transfer(
        self, db: Session, sample_accounts: tuple[Account, Account]
    ):
        """Test a successful external transfer."""
        source_account, _ = sample_accounts
        transfer_service = TransferService(db)

        initial_balance = source_account.balance
        transfer_amount = 500.0

        # Execute external transfer
        result = transfer_service.create_external_transfer(
            source_account_id=source_account.id,
            external_account_number="1234567890",
            external_bank_name="External Bank",
            external_routing_number="123456789",
            amount=transfer_amount,
            description="External transfer test",
        )

        # Verify result
        assert result["transfer_type"] == "external"
        assert result["status"] == "pending"  # External transfers start as pending
        assert result["amount"] == transfer_amount
        assert result["external_account_number"] == "1234567890"
        assert result["external_bank_name"] == "External Bank"
        assert result["transfer_id"].startswith("EXT-")

        # Verify balance was debited
        db.refresh(source_account)
        assert source_account.balance == initial_balance - transfer_amount

        # Verify transaction
        source_txn = (
            db.query(Transaction)
            .filter(Transaction.id == result["source_transaction_id"])
            .first()
        )

        assert source_txn is not None
        assert source_txn.transaction_type == "transfer_out"
        assert source_txn.transfer_type == "external"
        assert source_txn.external_account_number == "1234567890"

    def test_external_transfer_exceeds_limit(
        self, db: Session, sample_accounts: tuple[Account, Account]
    ):
        """Test external transfer exceeding limit is rejected."""
        source_account, _ = sample_accounts
        transfer_service = TransferService(db)

        # Try to transfer more than max_external_transfer_amount
        with pytest.raises(Exception) as exc_info:
            transfer_service.create_external_transfer(
                source_account_id=source_account.id,
                external_account_number="1234567890",
                external_bank_name="External Bank",
                external_routing_number="123456789",
                amount=settings.max_external_transfer_amount + 1000.0,
            )

        assert "exceeds maximum limit" in str(exc_info.value)


class TestTransferRetrieval:
    """Test transfer retrieval functionality."""

    def test_get_transfer_by_reference_id(
        self, db: Session, sample_accounts: tuple[Account, Account]
    ):
        """Test retrieving transfer details by reference ID."""
        source_account, dest_account = sample_accounts
        transfer_service = TransferService(db)

        # Create a transfer
        result = transfer_service.create_internal_transfer(
            source_account_id=source_account.id,
            destination_account_id=dest_account.id,
            amount=250.0,
            description="Test transfer",
        )

        reference_id = result["transfer_id"]

        # Retrieve transfer
        retrieved = transfer_service.get_transfer_by_reference_id(reference_id)

        assert retrieved["transfer_id"] == reference_id
        assert retrieved["amount"] == 250.0
        assert retrieved["status"] == "completed"
        assert retrieved["transfer_type"] == "internal"

    def test_get_nonexistent_transfer(self, db: Session):
        """Test retrieving non-existent transfer raises error."""
        transfer_service = TransferService(db)

        with pytest.raises(Exception) as exc_info:
            transfer_service.get_transfer_by_reference_id("TXN-NONEXISTENT")

        assert "not found" in str(exc_info.value).lower()


class TestTransferEndpoints:
    """Test transfer API endpoints."""

    def test_create_internal_transfer_endpoint(
        self, client, auth_headers, sample_accounts: tuple[Account, Account]
    ):
        """Test internal transfer endpoint."""
        source_account, dest_account = sample_accounts

        transfer_data = {
            "source_account_id": source_account.id,
            "destination_account_id": dest_account.id,
            "amount": 100.0,
            "description": "API test transfer",
        }

        response = client.post(
            "/api/v1/transfers/internal", json=transfer_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transfer_type"] == "internal"
        assert data["status"] == "completed"
        assert data["amount"] == 100.0

    def test_create_external_transfer_endpoint(
        self, client, auth_headers, sample_accounts: tuple[Account, Account]
    ):
        """Test external transfer endpoint."""
        source_account, _ = sample_accounts

        transfer_data = {
            "source_account_id": source_account.id,
            "external_account_number": "9876543210",
            "external_bank_name": "Test Bank",
            "external_routing_number": "987654321",
            "amount": 500.0,
            "description": "External API test",
        }

        response = client.post(
            "/api/v1/transfers/external", json=transfer_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transfer_type"] == "external"
        assert data["status"] == "pending"
        assert data["amount"] == 500.0

    def test_get_transfer_endpoint(
        self,
        client,
        auth_headers,
        db: Session,
        sample_accounts: tuple[Account, Account],
    ):
        """Test get transfer details endpoint."""
        source_account, dest_account = sample_accounts
        transfer_service = TransferService(db)

        # Create a transfer
        result = transfer_service.create_internal_transfer(
            source_account_id=source_account.id,
            destination_account_id=dest_account.id,
            amount=150.0,
        )

        reference_id = result["transfer_id"]

        # Retrieve via API
        response = client.get(f"/api/v1/transfers/{reference_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["transfer_id"] == reference_id
        assert data["amount"] == 150.0

    def test_unauthorized_transfer_request(
        self, client, sample_accounts: tuple[Account, Account]
    ):
        """Test transfer request without authentication fails."""
        source_account, dest_account = sample_accounts

        transfer_data = {
            "source_account_id": source_account.id,
            "destination_account_id": dest_account.id,
            "amount": 100.0,
        }

        response = client.post("/api/v1/transfers/internal", json=transfer_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestACIDCompliance:
    """Test ACID compliance of transfers."""

    def test_rollback_on_failure(
        self, db: Session, sample_accounts: tuple[Account, Account], monkeypatch
    ):
        """Test that failed transfers roll back all changes."""
        source_account, dest_account = sample_accounts
        transfer_service = TransferService(db)

        initial_source_balance = source_account.balance
        initial_dest_balance = dest_account.balance

        # Mock a failure during transaction
        def mock_commit_failure(*args, **kwargs):
            raise Exception("Simulated database error")

        monkeypatch.setattr(db, "commit", mock_commit_failure)

        # Try to transfer
        with pytest.raises(Exception):
            transfer_service.create_internal_transfer(
                source_account_id=source_account.id,
                destination_account_id=dest_account.id,
                amount=100.0,
            )

        # Verify balances unchanged
        db.rollback()  # Clean up
        db.refresh(source_account)
        db.refresh(dest_account)

        assert source_account.balance == initial_source_balance
        assert dest_account.balance == initial_dest_balance
