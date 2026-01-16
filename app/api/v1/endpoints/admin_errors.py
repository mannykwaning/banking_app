"""
Admin endpoints for error monitoring and reporting.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.error_log import (
    ErrorLogResponse,
    ErrorLogDetailResponse,
    ErrorLogSummary,
    ErrorLogsListResponse,
)
from app.services.error_log_service import ErrorLogService
from app.core.dependencies import get_db, get_current_admin_user
from app.core.exceptions import NotFoundException
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/errors", tags=["Admin - Error Tracking"])


def get_error_log_service(db: Session = Depends(get_db)) -> ErrorLogService:
    """Dependency to get error log service."""
    return ErrorLogService(db)


@router.get(
    "",
    response_model=ErrorLogsListResponse,
    summary="Get error logs",
    description="Retrieve error logs with filtering and pagination. Supports filtering by category, endpoint, status code, date range, and more.",
)
def get_errors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    category: Optional[str] = Query(
        None, description="Filter by category: validation, auth, server, database"
    ),
    endpoint: Optional[str] = Query(
        None, description="Filter by endpoint (partial match)"
    ),
    status_code: Optional[int] = Query(None, description="Filter by HTTP status code"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(
        None, description="Filter errors after this date (ISO format)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter errors before this date (ISO format)"
    ),
    error_service: ErrorLogService = Depends(get_error_log_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get paginated list of error logs with optional filtering.

    **Filters:**
    - category: validation, auth, server, database
    - endpoint: Partial match on endpoint path
    - status_code: HTTP status code (400, 401, 404, 500, etc.)
    - user_id: Filter by specific user
    - start_date/end_date: Date range in ISO format

    **Example:**
    - `/admin/errors?category=auth&status_code=401&limit=50`
    - `/admin/errors?endpoint=/api/v1/accounts&start_date=2026-01-01T00:00:00`
    """
    logger.info(
        "Fetching error logs",
        extra={
            "skip": skip,
            "limit": limit,
            "category": category,
            "endpoint": endpoint,
        },
    )

    result = error_service.get_errors(
        skip=skip,
        limit=limit,
        category=category,
        endpoint=endpoint,
        status_code=status_code,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )

    return ErrorLogsListResponse(**result)


@router.get(
    "/summary",
    response_model=ErrorLogSummary,
    summary="Get error summary",
    description="Get summary statistics of errors including counts by category, status code, and top failing endpoints.",
)
def get_error_summary(
    hours: int = Query(
        24, ge=1, le=720, description="Number of hours to look back (max 30 days)"
    ),
    error_service: ErrorLogService = Depends(get_error_log_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get error summary statistics.

    Returns aggregated error data including:
    - Total error count
    - Breakdown by category (validation, auth, server, database)
    - Breakdown by HTTP status code
    - Top 10 endpoints with most errors

    **Example:**
    - `/admin/errors/summary?hours=24` - Last 24 hours
    - `/admin/errors/summary?hours=168` - Last 7 days
    """
    logger.info("Fetching error summary", extra={"hours": hours})
    return error_service.get_error_summary(hours=hours)


@router.get(
    "/recent",
    response_model=list[ErrorLogResponse],
    summary="Get recent errors",
    description="Get most recent errors within specified time window.",
)
def get_recent_errors(
    hours: int = Query(
        24, ge=1, le=168, description="Number of hours to look back (max 7 days)"
    ),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    error_service: ErrorLogService = Depends(get_error_log_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get recent errors within the specified time window.

    Returns errors ordered by most recent first.

    **Example:**
    - `/admin/errors/recent?hours=1` - Last hour
    - `/admin/errors/recent?hours=24&limit=50` - Last 24 hours, max 50 records
    """
    logger.info("Fetching recent errors", extra={"hours": hours, "limit": limit})
    errors = error_service.get_recent_errors(hours=hours, limit=limit)
    return errors


@router.get(
    "/{error_id}",
    response_model=ErrorLogDetailResponse,
    summary="Get error details",
    description="Get detailed information about a specific error including full stack trace.",
)
def get_error_detail(
    error_id: int,
    error_service: ErrorLogService = Depends(get_error_log_service),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get detailed information about a specific error.

    Includes full sanitized stack trace and all context information.
    """
    logger.debug("Fetching error detail", extra={"error_id": error_id})

    error = error_service.get_error_by_id(error_id)
    if not error:
        raise NotFoundException(
            detail=f"Error log with ID {error_id} not found",
            context={"error_id": error_id},
        )

    return error
