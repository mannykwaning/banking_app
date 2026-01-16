"""
Card endpoints for the API.
"""

from fastapi import APIRouter, Depends, status
from typing import List
import logging

from app.schemas.card import (
    CardIssueRequest,
    CardResponse,
    CardDetailsResponse,
    CardStatusUpdate,
    MaskedCardNumber,
)
from app.services.card_service import CardService
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.card import CardType, CardStatus
from sqlalchemy.orm import Session
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cards", tags=["Cards"])


def get_card_service(db: Session = Depends(get_db)) -> CardService:
    """Dependency to get CardService instance."""
    return CardService(db)


@router.post(
    "",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Issue a new card",
)
def issue_card(
    request: CardIssueRequest,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Issue a new card for an account.

    Workflow: Issue Card Request → Validate Account → Generate Card Details → Store Encrypted

    - **account_id**: ID of the account to link the card to
    - **cardholder_name**: Name to appear on the card (max 26 characters)
    - **card_type**: Type of card (debit, credit, prepaid)
    """
    logger.info(
        "Issue card endpoint called",
        extra={
            "user_id": current_user.id,
            "account_id": request.account_id,
            "card_type": request.card_type,
        },
    )

    result = card_service.issue_card(
        account_id=request.account_id,
        cardholder_name=request.cardholder_name,
        card_type=CardType[request.card_type.value.upper()],
    )

    logger.info(
        "Card issued successfully",
        extra={
            "user_id": current_user.id,
            "card_id": result.id,
            "account_id": request.account_id,
        },
    )
    return result


@router.get(
    "",
    response_model=List[CardResponse],
    summary="List all cards",
)
def list_cards(
    skip: int = 0,
    limit: int = 100,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """List all cards with pagination."""
    return card_service.get_all_cards(skip=skip, limit=limit)


@router.get(
    "/{card_id}",
    response_model=CardResponse,
    summary="Get card by ID",
)
def get_card(
    card_id: int,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific card by ID (without sensitive data)."""
    return card_service.get_card_by_id(card_id)


@router.get(
    "/{card_id}/details",
    response_model=CardDetailsResponse,
    summary="Get card details with sensitive data",
)
def get_card_details(
    card_id: int,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get full card details including decrypted PAN and CVV.

    WARNING: This endpoint returns sensitive data. Use only for authorized operations.
    """
    logger.warning(
        "Card details requested - sensitive data access",
        extra={"user_id": current_user.id, "card_id": card_id},
    )

    result = card_service.get_card_details(card_id)
    card = result["card"]

    return CardDetailsResponse(
        id=card.id,
        account_id=card.account_id,
        card_number_last4=card.card_number_last4,
        cardholder_name=card.cardholder_name,
        card_type=card.card_type.value,
        status=card.status.value,
        expiry_month=card.expiry_month,
        expiry_year=card.expiry_year,
        issued_at=card.issued_at,
        created_at=card.created_at,
        updated_at=card.updated_at,
        card_number=result["card_number"],
        cvv=result["cvv"],
    )


@router.get(
    "/{card_id}/masked",
    response_model=MaskedCardNumber,
    summary="Get masked card number",
)
def get_masked_card_number(
    card_id: int,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """Get card number in masked format (e.g., ****-****-****-1234)."""
    masked = card_service.get_masked_card_number(card_id)
    return MaskedCardNumber(masked_number=masked)


@router.get(
    "/account/{account_id}",
    response_model=List[CardResponse],
    summary="Get cards by account ID",
)
def get_cards_by_account(
    account_id: int,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """Get all cards for a specific account."""
    return card_service.get_cards_by_account(account_id)


@router.patch(
    "/{card_id}/status",
    response_model=CardResponse,
    summary="Update card status",
)
def update_card_status(
    card_id: int,
    status_update: CardStatusUpdate,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update card status.

    - **active**: Card is active and can be used
    - **inactive**: Card is temporarily inactive
    - **blocked**: Card is blocked (security)
    - **expired**: Card has expired
    """
    logger.info(
        "Update card status endpoint called",
        extra={
            "user_id": current_user.id,
            "card_id": card_id,
            "new_status": status_update.status,
        },
    )

    result = card_service.update_card_status(
        card_id, CardStatus[status_update.status.value.upper()]
    )

    logger.info(
        "Card status updated successfully",
        extra={"user_id": current_user.id, "card_id": card_id},
    )
    return result


@router.post(
    "/{card_id}/block",
    response_model=CardResponse,
    summary="Block a card",
)
def block_card(
    card_id: int,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """Block a card (security operation)."""
    logger.warning(
        "Block card endpoint called",
        extra={"user_id": current_user.id, "card_id": card_id},
    )

    result = card_service.block_card(card_id)

    logger.info(
        "Card blocked successfully",
        extra={"user_id": current_user.id, "card_id": card_id},
    )
    return result


@router.post(
    "/{card_id}/activate",
    response_model=CardResponse,
    summary="Activate a card",
)
def activate_card(
    card_id: int,
    card_service: CardService = Depends(get_card_service),
    current_user: User = Depends(get_current_active_user),
):
    """Activate a card."""
    logger.info(
        "Activate card endpoint called",
        extra={"user_id": current_user.id, "card_id": card_id},
    )

    result = card_service.activate_card(card_id)

    logger.info(
        "Card activated successfully",
        extra={"user_id": current_user.id, "card_id": card_id},
    )
    return result
