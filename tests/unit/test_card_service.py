"""
Unit tests for CardService.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.services.card_service import CardService
from app.models.card import Card, CardType, CardStatus
from app.models.account import Account


class TestCardService:
    """Test suite for CardService."""

    @pytest.fixture
    def mock_card(self):
        """Create a mock card object."""
        card = Mock(spec=Card)
        card.id = 1
        card.account_id = 1
        card.card_number_last4 = "1234"
        card.encrypted_pan = "encrypted_pan"
        card.encrypted_cvv = "encrypted_cvv"
        card.cardholder_name = "JOHN DOE"
        card.card_type = CardType.DEBIT
        card.status = CardStatus.ACTIVE
        card.expiry_month = 12
        card.expiry_year = 2026
        return card

    @pytest.fixture
    def mock_account(self):
        """Create a mock account object."""
        account = Mock(spec=Account)
        account.id = 1
        account.account_number = "1234567890"
        account.account_holder = "John Doe"
        account.balance = 1000.0
        return account

    def test_generate_card_number(self, mock_db_session):
        """Test generating a valid 16-digit card number."""
        service = CardService(mock_db_session)

        # Execute
        card_number = service.generate_card_number()

        # Assert
        assert len(card_number) == 16
        assert card_number.isdigit()
        assert card_number.startswith("400000")  # Test BIN

    def test_calculate_luhn_check_digit(self, mock_db_session):
        """Test Luhn algorithm check digit calculation."""
        service = CardService(mock_db_session)

        # Test with known valid card number prefix
        partial = "400000000000000"
        check_digit = service._calculate_luhn_check_digit(partial)

        # Assert
        assert isinstance(check_digit, int)
        assert 0 <= check_digit <= 9

    def test_generate_cvv(self, mock_db_session):
        """Test generating a 3-digit CVV."""
        service = CardService(mock_db_session)

        # Execute
        cvv = service.generate_cvv()

        # Assert
        assert len(cvv) == 3
        assert cvv.isdigit()

    def test_calculate_expiry_date(self, mock_db_session):
        """Test calculating card expiry date (3 years from now)."""
        service = CardService(mock_db_session)

        # Execute
        month, year = service.calculate_expiry_date()

        # Assert
        assert 1 <= month <= 12
        assert year >= 2026  # Should be at least current year + 3

    @patch("app.services.card_service.encrypt_data")
    def test_issue_card_success(
        self, mock_encrypt, mock_db_session, mock_account, mock_card
    ):
        """Test successful card issuance."""
        service = CardService(mock_db_session)

        # Setup mocks
        service.account_repository.get_by_id = Mock(return_value=mock_account)
        service.repository.get_active_cards_by_account = Mock(return_value=[])
        service.repository.create = Mock(return_value=mock_card)
        mock_encrypt.return_value = "encrypted_data"

        # Execute
        result = service.issue_card(
            account_id=1, cardholder_name="JOHN DOE", card_type=CardType.DEBIT
        )

        # Assert
        assert result == mock_card
        service.account_repository.get_by_id.assert_called_once_with(1)
        service.repository.create.assert_called_once()

    def test_issue_card_account_not_found(self, mock_db_session):
        """Test card issuance fails when account doesn't exist."""
        service = CardService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.issue_card(
                account_id=999, cardholder_name="JOHN DOE", card_type=CardType.DEBIT
            )

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    def test_issue_card_too_many_cards(self, mock_db_session, mock_account):
        """Test card issuance fails when account has max cards."""
        service = CardService(mock_db_session)

        # Setup - account already has 5 active cards
        service.account_repository.get_by_id = Mock(return_value=mock_account)
        mock_cards = [Mock(spec=Card) for _ in range(5)]
        service.repository.get_active_cards_by_account = Mock(return_value=mock_cards)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.issue_card(
                account_id=1, cardholder_name="JOHN DOE", card_type=CardType.DEBIT
            )

        assert exc_info.value.status_code == 400
        assert "maximum number" in str(exc_info.value.detail).lower()

    def test_get_card_by_id_found(self, mock_db_session, mock_card):
        """Test getting a card by ID when it exists."""
        service = CardService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_card)

        # Execute
        result = service.get_card_by_id(1)

        # Assert
        assert result == mock_card

    def test_get_card_by_id_not_found(self, mock_db_session):
        """Test getting a card by ID when it doesn't exist."""
        service = CardService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_card_by_id(999)

        assert exc_info.value.status_code == 404

    def test_get_cards_by_account(self, mock_db_session, mock_account, mock_card):
        """Test getting all cards for an account."""
        service = CardService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=mock_account)
        service.repository.get_by_account_id = Mock(return_value=[mock_card])

        # Execute
        result = service.get_cards_by_account(1)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_card

    def test_get_cards_by_account_account_not_found(self, mock_db_session):
        """Test getting cards for non-existent account."""
        service = CardService(mock_db_session)
        service.account_repository.get_by_id = Mock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_cards_by_account(999)

        assert exc_info.value.status_code == 404

    def test_update_card_status(self, mock_db_session, mock_card):
        """Test updating card status."""
        service = CardService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_card)
        service.repository.update_status = Mock(return_value=mock_card)

        # Execute
        result = service.update_card_status(1, CardStatus.BLOCKED)

        # Assert
        assert result == mock_card
        service.repository.update_status.assert_called_once_with(
            mock_card, CardStatus.BLOCKED
        )

    def test_block_card(self, mock_db_session, mock_card):
        """Test blocking a card."""
        service = CardService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_card)
        service.repository.update_status = Mock(return_value=mock_card)

        # Execute
        result = service.block_card(1)

        # Assert
        assert result == mock_card
        service.repository.update_status.assert_called_once_with(
            mock_card, CardStatus.BLOCKED
        )

    def test_activate_card(self, mock_db_session, mock_card):
        """Test activating a card."""
        service = CardService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_card)
        service.repository.update_status = Mock(return_value=mock_card)

        # Execute
        result = service.activate_card(1)

        # Assert
        assert result == mock_card
        service.repository.update_status.assert_called_once_with(
            mock_card, CardStatus.ACTIVE
        )

    @patch("app.services.card_service.decrypt_data")
    def test_get_card_details(self, mock_decrypt, mock_db_session, mock_card):
        """Test getting card details with decrypted data."""
        service = CardService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_card)
        mock_decrypt.side_effect = lambda x: f"decrypted_{x}"

        # Execute
        result = service.get_card_details(1)

        # Assert
        assert "card" in result
        assert "card_number" in result
        assert "cvv" in result
        assert result["card"] == mock_card
        assert mock_decrypt.call_count == 2

    def test_get_masked_card_number(self, mock_db_session, mock_card):
        """Test getting masked card number."""
        service = CardService(mock_db_session)
        service.repository.get_by_id = Mock(return_value=mock_card)

        # Execute
        result = service.get_masked_card_number(1)

        # Assert
        assert result == "****-****-****-1234"
        assert "1234" in result

    def test_get_all_cards_with_pagination(self, mock_db_session, mock_card):
        """Test getting all cards with pagination."""
        service = CardService(mock_db_session)
        service.repository.get_all = Mock(return_value=[mock_card])

        # Execute
        result = service.get_all_cards(skip=0, limit=10)

        # Assert
        assert len(result) == 1
        service.repository.get_all.assert_called_once_with(skip=0, limit=10)
