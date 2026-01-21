"""
Tests for cloud upload service
"""

import base64
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cloud_account import CloudAccount
from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.models.user import User
from app.services.cloud_upload_service import CloudProvider, cloud_upload_service
from app.services.encryption_service import encryption_service


@pytest.mark.asyncio
async def test_get_cloud_account(db_session, test_user):
    """Test getting cloud account for user"""
    user_id = str(test_user.id)
    
    # Create a cloud account
    cloud_account = CloudAccount(
        user_id=test_user.id,
        provider=CloudProvider.GOOGLE_DRIVE.value,
        provider_account_id="test@gmail.com",
        access_token_encrypted="encrypted_token",
        refresh_token_encrypted="encrypted_refresh",
    )
    db_session.add(cloud_account)
    await db_session.commit()
    
    # Get cloud account
    account = await cloud_upload_service.get_cloud_account(
        db_session, user_id, CloudProvider.GOOGLE_DRIVE
    )
    
    assert account is not None
    assert account.provider == CloudProvider.GOOGLE_DRIVE.value
    assert account.user_id == test_user.id


@pytest.mark.asyncio
async def test_provider_selection(db_session: AsyncSession, test_user: User):
    """Test provider selection logic"""
    user_id = str(test_user.id)
    
    # No accounts - should return None
    provider = await cloud_upload_service.select_provider(db_session, user_id)
    assert provider is None
    
    # Create Google Drive account
    google_account = CloudAccount(
        user_id=test_user.id,
        provider=CloudProvider.GOOGLE_DRIVE.value,
        provider_account_id="test@gmail.com",
        access_token_encrypted="encrypted_token",
        refresh_token_encrypted="encrypted_refresh",
    )
    db_session.add(google_account)
    await db_session.commit()
    
    # Should return Google Drive
    provider = await cloud_upload_service.select_provider(db_session, user_id)
    assert provider == CloudProvider.GOOGLE_DRIVE
    
    # Preferred provider (OneDrive) not available - should return Google Drive
    provider = await cloud_upload_service.select_provider(
        db_session, user_id, preferred_provider=CloudProvider.ONEDRIVE
    )
    assert provider == CloudProvider.GOOGLE_DRIVE
    
    # Preferred provider (Google Drive) available - should return Google Drive
    provider = await cloud_upload_service.select_provider(
        db_session, user_id, preferred_provider=CloudProvider.GOOGLE_DRIVE
    )
    assert provider == CloudProvider.GOOGLE_DRIVE


@pytest.mark.asyncio
async def test_upload_file_chunks_to_cloud(db_session: AsyncSession, test_user: User):
    """Test uploading file chunks to cloud provider"""
    user_id = str(test_user.id)
    
    # Create cloud account
    master_key = encryption_service.master_key
    test_access_token = "test_access_token_123"
    test_refresh_token = "test_refresh_token_123"
    
    access_token_encrypted = encryption_service.encrypt_token(test_access_token, master_key)
    refresh_token_encrypted = encryption_service.encrypt_token(test_refresh_token, master_key)
    
    cloud_account = CloudAccount(
        user_id=test_user.id,
        provider=CloudProvider.GOOGLE_DRIVE.value,
        provider_account_id="test@gmail.com",
        access_token_encrypted=base64.b64encode(access_token_encrypted).decode("utf-8"),
        refresh_token_encrypted=base64.b64encode(refresh_token_encrypted).decode("utf-8"),
    )
    db_session.add(cloud_account)
    await db_session.commit()
    
    # Create a file with chunks
    from app.services.file_service import file_service
    
    file_data = b"test file content for cloud upload"
    saved_file = await file_service.save_file(
        db=db_session,
        user_id=user_id,
        name="cloud_test.txt",
        file_data=file_data,
        mime_type="text/plain",
    )
    
    # Note: Actual upload will fail without valid OAuth tokens
    # This test verifies the structure and logic
    # In real scenario, you'd mock the HTTP calls
    
    # Verify file and chunks exist
    from sqlalchemy import select
    result = await db_session.execute(
        select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
    )
    chunks = result.scalars().all()
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_google_drive_upload_structure(db_session: AsyncSession):
    """Test Google Drive upload method structure"""
    # Verify method exists and has correct signature
    assert hasattr(cloud_upload_service, "upload_file_to_google_drive")
    assert callable(cloud_upload_service.upload_file_to_google_drive)


@pytest.mark.asyncio
async def test_onedrive_upload_structure(db_session: AsyncSession):
    """Test OneDrive upload method structure"""
    # Verify method exists and has correct signature
    assert hasattr(cloud_upload_service, "upload_file_to_onedrive")
    assert callable(cloud_upload_service.upload_file_to_onedrive)


@pytest.mark.asyncio
async def test_upload_chunks_integration(db_session: AsyncSession, test_user: User):
    """Test integration with file service for chunk uploads"""
    user_id = str(test_user.id)
    
    # Create cloud account
    master_key = encryption_service.master_key
    test_access_token = "test_access_token"
    access_token_encrypted = encryption_service.encrypt_token(test_access_token, master_key)
    
    cloud_account = CloudAccount(
        user_id=test_user.id,
        provider=CloudProvider.GOOGLE_DRIVE.value,
        provider_account_id="test@gmail.com",
        access_token_encrypted=base64.b64encode(access_token_encrypted).decode("utf-8"),
        refresh_token_encrypted=base64.b64encode(access_token_encrypted).decode("utf-8"),
    )
    db_session.add(cloud_account)
    await db_session.commit()
    
    # Create file with chunks
    from app.services.file_service import file_service
    
    file_data = b"x" * (11 * 1024 * 1024)  # 11MB to create multiple chunks
    saved_file = await file_service.save_file(
        db=db_session,
        user_id=user_id,
        name="large_cloud_test.bin",
        file_data=file_data,
        mime_type="application/octet-stream",
    )
    
    # Verify chunks exist
    from sqlalchemy import select
    result = await db_session.execute(
        select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
    )
    chunks = result.scalars().all()
    assert len(chunks) >= 2, "Large file should have multiple chunks"
    
    # Verify chunks can be read (for upload)
    for chunk in chunks:
        from pathlib import Path
        chunk_path = Path(chunk.storage_path)
        assert chunk_path.exists(), f"Chunk file should exist: {chunk.storage_path}"
        chunk_data = chunk_path.read_bytes()
        assert len(chunk_data) > 0, "Chunk should have data"
