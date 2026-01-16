"""
Account Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class AccountBase(BaseModel):
    """Base schema for Account."""

    account_holder: str = Field(
        ..., min_length=1, description="Name of the account holder"
    )
    account_type: str = Field(..., description="Type of account (checking, savings)")


class AccountCreate(AccountBase):
    """Schema for creating a new account."""

    initial_balance: float = Field(default=0.0, ge=0, description="Initial balance")


class AccountResponse(AccountBase):
    """Schema for account response."""

    id: int
    account_number: str
    balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountWithTransactions(AccountResponse):
    """Schema for account with transactions."""

    transactions: List["TransactionResponse"] = []

    class Config:
        from_attributes = True


class AccountStatementResponse(BaseModel):
    """Schema for account statement with balance and activity."""

    account_id: int = Field(..., description="Account ID")
    account_number: str = Field(..., description="Account number")
    account_holder: str = Field(..., description="Name of the account holder")
    account_type: str = Field(..., description="Type of account")
    current_balance: float = Field(..., description="Current account balance")
    statement_period: dict = Field(
        ..., description="Statement period with start and end dates"
    )
    total_deposits: float = Field(
        default=0.0, description="Total deposits in the period"
    )
    total_withdrawals: float = Field(
        default=0.0, description="Total withdrawals in the period"
    )
    total_transfers_in: float = Field(
        default=0.0, description="Total transfers in during the period"
    )
    total_transfers_out: float = Field(
        default=0.0, description="Total transfers out during the period"
    )
    transaction_count: int = Field(
        default=0, description="Total number of transactions"
    )
    transactions: List["TransactionResponse"] = Field(
        default=[], description="List of transactions in the period"
    )
    created_at: datetime = Field(..., description="Statement generation date")

    class Config:
        from_attributes = True


# Forward reference resolution
from app.schemas.transaction import TransactionResponse

AccountWithTransactions.model_rebuild()
AccountStatementResponse.model_rebuild()
