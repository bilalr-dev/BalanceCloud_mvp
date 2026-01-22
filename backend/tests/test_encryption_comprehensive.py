"""
Comprehensive Encryption and Storage Tests

Tests encryption/decryption, chunking, key management, and performance
"""

import time
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models.encryption_key import EncryptionKey
from app.models.file import File
from app.models.storage_chunk import StorageChunk
from app.services.encryption_service import encryption_service
from app.services.file_service import file_service


class TestFileChunking:
    """Test file chunking with various sizes"""

    @pytest.mark.asyncio
    async def test_chunking_small_file(self, db_session, test_user):
        """Test chunking a small file (< 10MB)"""
        user_id = str(test_user.id)
        
        # Small file (1KB)
        file_data = b"x" * 1024
        
        saved_file = await file_service.save_file(
            db=db_session,
            user_id=user_id,
            name="small_file.txt",
            file_data=file_data,
            mime_type="text/plain",
        )
        
        # Should create 1 chunk
        result = await db_session.execute(
            select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
        )
        chunks = result.scalars().all()
        assert len(chunks) == 1
        assert chunks[0].chunk_index == 0

    @pytest.mark.asyncio
    async def test_chunking_medium_file(self, db_session, test_user):
        """Test chunking a medium file (exactly 10MB)"""
        user_id = str(test_user.id)
        
        # Exactly 10MB
        file_data = b"x" * (10 * 1024 * 1024)
        
        saved_file = await file_service.save_file(
            db=db_session,
            user_id=user_id,
            name="medium_file.txt",
            file_data=file_data,
            mime_type="text/plain",
        )
        
        # Should create 1 chunk (exactly at chunk size)
        result = await db_session.execute(
            select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
        )
        chunks = result.scalars().all()
        assert len(chunks) == 1

    @pytest.mark.asyncio
    async def test_chunking_large_file(self, db_session, test_user):
        """Test chunking a large file (multiple chunks)"""
        user_id = str(test_user.id)
        
        # 25MB file (should create 3 chunks: 10MB + 10MB + 5MB)
        file_data = b"x" * (25 * 1024 * 1024)
        
        saved_file = await file_service.save_file(
            db=db_session,
            user_id=user_id,
            name="large_file.txt",
            file_data=file_data,
            mime_type="text/plain",
        )
        
        result = await db_session.execute(
            select(StorageChunk)
            .where(StorageChunk.file_id == saved_file.id)
            .order_by(StorageChunk.chunk_index)
        )
        chunks = result.scalars().all()
        
        assert len(chunks) == 3
        assert chunks[0].chunk_index == 0
        assert chunks[1].chunk_index == 1
        assert chunks[2].chunk_index == 2
        
        # Verify chunk sizes
        assert chunks[0].chunk_size == 10 * 1024 * 1024
        assert chunks[1].chunk_size == 10 * 1024 * 1024
        assert chunks[2].chunk_size == 5 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_chunking_very_large_file(self, db_session, test_user):
        """Test chunking a very large file (100MB+)"""
        user_id = str(test_user.id)
        
        # 100MB file (should create 10 chunks)
        file_data = b"x" * (100 * 1024 * 1024)
        
        saved_file = await file_service.save_file(
            db=db_session,
            user_id=user_id,
            name="very_large_file.txt",
            file_data=file_data,
            mime_type="text/plain",
        )
        
        result = await db_session.execute(
            select(StorageChunk)
            .where(StorageChunk.file_id == saved_file.id)
            .order_by(StorageChunk.chunk_index)
        )
        chunks = result.scalars().all()
        
        assert len(chunks) == 10
        # Verify all chunks are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    @pytest.mark.asyncio
    async def test_chunking_empty_file(self, db_session, test_user):
        """Test chunking an empty file"""
        user_id = str(test_user.id)
        
        file_data = b""
        
        saved_file = await file_service.save_file(
            db=db_session,
            user_id=user_id,
            name="empty_file.txt",
            file_data=file_data,
            mime_type="text/plain",
        )
        
        result = await db_session.execute(
            select(StorageChunk).where(StorageChunk.file_id == saved_file.id)
        )
        chunks = result.scalars().all()
        
        # Empty file creates 0 chunks (no data to chunk)
        assert len(chunks) == 0


