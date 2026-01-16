"""
Pydantic schemas for error logs.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorLogBase(BaseModel):
    """Base error log schema."""

    category: str = Field(
        ..., description="Error category: validation, auth, server, database"
    )
    error_type: str = Field(..., description="Exception class name")
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Sanitized error message")
    http_method: Optional[str] = Field(None, description="HTTP method")
    endpoint: Optional[str] = Field(None, description="API endpoint")
    user_id: Optional[str] = Field(None, description="User ID (if authenticated)")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class ErrorLogResponse(ErrorLogBase):
    """Error log response schema."""

    id: int
    timestamp: datetime
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

    class Config:
        from_attributes = True


class ErrorLogDetailResponse(ErrorLogResponse):
    """Detailed error log response with stack trace."""

    stack_trace: Optional[str] = Field(None, description="Sanitized stack trace")


class ErrorLogSummary(BaseModel):
    """Error log summary statistics."""

    total_errors: int
    by_category: Dict[str, int]
    by_status_code: Dict[int, int]
    top_endpoints: List[Dict[str, Any]]
    time_window_hours: int


class ErrorLogsListResponse(BaseModel):
    """Paginated list of error logs."""

    errors: List[ErrorLogResponse]
    total: int
    skip: int
    limit: int
