"""
Pytest configuration for unit tests.
"""

import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    """Create a mock database session for unit tests."""
    return Mock(spec=Session)


@pytest.fixture
def mock_account():
    """Create a mock account object."""
    from app.models import Account

    account = Mock(spec=Account)
    account.id = 1
    account.account_number = "1234567890"
    account.account_holder = "John Doe"
    account.account_type = "checking"
    account.balance = 1000.0
    return account


@pytest.fixture
def mock_transaction():
    """Create a mock transaction object."""
    from app.models import Transaction

    transaction = Mock(spec=Transaction)
    transaction.id = 1
    transaction.account_id = 1
    transaction.transaction_type = "deposit"
    transaction.amount = 100.0
    transaction.description = "Test deposit"
    return transaction
