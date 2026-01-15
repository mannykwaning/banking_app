"""
FastAPI dependencies for dependency injection.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import AccountService, TransactionService


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    """Dependency to get AccountService instance."""
    return AccountService(db)


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    """Dependency to get TransactionService instance."""
    return TransactionService(db)
