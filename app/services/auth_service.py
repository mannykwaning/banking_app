"""
Authentication service for user authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, Token, TokenData
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        logger.info("Authentication attempt", extra={"username": username})

        user = self.user_repository.get_by_username(username)
        if not user:
            logger.warning(
                "Authentication failed - user not found", extra={"username": username}
            )
            return None
        if not self.verify_password(password, user.hashed_password):
            logger.warning(
                "Authentication failed - invalid password",
                extra={"username": username, "user_id": user.id},
            )
            return None

        logger.info(
            "Authentication successful",
            extra={"username": username, "user_id": user.id},
        )
        return user

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[TokenData]:
        """Decode and validate a JWT access token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            if username is None:
                logger.warning("Token validation failed - missing username in payload")
                return None
            logger.debug(
                "Token decoded successfully",
                extra={"username": username, "user_id": user_id},
            )
            return TokenData(username=username, user_id=user_id)
        except JWTError as e:
            logger.warning("Token validation failed", extra={"error": str(e)})
            return None

    def register_user(self, user_data: UserCreate, is_superuser: bool = False) -> User:
        """Register a new user with optional superuser privileges."""
        logger.info(
            "User registration attempt",
            extra={
                "username": user_data.username,
                "email": user_data.email,
                "is_superuser": is_superuser,
            },
        )

        # Check if user already exists
        if self.user_repository.exists_by_email(user_data.email):
            logger.warning(
                "Registration failed - email already exists",
                extra={"email": user_data.email},
            )
            raise ValueError("Email already registered")
        if self.user_repository.exists_by_username(user_data.username):
            logger.warning(
                "Registration failed - username already exists",
                extra={"username": user_data.username},
            )
            raise ValueError("Username already taken")

        # Hash password and create user
        hashed_password = self.get_password_hash(user_data.password)
        user = self.user_repository.create(
            user_data, hashed_password, is_superuser=is_superuser
        )

        logger.info(
            "User registered successfully",
            extra={
                "username": user.username,
                "user_id": user.id,
                "email": user.email,
                "is_superuser": user.is_superuser,
            },
        )
        return user

    def login(self, username: str, password: str) -> Token:
        """Login user and return access token."""
        logger.info("Login attempt", extra={"username": username})

        user = self.authenticate_user(username, password)
        if not user:
            logger.warning(
                "Login failed - authentication failed", extra={"username": username}
            )
            raise ValueError("Incorrect username or password")
        if not user.is_active:
            logger.warning(
                "Login failed - user account inactive",
                extra={"username": username, "user_id": user.id},
            )
            raise ValueError("User account is inactive")

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires,
        )

        logger.info(
            "Login successful", extra={"username": username, "user_id": user.id}
        )
        return Token(access_token=access_token, token_type="bearer")
