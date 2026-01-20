"""
Storage Chunk Model - Stores metadata for file chunks
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import BYTEA, UUID

from app.core.database import Base


class StorageChunk(Base):
    """Stores metadata for encrypted file chunks"""

    __tablename__ = "storage_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)  # Sequential index: 0, 1, 2, ...
    chunk_size = Column(Integer, nullable=False)  # Original size before encryption (bytes)
    encrypted_size = Column(
        Integer, nullable=False
    )  # Size of encrypted chunk including GCM tag (bytes)
    iv = Column(BYTEA, nullable=False)  # 12-byte IV (nonce) for AES-GCM
    encryption_key_encrypted = Column(
        String, nullable=False
    )  # Chunk key encrypted with user's master key (base64)
    checksum = Column(String(64), nullable=False)  # SHA-256 hash of encrypted chunk (hex)
    storage_path = Column(String, nullable=False)  # Path to encrypted chunk file on disk
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ensure one chunk per index per file
    __table_args__ = (UniqueConstraint("file_id", "chunk_index", name="uq_file_chunk_index"),)
