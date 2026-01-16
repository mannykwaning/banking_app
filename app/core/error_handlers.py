"""
Global exception handlers and error tracking middleware.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import logging
import uuid

from app.core.exceptions import BaseAppException
from app.core.error_utils import format_error_log_data, sanitize_dict
from app.services.error_log_service import ErrorLogService
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


async def log_error_to_database(
    request: Request,
    exception: Exception,
    status_code: int,
):
    """
    Log error to database with sanitization.

    Args:
        request: FastAPI request object
        exception: Exception that occurred
        status_code: HTTP status code
    """
    try:
        # Get user ID from request state if authenticated
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = getattr(request.state.user, "id", None)

        # Generate request ID if not present
        request_id = str(uuid.uuid4())

        # Format error data with sanitization
        error_data = format_error_log_data(
            exception=exception,
            status_code=status_code,
            endpoint=str(request.url.path),
            http_method=request.method,
            user_id=user_id,
            request_id=request_id,
        )

        # Log to database in a separate session
        db = SessionLocal()
        try:
            error_service = ErrorLogService(db)
            error_service.log_error(**error_data)
        finally:
            db.close()

    except Exception as e:
        # If error logging fails, log to standard logger
        logger.error(
            "Failed to log error to database",
            extra={"error": str(e)},
        )


async def base_app_exception_handler(request: Request, exc: BaseAppException):
    """
    Handle custom application exceptions.

    Args:
        request: FastAPI request object
        exc: Custom application exception

    Returns:
        JSON response with error details
    """
    # Log error to structured logging
    logger.error(
        f"{exc.category} error: {exc.detail}",
        extra={
            "category": exc.category,
            "status_code": exc.status_code,
            "endpoint": request.url.path,
            "method": request.method,
            "context": sanitize_dict(exc.context) if exc.context else {},
        },
    )

    # Log to database
    await log_error_to_database(request, exc, exc.status_code)

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSON response with validation error details
    """
    errors = exc.errors()

    # Log validation error
    logger.warning(
        "Validation error",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
            "errors": sanitize_dict({"validation_errors": errors}),
        },
    )

    # Log to database
    await log_error_to_database(request, exc, status.HTTP_422_UNPROCESSABLE_ENTITY)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Any unhandled exception

    Returns:
        JSON response with generic error message
    """
    # Log error to structured logging
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "endpoint": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )

    # Log to database
    await log_error_to_database(request, exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Return generic error message (don't expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Custom application exceptions
    app.add_exception_handler(BaseAppException, base_app_exception_handler)

    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered")
