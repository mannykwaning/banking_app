"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class AccountBase(BaseModel):
    """Base schema for Account."""
    account_holder: str = Field(..., min_length=1, description="Name of the account holder")
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


class TransactionBase(BaseModel):
    """Base schema for Transaction."""
    transaction_type: str = Field(..., description="Type of transaction (deposit, withdrawal)")
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


class AccountWithTransactions(AccountResponse):
    """Schema for account with transactions."""
    transactions: List[TransactionResponse] = []
    
    class Config:
        from_attributes = True
