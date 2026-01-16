"""
Utilities for error handling, PII sanitization, and error logging.
"""

import re
import traceback
from typing import Dict, Any, Optional
from datetime import datetime


# PII patterns to sanitize
PII_PATTERNS = {
    # Credit card numbers (various formats)
    "card_number": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    # Social Security Numbers
    "ssn": re.compile(r"\b\d{3}[-]?\d{2}[-]?\d{4}\b"),
    # Email addresses
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    # Phone numbers (US format)
    "phone": re.compile(r"\b(\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b"),
    # Password fields
    "password": re.compile(
        r'(password|passwd|pwd)[\s]*[=:]\s*[\'"]?([^\s\'"]+)', re.IGNORECASE
    ),
    # CVV/CVC codes
    "cvv": re.compile(r"\b(cvv|cvc)[\s]*[=:]\s*\d{3,4}\b", re.IGNORECASE),
    # Account numbers (10+ digits)
    "account_number": re.compile(
        r"\baccount[_\s]?number[\s]*[=:]\s*\d{8,}\b", re.IGNORECASE
    ),
    # Routing numbers
    "routing_number": re.compile(
        r"\brouting[_\s]?number[\s]*[=:]\s*\d{9}\b", re.IGNORECASE
    ),
    # API keys and tokens
    "api_key": re.compile(
        r'(api[_-]?key|token|bearer)[\s]*[=:]\s*[\'"]?([a-zA-Z0-9_-]{20,})',
        re.IGNORECASE,
    ),
}

# Sensitive field names to redact
SENSITIVE_FIELDS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "api_key",
    "token",
    "credit_card",
    "card_number",
    "cvv",
    "cvc",
    "ssn",
    "social_security",
    "pin",
    "hashed_password",
    "access_token",
    "refresh_token",
    "account_number",
    "routing_number",
    "external_account_number",
}


def sanitize_string(text: str) -> str:
    """
    Sanitize a string by removing or masking PII.

    Args:
        text: String to sanitize

    Returns:
        Sanitized string with PII masked
    """
    if not text:
        return text

    sanitized = text

    # Replace PII patterns with masked versions
    sanitized = PII_PATTERNS["card_number"].sub("XXXX-XXXX-XXXX-****", sanitized)
    sanitized = PII_PATTERNS["ssn"].sub("XXX-XX-****", sanitized)
    sanitized = PII_PATTERNS["email"].sub("***@***.***", sanitized)
    sanitized = PII_PATTERNS["phone"].sub("XXX-XXX-****", sanitized)
    sanitized = PII_PATTERNS["password"].sub(r"\1=***REDACTED***", sanitized)
    sanitized = PII_PATTERNS["cvv"].sub(r"\1=***", sanitized)
    sanitized = PII_PATTERNS["account_number"].sub(
        r"account_number=XXXXXXXX", sanitized
    )
    sanitized = PII_PATTERNS["routing_number"].sub(
        r"routing_number=XXXXXXXXX", sanitized
    )
    sanitized = PII_PATTERNS["api_key"].sub(r"\1=***REDACTED***", sanitized)

    return sanitized


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize a dictionary by removing or masking sensitive fields.

    Args:
        data: Dictionary to sanitize

    Returns:
        Sanitized dictionary with sensitive data masked
    """
    if not isinstance(data, dict):
        return data

    sanitized = {}

    for key, value in data.items():
        # Check if key is a sensitive field
        if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                (
                    sanitize_dict(item)
                    if isinstance(item, dict)
                    else sanitize_string(str(item))
                )
                for item in value
            ]
        elif isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        else:
            sanitized[key] = value

    return sanitized


def sanitize_stack_trace(stack_trace: str) -> str:
    """
    Sanitize a stack trace by removing PII.

    Args:
        stack_trace: Stack trace string

    Returns:
        Sanitized stack trace
    """
    return sanitize_string(stack_trace)


def extract_error_context(
    exception: Exception, sanitize: bool = True
) -> Dict[str, Any]:
    """
    Extract context information from an exception.

    Args:
        exception: Exception to extract context from
        sanitize: Whether to sanitize the context

    Returns:
        Dictionary of error context
    """
    context = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
    }

    # Extract additional context from custom exceptions
    if hasattr(exception, "context") and exception.context:
        context["additional_context"] = exception.context

    if sanitize:
        context = sanitize_dict(context)

    return context


def get_stack_trace(exception: Exception, sanitize: bool = True) -> str:
    """
    Get sanitized stack trace from an exception.

    Args:
        exception: Exception to get stack trace from
        sanitize: Whether to sanitize the stack trace

    Returns:
        Stack trace string
    """
    stack_trace = "".join(
        traceback.format_exception(type(exception), exception, exception.__traceback__)
    )

    if sanitize:
        stack_trace = sanitize_stack_trace(stack_trace)

    return stack_trace


def categorize_exception(exception: Exception) -> str:
    """
    Categorize an exception into one of the standard categories.

    Args:
        exception: Exception to categorize

    Returns:
        Category string: validation, auth, server, or database
    """
    from app.core.exceptions import BaseAppException
    from sqlalchemy.exc import SQLAlchemyError

    # Check if it's a custom exception with category
    if isinstance(exception, BaseAppException):
        return exception.category

    # Check for database exceptions
    if isinstance(exception, SQLAlchemyError):
        return "database"

    # Check exception type name
    exception_name = type(exception).__name__.lower()

    if any(
        keyword in exception_name for keyword in ["validation", "value", "assertion"]
    ):
        return "validation"
    elif any(
        keyword in exception_name for keyword in ["auth", "permission", "credential"]
    ):
        return "auth"
    elif any(keyword in exception_name for keyword in ["database", "sql", "integrity"]):
        return "database"
    else:
        return "server"


def format_error_log_data(
    exception: Exception,
    status_code: int,
    endpoint: Optional[str] = None,
    http_method: Optional[str] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Format error data for logging to database.

    Args:
        exception: Exception that occurred
        status_code: HTTP status code
        endpoint: API endpoint where error occurred
        http_method: HTTP method (GET, POST, etc.)
        user_id: User ID (if authenticated)
        request_id: Request ID for tracking
        additional_context: Additional context to include

    Returns:
        Dictionary of sanitized error data ready for database storage
    """
    category = categorize_exception(exception)
    error_type = type(exception).__name__
    message = str(exception)
    stack_trace = get_stack_trace(exception, sanitize=True)

    context = extract_error_context(exception, sanitize=True)
    if additional_context:
        context.update(sanitize_dict(additional_context))

    return {
        "category": category,
        "error_type": error_type,
        "http_method": http_method,
        "endpoint": endpoint,
        "status_code": status_code,
        "message": sanitize_string(message),
        "stack_trace": stack_trace,
        "user_id": user_id,
        "request_id": request_id,
        "context": context,
        "timestamp": datetime.utcnow(),
    }
