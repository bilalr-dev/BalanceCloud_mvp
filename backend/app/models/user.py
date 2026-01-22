"""
User Model - PostgreSQL with UUID
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


def get_default_storage_quota():
    """Get default storage quota from settings at runtime"""
    from app.core.config import settings
    return settings.DEFAULT_STORAGE_QUOTA_BYTES


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    storage_quota_bytes = Column(BigInteger, default=get_default_storage_quota, nullable=False)  # Storage quota in bytes (default: 10 GB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
