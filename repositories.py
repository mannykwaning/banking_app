"""
Repository layer for database operations.
Handles all database queries and CRUD operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from database import Account, Transaction


class AccountRepository:
    """Repository for Account database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, account: Account) -> Account:
        """Create a new account in the database."""
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Get an account by ID."""
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Get an account by account number."""
        return self.db.query(Account).filter(Account.account_number == account_number).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """Get all accounts with pagination."""
        return self.db.query(Account).offset(skip).limit(limit).all()
    
    def delete(self, account: Account) -> None:
        """Delete an account from the database."""
        self.db.delete(account)
        self.db.commit()
    
    def update(self, account: Account) -> Account:
        """Update an account in the database."""
        self.db.commit()
        self.db.refresh(account)
        return account


class TransactionRepository:
    """Repository for Transaction database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction in the database."""
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by ID."""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get all transactions with pagination."""
        return self.db.query(Transaction).offset(skip).limit(limit).all()
    
    def get_by_account_id(self, account_id: int) -> List[Transaction]:
        """Get all transactions for a specific account."""
        return self.db.query(Transaction).filter(Transaction.account_id == account_id).all()
