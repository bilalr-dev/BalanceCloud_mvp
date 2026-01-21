"""
Encryption Key Model - Stores encrypted user encryption keys
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class EncryptionKey(Base):
    """Stores user encryption keys encrypted with master key"""

    __tablename__ = "encryption_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One encryption key per user
        index=True,
    )
    key_encrypted = Column(
        String, nullable=False
    )  # base64(nonce + encrypted_key) - encrypted with master key
    salt = Column(
        String(64), nullable=False
    )  # base64(salt) - for future key derivation functions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
