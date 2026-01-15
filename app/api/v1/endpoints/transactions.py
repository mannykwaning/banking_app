"""
Transaction endpoints for the API.
"""

from fastapi import APIRouter, Depends, status
from typing import List

from app.schemas import TransactionCreate, TransactionResponse
from app.services import TransactionService
from app.core.dependencies import get_transaction_service

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
):
    """Create a new transaction (deposit or withdrawal)."""
    return transaction_service.create_transaction(
        account_id=transaction.account_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
    )


@router.get(
    "",
    response_model=List[TransactionResponse],
    summary="List all transactions",
)
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    transaction_service: TransactionService = Depends(get_transaction_service),
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
):
    """Get a specific transaction by ID."""
    return transaction_service.get_transaction_by_id(transaction_id)
