"""
Account database model.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Account(Base):
    """Bank Account model."""

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True, nullable=False)
    account_holder = Column(String, nullable=False)
    account_type = Column(String, nullable=False)  # e.g., "checking", "savings"
    balance = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with transactions
    transactions = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
        foreign_keys="Transaction.account_id",
    )
