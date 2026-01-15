"""
Account repository for data access operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Account


class AccountRepository:
    """Repository for Account entity data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        account_number: str,
        account_holder: str,
        account_type: str,
        balance: float,
    ) -> Account:
        """Create a new account in the database."""
        db_account = Account(
            account_number=account_number,
            account_holder=account_holder,
            account_type=account_type,
            balance=balance,
        )
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account

    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID."""
        return self.db.query(Account).filter(Account.id == account_id).first()

    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Get account by account number."""
        return (
            self.db.query(Account)
            .filter(Account.account_number == account_number)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """Get all accounts with pagination."""
        return self.db.query(Account).offset(skip).limit(limit).all()

    def update_balance(self, account: Account, new_balance: float) -> Account:
        """Update account balance."""
        account.balance = new_balance
        self.db.commit()
        self.db.refresh(account)
        return account

    def delete(self, account: Account) -> None:
        """Delete an account."""
        self.db.delete(account)
        self.db.commit()

    def exists_by_account_number(self, account_number: str) -> bool:
        """Check if an account with the given account number exists."""
        return (
            self.db.query(Account)
            .filter(Account.account_number == account_number)
            .first()
            is not None
        )
