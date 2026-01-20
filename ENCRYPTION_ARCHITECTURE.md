# Encryption Architecture Design

**Version:** 1.0  
**Date:** 2026-01-20  
**Status:** ✅ Design Complete - Ready for Implementation

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Key Management](#key-management)
4. [Chunking Strategy](#chunking-strategy)
5. [Database Schema](#database-schema)
6. [Encryption Flow](#encryption-flow)
7. [Security Considerations](#security-considerations)
8. [Implementation Details](#implementation-details)

---

## 🎯 Overview

This document defines the encryption architecture for BalanceCloud MVP v1, moving from simple file-level encryption to a sophisticated chunk-based encryption system with secure key management.

### Current State (MVP)
- **File-level encryption**: Entire files encrypted as single units
- **In-memory key storage**: User keys stored in memory (temporary)
- **Simple storage**: Two files per encrypted file (`.enc` + `.nonce`)

### Target State (MVP v1)
- **Chunk-based encryption**: Files split into 10MB chunks
- **Database key storage**: User encryption keys stored encrypted in database
- **Chunk-specific keys**: Each chunk has a unique derived key
- **Structured storage**: Chunks stored with metadata in database

---

## 🏗️ Architecture Principles

### 1. **Zero-Knowledge Architecture**
- Server never sees unencrypted file data
- User keys encrypted with master key before storage
- Master key never leaves server memory

### 2. **Per-User Encryption Keys**
- Each user has a unique 256-bit encryption key
- Keys are generated using cryptographically secure random number generator
- Keys are encrypted with master key before database storage

### 3. **Chunk-Based Encryption**
- Large files split into 10MB chunks for efficiency
- Each chunk encrypted independently
- Enables parallel processing and partial file access

### 4. **Key Derivation**
- Chunk-specific keys derived from user key using HKDF
- Unique keys per chunk prevent key reuse attacks
- File ID and chunk index ensure uniqueness

### 5. **Authenticated Encryption**
- AES-256-GCM for encryption and authentication
- Prevents tampering and ensures data integrity
- 96-bit nonces (IVs) for each encryption operation

---

## 🔐 Key Management

### Master Key

**Purpose:** Encrypt user encryption keys before database storage

**Derivation:**
```
Master Key = PBKDF2-HMAC-SHA256(
    password: ENCRYPTION_KEY (from environment)
    salt: "balancecloud_master_salt"
    iterations: 100,000
    length: 32 bytes (256 bits)
)
```

**Storage:** Never stored, only derived at runtime from `ENCRYPTION_KEY`

**Security:**
- Must be set via environment variable
- Never logged or exposed
- Rotated by changing `ENCRYPTION_KEY`

### User Encryption Keys

**Purpose:** Encrypt user's file data

**Generation:**
- 32 bytes (256 bits) of cryptographically secure random data
- Generated once per user on first file upload
- Stored encrypted in `encryption_keys` table

**Storage Format:**
```python
encrypted_user_key = AES-256-GCM(
    key: master_key
    plaintext: user_key (32 bytes)
    nonce: random 12 bytes
)
# Stored as: base64(nonce + ciphertext)
```

**Database Schema:**
```sql
CREATE TABLE encryption_keys (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_encrypted TEXT NOT NULL,  -- base64(nonce + encrypted_key)
    salt TEXT(64) NOT NULL,       -- base64(salt) for future use
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Chunk Keys

**Purpose:** Encrypt individual file chunks

**Derivation:**
```python
chunk_key = HKDF-SHA256(
    input_key_material: user_key
    info: f"{file_id}:{chunk_index}"
    length: 32 bytes
)
```

**Characteristics:**
- Derived from user key (not stored)
- Unique per chunk (file_id + chunk_index)
- Computed on-demand during encryption/decryption

---

## 📦 Chunking Strategy

### Chunk Size: 10MB

**Rationale:**
- **Balance between efficiency and security**: Large enough to minimize overhead, small enough for parallel processing
- **Memory efficiency**: Can process chunks in memory without excessive RAM usage
- **Network efficiency**: Enables streaming and partial downloads
- **Cloud storage compatibility**: Aligns with common cloud provider chunk sizes

### Chunking Algorithm

```python
CHUNK_SIZE = 10 * 1024 * 1024  # 10MB

def chunk_file(file_data: bytes) -> list[bytes]:
    """Split file into 10MB chunks"""
    chunks = []
    offset = 0
    while offset < len(file_data):
        chunk = file_data[offset:offset + CHUNK_SIZE]
        chunks.append(chunk)
        offset += CHUNK_SIZE
    return chunks
```

### Chunk Metadata

Each chunk requires:
- **Chunk index**: Sequential index (0, 1, 2, ...)
- **Chunk size**: Actual size of chunk (may be < 10MB for last chunk)
- **IV (Nonce)**: 12 bytes, unique per chunk
- **Encrypted chunk key**: Chunk key encrypted with user's master key
- **Checksum**: SHA-256 hash of encrypted chunk for integrity verification
- **Storage path**: Path to encrypted chunk file on disk

### Chunk Storage Structure

```
storage/
└── {user_id}/
    └── {file_id}/
        ├── chunk_0.enc    # Encrypted chunk 0
        ├── chunk_1.enc    # Encrypted chunk 1
        └── chunk_2.enc    # Encrypted chunk 2 (last chunk, may be < 10MB)
```

**Database Storage:**
- Chunk metadata stored in `storage_chunks` table
- Encrypted data stored as files on disk
- Enables efficient querying and management

---

## 🗄️ Database Schema

### Encryption Keys Table

```sql
CREATE TABLE encryption_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_encrypted TEXT NOT NULL,           -- base64(nonce + encrypted_key)
    salt TEXT(64) NOT NULL,                -- base64(salt) for future KDF
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id)                        -- One key per user
);

CREATE INDEX idx_encryption_keys_user_id ON encryption_keys(user_id);
```

**Fields:**
- `id`: Unique identifier for the encryption key record
- `user_id`: Foreign key to users table (one-to-one relationship)
- `key_encrypted`: User's encryption key encrypted with master key
- `salt`: Random salt (for future key derivation functions)
- `created_at`: Timestamp when key was created

### Storage Chunks Table

```sql
CREATE TABLE storage_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,          -- 0, 1, 2, ...
    chunk_size INTEGER NOT NULL,           -- Actual size of chunk in bytes
    encrypted_size INTEGER NOT NULL,       -- Size of encrypted chunk
    iv BYTEA NOT NULL,                     -- 12-byte IV (nonce)
    encryption_key_encrypted TEXT NOT NULL, -- Chunk key encrypted with user key
    checksum TEXT(64) NOT NULL,            -- SHA-256 of encrypted chunk
    storage_path TEXT NOT NULL,            -- Path to encrypted chunk file
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(file_id, chunk_index)           -- One chunk per index per file
);

CREATE INDEX idx_storage_chunks_file_id ON storage_chunks(file_id);
CREATE INDEX idx_storage_chunks_file_index ON storage_chunks(file_id, chunk_index);
```

**Fields:**
- `id`: Unique identifier for the chunk record
- `file_id`: Foreign key to files table
- `chunk_index`: Sequential index of chunk (0-based)
- `chunk_size`: Original size of chunk before encryption
- `encrypted_size`: Size of encrypted chunk (includes GCM tag)
- `iv`: Initialization vector (nonce) for AES-GCM
- `encryption_key_encrypted`: Chunk key encrypted with user's master key
- `checksum`: SHA-256 hash of encrypted chunk for integrity
- `storage_path`: File system path to encrypted chunk file
- `created_at`: Timestamp when chunk was created

**Relationships:**
- One file → Many chunks (one-to-many)
- Chunks ordered by `chunk_index` for reassembly

---

## 🔄 Encryption Flow

### File Upload Flow

```
1. User uploads file
   ↓
2. Get or create user encryption key
   - Check encryption_keys table
   - If exists: decrypt and return
   - If not: generate new key, encrypt with master key, store in DB
   ↓
3. Split file into 10MB chunks
   ↓
4. For each chunk:
   a. Derive chunk-specific key (HKDF)
   b. Generate random IV (12 bytes)
   c. Encrypt chunk with AES-256-GCM
   d. Encrypt chunk key with user key
   e. Calculate checksum of encrypted chunk
   f. Save encrypted chunk to disk
   g. Store chunk metadata in storage_chunks table
   ↓
5. Create file record in files table
   ↓
6. Return file metadata to user
```

### File Download Flow

```
1. User requests file download
   ↓
2. Get user encryption key from database
   - Query encryption_keys table
   - Decrypt with master key
   ↓
3. Query storage_chunks table for all chunks
   - Order by chunk_index
   ↓
4. For each chunk:
   a. Read encrypted chunk from disk
   b. Verify checksum
   c. Decrypt chunk key with user key
   d. Decrypt chunk with chunk key and IV
   e. Append decrypted chunk to output
   ↓
5. Stream reassembled file to user
```

### Key Retrieval Flow

```
1. Service needs user encryption key
   ↓
2. Query encryption_keys table WHERE user_id = ?
   ↓
3. If found:
   - Decrypt key_encrypted with master key
   - Return decrypted user key
   ↓
4. If not found:
   - Generate new user key (32 bytes random)
   - Encrypt with master key
   - Store in encryption_keys table
   - Return new user key
```

---

## 🔒 Security Considerations

### 1. **Key Storage Security**

**User Keys:**
- ✅ Encrypted with master key before database storage
- ✅ Never stored in plaintext
- ✅ Master key never stored (derived at runtime)

**Chunk Keys:**
- ✅ Derived on-demand (not stored)
- ✅ Encrypted with user key if stored temporarily
- ✅ Unique per chunk (prevents key reuse)

### 2. **Encryption Algorithm**

**AES-256-GCM:**
- ✅ Industry-standard encryption (AES-256)
- ✅ Authenticated encryption (GCM mode)
- ✅ Prevents tampering and ensures integrity
- ✅ 96-bit nonces (IVs) for each operation

### 3. **Key Derivation**

**HKDF (HMAC-based KDF):**
- ✅ Cryptographically secure key derivation
- ✅ Deterministic (same input = same output)
- ✅ Unique keys per chunk (file_id + chunk_index)

### 4. **Nonce Management**

**IV Generation:**
- ✅ Cryptographically secure random (os.urandom)
- ✅ Unique per encryption operation
- ✅ 12 bytes (96 bits) for GCM mode
- ✅ Stored with encrypted data

### 5. **Data Integrity**

**Checksums:**
- ✅ SHA-256 hash of encrypted chunks
- ✅ Verified on decryption
- ✅ Detects corruption or tampering

### 6. **Access Control**

**Database-Level:**
- ✅ Foreign key constraints ensure data integrity
- ✅ CASCADE delete removes keys/chunks when user/file deleted
- ✅ Unique constraints prevent duplicate keys

**Application-Level:**
- ✅ User keys only accessible to authenticated user
- ✅ Chunks only accessible to file owner
- ✅ Master key never exposed to users

---

## 🛠️ Implementation Details

### Encryption Service Methods

```python
class EncryptionService:
    # Constants
    CHUNK_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Master key management
    def __init__(self):
        # Derive master key from ENCRYPTION_KEY
        pass
    
    # User key management
    def generate_user_encryption_key() -> Tuple[bytes, bytes]
    def encrypt_user_key(user_key: bytes) -> str
    def decrypt_user_key(encrypted_key: str) -> bytes
    async def get_or_create_user_encryption_key(db, user_id) -> Tuple[bytes, bytes]
    
    # Chunk key derivation
    def derive_chunk_key(user_key: bytes, file_id: str, chunk_index: int) -> bytes
    
    # Chunk encryption/decryption
    def encrypt_file_chunk(chunk_data, user_key, file_id, chunk_index) -> Tuple[bytes, bytes, bytes]
    def decrypt_file_chunk(encrypted_chunk, iv, chunk_key_encrypted) -> bytes
    
    # Utilities
    def generate_iv() -> bytes
    def calculate_checksum(data: bytes) -> str
    def verify_checksum(data: bytes, expected: str) -> bool
```

### File Service Updates

```python
class FileService:
    # Chunking
    def _chunk_file(file_data: bytes) -> list[bytes]
    
    # Chunk storage
    async def _save_chunk(chunk_data, chunk_index, file_id, user_key) -> StorageChunk
    async def _get_chunk(chunk_id, user_key) -> bytes
    
    # File operations (updated for chunks)
    async def save_file(...) -> File
    async def get_file_data(...) -> bytes  # Reassembles chunks
```

### Database Models

```python
# app/models/encryption_key.py
class EncryptionKey(Base):
    id: UUID
    user_id: UUID
    key_encrypted: str
    salt: str
    created_at: datetime

# app/models/storage_chunk.py
class StorageChunk(Base):
    id: UUID
    file_id: UUID
    chunk_index: int
    chunk_size: int
    encrypted_size: int
    iv: bytes
    encryption_key_encrypted: str
    checksum: str
    storage_path: str
    created_at: datetime
```

---

## 📊 Performance Considerations

### Chunking Benefits

1. **Memory Efficiency:**
   - Process 10MB chunks instead of entire files
   - Enables handling of very large files (>1GB)

2. **Parallel Processing:**
   - Encrypt/decrypt chunks in parallel
   - Upload/download chunks concurrently

3. **Partial Access:**
   - Download specific chunks without full file
   - Enable streaming for large files

4. **Error Recovery:**
   - Retry individual chunks on failure
   - Resume interrupted uploads/downloads

### Storage Overhead

**Per Chunk:**
- Encrypted data: ~10MB + 16 bytes (GCM tag)
- Metadata: ~500 bytes (database record)
- IV: 12 bytes (stored in database)
- Checksum: 64 bytes (SHA-256 hex)

**Total Overhead:** ~0.5% for metadata + GCM tag

---

## ✅ Migration Path

### From MVP to MVP v1

1. **Database Migration:**
   - Create `encryption_keys` table
   - Create `storage_chunks` table
   - Migrate existing files (optional, can be gradual)

2. **Service Updates:**
   - Update `EncryptionService` with chunking methods
   - Update `FileService` to use chunks
   - Add chunk management methods

3. **Backward Compatibility:**
   - Support both old (file-level) and new (chunk-based) files
   - Migrate files on first access (lazy migration)

---

## 📝 Summary

### Key Design Decisions

1. ✅ **10MB chunks** - Balance between efficiency and overhead
2. ✅ **Database key storage** - Secure, persistent, queryable
3. ✅ **Chunk-specific keys** - Enhanced security via key derivation
4. ✅ **AES-256-GCM** - Industry-standard authenticated encryption
5. ✅ **HKDF key derivation** - Secure, deterministic chunk keys
6. ✅ **Checksum verification** - Data integrity protection

### Deliverables

- ✅ **Encryption architecture document** (this document)
- ✅ **Database schema** (defined above)
- ✅ **Chunking strategy** (10MB chunks, defined above)
- ✅ **Implementation ready** (models, schemas, services)

---

**Status:** ✅ **Design Complete**  
**Next Steps:** Implementation of models, schemas, and service updates
