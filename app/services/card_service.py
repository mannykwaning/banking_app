"""
Card service for business logic.
"""

from sqlalchemy.orm import Session
from typing import List
import secrets
import logging
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.repositories.card_repository import CardRepository
from app.repositories.account_repository import AccountRepository
from app.models.card import Card, CardType, CardStatus
from app.core.encryption import encrypt_data, decrypt_data

logger = logging.getLogger(__name__)


class CardService:
    """Service for card-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = CardRepository(db)
        self.account_repository = AccountRepository(db)

    def generate_card_number(self) -> str:
        """
        Generate a valid 16-digit card number using Luhn algorithm.
        First 6 digits are the BIN (Bank Identification Number).
        """
        # Use a fictional BIN for testing: 400000 (Visa test range)
        bin_number = "400000"

        # Generate 9 random digits for account identifier
        account_identifier = "".join(str(secrets.randbelow(10)) for _ in range(9))

        # Combine BIN and account identifier (15 digits so far)
        partial_number = bin_number + account_identifier

        # Calculate Luhn check digit
        check_digit = self._calculate_luhn_check_digit(partial_number)

        return partial_number + str(check_digit)

    def _calculate_luhn_check_digit(self, number: str) -> int:
        """Calculate Luhn check digit for card number validation."""
        digits = [int(d) for d in number]

        # Double every second digit from right to left
        for i in range(len(digits) - 1, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9

        # Sum all digits
        total = sum(digits)

        # Check digit makes the total a multiple of 10
        return (10 - (total % 10)) % 10

    def generate_cvv(self) -> str:
        """Generate a random 3-digit CVV."""
        return "".join(str(secrets.randbelow(10)) for _ in range(3))

    def calculate_expiry_date(self) -> tuple[int, int]:
        """
        Calculate card expiry date (3 years from now).
        Returns (month, year) tuple.
        """
        expiry_date = datetime.utcnow() + timedelta(days=365 * 3)
        return expiry_date.month, expiry_date.year

    def issue_card(
        self, account_id: int, cardholder_name: str, card_type: CardType
    ) -> Card:
        """
        Issue a new card with proper validation and encryption.
        Workflow: Validate Account → Generate Card Details → Store Encrypted
        """
        logger.info(
            "Issuing new card",
            extra={
                "account_id": account_id,
                "card_type": card_type.value,
                "cardholder_name": cardholder_name,
            },
        )

        # Step 1: Validate Account
        account = self.account_repository.get_by_id(account_id)
        if not account:
            logger.warning(
                "Card issuance failed - account not found",
                extra={"account_id": account_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found",
            )

        # Check if account already has too many cards (business rule: max 5 cards per account)
        existing_cards = self.repository.get_active_cards_by_account(account_id)
        if len(existing_cards) >= 5:
            logger.warning(
                "Card issuance failed - too many cards",
                extra={"account_id": account_id, "card_count": len(existing_cards)},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account has reached maximum number of active cards (5)",
            )

        # Step 2: Generate Card Details
        card_number = self.generate_card_number()
        cvv = self.generate_cvv()
        expiry_month, expiry_year = self.calculate_expiry_date()

        logger.info(
            "Card details generated",
            extra={
                "account_id": account_id,
                "card_last4": card_number[-4:],
                "expiry": f"{expiry_month:02d}/{expiry_year}",
            },
        )

        # Step 3: Store Encrypted
        encrypted_pan = encrypt_data(card_number)
        encrypted_cvv = encrypt_data(cvv)

        card = self.repository.create(
            account_id=account_id,
            card_number_last4=card_number[-4:],
            encrypted_pan=encrypted_pan,
            encrypted_cvv=encrypted_cvv,
            cardholder_name=cardholder_name,
            card_type=card_type,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
        )

        logger.info(
            "Card issued successfully",
            extra={
                "card_id": card.id,
                "account_id": account_id,
                "card_last4": card.card_number_last4,
            },
        )
        return card

    def get_card_by_id(self, card_id: int) -> Card:
        """Get a card by ID, raise 404 if not found."""
        logger.debug("Fetching card by ID", extra={"card_id": card_id})
        card = self.repository.get_by_id(card_id)
        if not card:
            logger.warning("Card not found", extra={"card_id": card_id})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with ID {card_id} not found",
            )
        return card

    def get_cards_by_account(self, account_id: int) -> List[Card]:
        """Get all cards for a specific account."""
        # Validate account exists
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found",
            )
        return self.repository.get_by_account_id(account_id)

    def get_all_cards(self, skip: int = 0, limit: int = 100) -> List[Card]:
        """Get all cards with pagination."""
        return self.repository.get_all(skip=skip, limit=limit)

    def update_card_status(self, card_id: int, new_status: CardStatus) -> Card:
        """Update card status (activate, block, etc.)."""
        logger.info(
            "Updating card status",
            extra={"card_id": card_id, "new_status": new_status.value},
        )

        card = self.get_card_by_id(card_id)
        card = self.repository.update_status(card, new_status)

        logger.info(
            "Card status updated successfully",
            extra={"card_id": card_id, "new_status": new_status.value},
        )
        return card

    def block_card(self, card_id: int) -> Card:
        """Block a card (convenience method)."""
        return self.update_card_status(card_id, CardStatus.BLOCKED)

    def activate_card(self, card_id: int) -> Card:
        """Activate a card (convenience method)."""
        return self.update_card_status(card_id, CardStatus.ACTIVE)

    def get_card_details(self, card_id: int) -> dict:
        """
        Get card details with decrypted sensitive data.
        WARNING: Use with caution - only for authorized operations.
        """
        card = self.get_card_by_id(card_id)

        # Decrypt sensitive data
        decrypted_pan = decrypt_data(card.encrypted_pan)
        decrypted_cvv = decrypt_data(card.encrypted_cvv)

        return {
            "card": card,
            "card_number": decrypted_pan,
            "cvv": decrypted_cvv,
        }

    def get_masked_card_number(self, card_id: int) -> str:
        """Get masked card number for display (e.g., ****-****-****-1234)."""
        card = self.get_card_by_id(card_id)
        return f"****-****-****-{card.card_number_last4}"
