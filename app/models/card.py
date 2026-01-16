"""
Card database model with encryption for sensitive data.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class CardType(enum.Enum):
    """Enum for card types."""

    DEBIT = "debit"
    CREDIT = "credit"
    PREPAID = "prepaid"


class CardStatus(enum.Enum):
    """Enum for card status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    EXPIRED = "expired"


class Card(Base):
    """Card model with encrypted sensitive data."""

    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    card_number_last4 = Column(
        String, nullable=False
    )  # Store only last 4 digits unencrypted
    encrypted_pan = Column(
        String, nullable=False
    )  # Encrypted full PAN (Primary Account Number)
    encrypted_cvv = Column(String, nullable=False)  # Encrypted CVV
    cardholder_name = Column(String, nullable=False)
    card_type = Column(SQLEnum(CardType), nullable=False)
    status = Column(SQLEnum(CardStatus), default=CardStatus.ACTIVE, nullable=False)
    expiry_month = Column(Integer, nullable=False)  # 1-12
    expiry_year = Column(Integer, nullable=False)  # Full year e.g., 2026
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship with account
    account = relationship("Account", backref="cards")

    def __repr__(self):
        return f"<Card {self.card_type.value} ending in {self.card_number_last4}>"
