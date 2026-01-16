# Error Tracking and Reporting System

## Overview

The Banking App API implements a comprehensive error tracking and reporting system with the following features:

- **Exception Handling**: Proper HTTP status codes for all error types
- **Structured Logging**: Contextual error logging with sanitization
- **Error Categorization**: Automatic categorization (validation, auth, server, database)
- **PII Sanitization**: Automatic removal of sensitive data from error logs
- **Error Storage**: Database persistence for error analysis
- **Admin Reporting**: REST API endpoints for error monitoring and analysis

## Architecture

### Error Flow

```
Request → Exception Occurs → Global Handler → Sanitize PII → Log to DB + Logger → Response
```

### Components

1. **Custom Exceptions** ([app/core/exceptions.py](../app/core/exceptions.py))
   - Categorized exception classes with proper HTTP status codes
   - Includes context for better debugging

2. **Error Utilities** ([app/core/error_utils.py](../app/core/error_utils.py))
   - PII sanitization functions
   - Error categorization logic
   - Stack trace formatting

3. **Error Handlers** ([app/core/error_handlers.py](../app/core/error_handlers.py))
   - Global exception handlers
   - Automatic error logging to database
   - Consistent error response format

4. **Error Storage** ([app/models/error_log.py](../app/models/error_log.py))
   - Database model for error persistence
   - Indexed fields for efficient querying

5. **Admin API** ([app/api/v1/endpoints/admin_errors.py](../app/api/v1/endpoints/admin_errors.py))
   - Error reporting endpoints
   - Filtering and pagination
   - Summary statistics

## Error Categories

### 1. Validation Errors (400, 422)

**Category**: `validation`

Issues with request data, business logic violations, or constraint violations.

**Examples**:

- Invalid input format
- Missing required fields
- Business rule violations (insufficient balance, etc.)

**Usage**:

```python
from app.core.exceptions import ValidationException

raise ValidationException(
    detail="Transfer amount exceeds daily limit",
    context={"amount": 150000, "daily_limit": 100000}
)
```

### 2. Authentication Errors (401)

**Category**: `auth`

Issues with authentication and authorization.

**Examples**:

- Invalid credentials
- Expired tokens
- Missing authentication

**Usage**:

```python
from app.core.exceptions import AuthenticationException

raise AuthenticationException(
    detail="Invalid or expired token",
    context={"token_expired": True}
)
```

### 3. Authorization Errors (403)

**Category**: `auth`

User lacks permission to perform the action.

**Usage**:

```python
from app.core.exceptions import AuthorizationException

raise AuthorizationException(
    detail="You don't have permission to access this account",
    context={"required_role": "admin"}
)
```

### 4. Not Found Errors (404)

**Category**: `validation`

Requested resource doesn't exist.

**Usage**:

```python
from app.core.exceptions import NotFoundException

raise NotFoundException(
    detail=f"Account with ID {account_id} not found",
    context={"account_id": account_id}
)
```

### 5. Database Errors (500)

**Category**: `database`

Database operation failures.

**Usage**:

```python
from app.core.exceptions import DatabaseException

raise DatabaseException(
    detail="Failed to commit transaction",
    context={"operation": "transfer"}
)
```

### 6. Server Errors (500)

**Category**: `server`

General server errors and unexpected exceptions.

**Usage**:

```python
from app.core.exceptions import ServerException

raise ServerException(
    detail="Unexpected error processing request",
    context={"service": "external_api"}
)
```

## PII Sanitization

The system automatically sanitizes the following sensitive information:

### Patterns Sanitized

- **Credit Card Numbers**: `1234-5678-9012-3456` → `XXXX-XXXX-XXXX-****`
- **SSN**: `123-45-6789` → `XXX-XX-****`
- **Email**: `user@example.com` → `***@***.***`
- **Phone Numbers**: `(555) 123-4567` → `XXX-XXX-****`
- **Passwords**: `password=secret123` → `password=***REDACTED***`
- **CVV/CVC**: `cvv=123` → `cvv=***`
- **Account Numbers**: `account_number=1234567890` → `account_number=XXXXXXXX`
- **Routing Numbers**: `routing_number=123456789` → `routing_number=XXXXXXXXX`
- **API Keys**: `api_key=abc123xyz789` → `api_key=***REDACTED***`

### Sensitive Fields

The following field names are automatically redacted:

```python
password, passwd, pwd, secret, api_key, token, credit_card, 
card_number, cvv, cvc, ssn, social_security, pin, hashed_password,
access_token, refresh_token, account_number, routing_number
```

## Admin Error Endpoints

### Authentication Required 🔒

**All admin error endpoints require authentication with admin (superuser) privileges.**

