"""
Main FastAPI application for the Banking App.
"""
from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager

from config import settings
from database import get_db, create_tables
from schemas import (
    AccountCreate,
    AccountResponse,
    AccountWithTransactions,
    TransactionCreate,
    TransactionResponse
)
from services import AccountService, TransactionService


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    create_tables()
    yield


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A starter banking application backend API with FastAPI and SQLite",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - health check."""
    return {
        "message": "Welcome to the Banking App API",
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


# Account endpoints
@app.post(
    f"{settings.api_prefix}/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts"]
)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Create a new bank account."""
    service = AccountService(db)
    return service.create_account(account)


@app.get(
    f"{settings.api_prefix}/accounts",
    response_model=List[AccountResponse],
    tags=["Accounts"]
)
def list_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all bank accounts."""
    service = AccountService(db)
    return service.list_accounts(skip=skip, limit=limit)


@app.get(
    f"{settings.api_prefix}/accounts/{{account_id}}",
    response_model=AccountWithTransactions,
    tags=["Accounts"]
)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """Get a specific account by ID with its transactions."""
    service = AccountService(db)
    return service.get_account(account_id)


@app.delete(
    f"{settings.api_prefix}/accounts/{{account_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Accounts"]
)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Delete a bank account."""
    service = AccountService(db)
    service.delete_account(account_id)
    return None


# Transaction endpoints
@app.post(
    f"{settings.api_prefix}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Transactions"]
)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction (deposit or withdrawal)."""
    service = TransactionService(db)
    return service.create_transaction(transaction)


@app.get(
    f"{settings.api_prefix}/transactions",
    response_model=List[TransactionResponse],
    tags=["Transactions"]
)
def list_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all transactions."""
    service = TransactionService(db)
    return service.list_transactions(skip=skip, limit=limit)


@app.get(
    f"{settings.api_prefix}/transactions/{{transaction_id}}",
    response_model=TransactionResponse,
    tags=["Transactions"]
)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get a specific transaction by ID."""
    service = TransactionService(db)
    return service.get_transaction(transaction_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

