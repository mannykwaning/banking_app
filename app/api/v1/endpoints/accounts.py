"""
Account endpoints for the API.
"""

from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.schemas import (
    AccountCreate,
    AccountResponse,
    AccountWithTransactions,
    AccountStatementResponse,
)
from app.services import AccountService
from app.core.dependencies import get_account_service, get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
def create_account(
    account: AccountCreate,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new bank account."""
    logger.info(
        "Create account endpoint called",
        extra={"user_id": current_user.id, "account_type": account.account_type},
    )
    result = account_service.create_account(
        account_holder=account.account_holder,
        account_type=account.account_type,
        initial_balance=account.initial_balance,
    )
    logger.info(
        "Create account endpoint successful",
        extra={"user_id": current_user.id, "account_id": result.id},
    )
    return result


@router.get(
    "",
    response_model=List[AccountResponse],
    summary="List all accounts",
)
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_active_user),
):
    """List all bank accounts with pagination."""
    return account_service.get_all_accounts(skip=skip, limit=limit)


@router.get(
    "/{account_id}",
    response_model=AccountWithTransactions,
    summary="Get account by ID",
)
def get_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific account by ID with its transactions."""
    return account_service.get_account_by_id(account_id)


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an account",
)
def delete_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a bank account."""
    logger.info(
        "Delete account endpoint called",
        extra={"user_id": current_user.id, "account_id": account_id},
    )
    account_service.delete_account(account_id)
    logger.info(
        "Delete account endpoint successful",
        extra={"user_id": current_user.id, "account_id": account_id},
    )
    return None


@router.get(
    "/{account_id}/statement",
    response_model=AccountStatementResponse,
    summary="Generate account statement",
)
def generate_account_statement(
    account_id: int,
    start_date: Optional[datetime] = Query(
        None,
        description="Start date for statement period (ISO format). Defaults to 30 days ago.",
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="End date for statement period (ISO format). Defaults to now.",
    ),
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate an account statement with balance and transaction activity.

    Returns account details, current balance, and transaction summary
    for the specified period (defaults to last 30 days).
    """
    logger.info(
        "Generate account statement endpoint called",
        extra={
            "user_id": current_user.id,
            "account_id": account_id,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    statement = account_service.generate_account_statement(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
    )
    logger.info(
        "Generate account statement endpoint successful",
        extra={
            "user_id": current_user.id,
            "account_id": account_id,
            "transaction_count": statement["transaction_count"],
        },
    )
    return statement
