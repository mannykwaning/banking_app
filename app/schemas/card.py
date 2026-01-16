"""
Card Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum


class CardTypeEnum(str, Enum):
    """Card type enumeration."""

    DEBIT = "debit"
    CREDIT = "credit"
    PREPAID = "prepaid"


class CardStatusEnum(str, Enum):
    """Card status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    EXPIRED = "expired"


class CardIssueRequest(BaseModel):
    """Schema for requesting a new card."""

    account_id: int = Field(..., description="ID of the account to link the card to")
    cardholder_name: str = Field(..., min_length=1, description="Name on the card")
    card_type: CardTypeEnum = Field(..., description="Type of card to issue")

    @field_validator("cardholder_name")
    @classmethod
    def validate_cardholder_name(cls, v: str) -> str:
        """Validate cardholder name format."""
        if not v.strip():
            raise ValueError("Cardholder name cannot be empty")
        if len(v) > 26:  # Standard card name length limit
            raise ValueError("Cardholder name too long (max 26 characters)")
        return v.upper()  # Card names are typically uppercase


class CardResponse(BaseModel):
    """Schema for card response (without sensitive data)."""

    id: int
    account_id: int
    card_number_last4: str
    cardholder_name: str
    card_type: CardTypeEnum
    status: CardStatusEnum
    expiry_month: int
    expiry_year: int
    issued_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CardDetailsResponse(CardResponse):
    """Schema for card details with sensitive data (use carefully)."""

    card_number: str = Field(..., description="Full card number (masked for display)")
    cvv: str = Field(..., description="Card CVV")


class CardStatusUpdate(BaseModel):
    """Schema for updating card status."""

    status: CardStatusEnum = Field(..., description="New card status")


class MaskedCardNumber(BaseModel):
    """Schema for displaying masked card number."""

    masked_number: str = Field(
        ..., description="Masked card number (e.g., ****-****-****-1234)"
    )
