"""
Account service for business logic.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import logging
from fastapi import HTTPException, status

from app.repositories import AccountRepository
from app.models import Account

logger = logging.getLogger(__name__)


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
        logger.info(
            "Creating new account",
            extra={
                "account_holder": account_holder,
                "account_type": account_type,
                "initial_balance": initial_balance,
            },
        )

        # Generate unique account number
        account_number = self.generate_account_number()

        # Validate initial balance
        if initial_balance < 0:
            logger.warning(
                "Account creation failed - negative initial balance",
                extra={"initial_balance": initial_balance},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Initial balance cannot be negative",
            )

        # Create account via repository
        account = self.repository.create(
            account_number=account_number,
            account_holder=account_holder,
            account_type=account_type,
            balance=initial_balance,
        )

        logger.info(
            "Account created successfully",
            extra={
                "account_id": account.id,
                "account_number": account_number,
                "account_holder": account_holder,
            },
        )
        return account

    def get_account_by_id(self, account_id: int) -> Account:
        """Get an account by ID, raise 404 if not found."""
        logger.debug("Fetching account by ID", extra={"account_id": account_id})
        account = self.repository.get_by_id(account_id)
        if not account:
            logger.warning("Account not found", extra={"account_id": account_id})
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
        logger.info("Deleting account", extra={"account_id": account_id})
        account = self.get_account_by_id(account_id)
        self.repository.delete(account)
        logger.info("Account deleted successfully", extra={"account_id": account_id})

    def generate_account_statement(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """
        Generate account statement with balance and activity.

        Args:
            account_id: The account ID
            start_date: Start date for the statement period (defaults to 30 days ago)
            end_date: End date for the statement period (defaults to now)

        Returns:
            Dictionary containing account statement data
        """
        logger.info(
            "Generating account statement",
            extra={
                "account_id": account_id,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        # Get account
        account = self.get_account_by_id(account_id)

        # Set default date range if not provided
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Get transactions for the period
        transactions = [
            t for t in account.transactions if start_date <= t.created_at <= end_date
        ]

        # Calculate totals by transaction type
        total_deposits = sum(
            t.amount for t in transactions if t.transaction_type == "deposit"
        )
        total_withdrawals = sum(
            t.amount for t in transactions if t.transaction_type == "withdrawal"
        )
        total_transfers_in = sum(
            t.amount for t in transactions if t.transaction_type == "transfer_in"
        )
        total_transfers_out = sum(
            t.amount for t in transactions if t.transaction_type == "transfer_out"
        )

        # Build statement response
        statement = {
            "account_id": account.id,
            "account_number": account.account_number,
            "account_holder": account.account_holder,
            "account_type": account.account_type,
            "current_balance": account.balance,
            "statement_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "total_transfers_in": total_transfers_in,
            "total_transfers_out": total_transfers_out,
            "transaction_count": len(transactions),
            "transactions": transactions,
            "created_at": datetime.utcnow(),
        }

        logger.info(
            "Account statement generated successfully",
            extra={
                "account_id": account_id,
                "transaction_count": len(transactions),
                "total_deposits": total_deposits,
                "total_withdrawals": total_withdrawals,
            },
        )

        return statement
