"""
Card repository for data access operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.card import Card, CardType, CardStatus


class CardRepository:
    """Repository for Card entity data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        account_id: int,
        card_number_last4: str,
        encrypted_pan: str,
        encrypted_cvv: str,
        cardholder_name: str,
        card_type: CardType,
        expiry_month: int,
        expiry_year: int,
    ) -> Card:
        """Create a new card in the database."""
        db_card = Card(
            account_id=account_id,
            card_number_last4=card_number_last4,
            encrypted_pan=encrypted_pan,
            encrypted_cvv=encrypted_cvv,
            cardholder_name=cardholder_name,
            card_type=card_type,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            status=CardStatus.ACTIVE,
            issued_at=datetime.utcnow(),
        )
        self.db.add(db_card)
        self.db.commit()
        self.db.refresh(db_card)
        return db_card

    def get_by_id(self, card_id: int) -> Optional[Card]:
        """Get card by ID."""
        return self.db.query(Card).filter(Card.id == card_id).first()

    def get_by_account_id(self, account_id: int) -> List[Card]:
        """Get all cards for a specific account."""
        return self.db.query(Card).filter(Card.account_id == account_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Card]:
        """Get all cards with pagination."""
        return self.db.query(Card).offset(skip).limit(limit).all()

    def update_status(self, card: Card, new_status: CardStatus) -> Card:
        """Update card status."""
        card.status = new_status
        card.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(card)
        return card

    def delete(self, card: Card) -> None:
        """Delete a card."""
        self.db.delete(card)
        self.db.commit()

    def get_active_cards_by_account(self, account_id: int) -> List[Card]:
        """Get all active cards for a specific account."""
        return (
            self.db.query(Card)
            .filter(Card.account_id == account_id, Card.status == CardStatus.ACTIVE)
            .all()
        )
