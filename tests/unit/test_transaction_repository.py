"""
Unit tests for TransactionRepository.
"""

import pytest
from unittest.mock import Mock
from app.repositories import TransactionRepository
from app.models import Transaction


class TestTransactionRepository:
    """Test suite for TransactionRepository."""

    def test_create_transaction(self, mock_db_session):
        """Test creating a transaction."""
        repo = TransactionRepository(mock_db_session)

        # Setup
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()

        # Execute
        result = repo.create(
            account_id=1,
            transaction_type="deposit",
            amount=100.0,
            description="Test deposit",
        )

        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        assert isinstance(result, Transaction)

    def test_get_by_id_found(self, mock_db_session, mock_transaction):
        """Test getting a transaction by ID when it exists."""
        repo = TransactionRepository(mock_db_session)

        # Setup
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_transaction
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.get_by_id(1)

        # Assert
        assert result == mock_transaction
        mock_db_session.query.assert_called_once_with(Transaction)

    def test_get_by_id_not_found(self, mock_db_session):
        """Test getting a transaction by ID when it doesn't exist."""
        repo = TransactionRepository(mock_db_session)

        # Setup
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.get_by_id(999)

        # Assert
        assert result is None

    def test_get_all(self, mock_db_session):
        """Test getting all transactions with pagination."""
        repo = TransactionRepository(mock_db_session)

        # Setup
        mock_transactions = [Mock(spec=Transaction) for _ in range(5)]
        mock_query = Mock()
        mock_offset = Mock()
        mock_limit = Mock()
        mock_limit.all.return_value = mock_transactions
        mock_offset.limit.return_value = mock_limit
        mock_query.offset.return_value = mock_offset
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.get_all(skip=0, limit=10)

        # Assert
        assert len(result) == 5
        mock_query.offset.assert_called_once_with(0)
        mock_offset.limit.assert_called_once_with(10)

    def test_get_by_account_id(self, mock_db_session):
        """Test getting transactions by account ID."""
        repo = TransactionRepository(mock_db_session)

        # Setup
        mock_transactions = [Mock(spec=Transaction) for _ in range(3)]
        mock_query = Mock()
        mock_filter = Mock()
        mock_offset = Mock()
        mock_limit = Mock()
        mock_limit.all.return_value = mock_transactions
        mock_offset.limit.return_value = mock_limit
        mock_filter.offset.return_value = mock_offset
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.get_by_account_id(1, skip=0, limit=10)

        # Assert
        assert len(result) == 3
        mock_filter.offset.assert_called_once_with(0)
        mock_offset.limit.assert_called_once_with(10)
