"""
Encryption Key Schemas - Pydantic models for encryption key operations
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EncryptionKeyBase(BaseModel):
    """Base schema for encryption key"""

    pass


class EncryptionKeyCreate(EncryptionKeyBase):
    """Schema for creating encryption key (internal use only)"""

    user_id: UUID
    key_encrypted: str  # base64(nonce + encrypted_key)
    salt: str  # base64(salt)


class EncryptionKeyResponse(EncryptionKeyBase):
    """Schema for encryption key response (metadata only, never returns actual key)"""

    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
