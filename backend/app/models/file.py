"""
File Model - PostgreSQL with UUID
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)  # Virtual path (e.g., "/folder/file.txt")
    size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String, nullable=True)
    is_folder = Column(Boolean, default=False)
    parent_id = Column(
        UUID(as_uuid=True), ForeignKey("files.id"), nullable=True
    )  # For folder hierarchy
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Storage info - for chunked storage
    # Note: For chunked files, storage_path is removed
    # Chunks are stored in storage_chunks table with references to this file
    # For backward compatibility with non-chunked files, storage_path can be nullable
    storage_path = Column(String, nullable=True)  # Legacy: Path to encrypted file (for non-chunked files)
