"""
Transaction Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from enum import Enum


class TransactionTypeEnum(str, Enum):
    """Transaction type enumeration."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"


class TransferTypeEnum(str, Enum):
    """Transfer type enumeration."""

    INTERNAL = "internal"
    EXTERNAL = "external"


class TransactionStatusEnum(str, Enum):
    """Transaction status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class TransactionBase(BaseModel):
    """Base schema for Transaction."""

    transaction_type: str = Field(
        ...,
        description="Type of transaction (deposit, withdrawal, transfer_out, transfer_in)",
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
    transfer_type: Optional[str] = None
    destination_account_id: Optional[int] = None
    external_account_number: Optional[str] = None
    external_bank_name: Optional[str] = None
    status: str = "completed"
    reference_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Transfer-specific schemas
class InternalTransferCreate(BaseModel):
    """Schema for creating an internal transfer."""

    source_account_id: int = Field(..., description="Source account ID")
    destination_account_id: int = Field(..., description="Destination account ID")
    amount: float = Field(..., gt=0, description="Transfer amount")
    description: Optional[str] = Field(None, description="Transfer description")

    @validator("destination_account_id")
    def validate_different_accounts(cls, v, values):
        """Ensure source and destination are different."""
        if "source_account_id" in values and v == values["source_account_id"]:
            raise ValueError("Source and destination accounts must be different")
        return v


class ExternalTransferCreate(BaseModel):
    """Schema for creating an external transfer."""

    source_account_id: int = Field(..., description="Source account ID")
    external_account_number: str = Field(
        ..., min_length=8, max_length=20, description="External account number"
    )
    external_bank_name: str = Field(
        ..., min_length=2, max_length=100, description="External bank name"
    )
    external_routing_number: str = Field(
        ..., min_length=9, max_length=9, description="Bank routing number"
    )
    amount: float = Field(..., gt=0, description="Transfer amount")
    description: Optional[str] = Field(None, description="Transfer description")

    @validator("external_account_number", "external_routing_number")
    def validate_numeric(cls, v):
        """Ensure account and routing numbers are numeric."""
        if not v.isdigit():
            raise ValueError("Account and routing numbers must contain only digits")
        return v


class TransferResponse(BaseModel):
    """Schema for transfer response."""

    transfer_id: str = Field(..., description="Unique transfer reference ID")
    source_transaction_id: int = Field(..., description="Source transaction ID")
    destination_transaction_id: Optional[int] = Field(
        None, description="Destination transaction ID (internal only)"
    )
    transfer_type: str = Field(..., description="Transfer type (internal/external)")
    amount: float = Field(..., description="Transfer amount")
    status: str = Field(..., description="Transfer status")
    source_account_id: int = Field(..., description="Source account ID")
    destination_account_id: Optional[int] = Field(
        None, description="Destination account ID (internal)"
    )
    external_account_number: Optional[str] = Field(
        None, description="External account number"
    )
    external_bank_name: Optional[str] = Field(None, description="External bank name")
    description: Optional[str] = Field(None, description="Transfer description")
    created_at: datetime = Field(..., description="Transfer creation time")

    class Config:
        from_attributes = True
