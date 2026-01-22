# Encryption Architecture Documentation

This document describes the encryption architecture and approach used in BalanceCloud MVP.

## Table of Contents

- [Overview](#overview)
- [Encryption Layers](#encryption-layers)
- [Key Management](#key-management)
- [File Chunking](#file-chunking)
- [Chunk Encryption](#chunk-encryption)
- [Security Properties](#security-properties)
- [Performance Characteristics](#performance-characteristics)
- [Compliance](#compliance)

## Overview

BalanceCloud uses a **multi-layer encryption architecture** with **chunk-level encryption** to ensure:
- **Zero-Trust**: Files are encrypted before leaving the gateway
- **Chunk-Level Security**: Each chunk has a unique encryption key
- **Key Isolation**: User keys are encrypted at rest
- **Forward Secrecy**: Compromising one chunk doesn't affect others

## Encryption Layers

### Layer 1: Master Key (Application Level)

**Purpose**: Encrypt user encryption keys at rest

- **Algorithm**: AES-256-GCM
- **Key Derivation**: PBKDF2-HMAC-SHA256 (100,000 iterations)
- **Source**: `ENCRYPTION_KEY` environment variable
- **Salt**: Fixed application salt (`balancecloud_mvp_salt`)

**Usage**: Encrypts user keys before storing in database

### Layer 2: User Key (User Level)

**Purpose**: Primary encryption key for each user

- **Algorithm**: Random 256-bit key generation
- **Storage**: Encrypted with master key, stored in `encryption_keys` table
- **Lifetime**: Per-user, persistent across sessions

**Usage**: 
- Derives chunk keys
- Encrypts chunk keys for storage

### Layer 3: Chunk Key (File Chunk Level)

**Purpose**: Unique encryption key for each file chunk

- **Algorithm**: HKDF-SHA256
- **Derivation**: From user key + file_id + chunk_index
- **Properties**: 
  - Each chunk has a unique key
  - Same chunk always derives to same key
  - Different chunks have different keys

**Usage**: Encrypts individual file chunks

## Key Management

### User Key Lifecycle

1. **Generation**: 
   - Random 256-bit key generated using `os.urandom(32)`
   - Generated on first file upload or user creation

2. **Encryption**:
   - Encrypted with master key using AES-256-GCM
   - Salt generated per encryption (PBKDF2)
   - Stored in database as base64-encoded strings

3. **Retrieval**:
   - Retrieved from database
   - Decrypted using master key
   - Cached in memory during session

4. **Rotation** (Future):
   - User keys can be rotated
   - Old files remain decryptable with old keys
   - New files use new keys

### Chunk Key Derivation

**Algorithm**: HKDF (HMAC-based Key Derivation Function)

```python
info = f"{file_id}:{chunk_index}".encode("utf-8")
chunk_key = HKDF(
    algorithm=SHA256,
    length=32,  # 256 bits
    salt=user_key,  # Full user key as salt
    info=info,
).derive(user_key)
```

**Properties**:
- **Deterministic**: Same inputs always produce same key
- **Unique**: Different file_id or chunk_index produces different key
- **Secure**: HKDF provides cryptographic security

## File Chunking

### Chunk Size

- **Default**: 10 MB per chunk
- **Configurable**: Via `chunk_size` parameter
- **Rationale**: 
  - Balance between security and performance
  - Efficient for cloud storage uploads
  - Manageable memory footprint

### Chunking Algorithm

```python
def chunk_file(file_data: bytes, chunk_size: int = 10 * 1024 * 1024) -> list[bytes]:
    chunks = []
    for i in range(0, len(file_data), chunk_size):
        chunks.append(file_data[i : i + chunk_size])
    return chunks
```

**Properties**:
- **Simple**: Sequential splitting
- **Efficient**: O(n) time complexity
- **Memory Efficient**: Can be streamed for large files

### Chunk Indexing

- Chunks are indexed starting from 0
- Sequential ordering ensures correct reassembly
- Stored in `storage_chunks` table with `chunk_index` field

## Chunk Encryption

### Encryption Process

1. **Derive Chunk Key**: `HKDF(user_key, file_id, chunk_index)`
2. **Generate IV**: Random 12-byte nonce (GCM requirement)
3. **Encrypt**: `AES-256-GCM.encrypt(iv, chunk_data, None)`
4. **Extract Tag**: GCM authentication tag (last 16 bytes)
5. **Store**: Encrypted data + IV + checksum

### Encryption Algorithm: AES-256-GCM

**Why GCM?**
- **Authenticated Encryption**: Provides both confidentiality and authenticity
- **Performance**: Hardware-accelerated on modern CPUs
- **Security**: Proven secure mode
- **Tag Verification**: Automatic integrity checking

**Parameters**:
- **Key Size**: 256 bits (32 bytes)
- **IV Size**: 96 bits (12 bytes)
- **Tag Size**: 128 bits (16 bytes)
- **Block Size**: 128 bits (AES standard)

### Encryption Format

```
[Encrypted Chunk] = [Ciphertext] + [GCM Tag (16 bytes)]
[Stored Data] = [Encrypted Chunk] + [IV (12 bytes)] + [Checksum (hex string)]
```

### Decryption Process

1. **Retrieve**: Encrypted data, IV, and checksum
2. **Verify Checksum**: Compare GCM tag with stored checksum
3. **Derive Chunk Key**: Same HKDF process as encryption
4. **Decrypt**: `AES-256-GCM.decrypt(iv, encrypted_data, None)`
5. **Verify**: GCM automatically verifies tag (raises exception if invalid)

## Security Properties

### Confidentiality

- **File Data**: Encrypted with AES-256-GCM
- **User Keys**: Encrypted at rest with master key
- **Chunk Keys**: Derived from user key (not stored)
- **OAuth Tokens**: Encrypted with master key

### Integrity

- **GCM Authentication**: Every chunk has authentication tag
- **Checksum Verification**: SHA-256 checksums for additional verification
- **Tamper Detection**: Modified chunks fail decryption

### Forward Secrecy

- **Chunk Isolation**: Each chunk has unique key
- **Key Derivation**: Compromising one chunk key doesn't reveal others
- **No Key Reuse**: Different files/chunks use different keys

### Key Security

- **Master Key**: Never stored, derived from environment variable
- **User Keys**: Encrypted at rest, never transmitted
- **Chunk Keys**: Derived on-demand, never stored
- **Key Rotation**: Supported (future enhancement)

## Performance Characteristics

### Encryption Throughput

Based on performance testing:

| Chunk Size | Encryption Speed | Decryption Speed |
|------------|-----------------|-------------------|
| 1 KB       | ~100+ MB/s      | ~100+ MB/s       |
| 10 KB      | ~100+ MB/s      | ~100+ MB/s       |
| 100 KB     | ~100+ MB/s      | ~100+ MB/s       |
| 1 MB       | ~50-100 MB/s    | ~50-100 MB/s     |
| 10 MB      | ~20-50 MB/s     | ~20-50 MB/s      |

*Actual performance depends on hardware and system load*

### Key Derivation Performance

- **HKDF Derivation**: ~10,000+ keys/second
- **Average Latency**: < 0.1 ms per key
- **Overhead**: Negligible for file operations

### Memory Usage

- **Chunking**: Memory efficient (can be streamed)
- **Encryption**: In-place where possible
- **Large Files**: Handled via chunking (10MB chunks)

## Compliance

### Encryption Standards

- **AES-256**: FIPS 140-2 approved
- **GCM Mode**: NIST recommended
- **HKDF**: RFC 5869 compliant
- **PBKDF2**: NIST SP 800-132 compliant

### Key Management

- **Key Generation**: Cryptographically secure random (`os.urandom`)
- **Key Storage**: Encrypted at rest
- **Key Derivation**: Standard algorithms (HKDF, PBKDF2)
- **Key Rotation**: Supported architecture

## Threat Model

### Protected Against

✅ **Data at Rest**: All data encrypted in database and storage  
✅ **Data in Transit**: HTTPS/TLS for API communication  
✅ **Cloud Provider Access**: Files encrypted before cloud upload  
✅ **Database Compromise**: User keys encrypted, chunk keys not stored  
✅ **Chunk Tampering**: GCM authentication detects modifications  
✅ **Key Reuse**: Each chunk has unique key  

### Not Protected Against

❌ **Compromised Master Key**: If `ENCRYPTION_KEY` is compromised, all data is at risk  
❌ **Memory Dumps**: Keys in memory during operation (mitigated by short-lived sessions)  
❌ **Side-Channel Attacks**: Not specifically hardened (standard implementation)  

## Best Practices

1. **Master Key Security**:
   - Store `ENCRYPTION_KEY` in secure environment variables
   - Never commit to version control
   - Rotate periodically

2. **Key Management**:
   - Use strong, random master key (32+ bytes)
   - Implement key rotation procedures
   - Monitor key access

3. **Performance**:
   - Use appropriate chunk sizes (10MB default)
   - Monitor encryption/decryption throughput
   - Optimize for your use case

4. **Backup**:
   - Backup encrypted data
   - Backup master key securely
   - Test recovery procedures

## Testing

Comprehensive tests are available in:
- `tests/test_encryption_comprehensive.py` - Full test suite
- `tests/test_chunked_encryption.py` - Chunking tests
- `scripts/test_encryption_performance.py` - Performance benchmarks

Run tests:
```bash
pytest tests/test_encryption_comprehensive.py -v
python scripts/test_encryption_performance.py
```

## References

- [AES-GCM Specification](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)
- [HKDF RFC 5869](https://tools.ietf.org/html/rfc5869)
- [PBKDF2 NIST SP 800-132](https://csrc.nist.gov/publications/detail/sp/800-132/final)
- [Encryption Service Contract](./ENCRYPTION_SERVICE_CONTRACT.md)
