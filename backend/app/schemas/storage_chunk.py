"""
Storage Chunk Schemas - Pydantic models for chunk operations
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class StorageChunkBase(BaseModel):
    """Base schema for storage chunk"""

    chunk_index: int
    chunk_size: int
    encrypted_size: int
    checksum: str


class StorageChunkCreate(StorageChunkBase):
    """Schema for creating storage chunk (internal use only)"""

    file_id: UUID
    iv: bytes  # 12-byte IV (nonce)
    encryption_key_encrypted: str  # base64(encrypted_chunk_key)
    storage_path: str


class StorageChunkResponse(StorageChunkBase):
    """Schema for storage chunk response"""

    id: UUID
    file_id: UUID
    storage_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class StorageChunkListResponse(BaseModel):
    """Schema for list of storage chunks"""

    chunks: list[StorageChunkResponse]
    total: int
    file_id: UUID
