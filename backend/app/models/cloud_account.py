"""
Cloud Account Model - Stores OAuth cloud provider accounts
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class CloudAccount(Base):
    """Stores OAuth cloud provider account information"""

    __tablename__ = "cloud_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = Column(String(50), nullable=False)  # 'google_drive', 'onedrive', 'dropbox'
    provider_account_id = Column(String(255), nullable=True)  # Provider's user ID
    access_token_encrypted = Column(String, nullable=False)  # Encrypted OAuth access token
    refresh_token_encrypted = Column(String, nullable=True)  # Encrypted OAuth refresh token
    token_expires_at = Column(DateTime, nullable=True)  # Token expiration timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ensure one account per provider per user
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_provider"),)
