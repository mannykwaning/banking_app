"""
Error log model for tracking and storing application errors.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from datetime import datetime

from app.core.database import Base


class ErrorLog(Base):
    """Error log model for tracking application errors with categorization."""

    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Error categorization
    category = Column(
        String(50), nullable=False, index=True
    )  # validation, auth, server, database
    error_type = Column(String(100), nullable=False, index=True)  # Exception class name

    # HTTP context
    http_method = Column(String(10), nullable=True)
    endpoint = Column(String(255), nullable=True, index=True)
    status_code = Column(Integer, nullable=False, index=True)

    # Error details
    message = Column(Text, nullable=False)  # Sanitized error message
    stack_trace = Column(Text, nullable=True)  # Full stack trace (sanitized)

    # User context (sanitized - no PII)
    user_id = Column(String, nullable=True, index=True)
    request_id = Column(String(100), nullable=True, index=True)

    # Additional context (sanitized)
    context = Column(JSON, nullable=True)  # Extra metadata

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<ErrorLog {self.id} - {self.category}:{self.error_type} at {self.timestamp}>"
