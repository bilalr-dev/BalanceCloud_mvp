"""
Tests for Cloud Download Service
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.cloud_account import CloudAccount
from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.services.cloud_download_service import CloudDownloadService, CloudProvider


@pytest.mark.asyncio
async def test_get_cloud_account(db_session, test_user):
    """Test getting cloud account for user and provider"""
    service = CloudDownloadService()
    
    # Create cloud account
    cloud_account = CloudAccount(
        id=uuid4(),
        user_id=test_user.id,
        provider=CloudProvider.GOOGLE_DRIVE.value,
        provider_account_id="test_account_id",
        access_token_encrypted="encrypted_token",
        refresh_token_encrypted="encrypted_refresh",
    )
    db_session.add(cloud_account)
    await db_session.commit()
    
    # Get cloud account
    result = await service.get_cloud_account(
        db_session, str(test_user.id), CloudProvider.GOOGLE_DRIVE
    )
    
    assert result is not None
    assert result.user_id == test_user.id
    assert result.provider == CloudProvider.GOOGLE_DRIVE.value


@pytest.mark.asyncio
async def test_download_file_from_google_drive():
    """Test downloading file from Google Drive"""
    service = CloudDownloadService()
    
    mock_data = b"encrypted chunk data"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.content = mock_data
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await service.download_file_from_google_drive(
            "test_access_token", "test_file_id"
        )
        
        assert result == mock_data
        mock_client_instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_download_file_from_onedrive():
    """Test downloading file from OneDrive"""
    service = CloudDownloadService()
    
    mock_data = b"encrypted chunk data"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.content = mock_data
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await service.download_file_from_onedrive(
            "test_access_token", "test_item_id"
        )
        
        assert result == mock_data
        mock_client_instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_download_file_chunks_from_cloud_missing_cloud_file_id(
    db_session, test_user
):
    """Test downloading chunks when cloud_file_id is missing"""
    service = CloudDownloadService()
    
    # Create file
    file = File(
        id=uuid4(),
        user_id=test_user.id,
        name="test_file.txt",
        size=100,
        is_folder=False,
    )
    db_session.add(file)
    await db_session.commit()
    
    # Create chunk without cloud_file_id
    chunk = StorageChunk(
        id=uuid4(),
        file_id=file.id,
        chunk_index=0,
        chunk_size=100,
        encrypted_size=120,
        iv=b"test_iv",
        encryption_key_encrypted="encrypted_key",
        checksum="test_checksum",
        storage_path="/path/to/chunk.enc",
    )
    db_session.add(chunk)
    await db_session.commit()
    
    # Create cloud account
    cloud_account = CloudAccount(
        id=uuid4(),
        user_id=test_user.id,
        provider=CloudProvider.GOOGLE_DRIVE.value,
        provider_account_id="test_account_id",
        access_token_encrypted="encrypted_token",
        refresh_token_encrypted="encrypted_refresh",
    )
    db_session.add(cloud_account)
    await db_session.commit()
    
    # Try to download - should raise error
    with pytest.raises(ValueError, match="Cloud file ID not found"):
        await service.download_file_chunks_from_cloud(
            db_session, str(test_user.id), file.id, CloudProvider.GOOGLE_DRIVE
        )


@pytest.mark.asyncio
async def test_download_file_chunks_from_cloud_wrong_provider(
    db_session, test_user
):
    """Test downloading chunks when provider doesn't match"""
    service = CloudDownloadService()
    
    # Create file
    file = File(
        id=uuid4(),
        user_id=test_user.id,
        name="test_file.txt",
        size=100,
        is_folder=False,
    )
    db_session.add(file)
    await db_session.commit()
    
    # Create chunk with cloud_file_id for Google Drive
    chunk = StorageChunk(
        id=uuid4(),
        file_id=file.id,
        chunk_index=0,
        chunk_size=100,
        encrypted_size=120,
        iv=b"test_iv",
        encryption_key_encrypted="encrypted_key",
        checksum="test_checksum",
        storage_path="/path/to/chunk.enc",
        cloud_file_id="google_drive_file_id",
        cloud_provider=CloudProvider.GOOGLE_DRIVE.value,
    )
    db_session.add(chunk)
    await db_session.commit()
    
    # Create OneDrive cloud account
    cloud_account = CloudAccount(
        id=uuid4(),
        user_id=test_user.id,
        provider=CloudProvider.ONEDRIVE.value,
        provider_account_id="test_account_id",
        access_token_encrypted="encrypted_token",
        refresh_token_encrypted="encrypted_refresh",
    )
    db_session.add(cloud_account)
    await db_session.commit()
    
    # Try to download with wrong provider - should raise error
    with pytest.raises(ValueError, match="is stored in"):
        await service.download_file_chunks_from_cloud(
            db_session, str(test_user.id), file.id, CloudProvider.ONEDRIVE
        )


