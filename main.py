"""
Main FastAPI application for the Banking App.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import random
import string

from config import settings
from database import get_db, create_tables, Account, Transaction
from schemas import (
    AccountCreate,
    AccountResponse,
    AccountWithTransactions,
    TransactionCreate,
    TransactionResponse
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A starter banking application backend API with FastAPI and SQLite",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Create tables on startup
@app.on_event("startup")
def startup_event():
    """Initialize database tables on startup."""
    create_tables()


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


# Helper function to generate account number
def generate_account_number() -> str:
    """Generate a random account number."""
    return ''.join(random.choices(string.digits, k=10))


# Account endpoints
@app.post(
    f"{settings.api_prefix}/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts"]
)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Create a new bank account."""
    # Generate unique account number
    account_number = generate_account_number()
    
    # Create new account
    db_account = Account(
        account_number=account_number,
        account_holder=account.account_holder,
        account_type=account.account_type,
        balance=account.initial_balance
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@app.get(
    f"{settings.api_prefix}/accounts",
    response_model=List[AccountResponse],
    tags=["Accounts"]
)
def list_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all bank accounts."""
    accounts = db.query(Account).offset(skip).limit(limit).all()
    return accounts


@app.get(
    f"{settings.api_prefix}/accounts/{{account_id}}",
    response_model=AccountWithTransactions,
    tags=["Accounts"]
)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """Get a specific account by ID with its transactions."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    return account


@app.delete(
    f"{settings.api_prefix}/accounts/{{account_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Accounts"]
)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Delete a bank account."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    
    db.delete(account)
    db.commit()
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
    # Check if account exists
    account = db.query(Account).filter(Account.id == transaction.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {transaction.account_id} not found"
        )
    
    # Validate transaction type
    if transaction.transaction_type not in ["deposit", "withdrawal"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type must be either 'deposit' or 'withdrawal'"
        )
    
    # Check sufficient balance for withdrawal
    if transaction.transaction_type == "withdrawal":
        if account.balance < transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance for withdrawal"
            )
        account.balance -= transaction.amount
    else:  # deposit
        account.balance += transaction.amount
    
    # Create transaction record
    db_transaction = Transaction(
        account_id=transaction.account_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@app.get(
    f"{settings.api_prefix}/transactions",
    response_model=List[TransactionResponse],
    tags=["Transactions"]
)
def list_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all transactions."""
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return transactions


@app.get(
    f"{settings.api_prefix}/transactions/{{transaction_id}}",
    response_model=TransactionResponse,
    tags=["Transactions"]
)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get a specific transaction by ID."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    return transaction


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
