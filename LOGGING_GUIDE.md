# Logging Configuration Guide

## Overview

The banking app backend includes comprehensive structured logging functionality using JSON format for easy parsing and analysis. Logs are written to both console and file outputs with configurable log levels and directories.

## Features

- **Structured JSON Logging**: All logs are formatted as JSON for easy parsing by log aggregation tools
- **Configurable Log Levels**: Set log level via environment variable (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Configurable Log Directory**: Specify where log files should be stored
- **Automatic Log Rotation**: Log files automatically rotate when they reach 10MB (keeps 5 backup files)
- **Dual Output**: Logs are written to both console and files
- **Separate Error Logs**: Critical errors are also written to a dedicated error log file
- **Request Logging Middleware**: Automatically logs all HTTP requests with timing information
- **Contextual Logging**: Logs include relevant context like user IDs, account IDs, etc.

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```env
# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=logs
```

#### LOG_LEVEL Options

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious problems

#### LOG_DIR

- Specifies the directory where log files will be stored
- Default: `logs/`
- Directory will be created automatically if it doesn't exist
- Can be an absolute or relative path

## Log Files

When configured, the application creates the following log files in the `LOG_DIR`:

1. **`banking_app_api.log`** (or based on your `APP_NAME`)
   - Contains all logs at the configured log level and above
   - Rotates when it reaches 10MB
   - Keeps 5 backup files

2. **`banking_app_api_error.log`**
   - Contains only ERROR and CRITICAL level logs
   - Rotates when it reaches 10MB
   - Keeps 5 backup files

## Log Format

All logs are structured as JSON with the following fields:

```json
{
  "timestamp": "2026-01-15 14:30:45",
  "level": "INFO",
  "logger": "app.services.auth_service",
  "module": "auth_service",
  "function": "login",
  "line": 95,
  "process_id": 12345,
  "thread_id": 67890,
  "message": "Login successful",
  "username": "john_doe",
  "user_id": 1
}
```

### Standard Fields

- **timestamp**: When the log was created
- **level**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **logger**: Name of the logger (typically the module path)
- **module**: Python module name
- **function**: Function name where log was created
- **line**: Line number in the source code
- **process_id**: OS process ID
- **thread_id**: Thread ID

### Custom Context Fields

Logs include additional contextual information depending on the operation:

- **username**: Username for authentication operations
- **user_id**: User ID for authenticated operations
- **account_id**: Account ID for account operations
- **transaction_id**: Transaction ID for transaction operations
- **error**: Error message for failures

## Logging Locations

### Application Startup

- Database initialization
- Application startup and shutdown events

### HTTP Requests

- All incoming HTTP requests with method, path, client IP
- Response status code and processing time
- Processing time also added as `X-Process-Time` header

### Authentication

- User registration attempts and results
- Login attempts (success and failure)
- Token validation
- Password verification failures

### Accounts

- Account creation with account details
- Account retrieval
- Account deletion

### Transactions

- Transaction creation with type and amount
- Transaction validation failures
- Balance updates
- Insufficient balance warnings

## Usage Examples

### In Python Code

```python
import logging

logger = logging.getLogger(__name__)

# Simple log
logger.info("Operation completed")

# Log with context
logger.info(
    "User registered successfully",
    extra={
        "username": user.username,
        "user_id": user.id,
        "email": user.email
    }
)

# Warning with context
logger.warning(
    "Invalid transaction attempt",
    extra={
        "account_id": account_id,
        "amount": amount,
        "reason": "insufficient balance"
    }
)

# Error logging
try:
    risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        extra={
            "operation": "risky_operation",
            "error": str(e)
        },
        exc_info=True  # Include stack trace
    )
```

## Viewing Logs

### Console Output

When running the application, logs are displayed in the console in JSON format:

```bash
python main.py
```

### File Output

View log files directly:

```bash
# View all logs
tail -f logs/banking_app_api.log

# View only errors
tail -f logs/banking_app_api_error.log

# Search for specific events
grep "Login successful" logs/banking_app_api.log

# Pretty print JSON logs
tail logs/banking_app_api.log | python -m json.tool
```

### Using jq for Log Analysis

If you have `jq` installed, you can easily query and filter logs:

```bash
# Get all ERROR level logs
cat logs/banking_app_api.log | jq 'select(.level == "ERROR")'

# Get logs for a specific user
cat logs/banking_app_api.log | jq 'select(.user_id == 1)'

# Get all transaction-related logs
cat logs/banking_app_api.log | jq 'select(.logger | contains("transaction"))'

# Count logs by level
cat logs/banking_app_api.log | jq -r '.level' | sort | uniq -c
```

## Production Considerations

### Log Aggregation

In production, consider using log aggregation tools such as:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

These tools can easily parse the JSON logs and provide powerful search and visualization capabilities.

### Log Rotation

The application includes built-in log rotation (10MB per file, 5 backups). For production, you might also want to set up system-level log rotation using `logrotate` on Linux.

Example `/etc/logrotate.d/banking-app`:

```
/path/to/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    copytruncate
}
```

### Security Considerations

1. **Never log sensitive data**: Passwords, tokens, credit card numbers, etc.
2. **Sanitize user input**: Be careful logging user-provided data
3. **Log access controls**: Ensure log files have appropriate permissions (600 or 640)
4. **Regular cleanup**: Implement retention policies to manage log storage

### Performance

- Logging is asynchronous at the OS level
- File I/O is buffered for efficiency
- Consider adjusting log level in production (INFO or WARNING instead of DEBUG)
- Monitor disk space usage for log files

## Troubleshooting

### No logs appearing

1. Check `LOG_LEVEL` is not set too high (try DEBUG)
2. Verify `LOG_DIR` permissions
3. Check console output for initialization logs

### Log files not created

1. Verify `LOG_DIR` environment variable is set
2. Check directory permissions
3. Ensure sufficient disk space

### Large log files

1. Check log rotation is working (max 10MB per file)
2. Consider increasing log level to WARNING or ERROR in production
3. Implement log retention policies

## Best Practices

1. **Use appropriate log levels**:
   - DEBUG: Development troubleshooting
   - INFO: Normal business events
   - WARNING: Unexpected but handled situations
   - ERROR: Errors that should be investigated
   - CRITICAL: Critical failures requiring immediate attention

2. **Include context**: Always add relevant IDs and parameters in `extra`

3. **Be concise**: Log messages should be clear and actionable

4. **Don't log in loops**: Be careful with high-frequency operations

5. **Log exceptions properly**: Use `exc_info=True` to include stack traces

## Additional Resources

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [python-json-logger](https://github.com/madzak/python-json-logger)
- [12-Factor App Logging](https://12factor.net/logs)
