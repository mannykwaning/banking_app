"""
Transfer service with ACID compliance, validation, and proper error handling.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Tuple
import logging
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.repositories import AccountRepository, TransactionRepository
from app.models import Transaction, Account
from app.core.config import settings

logger = logging.getLogger(__name__)


class TransferService:
    """Service for secure money transfers with ACID compliance."""

    def __init__(self, db: Session):
        self.db = db
        self.transaction_repository = TransactionRepository(db)
        self.account_repository = AccountRepository(db)

    def _validate_accounts(
        self, source_account: Account, destination_account: Optional[Account] = None
    ) -> None:
        """
        Step 1: Validate source and destination accounts.

        Args:
            source_account: Source account object
            destination_account: Destination account object (for internal transfers)

        Raises:
            HTTPException: If validation fails
        """
        if not source_account:
            logger.warning("Transfer validation failed - source account not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found"
            )

        if destination_account is not None:
            if not destination_account:
                logger.warning(
                    "Transfer validation failed - destination account not found"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Destination account not found",
                )

            if source_account.id == destination_account.id:
                logger.warning(
                    "Transfer validation failed - same source and destination",
                    extra={"account_id": source_account.id},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Source and destination accounts must be different",
                )

    def _check_transfer_limits(
        self, account: Account, amount: float, is_external: bool = False
    ) -> None:
        """
        Step 2: Check transfer limits (before balance check).

        Args:
            account: Source account
            amount: Transfer amount
            is_external: Whether this is an external transfer

        Raises:
            HTTPException: If limits are exceeded
        """
        # Check minimum transfer amount
        if amount < settings.min_transfer_amount:
            logger.warning(
                "Transfer failed - below minimum amount",
                extra={"amount": amount, "min_amount": settings.min_transfer_amount},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transfer amount must be at least ${settings.min_transfer_amount:.2f}",
            )

        # Check maximum single transfer amount
        max_amount = (
            settings.max_external_transfer_amount
            if is_external
            else settings.max_transfer_amount
        )
        if amount > max_amount:
            logger.warning(
                "Transfer failed - exceeds maximum amount",
                extra={
                    "amount": amount,
                    "max_amount": max_amount,
                    "is_external": is_external,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transfer amount exceeds maximum limit (${max_amount:.2f})",
            )

    def _check_balance(self, account: Account, amount: float) -> None:
        """
        Step 3: Check if account has sufficient balance.

        Args:
            account: Account to check
            amount: Transfer amount

        Raises:
            HTTPException: If insufficient balance
        """
        if account.balance < amount:
            logger.warning(
                "Transfer failed - insufficient balance",
                extra={
                    "account_id": account.id,
                    "balance": account.balance,
                    "requested_amount": amount,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: ${account.balance:.2f}, Required: ${amount:.2f}",
            )

        # Check if transfer would bring balance below minimum
        remaining_balance = account.balance - amount
        if remaining_balance < settings.min_account_balance:
            logger.warning(
                "Transfer failed - would exceed minimum balance",
                extra={
                    "account_id": account.id,
                    "remaining_balance": remaining_balance,
                    "min_balance": settings.min_account_balance,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transfer would bring balance below minimum (${settings.min_account_balance:.2f})",
            )

    def _check_daily_limit(self, account: Account, amount: float) -> None:
        """
        Step 4: Check daily transfer limit.

        Args:
            account: Source account
            amount: Transfer amount

        Raises:
            HTTPException: If daily limit exceeded
        """
        daily_total = self._get_daily_transfer_total(account.id)
        if daily_total + amount > settings.daily_transfer_limit:
            logger.warning(
                "Transfer failed - exceeds daily limit",
                extra={
                    "account_id": account.id,
                    "daily_total": daily_total,
                    "requested_amount": amount,
                    "daily_limit": settings.daily_transfer_limit,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transfer would exceed daily limit. Used: ${daily_total:.2f}, Limit: ${settings.daily_transfer_limit:.2f}",
            )

    def _get_daily_transfer_total(self, account_id: int) -> float:
        """
        Calculate total transfers made today from an account.

        Args:
            account_id: Account ID

        Returns:
            Total amount transferred today
        """
        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        transfers = (
            self.db.query(Transaction)
            .filter(
                Transaction.account_id == account_id,
                Transaction.transaction_type.in_(["transfer_out", "withdrawal"]),
                Transaction.status == "completed",
                Transaction.created_at >= today_start,
            )
            .all()
        )

        return sum(t.amount for t in transfers)

    def _execute_internal_transfer(
        self,
        source_account: Account,
        destination_account: Account,
        amount: float,
        description: Optional[str],
        reference_id: str,
    ) -> Tuple[Transaction, Transaction]:
        """
        Execute internal transfer with ACID guarantees.

        Step 4: Begin Transaction → Debit Source → Credit Destination → Update Balances

        Args:
            source_account: Source account
            destination_account: Destination account
            amount: Transfer amount
            description: Transfer description
            reference_id: Unique reference ID

        Returns:
            Tuple of (source_transaction, destination_transaction)

        Raises:
            HTTPException: If transfer fails
        """
        try:
            # Begin database transaction (ACID compliance)
            logger.info(
                "Starting internal transfer",
                extra={
                    "reference_id": reference_id,
                    "source_account_id": source_account.id,
                    "destination_account_id": destination_account.id,
                    "amount": amount,
                },
            )

            # Step 4a: Debit source account
            new_source_balance = source_account.balance - amount
            self.account_repository.update_balance(source_account, new_source_balance)

            # Step 4b: Create debit transaction
            source_transaction = Transaction(
                account_id=source_account.id,
                transaction_type="transfer_out",
                amount=amount,
                description=description
                or f"Transfer to account {destination_account.account_number}",
                transfer_type="internal",
                destination_account_id=destination_account.id,
                status="completed",
                reference_id=reference_id,
            )
            self.db.add(source_transaction)

            # Step 4c: Credit destination account
            new_destination_balance = destination_account.balance + amount
            self.account_repository.update_balance(
                destination_account, new_destination_balance
            )

            # Step 4d: Create credit transaction
            destination_transaction = Transaction(
                account_id=destination_account.id,
                transaction_type="transfer_in",
                amount=amount,
                description=description
                or f"Transfer from account {source_account.account_number}",
                transfer_type="internal",
                destination_account_id=source_account.id,
                status="completed",
                reference_id=reference_id,
            )
            self.db.add(destination_transaction)

            # Commit transaction (ACID compliance)
            self.db.commit()
            self.db.refresh(source_transaction)
            self.db.refresh(destination_transaction)

            logger.info(
                "Internal transfer completed successfully",
                extra={
                    "reference_id": reference_id,
                    "source_transaction_id": source_transaction.id,
                    "destination_transaction_id": destination_transaction.id,
                },
            )

            return source_transaction, destination_transaction

        except SQLAlchemyError as e:
            # Step 5: Rollback on failure
            self.db.rollback()
            logger.error(
                "Internal transfer failed - database error",
                extra={"reference_id": reference_id, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transfer failed due to database error. Transaction has been rolled back.",
            )
        except Exception as e:
            # Step 5: Rollback on any failure
            self.db.rollback()
            logger.error(
                "Internal transfer failed - unexpected error",
                extra={"reference_id": reference_id, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transfer failed. Transaction has been rolled back.",
            )

    def _execute_external_transfer(
        self,
        source_account: Account,
        external_account_number: str,
        external_bank_name: str,
        external_routing_number: str,
        amount: float,
        description: Optional[str],
        reference_id: str,
    ) -> Transaction:
        """
        Execute external transfer with ACID guarantees.

        Step 4: Begin Transaction → Debit Source → Log External Transfer

        Args:
            source_account: Source account
            external_account_number: External account number
            external_bank_name: External bank name
            external_routing_number: External routing number
            amount: Transfer amount
            description: Transfer description
            reference_id: Unique reference ID

        Returns:
            Source transaction

        Raises:
            HTTPException: If transfer fails
        """
        try:
            logger.info(
                "Starting external transfer",
                extra={
                    "reference_id": reference_id,
                    "source_account_id": source_account.id,
                    "external_bank": external_bank_name,
                    "amount": amount,
                },
            )

            # Step 4a: Debit source account
            new_source_balance = source_account.balance - amount
            self.account_repository.update_balance(source_account, new_source_balance)

            # Step 4b: Create transaction record
            source_transaction = Transaction(
                account_id=source_account.id,
                transaction_type="transfer_out",
                amount=amount,
                description=description or f"External transfer to {external_bank_name}",
                transfer_type="external",
                external_account_number=external_account_number,
                external_bank_name=external_bank_name,
                external_routing_number=external_routing_number,
                status="pending",  # External transfers start as pending
                reference_id=reference_id,
            )
            self.db.add(source_transaction)

            # Commit transaction (ACID compliance)
            self.db.commit()
            self.db.refresh(source_transaction)

            logger.info(
                "External transfer initiated successfully",
                extra={
                    "reference_id": reference_id,
                    "source_transaction_id": source_transaction.id,
                    "status": "pending",
                },
            )

            # In a real system, you would:
            # 1. Send to external payment processor
            # 2. Update status based on processor response
            # 3. Handle async status updates via webhooks

            return source_transaction

        except SQLAlchemyError as e:
            # Step 5: Rollback on failure
            self.db.rollback()
            logger.error(
                "External transfer failed - database error",
                extra={"reference_id": reference_id, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transfer failed due to database error. Transaction has been rolled back.",
            )
        except Exception as e:
            # Step 5: Rollback on any failure
            self.db.rollback()
            logger.error(
                "External transfer failed - unexpected error",
                extra={"reference_id": reference_id, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transfer failed. Transaction has been rolled back.",
            )

    def create_internal_transfer(
        self,
        source_account_id: int,
        destination_account_id: int,
        amount: float,
        description: Optional[str] = None,
    ) -> dict:
        """
        Create an internal transfer between two accounts.

        Flow: Validate → Check Balance → Check Limits → Execute → Log → Return Confirmation

        Args:
            source_account_id: Source account ID
            destination_account_id: Destination account ID
            amount: Transfer amount
            description: Transfer description

        Returns:
            Transfer details
        """
        # Generate unique reference ID
        reference_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        logger.info(
            "Internal transfer requested",
            extra={
                "reference_id": reference_id,
                "source_account_id": source_account_id,
                "destination_account_id": destination_account_id,
                "amount": amount,
            },
        )

        # Step 1: Validate accounts
        source_account = self.account_repository.get_by_id(source_account_id)
        destination_account = self.account_repository.get_by_id(destination_account_id)
        self._validate_accounts(source_account, destination_account)

        # Step 2: Check limits
        self._check_transfer_limits(source_account, amount, is_external=False)

        # Step 3: Check balance
        self._check_balance(source_account, amount)

        # Step 4: Execute transfer with ACID compliance
        source_txn, dest_txn = self._execute_internal_transfer(
            source_account, destination_account, amount, description, reference_id
        )

        # Step 6: Return confirmation
        return {
            "transfer_id": reference_id,
            "source_transaction_id": source_txn.id,
            "destination_transaction_id": dest_txn.id,
            "transfer_type": "internal",
            "amount": amount,
            "status": "completed",
            "source_account_id": source_account_id,
            "destination_account_id": destination_account_id,
            "description": description,
            "created_at": source_txn.created_at,
        }

    def create_external_transfer(
        self,
        source_account_id: int,
        external_account_number: str,
        external_bank_name: str,
        external_routing_number: str,
        amount: float,
        description: Optional[str] = None,
    ) -> dict:
        """
        Create an external transfer to another bank.

        Flow: Validate → Check Balance → Check Limits → Execute → Log → Return Confirmation

        Args:
            source_account_id: Source account ID
            external_account_number: External account number
            external_bank_name: External bank name
            external_routing_number: External routing number
            amount: Transfer amount
            description: Transfer description

        Returns:
            Transfer details
        """
        # Generate unique reference ID
        reference_id = f"EXT-{uuid.uuid4().hex[:12].upper()}"

        logger.info(
            "External transfer requested",
            extra={
                "reference_id": reference_id,
                "source_account_id": source_account_id,
                "external_bank": external_bank_name,
                "amount": amount,
            },
        )

        # Step 1: Validate source account
        source_account = self.account_repository.get_by_id(source_account_id)
        self._validate_accounts(source_account)

        # Step 2: Check limits (external transfers have lower limits)
        self._check_transfer_limits(source_account, amount, is_external=True)

        # Step 3: Check balance
        self._check_balance(source_account, amount)

        # Step 4: Execute transfer with ACID compliance
        source_txn = self._execute_external_transfer(
            source_account,
            external_account_number,
            external_bank_name,
            external_routing_number,
            amount,
            description,
            reference_id,
        )

        # Step 6: Return confirmation
        return {
            "transfer_id": reference_id,
            "source_transaction_id": source_txn.id,
            "destination_transaction_id": None,
            "transfer_type": "external",
            "amount": amount,
            "status": "pending",
            "source_account_id": source_account_id,
            "destination_account_id": None,
            "external_account_number": external_account_number,
            "external_bank_name": external_bank_name,
            "description": description,
            "created_at": source_txn.created_at,
        }

    def get_transfer_by_reference_id(self, reference_id: str) -> dict:
        """
        Get transfer details by reference ID.

        Args:
            reference_id: Transfer reference ID

        Returns:
            Transfer details

        Raises:
            HTTPException: If transfer not found
        """
        transactions = (
            self.db.query(Transaction)
            .filter(Transaction.reference_id == reference_id)
            .all()
        )

        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transfer with reference ID {reference_id} not found",
            )

        # Get the source transaction (transfer_out)
        source_txn = next(
            (t for t in transactions if t.transaction_type == "transfer_out"), None
        )
        if not source_txn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer details incomplete",
            )

        # Get destination transaction if internal
        dest_txn = next(
            (t for t in transactions if t.transaction_type == "transfer_in"), None
        )

        return {
            "transfer_id": reference_id,
            "source_transaction_id": source_txn.id,
            "destination_transaction_id": dest_txn.id if dest_txn else None,
            "transfer_type": source_txn.transfer_type,
            "amount": source_txn.amount,
            "status": source_txn.status,
            "source_account_id": source_txn.account_id,
            "destination_account_id": source_txn.destination_account_id,
            "external_account_number": source_txn.external_account_number,
            "external_bank_name": source_txn.external_bank_name,
            "description": source_txn.description,
            "created_at": source_txn.created_at,
            "updated_at": source_txn.updated_at,
        }
