"""
Transaction endpoints for the API.
"""

from fastapi import APIRouter, Depends, status
from typing import List
import logging

from app.schemas import TransactionCreate, TransactionResponse
from app.services import TransactionService
from app.core.dependencies import get_transaction_service, get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction",
)
def create_transaction(
    transaction: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new transaction (deposit or withdrawal)."""
    logger.info(
        "Create transaction endpoint called",
        extra={
            "user_id": current_user.id,
            "account_id": transaction.account_id,
            "type": transaction.transaction_type,
        },
    )
    result = transaction_service.create_transaction(
        account_id=transaction.account_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
    )
    logger.info(
        "Create transaction endpoint successful",
        extra={"user_id": current_user.id, "transaction_id": result.id},
    )
    return result


@router.get(
    "",
    response_model=List[TransactionResponse],
    summary="List all transactions",
)
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_active_user),
):
    """List all transactions with pagination."""
    return transaction_service.get_all_transactions(skip=skip, limit=limit)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction by ID",
)
def get_transaction(
    transaction_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific transaction by ID."""
    return transaction_service.get_transaction_by_id(transaction_id)