class TestEncryptionDecryption:
    """Test encryption and decryption functionality"""

    @pytest.mark.asyncio
    async def test_user_key_generation(self):
        """Test user key generation"""
        key1 = await encryption_service.generate_user_encryption_key()
        key2 = await encryption_service.generate_user_encryption_key()
        
        # Keys should be 32 bytes (256 bits)
        assert len(key1) == 32
        assert len(key2) == 32
        
        # Keys should be different
        assert key1 != key2

    @pytest.mark.asyncio
    async def test_user_key_encryption_decryption(self):
        """Test encrypting and decrypting user keys"""
        user_key = await encryption_service.generate_user_encryption_key()
        
        # Encrypt
        encrypted_key, salt = await encryption_service.encrypt_user_key(user_key)
        
        # Verify encrypted key is different
        assert encrypted_key != user_key
        assert len(salt) == 16
        
        # Decrypt
        decrypted_key = await encryption_service.decrypt_user_key(encrypted_key, salt)
        
        # Should match original
        assert decrypted_key == user_key

    @pytest.mark.asyncio
    async def test_chunk_key_derivation(self):
        """Test chunk key derivation"""
        user_key = await encryption_service.generate_user_encryption_key()
        file_id = str(uuid4())
        
        # Derive keys for different chunks
        key1 = encryption_service.derive_chunk_key(user_key, file_id, 0)
        key2 = encryption_service.derive_chunk_key(user_key, file_id, 1)
        key3 = encryption_service.derive_chunk_key(user_key, file_id, 0)  # Same chunk
        
        # Different chunks should have different keys
        assert key1 != key2
        
        # Same chunk should have same key
        assert key1 == key3
        
        # Keys should be 32 bytes
        assert len(key1) == 32
        assert len(key2) == 32

    @pytest.mark.asyncio
    async def test_file_chunk_encryption_decryption(self):
        """Test encrypting and decrypting file chunks"""
        user_key = await encryption_service.generate_user_encryption_key()
        file_id = str(uuid4())
        chunk_index = 0
        
        # Original chunk data
        chunk_data = b"test chunk data " * 1000  # ~16KB
        
        # Derive chunk key
        chunk_key = encryption_service.derive_chunk_key(user_key, file_id, chunk_index)
        
        # Encrypt chunk
        encrypted_data, iv, checksum_hex = encryption_service.encrypt_file_chunk(
            chunk_data, chunk_key
        )
        
        # Verify encrypted data is different
        assert encrypted_data != chunk_data
        assert len(iv) == 12  # GCM nonce is 12 bytes
        assert len(checksum_hex) == 32  # GCM tag hex is 32 chars (16 bytes * 2)
        
        # Verify checksum
        assert encryption_service.verify_checksum(encrypted_data, checksum_hex)
        
        # Decrypt chunk
        decrypted_data = encryption_service.decrypt_file_chunk(
            encrypted_data, chunk_key, iv
        )
        
        # Should match original
        assert decrypted_data == chunk_data

    @pytest.mark.asyncio
    async def test_checksum_verification(self):
        """Test checksum verification"""
        user_key = await encryption_service.generate_user_encryption_key()
        chunk_data = b"test data"
        chunk_key = encryption_service.derive_chunk_key(user_key, "file1", 0)
        
        encrypted_data, iv, checksum_hex = encryption_service.encrypt_file_chunk(
            chunk_data, chunk_key
        )
        
        # Valid checksum should pass
        assert encryption_service.verify_checksum(encrypted_data, checksum_hex)
        
        # Invalid checksum should fail
        invalid_checksum = "a" * 64
        assert not encryption_service.verify_checksum(encrypted_data, invalid_checksum)
        
        # Modified data should fail
        modified_data = encrypted_data[:-1] + b"x"
        assert not encryption_service.verify_checksum(modified_data, checksum_hex)


