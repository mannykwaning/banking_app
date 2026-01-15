"""
Unit tests for AccountService.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from app.services import AccountService
from app.models import Account


class TestAccountService:
    """Test suite for AccountService."""

    def test_generate_account_number_success(self, mock_db_session):
        """Test successful account number generation."""
        service = AccountService(mock_db_session)
        service.repository.exists_by_account_number = Mock(return_value=False)

        # Execute
        account_number = service.generate_account_number()

        # Assert
        assert len(account_number) == 10
        assert account_number.isdigit()

    def test_generate_account_number_retries(self, mock_db_session):
        """Test account number generation with retries."""
        service = AccountService(mock_db_session)
        # First two attempts exist, third doesn't
        service.repository.exists_by_account_number = Mock(
            side_effect=[True, True, False]
        )

        # Execute
        account_number = service.generate_account_number()

        # Assert
        assert len(account_number) == 10
        assert service.repository.exists_by_account_number.call_count == 3

    def test_generate_account_number_fails_after_max_attempts(self, mock_db_session):
        """Test account number generation fails after max attempts."""
        service = AccountService(mock_db_session)
        service.repository.exists_by_account_number = Mock(return_value=True)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.generate_account_number()

        assert exc_info.value.status_code == 500
        assert "Unable to generate unique account number" in str(exc_info.value.detail)

    def test_create_account_success(self, mock_db_session, mock_account):
        """Test successful account creation."""
        service = AccountService(mock_db_session)
        service.repository.exists_by_account_number = Mock(return_value=False)
        service.repository.create = Mock(return_value=mock_account)

        # Execute
        result = service.create_account("John Doe", "checking", 100.0)

        # Assert
        assert result == mock_account
        service.repository.create.assert_called_once()

    def test_create_account_negative_balance(self, mock_db_session):
        """Test creating account with negative balance fails."""
        service = AccountService(mock_db_session)
        service.repository.exists_by_account_number = Mock(return_value=False)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_account("John Doe", "checking", -100.0)

        assert exc_info.value.status_code == 400
        assert "negative" in str(exc_info.value.detail).lower()

    def test_get_account_by_id_found(self, mock_db_session, mock_account):
        """Test getting account by ID when it exists."""
        service = AccountService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_account)

        # Execute
        result = service.get_account_by_id(1)

        # Assert
        assert result == mock_account
        service.repository.get_by_id.assert_called_once_with(1)

    def test_get_account_by_id_not_found(self, mock_db_session):
        """Test getting account by ID when it doesn't exist."""
        service = AccountService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_account_by_id(999)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    def test_get_all_accounts(self, mock_db_session):
        """Test getting all accounts."""
        service = AccountService(mock_db_session)
        mock_accounts = [Mock(spec=Account) for _ in range(3)]
        service.repository.get_all = Mock(return_value=mock_accounts)

        # Execute
        result = service.get_all_accounts(skip=0, limit=10)

        # Assert
        assert len(result) == 3
        service.repository.get_all.assert_called_once_with(skip=0, limit=10)

    def test_delete_account_success(self, mock_db_session, mock_account):
        """Test successful account deletion."""
        service = AccountService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_account)
        service.repository.delete = Mock()

        # Execute
        service.delete_account(1)

        # Assert
        service.repository.delete.assert_called_once_with(mock_account)

    def test_delete_account_not_found(self, mock_db_session):
        """Test deleting non-existent account."""
        service = AccountService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.delete_account(999)

        assert exc_info.value.status_code == 404
