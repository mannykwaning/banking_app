"""
Transaction repository for data access operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Transaction


class TransactionRepository:
    """Repository for Transaction entity data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        account_id: int,
        transaction_type: str,
        amount: float,
        description: Optional[str] = None,
    ) -> Transaction:
        """Create a new transaction in the database."""
        db_transaction = Transaction(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID."""
        return (
            self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get all transactions with pagination."""
        return self.db.query(Transaction).offset(skip).limit(limit).all()

    def get_by_account_id(
        self, account_id: int, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for a specific account."""
        return (
            self.db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