class TestKeyStorageAndRetrieval:
    """Test key storage and retrieval from database"""

    @pytest.mark.asyncio
    async def test_get_or_create_user_key_new_user(self, db_session, test_user):
        """Test creating a new user key"""
        user_id = str(test_user.id)
        
        # Get or create key
        user_key = await encryption_service.get_or_create_user_encryption_key(
            db_session, user_id
        )
        
        # Should return a key
        assert user_key is not None
        assert len(user_key) == 32
        
        # Should be stored in database
        result = await db_session.execute(
            select(EncryptionKey).where(EncryptionKey.user_id == user_id)
        )
        key_record = result.scalar_one_or_none()
        assert key_record is not None
        assert key_record.key_encrypted is not None
        assert key_record.salt is not None

    @pytest.mark.asyncio
    async def test_get_or_create_user_key_existing_user(self, db_session, test_user):
        """Test retrieving existing user key"""
        user_id = str(test_user.id)
        
        # Create key first time
        key1 = await encryption_service.get_or_create_user_encryption_key(
            db_session, user_id
        )
        
        # Get key second time (should retrieve same key)
        key2 = await encryption_service.get_or_create_user_encryption_key(
            db_session, user_id
        )
        
        # Should be the same key
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_key_retrieval_after_encryption(self, db_session, test_user):
        """Test that retrieved key can decrypt previously encrypted data"""
        user_id = str(test_user.id)
        
        # Get user key
        user_key = await encryption_service.get_or_create_user_encryption_key(
            db_session, user_id
        )
        
        # Encrypt some data
        file_id = str(uuid4())
        chunk_key = encryption_service.derive_chunk_key(user_key, file_id, 0)
        chunk_data = b"test data"
        encrypted_data, iv, _ = encryption_service.encrypt_file_chunk(
            chunk_data, chunk_key
        )
        
        # Get key again (simulating new session)
        retrieved_key = await encryption_service.get_or_create_user_encryption_key(
            db_session, user_id
        )
        
        # Should be able to decrypt with retrieved key
        retrieved_chunk_key = encryption_service.derive_chunk_key(
            retrieved_key, file_id, 0
        )
        decrypted_data = encryption_service.decrypt_file_chunk(
            encrypted_data, retrieved_chunk_key, iv
        )
        
        assert decrypted_data == chunk_data


class TestLargeFileHandling:
    """Test handling of large files"""

    @pytest.mark.asyncio
    async def test_large_file_upload_download(self, db_session, test_user):
        """Test uploading and downloading a large file"""
        user_id = str(test_user.id)
        
        # 50MB file
        file_data = b"x" * (50 * 1024 * 1024)
        
        # Upload
        saved_file = await file_service.save_file(
            db=db_session,
            user_id=user_id,
            name="large_file.bin",
            file_data=file_data,
            mime_type="application/octet-stream",
        )
        
        # Download
        user_key = await encryption_service.get_or_create_user_encryption_key(
            db_session, user_id
        )
        downloaded_data = await file_service.get_file_data(
            db_session, user_id, str(saved_file.id), user_key
        )
        
        # Should match
        assert downloaded_data == file_data
        assert len(downloaded_data) == len(file_data)

    @pytest.mark.asyncio
    async def test_multiple_large_files(self, db_session, test_user):
        """Test handling multiple large files"""
        user_id = str(test_user.id)
        
        files_data = []
        file_ids = []
        
        # Upload 5 large files
        for i in range(5):
            file_data = b"x" * (20 * 1024 * 1024)  # 20MB each
            files_data.append(file_data)
            
            saved_file = await file_service.save_file(
                db=db_session,
                user_id=user_id,
                name=f"large_file_{i}.bin",
                file_data=file_data,
                mime_type="application/octet-stream",
            )
            file_ids.append(saved_file.id)
        
        # Download and verify all
        user_key = await encryption_service.get_or_create_user_encryption_key(
            db_session, user_id
        )
        
        for i, file_id in enumerate(file_ids):
            downloaded_data = await file_service.get_file_data(
                db_session, user_id, str(file_id), user_key
            )
            assert downloaded_data == files_data[i]


