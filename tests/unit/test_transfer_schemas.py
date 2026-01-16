"""
Unit tests for transfer schemas validation.
"""

import pytest
from pydantic import ValidationError

from app.schemas.transaction import (
    InternalTransferCreate,
    ExternalTransferCreate,
    TransferResponse,
)


class TestInternalTransferCreateSchema:
    """Test suite for InternalTransferCreate schema."""

    def test_valid_internal_transfer(self):
        """Test creating valid internal transfer schema."""
        data = {
            "source_account_id": 1,
            "destination_account_id": 2,
            "amount": 100.50,
            "description": "Test transfer",
        }

        transfer = InternalTransferCreate(**data)

        assert transfer.source_account_id == 1
        assert transfer.destination_account_id == 2
        assert transfer.amount == 100.50
        assert transfer.description == "Test transfer"

    def test_same_account_validation(self):
        """Test that same source and destination account raises error."""
        data = {
            "source_account_id": 1,
            "destination_account_id": 1,
            "amount": 100.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            InternalTransferCreate(**data)

        errors = exc_info.value.errors()
        # Check that destination_account_id validation failed
        assert any("destination_account_id" in str(error) for error in errors)

    def test_negative_amount(self):
        """Test that negative amount raises error."""
        data = {
            "source_account_id": 1,
            "destination_account_id": 2,
            "amount": -50.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            InternalTransferCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "amount" for error in errors)

    def test_zero_amount(self):
        """Test that zero amount raises error."""
        data = {
            "source_account_id": 1,
            "destination_account_id": 2,
            "amount": 0.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            InternalTransferCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "amount" for error in errors)

    def test_optional_description(self):
        """Test that description is optional."""
        data = {
            "source_account_id": 1,
            "destination_account_id": 2,
            "amount": 100.0,
        }

        transfer = InternalTransferCreate(**data)

        assert transfer.description is None

    def test_missing_required_fields(self):
        """Test that missing required fields raise error."""
        data = {"amount": 100.0}

        with pytest.raises(ValidationError) as exc_info:
            InternalTransferCreate(**data)

        errors = exc_info.value.errors()
        field_names = {error["loc"][0] for error in errors}
        assert "source_account_id" in field_names
        assert "destination_account_id" in field_names


class TestExternalTransferCreateSchema:
    """Test suite for ExternalTransferCreate schema."""

    def test_valid_external_transfer(self):
        """Test creating valid external transfer schema."""
        data = {
            "source_account_id": 1,
            "external_account_number": "1234567890",
            "external_bank_name": "Test Bank",
            "external_routing_number": "123456789",
            "amount": 500.0,
            "description": "External payment",
        }

        transfer = ExternalTransferCreate(**data)

        assert transfer.source_account_id == 1
        assert transfer.external_account_number == "1234567890"
        assert transfer.external_bank_name == "Test Bank"
        assert transfer.external_routing_number == "123456789"
        assert transfer.amount == 500.0

    def test_account_number_validation_too_short(self):
        """Test that account number less than 8 digits raises error."""
        data = {
            "source_account_id": 1,
            "external_account_number": "1234567",  # 7 digits
            "external_bank_name": "Test Bank",
            "external_routing_number": "123456789",
            "amount": 100.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            ExternalTransferCreate(**data)

        errors = exc_info.value.errors()
        assert any("external_account_number" in str(error) for error in errors)

    def test_account_number_validation_too_long(self):
        """Test that account number more than 20 digits raises error."""
        data = {
            "source_account_id": 1,
            "external_account_number": "123456789012345678901",  # 21 digits
            "external_bank_name": "Test Bank",
            "external_routing_number": "123456789",
            "amount": 100.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            ExternalTransferCreate(**data)

        errors = exc_info.value.errors()
        assert any("external_account_number" in str(error) for error in errors)

    def test_account_number_non_numeric(self):
        """Test that non-numeric account number raises error."""
        data = {
            "source_account_id": 1,
            "external_account_number": "12345ABC90",
            "external_bank_name": "Test Bank",
            "external_routing_number": "123456789",
            "amount": 100.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            ExternalTransferCreate(**data)

        errors = exc_info.value.errors()
        # Check that validation failed on external_account_number
        assert any("external_account_number" in str(error["loc"]) for error in errors)

    def test_routing_number_validation_wrong_length(self):
        """Test that routing number not exactly 9 digits raises error."""
        data = {
            "source_account_id": 1,
            "external_account_number": "1234567890",
            "external_bank_name": "Test Bank",
            "external_routing_number": "12345678",  # 8 digits
            "amount": 100.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            ExternalTransferCreate(**data)

        errors = exc_info.value.errors()
        assert any("external_routing_number" in str(error) for error in errors)

    def test_routing_number_non_numeric(self):
        """Test that non-numeric routing number raises error."""
        data = {
            "source_account_id": 1,
            "external_account_number": "1234567890",
            "external_bank_name": "Test Bank",
            "external_routing_number": "12345ABC9",
            "amount": 100.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            ExternalTransferCreate(**data)

        errors = exc_info.value.errors()
        # Check that validation failed on external_routing_number
        assert any("external_routing_number" in str(error["loc"]) for error in errors)

    def test_negative_amount(self):
        """Test that negative amount raises error."""
        data = {
            "source_account_id": 1,
            "external_account_number": "1234567890",
            "external_bank_name": "Test Bank",
            "external_routing_number": "123456789",
            "amount": -100.0,
        }

        with pytest.raises(ValidationError) as exc_info:
            ExternalTransferCreate(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "amount" for error in errors)

    def test_missing_required_fields(self):
        """Test that missing required fields raise error."""
        data = {"amount": 100.0}

        with pytest.raises(ValidationError) as exc_info:
            ExternalTransferCreate(**data)

        errors = exc_info.value.errors()
        field_names = {error["loc"][0] for error in errors}
        assert "source_account_id" in field_names
        assert "external_account_number" in field_names
        assert "external_bank_name" in field_names
        assert "external_routing_number" in field_names


class TestTransferResponseSchema:
    """Test suite for TransferResponse schema."""

    def test_valid_transfer_response(self):
        """Test creating valid transfer response schema."""
        from datetime import datetime

        data = {
            "transfer_id": "REF-123",
            "source_transaction_id": 1,
            "destination_transaction_id": 2,
            "transfer_type": "internal",
            "amount": 100.0,
            "status": "completed",
            "source_account_id": 1,
            "destination_account_id": 2,
            "description": "Test transfer",
            "created_at": datetime.utcnow(),
        }

        response = TransferResponse(**data)

        assert response.transfer_id == "REF-123"
        assert response.transfer_type == "internal"
        assert response.destination_account_id == 2

    def test_external_transfer_response(self):
        """Test transfer response with external account details."""
        from datetime import datetime

        data = {
            "transfer_id": "EXT-456",
            "source_transaction_id": 1,
            "transfer_type": "external",
            "amount": 500.0,
            "status": "pending",
            "source_account_id": 1,
            "description": "External transfer",
            "created_at": datetime.utcnow(),
            "external_account_number": "9876543210",
            "external_bank_name": "External Bank",
        }

        response = TransferResponse(**data)

        assert response.transfer_type == "external"
        assert response.external_account_number == "9876543210"
        assert response.external_bank_name == "External Bank"
        assert response.status == "pending"

    def test_optional_fields(self):
        """Test that optional fields can be None."""
        from datetime import datetime

        data = {
            "transfer_id": "REF-789",
            "source_transaction_id": 1,
            "transfer_type": "internal",
            "amount": 100.0,
            "status": "completed",
            "source_account_id": 1,
            "created_at": datetime.utcnow(),
        }

        response = TransferResponse(**data)

        assert response.description is None
        assert response.destination_account_id is None
        assert response.external_account_number is None
