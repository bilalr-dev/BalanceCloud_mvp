"""
Tests for chunked encryption functionality
"""

import pytest
from uuid import uuid4

from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.services.encryption_service import encryption_service
from app.services.file_service import file_service


@pytest.mark.asyncio
async def test_chunked_file_upload_and_download(db_session, test_user):
    """Test uploading and downloading a file with chunked encryption"""
    user_id = str(test_user.id)
    
    # Generate test file data (larger than chunk size to test chunking)
    chunk_size = 10 * 1024 * 1024  # 10MB
    file_data = b"test file content " * (chunk_size // 20 + 1)  # ~10MB+ of data
    
    # Upload file
    saved_file = await file_service.save_file(
        db=db_session,
        user_id=user_id,
        name="test_chunked_file.txt",
        file_data=file_data,
        mime_type="text/plain",
    )
    
    # Verify file was created
    assert saved_file.id is not None
    assert saved_file.size == len(file_data)
    assert saved_file.storage_path is None  # Chunked files don't use storage_path
    
    # Verify chunks were created
    from sqlalchemy import select
    result = await db_session.execute(
        select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
    )
    chunks = result.scalars().all()
    assert len(chunks) > 0  # Should have at least one chunk
    
    # Verify chunks are ordered correctly
    chunk_indices = [chunk.chunk_index for chunk in chunks]
    assert chunk_indices == sorted(chunk_indices)
    
    # Download and verify file
    user_key = await encryption_service.get_or_create_user_encryption_key(
        db_session, user_id
    )
    downloaded_data = await file_service.get_file_data(
        db_session, user_id, str(saved_file.id), user_key
    )
    
    # Verify data matches
    assert downloaded_data == file_data
    assert len(downloaded_data) == len(file_data)


@pytest.mark.asyncio
async def test_small_file_chunking(db_session, test_user):
    """Test that small files are still chunked (single chunk)"""
    user_id = str(test_user.id)
    
    # Small file (< 10MB)
    file_data = b"small file content"
    
    # Upload file
    saved_file = await file_service.save_file(
        db=db_session,
        user_id=user_id,
        name="small_file.txt",
        file_data=file_data,
        mime_type="text/plain",
    )
    
    # Verify single chunk was created
    from sqlalchemy import select
    result = await db_session.execute(
        select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
    )
    chunks = result.scalars().all()
    assert len(chunks) == 1  # Should have exactly one chunk
    
    # Verify chunk metadata
    chunk = chunks[0]
    assert chunk.chunk_index == 0
    assert chunk.chunk_size == len(file_data)
    assert chunk.iv is not None
    assert chunk.checksum is not None
    assert chunk.storage_path is not None


@pytest.mark.asyncio
async def test_multiple_chunks(db_session, test_user):
    """Test file that spans multiple chunks"""
    user_id = str(test_user.id)
    
    # Create file larger than chunk size
    chunk_size = 10 * 1024 * 1024  # 10MB
    file_data = b"x" * (chunk_size * 2 + 1000)  # ~20MB + 1KB
    
    # Upload file
    saved_file = await file_service.save_file(
        db=db_session,
        user_id=user_id,
        name="large_file.bin",
        file_data=file_data,
        mime_type="application/octet-stream",
    )
    
    # Verify multiple chunks were created
    from sqlalchemy import select
    result = await db_session.execute(
        select(StorageChunk)
        .where(StorageChunk.file_id == saved_file.id)
        .order_by(StorageChunk.chunk_index)
    )
    chunks = result.scalars().all()
    assert len(chunks) >= 2  # Should have at least 2 chunks
    
    # Verify chunk indices are sequential
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
    
    # Verify chunk sizes (last chunk may be smaller)
    total_size = sum(chunk.chunk_size for chunk in chunks)
    assert total_size == len(file_data)
    
    # Download and verify
    user_key = await encryption_service.get_or_create_user_encryption_key(
        db_session, user_id
    )
    downloaded_data = await file_service.get_file_data(
        db_session, user_id, str(saved_file.id), user_key
    )
    assert downloaded_data == file_data


@pytest.mark.asyncio
async def test_chunk_key_derivation(db_session, test_user):
    """Test that chunk keys are derived correctly"""
    user_id = str(test_user.id)
    user_key = await encryption_service.get_or_create_user_encryption_key(
        db_session, user_id
    )
    
    file_id = str(uuid4())
    
    # Derive keys for different chunks
    key1 = encryption_service.derive_chunk_key(user_key, file_id, 0)
    key2 = encryption_service.derive_chunk_key(user_key, file_id, 1)
    key3 = encryption_service.derive_chunk_key(user_key, file_id, 0)  # Same as key1
    
    # Verify keys are different for different indices
    assert key1 != key2
    
    # Verify same chunk index produces same key (deterministic)
    assert key1 == key3
    
    # Verify keys are 32 bytes (256 bits)
    assert len(key1) == 32
    assert len(key2) == 32


@pytest.mark.asyncio
async def test_chunk_encryption_decryption():
    """Test chunk encryption and decryption"""
    # Generate test data
    chunk_data = b"test chunk data " * 100
    
    # Generate chunk key
    user_key = await encryption_service.generate_user_encryption_key()
    file_id = "test-file-id"
    chunk_index = 0
    chunk_key = encryption_service.derive_chunk_key(user_key, file_id, chunk_index)
    
    # Encrypt chunk
    encrypted_data, iv, checksum = encryption_service.encrypt_file_chunk(
        chunk_data, chunk_key
    )
    
    # Verify encrypted data is different
    assert encrypted_data != chunk_data
    assert len(encrypted_data) > len(chunk_data)  # Includes GCM tag
    
    # Decrypt chunk
    decrypted_data = encryption_service.decrypt_file_chunk(
        encrypted_data, chunk_key, iv
    )
    
    # Verify data matches
    assert decrypted_data == chunk_data


@pytest.mark.asyncio
async def test_file_deletion_with_chunks(db_session, test_user):
    """Test that deleting a file also deletes its chunks"""
    user_id = str(test_user.id)
    
    # Upload file
    file_data = b"test content " * 1000
    saved_file = await file_service.save_file(
        db=db_session,
        user_id=user_id,
        name="to_delete.txt",
        file_data=file_data,
        mime_type="text/plain",
    )
    
    # Verify chunks exist
    from sqlalchemy import select
    result = await db_session.execute(
        select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
    )
    chunks_before = result.scalars().all()
    assert len(chunks_before) > 0
    
    # Delete file
    deleted = await file_service.delete_file(
        db_session, user_id, str(saved_file.id)
    )
    assert deleted is True
    
    # Verify chunks are deleted
    result = await db_session.execute(
        select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
    )
    chunks_after = result.scalars().all()
    assert len(chunks_after) == 0
