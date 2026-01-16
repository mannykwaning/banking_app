"""
Core configuration module for the Banking App API.
Loads environment variables from .env file based on ENVIRONMENT variable.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
import os
from typing import List


def generate_secret_key() -> str:
    """Generate a secure random secret key."""
    return secrets.token_hex(32)


def get_env_file() -> str:
    """
    Determine which .env file to load based on ENVIRONMENT variable.

    Priority:
    1. ENVIRONMENT variable (e.g., 'development', 'test', 'production')
    2. Falls back to .env if no ENVIRONMENT is set

    Returns:
        Path to the .env file to load
    """
    environment = os.getenv("ENVIRONMENT", "development")
    env_file = f".env.{environment}"

    # Check if environment-specific file exists, otherwise use default .env
    if os.path.exists(env_file):
        return env_file
    elif os.path.exists(".env"):
        return ".env"
    else:
        # No env file found, will use defaults
        return ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "development"

    # Database Configuration
    database_url: str = "sqlite:///:memory:"

    # Application Configuration
    app_name: str = "Banking App API"
    app_version: str = "1.0.0"
    debug: bool = True

    # API Configuration
    api_v1_prefix: str = "/api/v1"

    # Security - Generate a random key if not provided
    secret_key: str = generate_secret_key()

    # Logging Configuration
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_format: str = "json"  # "json" or "text"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"  # Date format for logs
    log_message_format: str = (
        "%(timestamp)s %(level)s %(name)s %(message)s"  # Format for structured logs
    )

    # Admin Setup (for creating initial superuser)
    admin_setup_key: str = (
        "change-me-in-production-admin-setup-key"  # Secret key for creating admin users
    )

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Transfer Limits Configuration
    max_transfer_amount: float = 100000.0  # Maximum single transfer amount
    daily_transfer_limit: float = 500000.0  # Maximum daily transfer amount per account
    min_transfer_amount: float = 0.01  # Minimum transfer amount
    max_external_transfer_amount: float = 50000.0  # Maximum external transfer amount

    # Account balance limits
    min_account_balance: float = 0.0  # Minimum balance to maintain

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Allow extra fields for flexibility
        extra="ignore",
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() in ["development", "dev"]

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() in ["production", "prod"]

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.environment.lower() == "test"


# Create a global settings instance
settings = Settings()
