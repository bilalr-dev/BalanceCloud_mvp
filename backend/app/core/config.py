"""
Configuration for MVP v1 - PostgreSQL and Redis

All sensitive values (SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY, OAuth credentials)
MUST be set via environment variables in .env file or system environment.
No hardcoded values are allowed for security reasons.
"""

from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All sensitive values must be provided via .env file or environment variables.
    See env.example for required variables.
    """
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Database - PostgreSQL
    # REQUIRED: Set DATABASE_URL environment variable
    # Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    # REQUIRED: Set via environment variables in .env file
    # Generate with: openssl rand -hex 32
    SECRET_KEY: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Encryption
    # REQUIRED: Set via environment variables in .env file
    # Generate with: openssl rand -hex 32
    ENCRYPTION_KEY: str = ""

    # OAuth - Google Drive
    # REQUIRED if using Google Drive integration
    # Get from: https://console.cloud.google.com/apis/credentials
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # OAuth - Microsoft OneDrive
    # REQUIRED if using OneDrive integration
    # Get from: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_REDIRECT_URI: str = ""
    MICROSOFT_TENANT_ID: str = "common"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # File Storage - Simple local directory
    STORAGE_PATH: str = "./storage"
    
    # Staging Area - Temporary storage for uploads and encrypted chunks
    STAGING_PATH: str = "./staging"
    STAGING_UPLOADS_PATH: str = "./staging/uploads"
    STAGING_ENCRYPTED_PATH: str = "./staging/encrypted"

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"


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
