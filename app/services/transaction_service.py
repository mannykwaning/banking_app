"""
Transaction service for business logic.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from fastapi import HTTPException, status

from app.repositories import AccountRepository, TransactionRepository
from app.models import Transaction

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for transaction-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = TransactionRepository(db)
        self.account_repository = AccountRepository(db)

    def create_transaction(
        self,
        account_id: int,
        transaction_type: str,
        amount: float,
        description: Optional[str] = None,
    ) -> Transaction:
        """Create a new transaction with business logic validation."""
        logger.info(
            "Creating transaction",
            extra={
                "account_id": account_id,
                "transaction_type": transaction_type,
                "amount": amount,
            },
        )

        # Verify account exists
        account = self.account_repository.get_by_id(account_id)
        if not account:
            logger.warning(
                "Transaction failed - account not found",
                extra={"account_id": account_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found",
            )

        # Validate transaction type
        valid_types = ["deposit", "withdrawal"]
        if transaction_type not in valid_types:
            logger.warning(
                "Transaction failed - invalid type",
                extra={"account_id": account_id, "transaction_type": transaction_type},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transaction type must be one of: {', '.join(valid_types)}",
            )

        # Validate amount
        if amount <= 0:
            logger.warning(
                "Transaction failed - invalid amount",
                extra={"account_id": account_id, "amount": amount},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction amount must be positive",
            )

        # Handle withdrawal - check sufficient balance
        if transaction_type == "withdrawal":
            if account.balance < amount:
                logger.warning(
                    "Transaction failed - insufficient balance",
                    extra={
                        "account_id": account_id,
                        "balance": account.balance,
                        "amount": amount,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient balance. Available: {account.balance}, Requested: {amount}",
                )
            new_balance = account.balance - amount
        else:  # deposit
            new_balance = account.balance + amount

        # Update account balance
        self.account_repository.update_balance(account, new_balance)

        # Create transaction record
        transaction = self.repository.create(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
        )

        logger.info(
            "Transaction completed successfully",
            extra={
                "transaction_id": transaction.id,
                "account_id": account_id,
                "transaction_type": transaction_type,
                "amount": amount,
                "new_balance": new_balance,
            },
        )
        return transaction

    def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        """Get a transaction by ID, raise 404 if not found."""
        logger.debug(
            "Fetching transaction by ID", extra={"transaction_id": transaction_id}
        )
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            logger.warning(
                "Transaction not found", extra={"transaction_id": transaction_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found",
            )
        return transaction

    def get_all_transactions(
        self, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions with pagination."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_transactions_by_account(
        self, account_id: int, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for a specific account."""
        # Verify account exists
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with ID {account_id} not found",
            )
        return self.repository.get_by_account_id(account_id, skip=skip, limit=limit)
