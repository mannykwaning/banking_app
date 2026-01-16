"""
Repository for error log operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta

from app.models.error_log import ErrorLog


class ErrorLogRepository:
    """Repository for error log data access operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
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
        Create a new error log entry.

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
            context: Additional context

        Returns:
            Created ErrorLog instance
        """
        error_log = ErrorLog(
            category=category,
            error_type=error_type,
            http_method=http_method,
            endpoint=endpoint,
            status_code=status_code,
            message=message,
            stack_trace=stack_trace,
            user_id=user_id,
            request_id=request_id,
            context=context,
        )
        self.db.add(error_log)
        self.db.commit()
        self.db.refresh(error_log)
        return error_log

    def get_by_id(self, error_id: int) -> Optional[ErrorLog]:
        """Get an error log by ID."""
        return self.db.query(ErrorLog).filter(ErrorLog.id == error_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[ErrorLog]:
        """
        Get error logs with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            category: Filter by error category
            endpoint: Filter by endpoint
            status_code: Filter by HTTP status code
            user_id: Filter by user ID
            start_date: Filter errors after this date
            end_date: Filter errors before this date

        Returns:
            List of ErrorLog instances
        """
        query = self.db.query(ErrorLog)

        if category:
            query = query.filter(ErrorLog.category == category)
        if endpoint:
            query = query.filter(ErrorLog.endpoint.like(f"%{endpoint}%"))
        if status_code:
            query = query.filter(ErrorLog.status_code == status_code)
        if user_id:
            query = query.filter(ErrorLog.user_id == user_id)
        if start_date:
            query = query.filter(ErrorLog.timestamp >= start_date)
        if end_date:
            query = query.filter(ErrorLog.timestamp <= end_date)

        return query.order_by(desc(ErrorLog.timestamp)).offset(skip).limit(limit).all()

    def get_count(
        self,
        category: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Get count of error logs with optional filtering."""
        query = self.db.query(func.count(ErrorLog.id))

        if category:
            query = query.filter(ErrorLog.category == category)
        if endpoint:
            query = query.filter(ErrorLog.endpoint.like(f"%{endpoint}%"))
        if status_code:
            query = query.filter(ErrorLog.status_code == status_code)
        if start_date:
            query = query.filter(ErrorLog.timestamp >= start_date)
        if end_date:
            query = query.filter(ErrorLog.timestamp <= end_date)

        return query.scalar()

    def get_recent_errors(self, hours: int = 24, limit: int = 100) -> List[ErrorLog]:
        """Get recent errors within the specified number of hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.db.query(ErrorLog)
            .filter(ErrorLog.timestamp >= cutoff_time)
            .order_by(desc(ErrorLog.timestamp))
            .limit(limit)
            .all()
        )

    def get_error_summary(self, hours: int = 24) -> dict:
        """
        Get summary statistics of errors.

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary with error statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Total errors
        total = (
            self.db.query(func.count(ErrorLog.id))
            .filter(ErrorLog.timestamp >= cutoff_time)
            .scalar()
        )

        # Errors by category
        by_category = dict(
            self.db.query(ErrorLog.category, func.count(ErrorLog.id))
            .filter(ErrorLog.timestamp >= cutoff_time)
            .group_by(ErrorLog.category)
            .all()
        )

        # Errors by status code
        by_status = dict(
            self.db.query(ErrorLog.status_code, func.count(ErrorLog.id))
            .filter(ErrorLog.timestamp >= cutoff_time)
            .group_by(ErrorLog.status_code)
            .all()
        )

        # Top error endpoints
        top_endpoints = (
            self.db.query(ErrorLog.endpoint, func.count(ErrorLog.id))
            .filter(ErrorLog.timestamp >= cutoff_time, ErrorLog.endpoint.isnot(None))
            .group_by(ErrorLog.endpoint)
            .order_by(desc(func.count(ErrorLog.id)))
            .limit(10)
            .all()
        )

        return {
            "total_errors": total,
            "by_category": by_category,
            "by_status_code": by_status,
            "top_endpoints": [{"endpoint": e[0], "count": e[1]} for e in top_endpoints],
            "time_window_hours": hours,
        }

    def delete_old_errors(self, days: int = 90) -> int:
        """
        Delete error logs older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = (
            self.db.query(ErrorLog).filter(ErrorLog.timestamp < cutoff_date).delete()
        )
        self.db.commit()
        return deleted
