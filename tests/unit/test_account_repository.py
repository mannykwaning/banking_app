"""
Unit tests for AccountRepository.
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.repositories import AccountRepository
from app.models import Account


class TestAccountRepository:
    """Test suite for AccountRepository."""

    def test_create_account(self, mock_db_session):
        """Test creating an account."""
        repo = AccountRepository(mock_db_session)

        # Setup
        mock_account = Mock(spec=Account)
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()

        # Execute
        result = repo.create(
            account_number="1234567890",
            account_holder="John Doe",
            account_type="checking",
            balance=100.0,
        )

        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        assert isinstance(result, Account)

    def test_get_by_id_found(self, mock_db_session, mock_account):
        """Test getting an account by ID when it exists."""
        repo = AccountRepository(mock_db_session)

        # Setup
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_account
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.get_by_id(1)

        # Assert
        assert result == mock_account
        mock_db_session.query.assert_called_once_with(Account)

    def test_get_by_id_not_found(self, mock_db_session):
        """Test getting an account by ID when it doesn't exist."""
        repo = AccountRepository(mock_db_session)

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

    def test_get_by_account_number(self, mock_db_session, mock_account):
        """Test getting an account by account number."""
        repo = AccountRepository(mock_db_session)

        # Setup
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_account
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.get_by_account_number("1234567890")

        # Assert
        assert result == mock_account

    def test_get_all(self, mock_db_session):
        """Test getting all accounts with pagination."""
        repo = AccountRepository(mock_db_session)

        # Setup
        mock_accounts = [Mock(spec=Account) for _ in range(5)]
        mock_query = Mock()
        mock_offset = Mock()
        mock_limit = Mock()
        mock_limit.all.return_value = mock_accounts
        mock_offset.limit.return_value = mock_limit
        mock_query.offset.return_value = mock_offset
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.get_all(skip=0, limit=10)

        # Assert
        assert len(result) == 5
        mock_query.offset.assert_called_once_with(0)
        mock_offset.limit.assert_called_once_with(10)

    def test_update_balance(self, mock_db_session, mock_account):
        """Test updating account balance."""
        repo = AccountRepository(mock_db_session)

        # Setup
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()

        # Execute
        result = repo.update_balance(mock_account, 500.0)

        # Assert
        assert mock_account.balance == 500.0
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_account)

    def test_delete_account(self, mock_db_session, mock_account):
        """Test deleting an account."""
        repo = AccountRepository(mock_db_session)

        # Setup
        mock_db_session.delete = Mock()
        mock_db_session.commit = Mock()

        # Execute
        repo.delete(mock_account)

        # Assert
        mock_db_session.delete.assert_called_once_with(mock_account)
        mock_db_session.commit.assert_called_once()

    def test_exists_by_account_number_true(self, mock_db_session, mock_account):
        """Test checking if account exists when it does."""
        repo = AccountRepository(mock_db_session)

        # Setup
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_account
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.exists_by_account_number("1234567890")

        # Assert
        assert result is True

    def test_exists_by_account_number_false(self, mock_db_session):
        """Test checking if account exists when it doesn't."""
        repo = AccountRepository(mock_db_session)

        # Setup
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repo.exists_by_account_number("9999999999")

        # Assert
        assert result is False
