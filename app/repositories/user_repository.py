"""
User repository for database operations.
"""

from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """Repository for User model operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self, user_data: UserCreate, hashed_password: str, is_superuser: bool = False
    ) -> User:
        """Create a new user with hashed password."""
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=is_superuser,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update(self, user: User) -> User:
        """Update user information."""
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Delete a user."""
        self.db.delete(user)
        self.db.commit()

    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return self.db.query(User).filter(User.email == email).first() is not None

    def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        return self.db.query(User).filter(User.username == username).first() is not None
