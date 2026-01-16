"""
Structured logging configuration for the Banking App API.
Uses JSON formatting for structured logs with configurable levels and output.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Literal
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to the log record."""
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add process/thread info
        log_record["process_id"] = record.process
        log_record["thread_id"] = record.thread


class CustomTextFormatter(logging.Formatter):
    """Custom text formatter for human-readable structured logging."""

    def format(self, record):
        """Format the log record with custom fields."""
        # Add custom attributes to the record
        record.timestamp = self.formatTime(record, self.datefmt)
        record.level = record.levelname
        record.logger = record.name

        # Format the base message
        formatted = super().format(record)

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            extra_str = " ".join(f"{k}={v}" for k, v in record.extra_data.items())
            formatted = f"{formatted} | {extra_str}"

        return formatted


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    app_name: str = "banking_app",
    log_format: Literal["json", "text"] = "json",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    message_format: str = "%(timestamp)s %(level)s %(name)s %(message)s",
) -> None:
    """
    Setup structured logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files. If None, only console logging is enabled
        app_name: Application name for log files
        log_format: Log format - "json" for structured JSON logs, "text" for human-readable logs
        date_format: Date format string for timestamps
        message_format: Message format string (used for both JSON and text formatting)
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create formatter based on log_format setting
    if log_format.lower() == "json":
        formatter = CustomJsonFormatter(message_format, datefmt=date_format)
    else:
        # For text format, convert to standard logging format
        text_format = message_format.replace("%(timestamp)s", "%(asctime)s")
        text_format = text_format.replace("%(level)s", "%(levelname)s")
        text_format = text_format.replace("%(logger)s", "%(name)s")
        formatter = CustomTextFormatter(text_format, datefmt=date_format)

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handlers if log directory is provided
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Main log file with rotation
        main_log_file = log_path / f"{app_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Error log file (only ERROR and CRITICAL)
        error_log_file = log_path / f"{app_name}_error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

    # Log the initialization
    logging.info(
        "Logging initialized",
        extra={
            "log_level": log_level,
            "log_dir": log_dir,
            "app_name": app_name,
            "log_format": log_format,
            "date_format": date_format,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
