"""
Configuration module for the Banking App API.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "sqlite:///./banking.db"
    
    # Application Configuration
    app_name: str = "Banking App API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Configuration
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create a global settings instance
settings = Settings()
