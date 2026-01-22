#!/usr/bin/env python3
"""
Encryption Performance Testing Script

Tests encryption/decryption performance with various file sizes
"""

import asyncio
import time
from uuid import uuid4

from app.services.encryption_service import encryption_service


async def test_encryption_performance():
    """Test encryption performance with various chunk sizes"""
    print("=" * 60)
    print("Encryption Performance Testing")
    print("=" * 60)

    user_key = await encryption_service.generate_user_encryption_key()
    file_id = str(uuid4())

    # Test different chunk sizes
    test_sizes = [
        (1 * 1024, "1KB"),
        (10 * 1024, "10KB"),
        (100 * 1024, "100KB"),
        (1024 * 1024, "1MB"),
        (10 * 1024 * 1024, "10MB"),
    ]

    print("\nEncryption Performance:")
    print("-" * 60)
    print(f"{'Size':<10} {'Time (ms)':<15} {'Throughput (MB/s)':<20}")
    print("-" * 60)

    for size_bytes, size_label in test_sizes:
        chunk_data = b"x" * size_bytes
        chunk_key = encryption_service.derive_chunk_key(user_key, file_id, 0)

        # Time encryption
        start = time.time()
        for _ in range(10):
            encryption_service.encrypt_file_chunk(chunk_data, chunk_key)
        elapsed = (time.time() - start) * 1000  # Convert to milliseconds

        avg_time = elapsed / 10
        throughput = (size_bytes * 10) / (elapsed / 1000) / (1024 * 1024)

        print(f"{size_label:<10} {avg_time:<15.2f} {throughput:<20.2f}")

    print("\nDecryption Performance:")
    print("-" * 60)
    print(f"{'Size':<10} {'Time (ms)':<15} {'Throughput (MB/s)':<20}")
    print("-" * 60)

    for size_bytes, size_label in test_sizes:
        chunk_data = b"x" * size_bytes
        chunk_key = encryption_service.derive_chunk_key(user_key, file_id, 0)

        # Encrypt first
        encrypted_data, iv, _ = encryption_service.encrypt_file_chunk(
            chunk_data, chunk_key
        )

        # Time decryption
        start = time.time()
        for _ in range(10):
            encryption_service.decrypt_file_chunk(encrypted_data, chunk_key, iv)
        elapsed = (time.time() - start) * 1000

        avg_time = elapsed / 10
        throughput = (size_bytes * 10) / (elapsed / 1000) / (1024 * 1024)

        print(f"{size_label:<10} {avg_time:<15.2f} {throughput:<20.2f}")

    print("\nKey Derivation Performance:")
    print("-" * 60)
    iterations = 10000
    start = time.time()
    for i in range(iterations):
        encryption_service.derive_chunk_key(user_key, file_id, i)
    elapsed = time.time() - start

    print(f"Derived {iterations} keys in {elapsed:.2f} seconds")
    print(f"Rate: {iterations / elapsed:.0f} keys/second")
    print(f"Average: {(elapsed / iterations) * 1000:.3f} ms/key")


async def test_memory_usage():
    """Test memory efficiency with large files"""
    print("\n" + "=" * 60)
    print("Memory Usage Testing")
    print("=" * 60)

    import sys

    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
    except ImportError:
        print("psutil not available, skipping memory tests")
        return

    user_key = await encryption_service.generate_user_encryption_key()
    file_id = str(uuid4())

    # Test with 100MB file
    file_size = 100 * 1024 * 1024
    file_data = b"x" * file_size

    # Measure memory before
    mem_before = process.memory_info().rss / (1024 * 1024)  # MB

    # Chunk and encrypt
    chunks = encryption_service.chunk_file(file_data)
    encrypted_chunks = []

    for i, chunk_data in enumerate(chunks):
        chunk_key = encryption_service.derive_chunk_key(user_key, file_id, i)
        encrypted_data, iv, _ = encryption_service.encrypt_file_chunk(
            chunk_data, chunk_key
        )
        encrypted_chunks.append((encrypted_data, iv))

    # Measure memory after encryption
    mem_after_encrypt = process.memory_info().rss / (1024 * 1024)

    # Decrypt
    decrypted_chunks = []
    for i, (encrypted_data, iv) in enumerate(encrypted_chunks):
        chunk_key = encryption_service.derive_chunk_key(user_key, file_id, i)
        decrypted_data = encryption_service.decrypt_file_chunk(
            encrypted_data, chunk_key, iv
        )
        decrypted_chunks.append(decrypted_data)

    # Measure memory after decryption
    mem_after_decrypt = process.memory_info().rss / (1024 * 1024)

    print(f"\nFile size: {file_size / (1024 * 1024):.1f} MB")
    print(f"Number of chunks: {len(chunks)}")
    print(f"Memory before: {mem_before:.1f} MB")
    print(f"Memory after encryption: {mem_after_encrypt:.1f} MB")
    print(f"Memory increase: {mem_after_encrypt - mem_before:.1f} MB")
    print(f"Memory after decryption: {mem_after_decrypt:.1f} MB")

    # Verify correctness
    reassembled = b"".join(decrypted_chunks)
    assert reassembled == file_data, "Decrypted data doesn't match original!"
    print("\n✅ Memory test passed - data integrity verified")


async def main():
    """Run all performance tests"""
    await test_encryption_performance()
    await test_memory_usage()

    print("\n" + "=" * 60)
    print("Performance testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
