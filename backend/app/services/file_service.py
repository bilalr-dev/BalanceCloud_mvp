"""
Simplified File Service for MVP - Local storage only
"""

import os
from pathlib import Path
from typing import Optional
from uuid import uuid4

import aiofiles
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.file import File
from app.services.encryption_service import encryption_service


class FileService:
    """Simplified file service - local storage with encryption"""

    def __init__(self):
        self.storage_path = Path(settings.STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_user_storage_path(self, user_id: str) -> Path:
        """Get storage directory for a user"""
        user_dir = self.storage_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    async def create_folder(
        self, db: AsyncSession, user_id: str, name: str, parent_id: Optional[str] = None
    ) -> File:
        """Create a folder"""
        # Build path
        if parent_id:
            parent = await self.get_file(db, user_id, parent_id)
            if not parent:
                raise ValueError("Parent folder not found")
            path = f"{parent.path.rstrip('/')}/{name}"
        else:
            path = f"/{name}"

        # Check if folder already exists
        result = await db.execute(
            select(File).where(
                and_(File.user_id == user_id, File.path == path, File.is_folder == True)
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Folder already exists")

        folder = File(
            user_id=user_id,
            name=name,
            path=path,
            size=0,
            is_folder=True,
            parent_id=parent_id,
            storage_path="",  # Folders don't have storage
        )
        db.add(folder)
        await db.commit()
        await db.refresh(folder)
        return folder

    async def save_file(
        self,
        db: AsyncSession,
        user_id: str,
        name: str,
        file_data: bytes,
        mime_type: Optional[str],
        parent_id: Optional[str] = None,
        user_key: bytes = None,
    ) -> File:
        """Save an encrypted file"""
        # Build path
        if parent_id:
            parent = await self.get_file(db, user_id, parent_id)
            if not parent:
                raise ValueError("Parent folder not found")
            path = f"{parent.path.rstrip('/')}/{name}"
        else:
            path = f"/{name}"

        # Encrypt file
        if user_key is None:
            # Generate a simple key for MVP (in production, get from user's encryption key)
            user_key = encryption_service.generate_user_key()

        encrypted_data, nonce = encryption_service.encrypt_file(file_data, user_key)

        # Save to disk
        file_id = uuid4()
        user_storage = self._get_user_storage_path(str(user_id))
        storage_file_path = user_storage / f"{file_id}.enc"
        nonce_file_path = user_storage / f"{file_id}.nonce"

        async with aiofiles.open(storage_file_path, "wb") as f:
            await f.write(encrypted_data)
        async with aiofiles.open(nonce_file_path, "wb") as f:
            await f.write(nonce)

        # Store metadata
        file = File(
            id=file_id,
            user_id=user_id,
            name=name,
            path=path,
            size=len(file_data),  # Original size
            mime_type=mime_type,
            is_folder=False,
            parent_id=parent_id,
            storage_path=str(storage_file_path),
        )
        db.add(file)
        await db.commit()
        await db.refresh(file)
        return file

    async def get_file(
        self, db: AsyncSession, user_id: str, file_id: str
    ) -> Optional[File]:
        """Get file metadata"""
        result = await db.execute(
            select(File).where(and_(File.id == file_id, File.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def get_file_data(
        self, db: AsyncSession, user_id: str, file_id: str, user_key: bytes
    ) -> bytes:
        """Get and decrypt file data"""
        file = await self.get_file(db, user_id, file_id)
        if not file:
            raise ValueError("File not found")
        if file.is_folder:
            raise ValueError("Cannot read folder as file")

        # Read encrypted data and nonce
        storage_path = Path(file.storage_path)
        nonce_path = storage_path.parent / f"{str(file.id)}.nonce"

        async with aiofiles.open(storage_path, "rb") as f:
            encrypted_data = await f.read()
        async with aiofiles.open(nonce_path, "rb") as f:
            nonce = await f.read()

        # Decrypt
        return encryption_service.decrypt_file(encrypted_data, nonce, user_key)

    async def list_files(
        self, db: AsyncSession, user_id: str, parent_id: Optional[str] = None
    ) -> list[File]:
        """List files in a folder"""
        result = await db.execute(
            select(File).where(
                and_(File.user_id == user_id, File.parent_id == parent_id)
            )
        )
        return list(result.scalars().all())

    async def delete_file(self, db: AsyncSession, user_id: str, file_id: str) -> bool:
        """Delete a file"""
        file = await self.get_file(db, user_id, file_id)
        if not file:
            return False

        # Delete from disk if not a folder
        if not file.is_folder:
            storage_path = Path(file.storage_path)
            nonce_path = storage_path.parent / f"{str(file.id)}.nonce"
            if storage_path.exists():
                os.remove(storage_path)
            if nonce_path.exists():
                os.remove(nonce_path)

        db.delete(file)
        await db.commit()
        return True


# Create singleton instance
file_service = FileService()
