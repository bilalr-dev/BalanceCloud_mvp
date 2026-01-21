"""
Configuration for MVP v1 - PostgreSQL and Redis
"""

import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Database - PostgreSQL
    # REQUIRED: Set DATABASE_URL environment variable
    # Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Security
    # REQUIRED: Set via environment variables
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # Encryption
    # REQUIRED: Set via environment variables
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")

    # OAuth - Google Drive
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/cloud-accounts/callback/google_drive"
    )

    # OAuth - Microsoft OneDrive
    MICROSOFT_CLIENT_ID: str = os.getenv("MICROSOFT_CLIENT_ID", "")
    MICROSOFT_CLIENT_SECRET: str = os.getenv("MICROSOFT_CLIENT_SECRET", "")
    MICROSOFT_REDIRECT_URI: str = os.getenv(
        "MICROSOFT_REDIRECT_URI", "http://localhost:8000/api/cloud-accounts/callback/onedrive"
    )
    MICROSOFT_TENANT_ID: str = os.getenv("MICROSOFT_TENANT_ID", "common")

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
        os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")
    )

    # File Storage - Simple local directory
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./storage")
    
    # Staging Area - Temporary storage for uploads and encrypted chunks
    STAGING_PATH: str = os.getenv("STAGING_PATH", "./staging")
    STAGING_UPLOADS_PATH: str = os.getenv("STAGING_UPLOADS_PATH", "./staging/uploads")
    STAGING_ENCRYPTED_PATH: str = os.getenv("STAGING_ENCRYPTED_PATH", "./staging/encrypted")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        case_sensitive = True


settings = Settings()

# Validate required settings
if not settings.DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Set it in .env file or environment variables."
    )
if not settings.SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is required. "
        "Set it in .env file or environment variables."
    )
if not settings.JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY environment variable is required. "
        "Set it in .env file or environment variables."
    )
if not settings.ENCRYPTION_KEY:
    raise ValueError(
        "ENCRYPTION_KEY environment variable is required. "
        "Set it in .env file or environment variables."
    )
