"""
Service for error logging operations.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.repositories.error_log_repository import ErrorLogRepository
from app.models.error_log import ErrorLog


logger = logging.getLogger(__name__)


class ErrorLogService:
    """Service for error logging business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ErrorLogRepository(db)

    def log_error(
        self,
        category: str,
        error_type: str,
        status_code: int,
        message: str,
        http_method: Optional[str] = None,
        endpoint: Optional[str] = None,
        stack_trace: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> ErrorLog:
        """
        Log an error to the database.

        All PII should be sanitized before calling this method.

        Args:
            category: Error category (validation, auth, server, database)
            error_type: Exception class name
            status_code: HTTP status code
            message: Sanitized error message
            http_method: HTTP method
            endpoint: API endpoint
            stack_trace: Sanitized stack trace
            user_id: User ID (if authenticated)
            request_id: Request ID for tracking
            context: Additional sanitized context

        Returns:
            Created ErrorLog instance
        """
        try:
            return self.repository.create(
                category=category,
                error_type=error_type,
                status_code=status_code,
                message=message,
                http_method=http_method,
                endpoint=endpoint,
                stack_trace=stack_trace,
                user_id=user_id,
                request_id=request_id,
                context=context,
            )
        except Exception as e:
            # If error logging fails, log to standard logger but don't crash
            logger.error(
                "Failed to log error to database",
                extra={"error": str(e), "original_error": error_type},
            )
            return None

    def get_errors(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """
        Get error logs with filtering and pagination.

        Returns:
            Dictionary with errors and metadata
        """
        errors = self.repository.get_all(
            skip=skip,
            limit=limit,
            category=category,
            endpoint=endpoint,
            status_code=status_code,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        total = self.repository.get_count(
            category=category,
            endpoint=endpoint,
            status_code=status_code,
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "errors": errors,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def get_error_by_id(self, error_id: int) -> Optional[ErrorLog]:
        """Get a specific error log by ID."""
        return self.repository.get_by_id(error_id)

    def get_recent_errors(self, hours: int = 24, limit: int = 100) -> List[ErrorLog]:
        """Get recent errors within the specified number of hours."""
        return self.repository.get_recent_errors(hours=hours, limit=limit)

    def get_error_summary(self, hours: int = 24) -> dict:
        """Get summary statistics of errors."""
        return self.repository.get_error_summary(hours=hours)

    def cleanup_old_errors(self, days: int = 90) -> int:
        """
        Clean up old error logs.

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted records
        """
        deleted = self.repository.delete_old_errors(days=days)
        logger.info(
            "Cleaned up old error logs",
            extra={"deleted_count": deleted, "retention_days": days},
        )
        return deleted
