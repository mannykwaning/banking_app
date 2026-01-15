"""
Service layer for business logic.
Handles business rules and orchestrates repository operations.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import secrets

from database import Account, Transaction
from repositories import AccountRepository, TransactionRepository
from schemas import AccountCreate, TransactionCreate


class AccountService:
    """Service for account business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AccountRepository(db)
    
    def generate_account_number(self) -> str:
        """Generate a unique random account number."""
        max_attempts = 100
        for _ in range(max_attempts):
            # Generate a secure random 10-digit account number
            account_number = ''.join(str(secrets.randbelow(10)) for _ in range(10))
            # Check if it already exists
            existing = self.repository.get_by_account_number(account_number)
            if not existing:
                return account_number
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate unique account number"
        )
    
    def create_account(self, account_data: AccountCreate) -> Account:
        """Create a new bank account with business logic."""
        # Generate unique account number
        account_number = self.generate_account_number()
        
        # Create account object
        account = Account(
            account_number=account_number,
            account_holder=account_data.account_holder,
            account_type=account_data.account_type,
            balance=account_data.initial_balance
        )
        
        # Save to database
        return self.repository.create(account)
    
    def get_account(self, account_id: int) -> Account:
        """Get an account by ID."""
        account = self.repository.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found"
            )
        return account
    
    def list_accounts(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """List all accounts."""
        return self.repository.get_all(skip=skip, limit=limit)
    
    def delete_account(self, account_id: int) -> None:
        """Delete an account."""
        account = self.repository.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found"
            )
        self.repository.delete(account)


class TransactionService:
    """Service for transaction business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = TransactionRepository(db)
        self.account_repository = AccountRepository(db)
    
    def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        """Create a new transaction with business logic."""
        # Check if account exists
        account = self.account_repository.get_by_id(transaction_data.account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {transaction_data.account_id} not found"
            )
        
        # Validate transaction type
        if transaction_data.transaction_type not in ["deposit", "withdrawal"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction type must be either 'deposit' or 'withdrawal'"
            )
        
        # Check sufficient balance for withdrawal
        if transaction_data.transaction_type == "withdrawal":
            if account.balance < transaction_data.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance for withdrawal"
                )
            account.balance -= transaction_data.amount
        else:  # deposit
            account.balance += transaction_data.amount
        
        # Create transaction record
        transaction = Transaction(
            account_id=transaction_data.account_id,
            transaction_type=transaction_data.transaction_type,
            amount=transaction_data.amount,
            description=transaction_data.description
        )
        
        # Save transaction and update account
        self.account_repository.update(account)
        return self.repository.create(transaction)
    
    def get_transaction(self, transaction_id: int) -> Transaction:
        """Get a transaction by ID."""
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found"
            )
        return transaction
    
    def list_transactions(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """List all transactions."""
        return self.repository.get_all(skip=skip, limit=limit)