To access these endpoints:

1. Login to get a JWT token
2. Include the token in the Authorization header: `Authorization: Bearer <your_token>`
3. User must have `is_superuser=True`

If you don't have admin privileges, you'll receive a 403 Forbidden error.

### Base URL

```
GET /api/v1/admin/errors
```

### 1. List Errors

**Endpoint**: `GET /api/v1/admin/errors`

**Query Parameters**:

- `skip` (int, default: 0): Pagination offset
- `limit` (int, default: 100, max: 500): Number of records
- `category` (string): Filter by category (validation, auth, server, database)
- `endpoint` (string): Filter by endpoint (partial match)
- `status_code` (int): Filter by HTTP status code
- `user_id` (string): Filter by user ID
- `start_date` (datetime): Start of date range (ISO format)
- `end_date` (datetime): End of date range (ISO format)

**Example Requests**:

```bash
# First, login to get a token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=adminpass" | jq -r '.access_token')

# Get last 50 authentication errors
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/errors?category=auth&limit=50"

# Get 500 errors from specific endpoint
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/errors?status_code=500&endpoint=/api/v1/transfers"

# Get errors in date range
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/errors?start_date=2026-01-01T00:00:00&end_date=2026-01-15T23:59:59"
```

**Response**:

```json
{
  "errors": [
    {
      "id": 123,
      "category": "validation",
      "error_type": "ValidationException",
      "status_code": 400,
      "message": "Insufficient balance. Available: $500.00, Required: $1000.00",
      "http_method": "POST",
      "endpoint": "/api/v1/transfers/internal",
      "user_id": "user-123",
      "request_id": "req-abc-xyz",
      "timestamp": "2026-01-15T10:30:00",
      "context": {
        "available": 500.0,
        "required": 1000.0
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### 2. Error Summary

**Endpoint**: `GET /api/v1/admin/errors/summary`

**Query Parameters**:

- `hours` (int, default: 24, max: 720): Time window in hours

**Example**:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/errors/summary?hours=24"
```

**Response**:

```json
{
  "total_errors": 42,
  "by_category": {
    "validation": 25,
    "auth": 10,
    "server": 5,
    "database": 2
  },
  "by_status_code": {
    "400": 20,
    "401": 10,
    "404": 7,
    "500": 5
  },
  "top_endpoints": [
    {
      "endpoint": "/api/v1/transfers/internal",
      "count": 15
    },
    {
      "endpoint": "/api/v1/auth/login",
      "count": 10
    }
  ],
  "time_window_hours": 24
}
```

### 3. Recent Errors

**Endpoint**: `GET /api/v1/admin/errors/recent`

**Query Parameters**:

- `hours` (int, default: 24, max: 168): Time window in hours
- `limit` (int, default: 100, max: 500): Number of records

**Example**:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/errors/recent?hours=1&limit=20"
```

### 4. Error Details

**Endpoint**: `GET /api/v1/admin/errors/{error_id}`

**Example**:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/errors/123"
```

**Response**:

```json
{
  "id": 123,
  "category": "database",
  "error_type": "DatabaseException",
  "status_code": 500,
  "message": "Failed to commit transaction",
  "http_method": "POST",
  "endpoint": "/api/v1/transfers/internal",
  "user_id": "user-123",
  "request_id": "req-abc-xyz",
  "timestamp": "2026-01-15T10:30:00",
  "context": {
    "operation": "transfer"
  },
  "stack_trace": "Traceback (most recent call last):\n  File \"...\", line 42, in execute_transfer\n    db.commit()\n..."
}
```

## Usage Examples

### In Service Layer

```python
from app.core.exceptions import (
    ValidationException,
    NotFoundException,
    DatabaseException,
)

class AccountService:
    def transfer_funds(self, source_id: int, dest_id: int, amount: float):
        # Check source account exists
        source = self.repository.get_by_id(source_id)
        if not source:
            raise NotFoundException(
                detail=f"Source account {source_id} not found",
                context={"account_id": source_id}
            )
        
        # Validate balance
        if source.balance < amount:
            raise ValidationException(
                detail=f"Insufficient balance. Available: ${source.balance:.2f}, Required: ${amount:.2f}",
                context={"available": source.balance, "required": amount}
            )
        
        try:
            # Perform transfer
            self.db.execute_transfer(source_id, dest_id, amount)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException(
                detail="Transfer failed due to database error",
                context={"operation": "transfer", "error": str(e)}
            )
```

### In API Endpoints