class TestPerformance:
    """Performance testing for encryption operations"""

    @pytest.mark.asyncio
    async def test_encryption_throughput(self):
        """Test encryption throughput"""
        user_key = await encryption_service.generate_user_encryption_key()
        file_id = str(uuid4())
        
        # Test with 1MB chunks
        chunk_data = b"x" * (1024 * 1024)
        chunk_key = encryption_service.derive_chunk_key(user_key, file_id, 0)
        
        # Time encryption
        start = time.time()
        for _ in range(10):
            encryption_service.encrypt_file_chunk(chunk_data, chunk_key)
        elapsed = time.time() - start
        
        # Should encrypt 10MB in reasonable time (< 5 seconds)
        assert elapsed < 5.0
        throughput = (10 * 1024 * 1024) / elapsed
        print(f"Encryption throughput: {throughput / (1024 * 1024):.2f} MB/s")

    @pytest.mark.asyncio
    async def test_decryption_throughput(self):
        """Test decryption throughput"""
        user_key = await encryption_service.generate_user_encryption_key()
        file_id = str(uuid4())
        
        chunk_data = b"x" * (1024 * 1024)
        chunk_key = encryption_service.derive_chunk_key(user_key, file_id, 0)
        
        # Encrypt first
        encrypted_data, iv, _ = encryption_service.encrypt_file_chunk(
            chunk_data, chunk_key
        )
        
        # Time decryption
        start = time.time()
        for _ in range(10):
            encryption_service.decrypt_file_chunk(encrypted_data, chunk_key, iv)
        elapsed = time.time() - start
        
        # Should decrypt 10MB in reasonable time (< 5 seconds)
        assert elapsed < 5.0
        throughput = (10 * 1024 * 1024) / elapsed
        print(f"Decryption throughput: {throughput / (1024 * 1024):.2f} MB/s")

    @pytest.mark.asyncio
    async def test_key_derivation_performance(self):
        """Test chunk key derivation performance"""
        user_key = await encryption_service.generate_user_encryption_key()
        file_id = str(uuid4())
        
        # Time key derivation
        start = time.time()
        for i in range(1000):
            encryption_service.derive_chunk_key(user_key, file_id, i)
        elapsed = time.time() - start
        
        # Should derive 1000 keys quickly (< 1 second)
        assert elapsed < 1.0
        print(f"Key derivation: {1000 / elapsed:.0f} keys/second")

    @pytest.mark.asyncio
    async def test_end_to_end_performance(self, db_session, test_user):
        """Test end-to-end file upload/download performance"""
        user_id = str(test_user.id)
        
        # 10MB file
        file_data = b"x" * (10 * 1024 * 1024)
        
        # Time upload
        start = time.time()
        saved_file = await file_service.save_file(
            db=db_session,
            user_id=user_id,
            name="perf_test.bin",
            file_data=file_data,
            mime_type="application/octet-stream",
        )
        upload_time = time.time() - start
        
        # Time download
        user_key = await encryption_service.get_or_create_user_encryption_key(
            db_session, user_id
        )
        start = time.time()
        downloaded_data = await file_service.get_file_data(
            db_session, user_id, str(saved_file.id), user_key
        )
        download_time = time.time() - start
        
        # Verify correctness
        assert downloaded_data == file_data
        
        # Performance should be reasonable
        assert upload_time < 10.0  # 10MB upload in < 10 seconds
        assert download_time < 10.0  # 10MB download in < 10 seconds
        
        print(f"Upload: {len(file_data) / upload_time / (1024 * 1024):.2f} MB/s")
        print(f"Download: {len(file_data) / download_time / (1024 * 1024):.2f} MB/s")
