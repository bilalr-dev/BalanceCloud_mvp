"""
Cloud Download Service - Download encrypted chunks from cloud providers
"""

import base64
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.cloud_account import CloudAccount
from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.services.cloud_upload_service import CloudUploadService
from app.services.encryption_service import encryption_service
from app.services.file_service import file_service


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    GOOGLE_DRIVE = "google_drive"
    ONEDRIVE = "onedrive"


class CloudDownloadService:
    """Service for downloading encrypted file chunks from cloud storage providers"""

    def __init__(self):
        # Google Drive API endpoints
        self.google_drive_api_url = "https://www.googleapis.com/drive/v3/files"
        self.google_drive_download_url = "https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        
        # OneDrive API endpoints
        self.onedrive_api_url = "https://graph.microsoft.com/v1.0/me/drive"
        self.onedrive_download_url = "https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/content"

    async def get_cloud_account(
        self, db: AsyncSession, user_id: str, provider: CloudProvider
    ) -> Optional[CloudAccount]:
        """
        Get cloud account for user and provider
        
        Args:
            db: Database session
            user_id: User ID
            provider: Cloud provider
            
        Returns:
            CloudAccount if found, None otherwise
        """
        result = await db.execute(
            select(CloudAccount).where(
                CloudAccount.user_id == user_id,
                CloudAccount.provider == provider.value
            )
        )
        return result.scalar_one_or_none()

    async def get_access_token(
        self, db: AsyncSession, cloud_account: CloudAccount
    ) -> str:
        """
        Get valid access token, refreshing if necessary
        
        Args:
            db: Database session
            cloud_account: Cloud account record
            
        Returns:
            Decrypted access token
        """
        # Decrypt access token (same logic as upload service)
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"balancecloud_mvp_salt",
            iterations=100000,
            backend=default_backend(),
        )
        master_key = kdf.derive(settings.ENCRYPTION_KEY.encode())
        
        access_token_encrypted_bytes = base64.b64decode(cloud_account.access_token_encrypted)
        access_token = encryption_service.decrypt_token(
            access_token_encrypted_bytes, master_key
        )
        
        # Check if token is expired
        if cloud_account.token_expires_at and cloud_account.token_expires_at <= datetime.utcnow():
            # Token expired, refresh it
            refresh_token_encrypted_bytes = base64.b64decode(cloud_account.refresh_token_encrypted)
            refresh_token = encryption_service.decrypt_token(
                refresh_token_encrypted_bytes, master_key
            )
            
            # Refresh token based on provider
            upload_service = CloudUploadService()
            if cloud_account.provider == CloudProvider.GOOGLE_DRIVE.value:
                new_tokens = await upload_service._refresh_google_token(refresh_token)
            elif cloud_account.provider == CloudProvider.ONEDRIVE.value:
                new_tokens = await upload_service._refresh_onedrive_token(refresh_token)
            else:
                raise ValueError(f"Unsupported provider: {cloud_account.provider}")
            
            # Encrypt and store new tokens
            new_access_token_encrypted = encryption_service.encrypt_token(
                new_tokens["access_token"], master_key
            )
            new_refresh_token_encrypted = encryption_service.encrypt_token(
                new_tokens["refresh_token"], master_key
            )
            
            # Update cloud account
            cloud_account.access_token_encrypted = base64.b64encode(new_access_token_encrypted).decode("utf-8")
            cloud_account.refresh_token_encrypted = base64.b64encode(new_refresh_token_encrypted).decode("utf-8")
            cloud_account.token_expires_at = datetime.utcnow() + timedelta(seconds=new_tokens["expires_in"])
            await db.commit()
            await db.refresh(cloud_account)
            
            return new_tokens["access_token"]
        
        return access_token

    async def download_file_from_google_drive(
        self,
        access_token: str,
        cloud_file_id: str,
    ) -> bytes:
        """
        Download file from Google Drive
        
        Args:
            access_token: Google Drive access token
            cloud_file_id: Google Drive file ID
            
        Returns:
            File data bytes
        """
        download_url = self.google_drive_download_url.format(file_id=cloud_file_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                download_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=60.0,  # 60 second timeout for large chunks
            )
            response.raise_for_status()
            return response.content

    async def download_file_from_onedrive(
        self,
        access_token: str,
        cloud_file_id: str,
    ) -> bytes:
        """
        Download file from OneDrive
        
        Args:
            access_token: OneDrive access token
            cloud_file_id: OneDrive item ID
            
        Returns:
            File data bytes
        """
        download_url = self.onedrive_download_url.format(item_id=cloud_file_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                download_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=60.0,  # 60 second timeout for large chunks
            )
            response.raise_for_status()
            return response.content

    async def download_file_chunks_from_cloud(
        self,
        db: AsyncSession,
        user_id: str,
        file_id: UUID,
        provider: CloudProvider,
    ) -> bytes:
        """
        Download encrypted file chunks from cloud provider and reassemble file
        
        Pipeline:
        1. Get cloud account for user and provider
        2. Get file and chunks from database
        3. Get access token (refresh if needed)
        4. Download each encrypted chunk from cloud
        5. Decrypt chunks
        6. Verify checksums
        7. Reassemble file
        
        Args:
            db: Database session
            user_id: User ID
            file_id: File ID
            provider: Cloud provider
            
        Returns:
            Decrypted file data bytes
        """
        from datetime import timedelta
        
        # Get cloud account
        cloud_account = await self.get_cloud_account(db, user_id, provider)
        if not cloud_account:
            raise ValueError(f"No cloud account found for provider: {provider.value}")

        # Get file
        file = await file_service.get_file(db, user_id, str(file_id))
        if not file:
            raise ValueError("File not found")
        if file.is_folder:
            raise ValueError("Cannot download folder as file")

        # Get chunks ordered by chunk_index
        result = await db.execute(
            select(StorageChunk)
            .where(StorageChunk.file_id == file_id)
            .order_by(StorageChunk.chunk_index)
        )
        chunks = result.scalars().all()
        if not chunks:
            raise ValueError("No chunks found for file")

        # Get user encryption key
        user_key = await encryption_service.get_or_create_user_encryption_key(db, user_id)

        # Get access token
        access_token = await self.get_access_token(db, cloud_account)

        # Download, decrypt, and reassemble chunks
        decrypted_chunks = []
        for chunk in chunks:
            # Get cloud_file_id from chunk metadata
            cloud_file_id = chunk.cloud_file_id
            
            if not cloud_file_id:
                raise ValueError(
                    f"Cloud file ID not found for chunk {chunk.chunk_index}. "
                    f"Chunks must be uploaded to cloud first. "
                    f"Use cloud_upload_service.upload_file_chunks_to_cloud() to upload chunks."
                )
            
            # Verify chunk is stored in the requested provider
            if chunk.cloud_provider != provider.value:
                raise ValueError(
                    f"Chunk {chunk.chunk_index} is stored in {chunk.cloud_provider}, "
                    f"but requested provider is {provider.value}"
                )
            
            # Download chunk from cloud based on provider
            if provider == CloudProvider.GOOGLE_DRIVE:
                encrypted_chunk_data = await self.download_file_from_google_drive(
                    access_token,
                    cloud_file_id,
                )
            elif provider == CloudProvider.ONEDRIVE:
                encrypted_chunk_data = await self.download_file_from_onedrive(
                    access_token,
                    cloud_file_id,
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Verify checksum (per contract - checksum is hex string)
            if not encryption_service.verify_checksum(encrypted_chunk_data, chunk.checksum):
                raise ValueError(f"Checksum verification failed for chunk {chunk.chunk_index}")
            
            # Derive chunk key (per contract - keys are derived deterministically)
            chunk_key = encryption_service.derive_chunk_key(
                user_key, str(file_id), chunk.chunk_index
            )
            
            # Decrypt chunk
            decrypted_chunk = encryption_service.decrypt_file_chunk(
                encrypted_chunk_data, chunk_key, chunk.iv
            )
            decrypted_chunks.append(decrypted_chunk)

        # Reassemble file
        return b"".join(decrypted_chunks)