```python
from fastapi import APIRouter, Depends
from app.services.account_service import AccountService
from app.core.exceptions import ValidationException

router = APIRouter()

@router.post("/transfer")
def create_transfer(
    transfer_data: TransferCreate,
    service: AccountService = Depends(get_service),
):
    # Service raises exceptions automatically
    # Global error handler catches and logs them
    return service.transfer_funds(
        source_id=transfer_data.source_id,
        dest_id=transfer_data.dest_id,
        amount=transfer_data.amount,
    )
```

## Database Schema

### error_logs Table

```sql
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY,
    category VARCHAR(50) NOT NULL,           -- validation, auth, server, database
    error_type VARCHAR(100) NOT NULL,        -- Exception class name
    http_method VARCHAR(10),                 -- GET, POST, etc.
    endpoint VARCHAR(255),                   -- /api/v1/...
    status_code INTEGER NOT NULL,            -- 400, 401, 500, etc.
    message TEXT NOT NULL,                   -- Sanitized error message
    stack_trace TEXT,                        -- Sanitized stack trace
    user_id VARCHAR,                         -- User ID (if authenticated)
    request_id VARCHAR(100),                 -- Request tracking ID
    context JSON,                            -- Additional sanitized context
    timestamp DATETIME NOT NULL DEFAULT NOW,
    
    -- Indexes for efficient querying
    INDEX idx_category (category),
    INDEX idx_error_type (error_type),
    INDEX idx_endpoint (endpoint),
    INDEX idx_status_code (status_code),
    INDEX idx_user_id (user_id),
    INDEX idx_request_id (request_id),
    INDEX idx_timestamp (timestamp)
);
```

## Monitoring and Maintenance

### Log Retention

Error logs are stored indefinitely by default. To clean up old logs:

```python
from app.services.error_log_service import ErrorLogService

# Delete errors older than 90 days
service = ErrorLogService(db)
deleted_count = service.cleanup_old_errors(days=90)
```

### Alerting Integration

Monitor error rates using the summary endpoint:

```bash
#!/bin/bash
# Check error rate every 5 minutes
ERRORS=$(curl -s "http://localhost:8000/api/v1/admin/errors/summary?hours=1" | jq '.total_errors')

if [ "$ERRORS" -gt 100 ]; then
    echo "High error rate: $ERRORS errors in last hour"
    # Send alert
fi
```

## Best Practices

### 1. Use Appropriate Exception Types

Always use the most specific exception type:

```python
# Good
raise NotFoundException(detail="Account not found")

# Bad
raise HTTPException(status_code=404, detail="Account not found")
```

### 2. Include Context

Always include relevant context for debugging:

```python
raise ValidationException(
    detail="Transfer amount too large",
    context={
        "amount": amount,
        "limit": limit,
        "account_id": account_id,
    }
)
```

### 3. Never Log Sensitive Data Directly

Use the sanitization utilities:

```python
from app.core.error_utils import sanitize_dict

# Sanitize before logging
safe_context = sanitize_dict(user_input)
logger.error("Validation failed", extra={"context": safe_context})
```

### 4. Rollback Database Transactions

Always rollback on errors:

```python
try:
    db.execute_operation()
    db.commit()
except Exception as e:
    db.rollback()
    raise DatabaseException(detail="Operation failed")
```

## Testing

### Test Error Logging

```python
def test_error_logging():
    response = client.post("/api/v1/transfers/internal", json={
        "source_account_id": 999,  # Non-existent
        "destination_account_id": 1,
        "amount": 100,
    })
    
    assert response.status_code == 404
    
    # Check error was logged
    errors = client.get("/api/v1/admin/errors?endpoint=/api/v1/transfers")
    assert errors.json()["total"] > 0
```

### Test PII Sanitization

```python
from app.core.error_utils import sanitize_string

def test_sanitization():
    text = "Card: 1234-5678-9012-3456, CVV: 123"
    sanitized = sanitize_string(text)
    
    assert "1234-5678-9012-3456" not in sanitized
    assert "123" not in sanitized
    assert "XXXX-XXXX-XXXX-****" in sanitized
```

## Security Considerations

1. **PII Protection**: All error logs are automatically sanitized
2. **Access Control**: Admin endpoints require authentication with superuser privileges
3. **Authorization**: Only users with `is_superuser=True` can access error reports
4. **Rate Limiting**: Consider rate limiting error endpoints to prevent abuse
5. **Log Retention**: Implement log rotation and cleanup policies
6. **Stack Traces**: Stack traces are sanitized but may contain file paths
7. **Audit Trail**: All admin access to errors should be logged for compliance

## Related Documentation

- [Project Architecture](ARCHITECTURE.md)
- [Logging Configuration](LOGGING_GUIDE.md)
- [API Documentation](../README.md)
- [Security Best Practices](AUTH_GUIDE.md)