@pytest.mark.asyncio
async def test_download_file_chunks_from_cloud_integration(
    db_session, test_user, mock_encryption_service
):
    """Test full integration: download chunks, decrypt, reassemble"""
    service = CloudDownloadService()
    
    # Create file
    file = File(
        id=uuid4(),
        user_id=test_user.id,
        name="test_file.txt",
        size=200,
        is_folder=False,
    )
    db_session.add(file)
    await db_session.commit()
    
    # Create cloud account
    cloud_account = CloudAccount(
        id=uuid4(),
        user_id=test_user.id,
        provider=CloudProvider.GOOGLE_DRIVE.value,
        provider_account_id="test_account_id",
        access_token_encrypted="encrypted_token",
        refresh_token_encrypted="encrypted_refresh",
    )
    db_session.add(cloud_account)
    await db_session.commit()
    
    # Create chunks with cloud_file_id
    chunk1 = StorageChunk(
        id=uuid4(),
        file_id=file.id,
        chunk_index=0,
        chunk_size=100,
        encrypted_size=120,
        iv=b"test_iv_1",
        encryption_key_encrypted="encrypted_key_1",
        checksum="checksum_1",
        storage_path="/path/to/chunk_0.enc",
        cloud_file_id="cloud_file_id_1",
        cloud_provider=CloudProvider.GOOGLE_DRIVE.value,
    )
    chunk2 = StorageChunk(
        id=uuid4(),
        file_id=file.id,
        chunk_index=1,
        chunk_size=100,
        encrypted_size=120,
        iv=b"test_iv_2",
        encryption_key_encrypted="encrypted_key_2",
        checksum="checksum_2",
        storage_path="/path/to/chunk_1.enc",
        cloud_file_id="cloud_file_id_2",
        cloud_provider=CloudProvider.GOOGLE_DRIVE.value,
    )
    db_session.add(chunk1)
    db_session.add(chunk2)
    await db_session.commit()
    
    # Mock download responses
    mock_chunk_data_1 = b"encrypted_chunk_1"
    mock_chunk_data_2 = b"encrypted_chunk_2"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response_1 = MagicMock()
        mock_response_1.content = mock_chunk_data_1
        mock_response_1.raise_for_status = MagicMock()
        
        mock_response_2 = MagicMock()
        mock_response_2.content = mock_chunk_data_2
        mock_response_2.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.get = AsyncMock(
            side_effect=[mock_response_1, mock_response_2]
        )
        mock_client.return_value = mock_client_instance
        
        # Mock encryption service methods
        with patch(
            "app.services.cloud_download_service.encryption_service"
        ) as mock_encryption:
            mock_encryption.get_or_create_user_encryption_key = AsyncMock(
                return_value=b"user_key"
            )
            mock_encryption.verify_checksum = MagicMock(return_value=True)
            mock_encryption.derive_chunk_key = MagicMock(return_value=b"chunk_key")
            mock_encryption.decrypt_file_chunk = MagicMock(
                side_effect=[b"decrypted_chunk_1", b"decrypted_chunk_2"]
            )
            
            result = await service.download_file_chunks_from_cloud(
                db_session, str(test_user.id), file.id, CloudProvider.GOOGLE_DRIVE
            )
            
            # Verify result is reassembled file
            assert result == b"decrypted_chunk_1decrypted_chunk_2"
            
            # Verify download was called for both chunks
            assert mock_client_instance.get.call_count == 2
            
            # Verify checksum verification was called
            assert mock_encryption.verify_checksum.call_count == 2
            
            # Verify decryption was called
            assert mock_encryption.decrypt_file_chunk.call_count == 2
