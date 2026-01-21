"""
File Service - Chunked encryption storage
"""

import base64
import os
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

import aiofiles
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.services.encryption_service import encryption_service


class FileService:
    """File service with chunked encryption storage and staging area"""

    def __init__(self):
        self.storage_path = Path(settings.STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Staging area paths
        self.staging_path = Path(settings.STAGING_PATH)
        self.staging_uploads_path = Path(settings.STAGING_UPLOADS_PATH)
        self.staging_encrypted_path = Path(settings.STAGING_ENCRYPTED_PATH)
        
        # Create staging directories
        self.staging_path.mkdir(parents=True, exist_ok=True)
        self.staging_uploads_path.mkdir(parents=True, exist_ok=True)
        self.staging_encrypted_path.mkdir(parents=True, exist_ok=True)
        
        self.chunk_size = 10 * 1024 * 1024  # 10MB chunks

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
        """
        Save a file with chunked encryption using staging area
        
        Pipeline:
        1. Save uploaded file to staging/uploads
        2. Chunk file
        3. Encrypt chunks and save to staging/encrypted
        4. Move encrypted chunks to final storage
        5. Store metadata in database
        6. Clean up staging area
        
        Args:
            db: Database session
            user_id: User ID
            name: File name
            file_data: File data bytes
            mime_type: MIME type
            parent_id: Parent folder ID (optional)
            user_key: User encryption key (if None, fetched from DB)
            
        Returns:
            File model instance
        """
        # Get user encryption key from database
        if user_key is None:
            user_key = await encryption_service.get_or_create_user_encryption_key(db, user_id)

        # Build path
        if parent_id:
            parent = await self.get_file(db, user_id, parent_id)
            if not parent:
                raise ValueError("Parent folder not found")
            path = f"{parent.path.rstrip('/')}/{name}"
        else:
            path = f"/{name}"

        # Create file record
        file_id = uuid4()
        file = File(
            id=file_id,
            user_id=user_id,
            name=name,
            path=path,
            size=len(file_data),  # Original size
            mime_type=mime_type,
            is_folder=False,
            parent_id=parent_id,
            storage_path=None,  # Chunked files don't use storage_path
        )
        db.add(file)
        await db.flush()  # Flush to get file_id

        # Step 1: Save uploaded file to staging/uploads
        staging_upload_path = self.staging_uploads_path / f"{file_id}_upload"
        async with aiofiles.open(staging_upload_path, "wb") as f:
            await f.write(file_data)

        encrypted_chunks_info = []
        staging_paths_to_cleanup = []
        
        try:
            # Step 2: Chunk the file
            chunks = encryption_service.chunk_file(file_data, self.chunk_size)
            
            # Step 3: Encrypt chunks and save to staging/encrypted
            user_storage = self._get_user_storage_path(str(user_id))
            
            for chunk_index, chunk_data in enumerate(chunks):
                # Derive chunk-specific key
                chunk_key = encryption_service.derive_chunk_key(
                    user_key, str(file_id), chunk_index
                )
                
                # Encrypt chunk
                encrypted_data, iv, checksum_hex = encryption_service.encrypt_file_chunk(
                    chunk_data, chunk_key
                )
                
                # Encrypt chunk key with user key for storage (per contract)
                encrypted_chunk_key, chunk_key_salt = await encryption_service.encrypt_user_key(
                    chunk_key
                )
                
                # Save encrypted chunk to staging/encrypted
                staging_encrypted_path = self.staging_encrypted_path / f"{file_id}_{chunk_index}.enc"
                async with aiofiles.open(staging_encrypted_path, "wb") as f:
                    await f.write(encrypted_data)
                
                staging_paths_to_cleanup.append(staging_encrypted_path)
                
                encrypted_chunks_info.append({
                    "chunk_index": chunk_index,
                    "chunk_data": chunk_data,
                    "encrypted_data": encrypted_data,
                    "iv": iv,
                    "checksum_hex": checksum_hex,
                    "encrypted_chunk_key": encrypted_chunk_key,
                    "staging_path": staging_encrypted_path,
                })
            
            # Step 4: Move encrypted chunks to final storage and store metadata
            for chunk_info in encrypted_chunks_info:
                # Final storage path
                chunk_storage_path = user_storage / f"{file_id}_{chunk_info['chunk_index']}.enc"
                
                # Copy from staging to final storage (rename fails across filesystems in Docker)
                async with aiofiles.open(chunk_info["staging_path"], "rb") as src:
                    async with aiofiles.open(chunk_storage_path, "wb") as dst:
                        content = await src.read()
                        await dst.write(content)
                
                # Delete staging file after successful copy
                chunk_info["staging_path"].unlink()
                
                # Store chunk metadata (aligned with contract)
                storage_chunk = StorageChunk(
                    file_id=file_id,
                    chunk_index=chunk_info["chunk_index"],
                    chunk_size=len(chunk_info["chunk_data"]),
                    encrypted_size=len(chunk_info["encrypted_data"]),
                    iv=chunk_info["iv"],
                    encryption_key_encrypted=base64.b64encode(chunk_info["encrypted_chunk_key"]).decode("utf-8"),  # Encrypted chunk key (per contract)
                    checksum=chunk_info["checksum_hex"],  # Hex string (per contract)
                    storage_path=str(chunk_storage_path),
                )
                db.add(storage_chunk)

            await db.commit()
            await db.refresh(file)
            
            # Step 6: Clean up staging area (success case)
            if staging_upload_path.exists():
                staging_upload_path.unlink()
            
            return file
            
        except Exception as e:
            # Clean up staging area on error
            if staging_upload_path.exists():
                staging_upload_path.unlink()
            # Clean up any encrypted chunks in staging
            for staging_path in staging_paths_to_cleanup:
                if staging_path.exists():
                    staging_path.unlink()
            raise

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
        """
        Get and decrypt file data (reassembles chunks)
        
        Supports both local storage and cloud storage:
        - If chunks are in cloud (have cloud_file_id), download from cloud
        - Otherwise, read from local disk
        
        Args:
            db: Database session
            user_id: User ID
            file_id: File ID
            user_key: User encryption key
            
        Returns:
            Decrypted file data bytes
        """
        file = await self.get_file(db, user_id, file_id)
        if not file:
            raise ValueError("File not found")
        if file.is_folder:
            raise ValueError("Cannot read folder as file")

        # Get all chunks for this file, ordered by chunk_index
        file_uuid = UUID(file_id)
        result = await db.execute(
            select(StorageChunk)
            .where(StorageChunk.file_id == file_uuid)
            .order_by(StorageChunk.chunk_index)
        )
        chunks = result.scalars().all()

        if not chunks:
            # Fallback: try legacy non-chunked storage
            if file.storage_path:
                storage_path = Path(file.storage_path)
                nonce_path = storage_path.parent / f"{str(file.id)}.nonce"
                if storage_path.exists():
                    async with aiofiles.open(storage_path, "rb") as f:
                        encrypted_data = await f.read()
                    async with aiofiles.open(nonce_path, "rb") as f:
                        nonce = await f.read()
                    return encryption_service.decrypt_file(encrypted_data, nonce, user_key)
            raise ValueError("No chunks found for file")

        # Check if chunks are stored in cloud
        first_chunk = chunks[0]
        if first_chunk.cloud_file_id and first_chunk.cloud_provider:
            # Chunks are in cloud - use cloud download service
            from app.services.cloud_download_service import CloudDownloadService, CloudProvider
            
            cloud_download_service = CloudDownloadService()
            provider = CloudProvider(first_chunk.cloud_provider)
            
            return await cloud_download_service.download_file_chunks_from_cloud(
                db, user_id, file_uuid, provider
            )

        # Chunks are stored locally - read from disk
        decrypted_chunks = []
        for chunk in chunks:
            # Derive chunk key (per contract - keys are derived deterministically)
            chunk_key = encryption_service.derive_chunk_key(
                user_key, str(file_id), chunk.chunk_index
            )
            
            # Read encrypted chunk from disk
            chunk_path = Path(chunk.storage_path)
            if not chunk_path.exists():
                raise ValueError(
                    f"Chunk file not found on disk: {chunk.storage_path} "
                    f"(chunk_index: {chunk.chunk_index})"
                )
            async with aiofiles.open(chunk_path, "rb") as f:
                encrypted_data = await f.read()
            
            # Verify checksum (per contract - checksum is hex string)
            if not encryption_service.verify_checksum(encrypted_data, chunk.checksum):
                raise ValueError(f"Checksum verification failed for chunk {chunk.chunk_index}")
            
            # Decrypt chunk
            decrypted_chunk = encryption_service.decrypt_file_chunk(
                encrypted_data, chunk_key, chunk.iv
            )
            decrypted_chunks.append(decrypted_chunk)

        # Reassemble file
        return b"".join(decrypted_chunks)

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
        """Delete a file and all its chunks"""
        
        file = await self.get_file(db, user_id, file_id)
        if not file:
            return False

        # Delete chunks if not a folder
        if not file.is_folder:
            # Get all chunks to delete their files from disk
            file_uuid = UUID(file_id)
            result = await db.execute(
                select(StorageChunk).where(StorageChunk.file_id == file_uuid)
            )
            chunks = result.scalars().all()
            
            # Delete chunk files from disk
            # Note: Chunks will be auto-deleted from DB via CASCADE when file is deleted
            for chunk in chunks:
                chunk_path = Path(chunk.storage_path)
                if chunk_path.exists():
                    chunk_path.unlink()
            
            # Fallback: delete legacy non-chunked file
            if file.storage_path:
                storage_path = Path(file.storage_path)
                nonce_path = storage_path.parent / f"{str(file.id)}.nonce"
                if storage_path.exists():
                    os.remove(storage_path)
                if nonce_path.exists():
                    os.remove(nonce_path)

        # Delete the file record using direct DELETE statement
        # CASCADE will automatically delete associated chunks
        file_uuid = UUID(file_id)
        await db.execute(
            delete(File).where(File.id == file_uuid, File.user_id == UUID(user_id))
        )
        await db.commit()
        return True


# Create singleton instance
file_service = FileService()
