"""
Account service for business logic.
"""

from sqlalchemy.orm import Session
from typing import List
import secrets
from fastapi import HTTPException, status

from app.repositories import AccountRepository
from app.models import Account


class AccountService:
    """Service for account-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = AccountRepository(db)

    def generate_account_number(self) -> str:
        """Generate a unique random account number."""
        max_attempts = 100
        for _ in range(max_attempts):
            # Generate a secure random 10-digit account number
            account_number = "".join(str(secrets.randbelow(10)) for _ in range(10))
            # Check if it already exists
            if not self.repository.exists_by_account_number(account_number):
                return account_number
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate unique account number",
        )

    def create_account(
        self, account_holder: str, account_type: str, initial_balance: float = 0.0
    ) -> Account:
        """Create a new bank account with business logic validation."""
        # Generate unique account number
        account_number = self.generate_account_number()

        # Validate initial balance
        if initial_balance < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Initial balance cannot be negative",
            )

        # Create account via repository
        return self.repository.create(
            account_number=account_number,
            account_holder=account_holder,
            account_type=account_type,
            balance=initial_balance,
        )

    def get_account_by_id(self, account_id: int) -> Account:
        """Get an account by ID, raise 404 if not found."""
        account = self.repository.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found",
            )
        return account

    def get_all_accounts(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """Get all accounts with pagination."""
        return self.repository.get_all(skip=skip, limit=limit)

    def delete_account(self, account_id: int) -> None:
        """Delete an account by ID."""
        account = self.get_account_by_id(account_id)
        self.repository.delete(account)
