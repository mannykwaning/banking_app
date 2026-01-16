"""
Transaction database model.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class TransactionType(str, enum.Enum):
    """Transaction type enumeration."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"


class TransferType(str, enum.Enum):
    """Transfer type enumeration."""

    INTERNAL = "internal"
    EXTERNAL = "external"


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class Transaction(Base):
    """Transaction model."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    transaction_type = Column(
        String, nullable=False
    )  # e.g., "deposit", "withdrawal", "transfer_out", "transfer_in"
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)

    # Transfer-specific fields
    transfer_type = Column(String, nullable=True)  # "internal" or "external"
    destination_account_id = Column(
        Integer, ForeignKey("accounts.id"), nullable=True
    )  # For internal transfers
    external_account_number = Column(String, nullable=True)  # For external transfers
    external_bank_name = Column(String, nullable=True)  # For external transfers
    external_routing_number = Column(String, nullable=True)  # For external transfers

    # Status tracking
    status = Column(
        String, default="completed", nullable=False
    )  # "pending", "completed", "failed", "reversed"
    reference_id = Column(
        String, nullable=True, index=True
    )  # For linking related transactions

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with account
    account = relationship(
        "Account", back_populates="transactions", foreign_keys=[account_id]
    )
