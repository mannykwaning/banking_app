"""
Custom exception classes with proper categorization and HTTP status codes.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Base exception class for all application exceptions."""

    def __init__(
        self,
        detail: str,
        status_code: int,
        category: str,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.category = category
        self.context = context or {}


class ValidationException(BaseAppException):
    """Exception for validation errors (400 Bad Request)."""

    def __init__(
        self,
        detail: str,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            category="validation",
            context=context,
            headers=headers,
        )


class AuthenticationException(BaseAppException):
    """Exception for authentication errors (401 Unauthorized)."""

    def __init__(
        self,
        detail: str = "Could not validate credentials",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            category="auth",
            context=context,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(BaseAppException):
    """Exception for authorization errors (403 Forbidden)."""

    def __init__(
        self,
        detail: str = "Insufficient permissions",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            category="auth",
            context=context,
        )


class NotFoundException(BaseAppException):
    """Exception for resource not found errors (404 Not Found)."""

    def __init__(
        self,
        detail: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            category="validation",
            context=context,
        )


class DatabaseException(BaseAppException):
    """Exception for database errors (500 Internal Server Error)."""

    def __init__(
        self,
        detail: str = "Database operation failed",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            category="database",
            context=context,
        )


class ServerException(BaseAppException):
    """Exception for general server errors (500 Internal Server Error)."""

    def __init__(
        self,
        detail: str = "Internal server error",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            category="server",
            context=context,
        )


class BusinessLogicException(BaseAppException):
    """Exception for business logic violations (422 Unprocessable Entity)."""

    def __init__(
        self,
        detail: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            category="validation",
            context=context,
        )
