"""
Unit tests for CardRepository.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from app.repositories.card_repository import CardRepository
from app.models.card import Card, CardType, CardStatus


class TestCardRepository:
    """Test suite for CardRepository."""

    def test_create_card(self, mock_db_session):
        """Test creating a card in the database."""
        repository = CardRepository(mock_db_session)

        # Setup
        mock_card = Mock(spec=Card)
        mock_card.id = 1
        mock_card.account_id = 1
        mock_card.card_number_last4 = "1234"

        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock(side_effect=lambda x: setattr(x, "id", 1))

        # Execute
        result = repository.create(
            account_id=1,
            card_number_last4="1234",
            encrypted_pan="encrypted_pan_data",
            encrypted_cvv="encrypted_cvv_data",
            cardholder_name="JOHN DOE",
            card_type=CardType.DEBIT,
            expiry_month=12,
            expiry_year=2026,
        )

        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    def test_get_by_id_found(self, mock_db_session):
        """Test getting a card by ID when it exists."""
        repository = CardRepository(mock_db_session)

        # Setup
        mock_card = Mock(spec=Card)
        mock_card.id = 1

        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = mock_card

        # Execute
        result = repository.get_by_id(1)

        # Assert
        assert result == mock_card
        mock_db_session.query.assert_called_once_with(Card)

    def test_get_by_id_not_found(self, mock_db_session):
        """Test getting a card by ID when it doesn't exist."""
        repository = CardRepository(mock_db_session)

        # Setup
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None

        # Execute
        result = repository.get_by_id(999)

        # Assert
        assert result is None

    def test_get_by_account_id(self, mock_db_session):
        """Test getting all cards for an account."""
        repository = CardRepository(mock_db_session)

        # Setup
        mock_cards = [Mock(spec=Card), Mock(spec=Card)]
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = mock_cards

        # Execute
        result = repository.get_by_account_id(1)

        # Assert
        assert result == mock_cards
        assert len(result) == 2

    def test_get_all_with_pagination(self, mock_db_session):
        """Test getting all cards with pagination."""
        repository = CardRepository(mock_db_session)

        # Setup
        mock_cards = [Mock(spec=Card) for _ in range(3)]
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_cards

        # Execute
        result = repository.get_all(skip=0, limit=10)

        # Assert
        assert result == mock_cards
        mock_query.offset.assert_called_once_with(0)

    def test_update_status(self, mock_db_session):
        """Test updating card status."""
        repository = CardRepository(mock_db_session)

        # Setup
        mock_card = Mock(spec=Card)
        mock_card.status = CardStatus.ACTIVE

        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()

        # Execute
        result = repository.update_status(mock_card, CardStatus.BLOCKED)

        # Assert
        assert mock_card.status == CardStatus.BLOCKED
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    def test_delete_card(self, mock_db_session):
        """Test deleting a card."""
        repository = CardRepository(mock_db_session)

        # Setup
        mock_card = Mock(spec=Card)
        mock_db_session.delete = Mock()
        mock_db_session.commit = Mock()

        # Execute
        repository.delete(mock_card)

        # Assert
        mock_db_session.delete.assert_called_once_with(mock_card)
        mock_db_session.commit.assert_called_once()

    def test_get_active_cards_by_account(self, mock_db_session):
        """Test getting only active cards for an account."""
        repository = CardRepository(mock_db_session)

        # Setup
        mock_active_cards = [Mock(spec=Card) for _ in range(2)]
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = mock_active_cards

        # Execute
        result = repository.get_active_cards_by_account(1)

        # Assert
        assert result == mock_active_cards
        assert len(result) == 2
