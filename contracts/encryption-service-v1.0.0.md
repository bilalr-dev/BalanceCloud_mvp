# Encryption Service Contract v1.0.0

**Owner:** Bilal (Encryption & File Services)  
**Version:** 1.0.0  
**Status:** 📝 Draft  
**Last Updated:** 2026-01-20  
**Dependencies:** None

---

## Overview

This contract defines the Encryption Service interface for file encryption, chunking, and key management. It specifies how files are encrypted, chunked, and how encryption keys are stored and managed.

**Based on:** TASKS_PLANING.md - Day 1-3 tasks for Encryption & File Services

**Key Features:**
- File chunking (10MB chunks)
- User encryption key storage (encrypted in database)
- Chunk-level encryption with derived keys
- AES-256-GCM encryption

---

## Service Interface

### Key Management

```python
class EncryptionService:
    """Encryption service interface"""
    
    # User Key Management
    async def generate_user_encryption_key(self) -> bytes:
        """Generate a new user encryption key (256 bits)"""
        pass
    
    async def get_or_create_user_encryption_key(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> bytes:
        """Get existing user key or create new one"""
        # Returns: decrypted user encryption key (bytes)
        pass
    
    async def encrypt_user_key(
        self, 
        user_key: bytes
    ) -> tuple[bytes, bytes]:
        """Encrypt user key with application master key"""
        # Returns: (encrypted_key, salt)
        pass
    
    async def decrypt_user_key(
        self, 
        encrypted_key: bytes, 
        salt: bytes
    ) -> bytes:
        """Decrypt user key using application master key"""
        # Returns: decrypted user key (bytes)
        pass
    
    # Chunk Key Derivation
    def derive_chunk_key(
        self, 
        user_key: bytes, 
        file_id: str, 
        chunk_index: int
    ) -> bytes:
        """Derive encryption key for a specific chunk"""
        # Uses HKDF to derive chunk-specific key
        # Returns: 256-bit chunk key
        pass
    
    # File Chunking
    def chunk_file(
        self, 
        file_data: bytes, 
        chunk_size: int = 10 * 1024 * 1024
    ) -> list[bytes]:
        """Split file into chunks"""
        # Default chunk size: 10MB
        # Returns: list of chunk bytes
        pass
    
    # Chunk Encryption/Decryption
    def encrypt_file_chunk(
        self, 
        chunk_data: bytes, 
        chunk_key: bytes
    ) -> tuple[bytes, bytes, bytes]:
        """Encrypt a file chunk"""
        # Returns: (encrypted_data, iv, checksum)
        # Uses AES-256-GCM
        pass
    
    def decrypt_file_chunk(
        self, 
        encrypted_data: bytes, 
        chunk_key: bytes, 
        iv: bytes
    ) -> bytes:
        """Decrypt a file chunk"""
        # Returns: decrypted chunk data
        # Verifies checksum automatically (GCM)
        pass
    
    # Token Encryption (for OAuth tokens)
    def encrypt_token(
        self, 
        token: str, 
        key: bytes
    ) -> bytes:
        """Encrypt OAuth token"""
        # Uses AES-256-GCM
        # Returns: encrypted token bytes
        pass
    
    def decrypt_token(
        self, 
        encrypted_token: bytes, 
        key: bytes
    ) -> str:
        """Decrypt OAuth token"""
        # Returns: decrypted token string
        pass
```

---

## Chunking Strategy

### Chunk Size
- **Default:** 10MB (10 * 1024 * 1024 bytes)
- **Rationale:** Balance between API call overhead and memory usage
- **Configurable:** Can be adjusted per file type if needed

### Chunk Structure

Each chunk is stored with:
- **Chunk Index:** Sequential index (0, 1, 2, ...)
- **Chunk Size:** Original chunk size in bytes
- **Encrypted Size:** Size after encryption (slightly larger due to GCM tag)
- **IV (Initialization Vector):** Random IV for each chunk
- **Encryption Key:** Derived key for this chunk (encrypted)
- **Checksum:** GCM authentication tag (embedded in encrypted data)

### Chunk Storage

**Database Model:** `StorageChunk`
```python
{
    "id": UUID,
    "file_id": UUID (foreign key to File),
    "chunk_index": int,
    "chunk_size": int,
    "encrypted_size": int,
    "iv": bytes (base64 encoded),
    "encryption_key_encrypted": bytes (base64 encoded),
    "checksum": str (hex),
    "storage_path": str (path to encrypted chunk file),
    "created_at": datetime,
    "updated_at": datetime
}
```

---

## Key Storage

### User Encryption Keys

**Database Model:** `EncryptionKey`
```python
{
    "id": UUID,
    "user_id": UUID (foreign key to User, unique),
    "key_encrypted": bytes (base64 encoded),
    "salt": bytes (base64 encoded),
    "created_at": datetime,
    "updated_at": datetime
}
```

**Encryption Process:**
1. Generate random 256-bit user key
2. Generate random salt
3. Derive key encryption key using PBKDF2HMAC (application master key + salt)
4. Encrypt user key with derived key using AES-256-GCM
5. Store encrypted key and salt in database

