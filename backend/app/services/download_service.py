"""
Download Service - Streaming file download with chunk fetching, decryption, and reassembly
"""

import io
from typing import AsyncGenerator, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.services.cloud_download_service import CloudDownloadService, CloudProvider
from app.services.encryption_service import encryption_service
from app.services.file_service import file_service


class DownloadService:
    """Service for streaming file downloads with chunk fetching, decryption, and reassembly"""

    async def stream_file_download(
        self,
        db: AsyncSession,
        user_id: str,
        file_id: str,
        user_key: bytes,
        chunk_size: int = 8192,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream file download with chunk fetching, decryption, and reassembly
        
        Pipeline:
        1. Get file metadata
        2. Get chunks from database (ordered by chunk_index)
        3. For each chunk:
           - Fetch from cloud or local storage
           - Verify checksum
           - Decrypt chunk
           - Yield decrypted data in streaming fashion
        4. Reassemble file as chunks are streamed
        
        Args:
            db: Database session
            user_id: User ID
            file_id: File ID
            user_key: User encryption key
            chunk_size: Size of streaming chunks (default: 8KB)
            
        Yields:
            Decrypted file data chunks as bytes
        """
        # Get file metadata
        file = await file_service.get_file(db, user_id, file_id)
        if not file:
            raise ValueError("File not found")
        if file.is_folder:
            raise ValueError("Cannot download folder as file")

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
                from pathlib import Path
                import aiofiles
                
                storage_path = Path(file.storage_path)
                nonce_path = storage_path.parent / f"{str(file.id)}.nonce"
                if storage_path.exists():
                    async with aiofiles.open(storage_path, "rb") as f:
                        encrypted_data = await f.read()
                    async with aiofiles.open(nonce_path, "rb") as f:
                        nonce = await f.read()
                    decrypted_data = encryption_service.decrypt_file(
                        encrypted_data, nonce, user_key
                    )
                    # Stream legacy file in chunks
                    buffer = io.BytesIO(decrypted_data)
                    while True:
                        chunk = buffer.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
                    return
            raise ValueError("No chunks found for file")

        # Check if chunks are stored in cloud
        first_chunk = chunks[0]
        if first_chunk.cloud_file_id and first_chunk.cloud_provider:
            # Chunks are in cloud - stream download from cloud
            async for data_chunk in self._stream_from_cloud(
                db, user_id, file_uuid, chunks, user_key, chunk_size
            ):
                yield data_chunk
        else:
            # Chunks are stored locally - stream from disk
            async for data_chunk in self._stream_from_local(
                file_id, chunks, user_key, chunk_size
            ):
                yield data_chunk

    async def _stream_from_cloud(
        self,
        db: AsyncSession,
        user_id: str,
        file_id: UUID,
        chunks: list[StorageChunk],
        user_key: bytes,
        stream_chunk_size: int,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream file download from cloud storage
        
        Args:
            db: Database session
            user_id: User ID
            file_id: File ID
            chunks: List of storage chunks
            user_key: User encryption key
            stream_chunk_size: Size of streaming chunks
            
        Yields:
            Decrypted file data chunks
        """
        # Get cloud provider from first chunk
        provider = CloudProvider(chunks[0].cloud_provider)
        
        # Get cloud account
        cloud_download_service = CloudDownloadService()
        cloud_account = await cloud_download_service.get_cloud_account(db, user_id, provider)
        if not cloud_account:
            raise ValueError(f"No cloud account found for provider: {provider.value}")

        # Get access token
        access_token = await cloud_download_service.get_access_token(db, cloud_account)

        # Stream each chunk
        for chunk in chunks:
            # Download encrypted chunk from cloud
            if provider == CloudProvider.GOOGLE_DRIVE:
                encrypted_chunk_data = await cloud_download_service.download_file_from_google_drive(
                    access_token, chunk.cloud_file_id
                )
            elif provider == CloudProvider.ONEDRIVE:
                encrypted_chunk_data = await cloud_download_service.download_file_from_onedrive(
                    access_token, chunk.cloud_file_id
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            # Verify checksum
            if not encryption_service.verify_checksum(encrypted_chunk_data, chunk.checksum):
                raise ValueError(f"Checksum verification failed for chunk {chunk.chunk_index}")

            # Derive chunk key
            chunk_key = encryption_service.derive_chunk_key(
                user_key, str(file_id), chunk.chunk_index
            )

            # Decrypt chunk
            decrypted_chunk = encryption_service.decrypt_file_chunk(
                encrypted_chunk_data, chunk_key, chunk.iv
            )

            # Stream decrypted chunk in smaller pieces
            buffer = io.BytesIO(decrypted_chunk)
            while True:
                data_chunk = buffer.read(stream_chunk_size)
                if not data_chunk:
                    break
                yield data_chunk

    async def _stream_from_local(
        self,
        file_id: str,
        chunks: list[StorageChunk],
        user_key: bytes,
        stream_chunk_size: int,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream file download from local storage
        
        Args:
            file_id: File ID
            chunks: List of storage chunks
            user_key: User encryption key
            stream_chunk_size: Size of streaming chunks
            
        Yields:
            Decrypted file data chunks
        """
        import aiofiles
        from pathlib import Path

        # Stream each chunk
        for chunk in chunks:
            # Derive chunk key
            chunk_key = encryption_service.derive_chunk_key(
                user_key, file_id, chunk.chunk_index
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

            # Verify checksum
            if not encryption_service.verify_checksum(encrypted_data, chunk.checksum):
                raise ValueError(f"Checksum verification failed for chunk {chunk.chunk_index}")

            # Decrypt chunk
            decrypted_chunk = encryption_service.decrypt_file_chunk(
                encrypted_data, chunk_key, chunk.iv
            )

            # Stream decrypted chunk in smaller pieces
            buffer = io.BytesIO(decrypted_chunk)
            while True:
                data_chunk = buffer.read(stream_chunk_size)
                if not data_chunk:
                    break
                yield data_chunk

    async def download_file_full(
        self,
        db: AsyncSession,
        user_id: str,
        file_id: str,
        user_key: bytes,
    ) -> bytes:
        """
        Download entire file (non-streaming) - for compatibility
        
        Args:
            db: Database session
            user_id: User ID
            file_id: File ID
            user_key: User encryption key
            
        Returns:
            Complete decrypted file data as bytes
        """
        chunks = []
        async for chunk in self.stream_file_download(db, user_id, file_id, user_key):
            chunks.append(chunk)
        return b"".join(chunks)


# Create singleton instance
download_service = DownloadService()
