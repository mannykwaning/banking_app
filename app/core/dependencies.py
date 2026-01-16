"""
FastAPI dependencies for dependency injection.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import AccountService, TransactionService
from app.services.auth_service import AuthService
from app.services.transfer_service import TransferService
from app.repositories.user_repository import UserRepository
from app.models.user import User


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    """Dependency to get AccountService instance."""
    return AccountService(db)


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    """Dependency to get TransactionService instance."""
    return TransactionService(db)


def get_transfer_service(db: Session = Depends(get_db)) -> TransferService:
    """Dependency to get TransferService instance."""
    return TransferService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance."""
    user_repository = UserRepository(db)
    return AuthService(user_repository)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    auth_service = AuthService(UserRepository(db))
    token_data = auth_service.decode_access_token(token)

    if token_data is None or token_data.username is None:
        raise credentials_exception

    # Get user from database
    user_repository = UserRepository(db)
    user = user_repository.get_by_username(token_data.username)

    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency to get current admin user (superuser)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource. Admin privileges required.",
        )
    return current_user
