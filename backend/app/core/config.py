"""
Configuration for MVP v1 - PostgreSQL and Redis
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database - PostgreSQL
    # Default is for local development only - use environment variables in production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://balancecloud:balancecloud_dev@localhost:5432/balancecloud_mvp",  # Dev default only
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Security
    # IMPORTANT: These defaults are for development only - MUST be set via environment variables in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-mvp")  # Dev default only
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production-mvp")  # Dev default only
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # Encryption
    # IMPORTANT: This default is for development only - MUST be set via environment variables in production
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "change-me-in-production-mvp")  # Dev default only

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

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        case_sensitive = True


settings = Settings()
