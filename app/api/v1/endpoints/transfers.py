"""
Transfer endpoints for secure money transfers.
"""

from fastapi import APIRouter, Depends, status
import logging

from app.schemas.transaction import (
    InternalTransferCreate,
    ExternalTransferCreate,
    TransferResponse,
)
from app.services.transfer_service import TransferService
from app.core.dependencies import get_transfer_service, get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post(
    "/internal",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an internal transfer",
    description="Transfer money between two accounts within the system with ACID compliance",
)
def create_internal_transfer(
    transfer: InternalTransferCreate,
    transfer_service: TransferService = Depends(get_transfer_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create an internal transfer between two accounts.

    Flow:
    1. Validates source and destination accounts exist and are different
    2. Checks source account has sufficient balance
    3. Verifies transfer amount is within limits (single and daily)
    4. Executes transfer with ACID guarantees (atomic debit/credit)
    5. Logs transaction history
    6. Returns transfer confirmation

    On failure, automatically rolls back all changes.
    """
    logger.info(
        "Internal transfer endpoint called",
        extra={
            "user_id": current_user.id,
            "source_account_id": transfer.source_account_id,
            "destination_account_id": transfer.destination_account_id,
            "amount": transfer.amount,
        },
    )

    result = transfer_service.create_internal_transfer(
        source_account_id=transfer.source_account_id,
        destination_account_id=transfer.destination_account_id,
        amount=transfer.amount,
        description=transfer.description,
    )

    logger.info(
        "Internal transfer completed",
        extra={"user_id": current_user.id, "transfer_id": result["transfer_id"]},
    )

    return TransferResponse(**result)


@router.post(
    "/external",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an external transfer",
    description="Transfer money to an external bank account with validation and limits",
)
def create_external_transfer(
    transfer: ExternalTransferCreate,
    transfer_service: TransferService = Depends(get_transfer_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create an external transfer to another bank.

    Flow:
    1. Validates source account exists
    2. Validates external account details (account number, routing number)
    3. Checks source account has sufficient balance
    4. Verifies transfer amount is within external transfer limits
    5. Executes transfer with ACID guarantees
    6. Initiates external payment processing (status: pending)
    7. Returns transfer confirmation

    On failure, automatically rolls back all changes.
    Note: External transfers have lower limits and start in 'pending' status.
    """
    logger.info(
        "External transfer endpoint called",
        extra={
            "user_id": current_user.id,
            "source_account_id": transfer.source_account_id,
            "external_bank": transfer.external_bank_name,
            "amount": transfer.amount,
        },
    )

    result = transfer_service.create_external_transfer(
        source_account_id=transfer.source_account_id,
        external_account_number=transfer.external_account_number,
        external_bank_name=transfer.external_bank_name,
        external_routing_number=transfer.external_routing_number,
        amount=transfer.amount,
        description=transfer.description,
    )

    logger.info(
        "External transfer initiated",
        extra={"user_id": current_user.id, "transfer_id": result["transfer_id"]},
    )

    return TransferResponse(**result)


@router.get(
    "/{reference_id}",
    response_model=TransferResponse,
    summary="Get transfer details",
    description="Retrieve transfer details and status by reference ID",
)
def get_transfer(
    reference_id: str,
    transfer_service: TransferService = Depends(get_transfer_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get transfer details by reference ID.

    Returns complete transfer information including:
    - Transfer status (pending, completed, failed, reversed)
    - Source and destination transaction IDs
    - Account details
    - Timestamps
    """
    logger.info(
        "Get transfer endpoint called",
        extra={"user_id": current_user.id, "reference_id": reference_id},
    )

    result = transfer_service.get_transfer_by_reference_id(reference_id)
    return TransferResponse(**result)
