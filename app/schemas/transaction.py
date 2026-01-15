"""
Transaction Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TransactionBase(BaseModel):
    """Base schema for Transaction."""

    transaction_type: str = Field(
        ..., description="Type of transaction (deposit, withdrawal)"
    )
    amount: float = Field(..., gt=0, description="Transaction amount")
    description: Optional[str] = Field(None, description="Transaction description")


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""

    account_id: int = Field(..., description="Account ID")


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""

    id: int
    account_id: int
    created_at: datetime

    class Config:
        from_attributes = True
