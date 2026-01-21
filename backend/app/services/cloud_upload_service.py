"""
Cloud Upload Service - Upload encrypted chunks to cloud providers
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
from app.services.encryption_service import encryption_service
from app.services.file_service import file_service


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    GOOGLE_DRIVE = "google_drive"
    ONEDRIVE = "onedrive"


class CloudUploadService:
    """Service for uploading encrypted file chunks to cloud storage providers"""

    def __init__(self):
        # Google Drive API endpoints
        self.google_drive_upload_url = "https://www.googleapis.com/upload/drive/v3/files"
        self.google_drive_api_url = "https://www.googleapis.com/drive/v3/files"
        
        # OneDrive API endpoints
        self.onedrive_upload_url = "https://graph.microsoft.com/v1.0/me/drive/root:/{path}:/content"
        self.onedrive_api_url = "https://graph.microsoft.com/v1.0/me/drive"

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
        # Decrypt access token (tokens are encrypted with master key)
        # Master key is derived from ENCRYPTION_KEY in encryption_service
        # We need to get the master key - it's stored as an instance variable
        # For now, we'll derive it the same way encryption_service does
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
            await self._refresh_token(db, cloud_account)
            # Get new token
            await db.refresh(cloud_account)
            access_token_encrypted_bytes = base64.b64decode(cloud_account.access_token_encrypted)
            access_token = encryption_service.decrypt_token(
                access_token_encrypted_bytes, master_key
            )
        
        return access_token

    async def _refresh_token(
        self, db: AsyncSession, cloud_account: CloudAccount
    ) -> None:
        """
        Refresh access token for cloud account
        
        Args:
            db: Database session
            cloud_account: Cloud account record
        """
        # Decrypt refresh token
        if not cloud_account.refresh_token_encrypted:
            raise ValueError("No refresh token available")
        
        # Get master key (same derivation as encryption_service)
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
        
        refresh_token_encrypted = base64.b64decode(cloud_account.refresh_token_encrypted)
        refresh_token = encryption_service.decrypt_token(
            refresh_token_encrypted, master_key
        )
        
        # Refresh token based on provider
        if cloud_account.provider == CloudProvider.GOOGLE_DRIVE.value:
            new_tokens = await self._refresh_google_token(refresh_token)
        elif cloud_account.provider == CloudProvider.ONEDRIVE.value:
            new_tokens = await self._refresh_onedrive_token(refresh_token)
        else:
            raise ValueError(f"Unsupported provider: {cloud_account.provider}")
        
        # Encrypt and store new tokens
        access_token_encrypted_bytes = encryption_service.encrypt_token(
            new_tokens["access_token"], master_key
        )
        refresh_token_encrypted_bytes = encryption_service.encrypt_token(
            new_tokens.get("refresh_token", refresh_token), master_key
        )
        
        cloud_account.access_token_encrypted = base64.b64encode(access_token_encrypted_bytes).decode("utf-8")
        cloud_account.refresh_token_encrypted = base64.b64encode(refresh_token_encrypted_bytes).decode("utf-8")
        
        # Update expiration
        expires_in = new_tokens.get("expires_in", 3600)
        cloud_account.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        await db.commit()

    async def _refresh_google_token(self, refresh_token: str) -> dict:
        """
        Refresh Google Drive access token
        
        Args:
            refresh_token: Google refresh token
            
        Returns:
            {
                "access_token": "...",
                "refresh_token": "...",  # May be same as input if not provided
                "expires_in": 3600
            }
        """
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError(
                "Google OAuth credentials not configured. "
                "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment variables."
            )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", refresh_token),  # Google may not return new refresh token
                "expires_in": result.get("expires_in", 3600),
            }

    async def _refresh_onedrive_token(self, refresh_token: str) -> dict:
        """
        Refresh OneDrive access token
        
        Args:
            refresh_token: Microsoft refresh token
            
        Returns:
            {
                "access_token": "...",
                "refresh_token": "...",  # May be same as input if not provided
                "expires_in": 3600
            }
        """
        if not settings.MICROSOFT_CLIENT_ID or not settings.MICROSOFT_CLIENT_SECRET:
            raise ValueError(
                "Microsoft OAuth credentials not configured. "
                "Please set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET in your environment variables."
            )
        
        # Microsoft OneDrive scopes
        scopes = "Files.ReadWrite offline_access"
        
        token_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "client_id": settings.MICROSOFT_CLIENT_ID,
                    "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                    "scope": scopes,
                },
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", refresh_token),  # Microsoft may not return new refresh token
                "expires_in": result.get("expires_in", 3600),
            }

    async def upload_file_to_google_drive(
        self,
        access_token: str,
        file_name: str,
        file_data: bytes,
        mime_type: str = "application/octet-stream",
    ) -> dict:
        """
        Upload file to Google Drive
        
        Args:
            access_token: Google Drive access token
            file_name: Name of the file
            file_data: File data bytes
            mime_type: MIME type of the file
            
        Returns:
            {
                "cloud_file_id": "...",
                "file_size": 1024,
                "uploaded_at": "2026-01-20T10:00:00Z"
            }
        """
        # For files > 5MB, use resumable upload
        # For now, use simple upload (files are chunked, so chunks should be < 5MB)
        async with httpx.AsyncClient() as client:
            # Create file metadata
            import json
            metadata = {
                "name": file_name,
            }
            
            # Upload file using multipart upload
            # Google Drive multipart upload requires specific format
            boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
            metadata_json = json.dumps(metadata)
            
            # Create multipart form data
            body_parts = [
                f"--{boundary}",
                'Content-Disposition: form-data; name="metadata"; filename="metadata.json"',
                "Content-Type: application/json",
                "",
                metadata_json,
                f"--{boundary}",
                f'Content-Disposition: form-data; name="file"; filename="{file_name}"',
                f"Content-Type: {mime_type}",
                "",
            ]
            body = "\r\n".join(body_parts).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")
            
            response = await client.post(
                f"{self.google_drive_upload_url}?uploadType=multipart",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": f"multipart/related; boundary={boundary}",
                },
                content=body,
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "cloud_file_id": result["id"],
                "file_size": len(file_data),
                "uploaded_at": datetime.utcnow().isoformat() + "Z",
            }

    async def upload_file_to_onedrive(
        self,
        access_token: str,
        file_name: str,
        file_data: bytes,
        mime_type: str = "application/octet-stream",
    ) -> dict:
        """
        Upload file to OneDrive
        
        Args:
            access_token: OneDrive access token
            file_name: Name of the file
            file_data: File data bytes
            mime_type: MIME type of the file
            
        Returns:
            {
                "cloud_file_id": "...",
                "file_size": 1024,
                "uploaded_at": "2026-01-20T10:00:00Z"
            }
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": mime_type,
        }
        
        async with httpx.AsyncClient() as client:
            # Upload file to OneDrive root
            upload_url = self.onedrive_upload_url.format(path=file_name)
            response = await client.put(
                upload_url,
                headers=headers,
                content=file_data,
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "cloud_file_id": result["id"],
                "file_size": len(file_data),
                "uploaded_at": datetime.utcnow().isoformat() + "Z",
            }

    async def upload_file_chunks_to_cloud(
        self,
        db: AsyncSession,
        user_id: str,
        file_id: UUID,
        provider: CloudProvider,
    ) -> dict:
        """
        Upload encrypted file chunks to cloud provider
        
        Pipeline:
        1. Get cloud account for user and provider
        2. Get file and chunks from database
        3. Get access token (refresh if needed)
        4. Upload each encrypted chunk to cloud
        5. Store cloud file IDs in metadata
        
        Args:
            db: Database session
            user_id: User ID
            file_id: File ID
            provider: Cloud provider
            
        Returns:
            {
                "file_id": "...",
                "provider": "google_drive",
                "cloud_file_ids": ["id1", "id2", ...],
                "uploaded_at": "2026-01-20T10:00:00Z"
            }
        """
        # Get cloud account
        cloud_account = await self.get_cloud_account(db, user_id, provider)
        if not cloud_account:
            raise ValueError(f"No cloud account found for provider: {provider.value}")

        # Get file
        file = await file_service.get_file(db, user_id, str(file_id))
        if not file:
            raise ValueError("File not found")

        # Get chunks
        result = await db.execute(
            select(StorageChunk)
            .where(StorageChunk.file_id == file_id)
            .order_by(StorageChunk.chunk_index)
        )
        chunks = result.scalars().all()
        if not chunks:
            raise ValueError("No chunks found for file")

        # Get access token
        access_token = await self.get_access_token(db, cloud_account)

        # Upload each chunk
        cloud_file_ids = []
        for chunk in chunks:
            # Read encrypted chunk from disk
            from pathlib import Path
            chunk_path = Path(chunk.storage_path)
            if not chunk_path.exists():
                raise ValueError(f"Chunk file not found: {chunk.storage_path}")
            
            chunk_data = chunk_path.read_bytes()
            
            # Upload chunk based on provider
            chunk_name = f"{file_id}_{chunk.chunk_index}.enc"
            if provider == CloudProvider.GOOGLE_DRIVE:
                result = await self.upload_file_to_google_drive(
                    access_token,
                    chunk_name,
                    chunk_data,
                    "application/octet-stream",
                )
            elif provider == CloudProvider.ONEDRIVE:
                result = await self.upload_file_to_onedrive(
                    access_token,
                    chunk_name,
                    chunk_data,
                    "application/octet-stream",
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            cloud_file_ids.append(result["cloud_file_id"])

        return {
            "file_id": str(file_id),
            "provider": provider.value,
            "cloud_file_ids": cloud_file_ids,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
        }

    async def select_provider(
        self, db: AsyncSession, user_id: str, preferred_provider: Optional[CloudProvider] = None
    ) -> Optional[CloudProvider]:
        """
        Select cloud provider for upload
        
        Logic:
        1. If preferred_provider is specified and connected, use it
        2. Otherwise, use first available connected provider
        3. Return None if no providers are connected
        
        Args:
            db: Database session
            user_id: User ID
            preferred_provider: Preferred provider (optional)
            
        Returns:
            Selected provider or None
        """
        # Check preferred provider first
        if preferred_provider:
            account = await self.get_cloud_account(db, user_id, preferred_provider)
            if account:
                return preferred_provider
        
        # Get all connected accounts
        result = await db.execute(
            select(CloudAccount).where(CloudAccount.user_id == user_id)
        )
        accounts = result.scalars().all()
        
        if not accounts:
            return None
        
        # Return first available provider
        # Priority: Google Drive > OneDrive
        for provider in [CloudProvider.GOOGLE_DRIVE, CloudProvider.ONEDRIVE]:
            for account in accounts:
                if account.provider == provider.value:
                    return provider
        
        # Return first account's provider
        return CloudProvider(accounts[0].provider)


# Create singleton instance
cloud_upload_service = CloudUploadService()
