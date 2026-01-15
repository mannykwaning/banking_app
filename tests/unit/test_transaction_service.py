"""
Unit tests for TransactionService.
"""

import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from app.services import TransactionService
from app.models import Transaction


class TestTransactionService:
    """Test suite for TransactionService."""

    def test_create_deposit_transaction(
        self, mock_db_session, mock_account, mock_transaction
    ):
        """Test creating a deposit transaction."""
        service = TransactionService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=mock_account)
        service.account_repository.update_balance = Mock()
        service.repository.create = Mock(return_value=mock_transaction)

        # Execute
        result = service.create_transaction(1, "deposit", 100.0, "Test deposit")

        # Assert
        assert result == mock_transaction
        service.account_repository.update_balance.assert_called_once()
        service.repository.create.assert_called_once()

    def test_create_withdrawal_transaction(
        self, mock_db_session, mock_account, mock_transaction
    ):
        """Test creating a withdrawal transaction."""
        service = TransactionService(mock_db_session)
        mock_account.balance = 500.0
        service.account_repository.get_by_id = Mock(return_value=mock_account)
        service.account_repository.update_balance = Mock()
        service.repository.create = Mock(return_value=mock_transaction)

        # Execute
        result = service.create_transaction(1, "withdrawal", 100.0, "Test withdrawal")

        # Assert
        assert result == mock_transaction
        service.account_repository.update_balance.assert_called_once()

    def test_create_transaction_account_not_found(self, mock_db_session):
        """Test creating transaction for non-existent account."""
        service = TransactionService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_transaction(999, "deposit", 100.0)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    def test_create_transaction_invalid_type(self, mock_db_session, mock_account):
        """Test creating transaction with invalid type."""
        service = TransactionService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=mock_account)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_transaction(1, "invalid_type", 100.0)

        assert exc_info.value.status_code == 400
        assert "type" in str(exc_info.value.detail).lower()

    def test_create_transaction_negative_amount(self, mock_db_session, mock_account):
        """Test creating transaction with negative amount."""
        service = TransactionService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=mock_account)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_transaction(1, "deposit", -100.0)

        assert exc_info.value.status_code == 400
        assert "positive" in str(exc_info.value.detail).lower()

    def test_create_transaction_zero_amount(self, mock_db_session, mock_account):
        """Test creating transaction with zero amount."""
        service = TransactionService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=mock_account)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_transaction(1, "deposit", 0.0)

        assert exc_info.value.status_code == 400

    def test_create_withdrawal_insufficient_balance(
        self, mock_db_session, mock_account
    ):
        """Test withdrawal with insufficient balance."""
        service = TransactionService(mock_db_session)
        mock_account.balance = 50.0
        service.account_repository.get_by_id = Mock(return_value=mock_account)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_transaction(1, "withdrawal", 100.0)

        assert exc_info.value.status_code == 400
        assert "insufficient" in str(exc_info.value.detail).lower()

    def test_get_transaction_by_id_found(self, mock_db_session, mock_transaction):
        """Test getting transaction by ID when it exists."""
        service = TransactionService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_transaction)

        # Execute
        result = service.get_transaction_by_id(1)

        # Assert
        assert result == mock_transaction

    def test_get_transaction_by_id_not_found(self, mock_db_session):
        """Test getting transaction by ID when it doesn't exist."""
        service = TransactionService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_transaction_by_id(999)

        assert exc_info.value.status_code == 404

    def test_get_all_transactions(self, mock_db_session):
        """Test getting all transactions."""
        service = TransactionService(mock_db_session)
        mock_transactions = [Mock(spec=Transaction) for _ in range(3)]
        service.repository.get_all = Mock(return_value=mock_transactions)

        # Execute
        result = service.get_all_transactions(skip=0, limit=10)

        # Assert
        assert len(result) == 3

    def test_get_transactions_by_account(self, mock_db_session, mock_account):
        """Test getting transactions for a specific account."""
        service = TransactionService(mock_db_session)
        mock_transactions = [Mock(spec=Transaction) for _ in range(2)]
        service.account_repository.get_by_id = Mock(return_value=mock_account)
        service.repository.get_by_account_id = Mock(return_value=mock_transactions)

        # Execute
        result = service.get_transactions_by_account(1, skip=0, limit=10)

        # Assert
        assert len(result) == 2
        service.repository.get_by_account_id.assert_called_once_with(
            1, skip=0, limit=10
        )

    def test_get_transactions_by_account_not_found(self, mock_db_session):
        """Test getting transactions for non-existent account."""
        service = TransactionService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_transactions_by_account(999)

        assert exc_info.value.status_code == 404
