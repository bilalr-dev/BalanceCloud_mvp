"""
Tests for Download Service
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.services.download_service import DownloadService


@pytest.mark.asyncio
async def test_stream_file_download_local(db_session, test_user):
    """Test streaming download from local storage"""
    service = DownloadService()
    
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
    
    # Create chunks
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
    )
    db_session.add(chunk1)
    db_session.add(chunk2)
    await db_session.commit()
    
    # Mock encryption service
    with patch("app.services.download_service.encryption_service") as mock_encryption:
        mock_encryption.get_or_create_user_encryption_key = AsyncMock(
            return_value=b"user_key"
        )
        mock_encryption.derive_chunk_key = MagicMock(return_value=b"chunk_key")
        mock_encryption.verify_checksum = MagicMock(return_value=True)
        mock_encryption.decrypt_file_chunk = MagicMock(
            side_effect=[b"decrypted_chunk_1", b"decrypted_chunk_2"]
        )
        
        # Mock file reading
        with patch("aiofiles.open", new_callable=AsyncMock) as mock_open:
            mock_file = AsyncMock()
            mock_file.read = AsyncMock(side_effect=[b"encrypted_chunk_1", b"encrypted_chunk_2"])
            mock_open.return_value.__aenter__ = AsyncMock(return_value=mock_file)
            mock_open.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Mock path exists
            with patch("pathlib.Path.exists", return_value=True):
                # Get user key
                from app.services.encryption_service import encryption_service as real_encryption
                user_key = await real_encryption.get_or_create_user_encryption_key(
                    db_session, str(test_user.id)
                )
                
                # Stream download
                chunks = []
                async for chunk in service.stream_file_download(
                    db_session, str(test_user.id), str(file.id), user_key
                ):
                    chunks.append(chunk)
                
                # Verify chunks were streamed
                assert len(chunks) > 0
                assert b"decrypted_chunk_1" in b"".join(chunks) or b"decrypted_chunk_2" in b"".join(chunks)


@pytest.mark.asyncio
async def test_stream_file_download_cloud(db_session, test_user):
    """Test streaming download from cloud storage"""
    service = DownloadService()
    
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
        cloud_provider="google_drive",
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
        cloud_provider="google_drive",
    )
    db_session.add(chunk1)
    db_session.add(chunk2)
    await db_session.commit()
    
    # Mock cloud download service
    with patch("app.services.download_service.CloudDownloadService") as mock_cloud_service_class:
        mock_cloud_service = AsyncMock()
        mock_cloud_service_class.return_value = mock_cloud_service
        
        mock_cloud_service.get_cloud_account = AsyncMock(return_value=MagicMock())
        mock_cloud_service.get_access_token = AsyncMock(return_value="access_token")
        mock_cloud_service.download_file_from_google_drive = AsyncMock(
            side_effect=[b"encrypted_chunk_1", b"encrypted_chunk_2"]
        )
        
        # Mock encryption service
        with patch("app.services.download_service.encryption_service") as mock_encryption:
            mock_encryption.verify_checksum = MagicMock(return_value=True)
            mock_encryption.derive_chunk_key = MagicMock(return_value=b"chunk_key")
            mock_encryption.decrypt_file_chunk = MagicMock(
                side_effect=[b"decrypted_chunk_1", b"decrypted_chunk_2"]
            )
            
            # Get user key
            from app.services.encryption_service import encryption_service as real_encryption
            user_key = await real_encryption.get_or_create_user_encryption_key(
                db_session, str(test_user.id)
            )
            
            # Stream download
            chunks = []
            async for chunk in service.stream_file_download(
                db_session, str(test_user.id), str(file.id), user_key
            ):
                chunks.append(chunk)
            
            # Verify chunks were streamed
            assert len(chunks) > 0


@pytest.mark.asyncio
async def test_download_file_full(db_session, test_user):
    """Test full file download (non-streaming)"""
    service = DownloadService()
    
    # Mock stream_file_download
    async def mock_stream():
        yield b"chunk1"
        yield b"chunk2"
        yield b"chunk3"
    
    with patch.object(
        service, "stream_file_download", return_value=mock_stream()
    ):
        result = await service.download_file_full(
            db_session, str(test_user.id), "test_file_id", b"user_key"
        )
        
        assert result == b"chunk1chunk2chunk3"


@pytest.mark.asyncio
async def test_checksum_verification_failure(db_session, test_user):
    """Test checksum verification failure during download"""
    service = DownloadService()
    
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
    
    # Create chunk
    chunk = StorageChunk(
        id=uuid4(),
        file_id=file.id,
        chunk_index=0,
        chunk_size=100,
        encrypted_size=120,
        iv=b"test_iv",
        encryption_key_encrypted="encrypted_key",
        checksum="checksum",
        storage_path="/path/to/chunk.enc",
    )
    db_session.add(chunk)
    await db_session.commit()
    
    # Mock encryption service with checksum failure
    with patch("app.services.download_service.encryption_service") as mock_encryption:
        mock_encryption.get_or_create_user_encryption_key = AsyncMock(
            return_value=b"user_key"
        )
        mock_encryption.verify_checksum = MagicMock(return_value=False)
        
        # Mock file reading
        with patch("aiofiles.open", new_callable=AsyncMock):
            with patch("pathlib.Path.exists", return_value=True):
                # Get user key
                from app.services.encryption_service import encryption_service as real_encryption
                user_key = await real_encryption.get_or_create_user_encryption_key(
                    db_session, str(test_user.id)
                )
                
                # Stream download should raise error
                with pytest.raises(ValueError, match="Checksum verification failed"):
                    async for _ in service.stream_file_download(
                        db_session, str(test_user.id), str(file.id), user_key
                    ):
                        pass