**Decryption Process:**
1. Retrieve encrypted key and salt from database
2. Derive key encryption key using PBKDF2HMAC (application master key + salt)
3. Decrypt user key using derived key
4. Return decrypted user key

### Application Master Key

- **Source:** `ENCRYPTION_KEY` environment variable
- **Format:** 32-byte (256-bit) key
- **Usage:** Used to encrypt user keys (never used directly for file encryption)
- **Security:** Must be kept secret, rotated periodically

---

## Encryption Algorithms

### File/Chunk Encryption
- **Algorithm:** AES-256-GCM
- **Key Size:** 256 bits
- **IV Size:** 96 bits (12 bytes)
- **Authentication:** Built-in (GCM tag)

### Key Derivation
- **For User Keys:** PBKDF2HMAC
  - Iterations: 100,000
  - Hash: SHA-256
  - Salt: Random per user
  
- **For Chunk Keys:** HKDF
  - Hash: SHA-256
  - Info: `file_id + chunk_index`
  - Salt: User key

### Token Encryption
- **Algorithm:** AES-256-GCM
- **Key:** Application master key (or derived key)
- **Purpose:** Encrypt OAuth access/refresh tokens

---

## File Encryption Flow

### Upload Flow

1. **Receive file data**
2. **Get or create user encryption key**
   - Check database for existing key
   - If not exists, generate new key and store encrypted
3. **Chunk file**
   - Split into 10MB chunks
4. **For each chunk:**
   - Derive chunk key: `HKDF(user_key, file_id, chunk_index)`
   - Encrypt chunk: `AES-256-GCM(chunk_data, chunk_key)`
   - Store chunk metadata in database
   - Save encrypted chunk to storage
5. **Create file record**
   - Store file metadata (name, size, mime_type, etc.)
   - Link to storage chunks

### Download Flow

1. **Get file metadata**
2. **Get user encryption key**
   - Decrypt from database
3. **For each chunk (in order):**
   - Load chunk metadata from database
   - Derive chunk key: `HKDF(user_key, file_id, chunk_index)`
   - Load encrypted chunk from storage
   - Decrypt chunk: `AES-256-GCM(encrypted_data, chunk_key, iv)`
   - Verify checksum (automatic with GCM)
4. **Reassemble file**
   - Concatenate decrypted chunks in order
   - Return complete file data

---

## Integration Points

### With File Service
- File service calls encryption service for chunking
- File service calls encryption service for encryption/decryption
- File service manages chunk metadata storage

### With Cloud Upload Service
- Cloud upload service uses encrypted chunks
- Chunks are uploaded individually to cloud storage
- Chunk metadata stored in database

### With Cloud Download Service
- Cloud download service fetches encrypted chunks
- Chunks are decrypted and reassembled
- File returned to user

### With Cloud Connector Service
- Cloud connector service uses token encryption
- OAuth tokens encrypted before storage
- Tokens decrypted when needed for API calls

---

## Security Considerations

### Key Management
- User keys never stored in plaintext
- Application master key never stored in code
- Keys rotated periodically (future enhancement)

### Chunk Security
- Each chunk encrypted with unique key
- Unique IV per chunk
- Checksum verification on decryption

### Token Security
- OAuth tokens encrypted at rest
- Tokens decrypted only when needed
- Tokens refreshed before expiration

---

## Mock Implementation

**For Testing:**
```python
class MockEncryptionService:
    """Mock encryption service for testing"""
    
    def encrypt_file_chunk(self, chunk_data, chunk_key):
        # Return mock encrypted data
        return (b"mock_encrypted", b"mock_iv", b"mock_checksum")
    
    def decrypt_file_chunk(self, encrypted_data, chunk_key, iv):
        # Return original data (no actual encryption)
        return b"mock_decrypted_chunk"
```

---

## Change Log

### v1.0.0 (2026-01-20) - Initial Draft
- User key management defined
- Chunk key derivation specified
- File chunking strategy defined (10MB chunks)
- Chunk encryption/decryption methods defined
- Token encryption methods defined

---

## Implementation Tasks (from TASKS_PLANING.md)

### Day 1: Encryption Architecture Design
- [ ] Design chunking strategy (10MB chunks)
- [ ] Plan key storage in database (encrypted user keys)
- [ ] Review full version encryption service
- [ ] Create `encryption_key` model/schema
- [ ] Design chunk storage structure
- [ ] Update encryption service architecture

### Day 2: Enhanced Encryption Service
- [ ] Implement user key storage in database
- [ ] Update encryption service for chunking
- [ ] Implement chunk key derivation (HKDF)
- [ ] Create chunk encryption/decryption methods
- [ ] Update file service for chunking
- [ ] Test encryption with chunks

### Day 3: File Operations & Cloud Upload
- [ ] Create staging area structure
- [ ] Implement file upload pipeline
- [ ] Add file chunking logic
- [ ] Create chunk metadata storage
- [ ] Update file routes for chunked uploads
- [ ] Test large file uploads

---

**Contract Owner:** Bilal (Encryption & File Services)  
**Status:** Draft - Implementation in progress per TASKS_PLANING.md
