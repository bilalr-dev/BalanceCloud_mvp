"""
Encryption Service - Aligned with Encryption Service Contract v1.0.0
AES-256-GCM encryption with chunking support
"""

import base64
import hashlib
import os
from typing import Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.encryption_key import EncryptionKey


class EncryptionService:
    """Encryption service aligned with Encryption Service Contract v1.0.0"""

    def __init__(self):
        # Master key for encrypting user keys (derived from ENCRYPTION_KEY)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"balancecloud_mvp_salt",
            iterations=100000,
            backend=default_backend(),
        )
        encryption_key = settings.ENCRYPTION_KEY.encode()
        self.master_key = kdf.derive(encryption_key)
        self.master_aesgcm = AESGCM(self.master_key)

    # User Key Management - Aligned with Contract

    async def generate_user_encryption_key(self) -> bytes:
        """Generate a new user encryption key (256 bits)"""
        return os.urandom(32)  # 256-bit key

    async def encrypt_user_key(self, user_key: bytes) -> tuple[bytes, bytes]:
        """
        Encrypt user key with application master key
        
        Returns:
            (encrypted_key, salt) tuple
        """
        # Generate random salt
        salt = os.urandom(16)
        
        # Derive key encryption key using PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        kek = kdf.derive(self.master_key)
        
        # Encrypt user key with derived key using AES-256-GCM
        nonce = os.urandom(12)
        aesgcm = AESGCM(kek)
        ciphertext = aesgcm.encrypt(nonce, user_key, None)
        encrypted_key = nonce + ciphertext
        
        return (encrypted_key, salt)

    async def decrypt_user_key(self, encrypted_key: bytes, salt: bytes) -> bytes:
        """
        Decrypt user key using application master key
        
        Args:
            encrypted_key: Encrypted user key bytes
            salt: Salt bytes used for key derivation
            
        Returns:
            Decrypted user key bytes
        """
        # Derive key encryption key using PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        kek = kdf.derive(self.master_key)
        
        # Decrypt user key
        nonce = encrypted_key[:12]
        ciphertext = encrypted_key[12:]
        aesgcm = AESGCM(kek)
        decrypted_key = aesgcm.decrypt(nonce, ciphertext, None)
        
        return decrypted_key

    async def get_or_create_user_encryption_key(
        self, db: AsyncSession, user_id: str
    ) -> bytes:
        """
        Get existing user key or create new one
        
        Returns:
            Decrypted user encryption key (bytes)
        """
        # Check if key exists in database
        from sqlalchemy import select
        
        result = await db.execute(
            select(EncryptionKey).where(EncryptionKey.user_id == user_id)
        )
        encryption_key_record = result.scalar_one_or_none()
        
        if encryption_key_record:
            # Decrypt and return existing key
            encrypted_key_bytes = base64.b64decode(encryption_key_record.key_encrypted)
            salt_bytes = base64.b64decode(encryption_key_record.salt)
            return await self.decrypt_user_key(encrypted_key_bytes, salt_bytes)
        else:
            # Generate new key
            user_key = await self.generate_user_encryption_key()
            
            # Encrypt key for storage
            encrypted_key, salt = await self.encrypt_user_key(user_key)
            
            # Store in database
            encryption_key_record = EncryptionKey(
                user_id=user_id,
                key_encrypted=base64.b64encode(encrypted_key).decode("utf-8"),
                salt=base64.b64encode(salt).decode("utf-8"),
            )
            db.add(encryption_key_record)
            await db.commit()
            await db.refresh(encryption_key_record)
            
            return user_key

    # Chunk Key Derivation - Aligned with Contract

    def derive_chunk_key(
        self, user_key: bytes, file_id: str, chunk_index: int
    ) -> bytes:
        """
        Derive encryption key for a specific chunk using HKDF
        
        Args:
            user_key: User's encryption key
            file_id: File ID (UUID string)
            chunk_index: Chunk index (0, 1, 2, ...)
            
        Returns:
            256-bit chunk key
        """
        # Create info string for HKDF
        info = f"{file_id}:{chunk_index}".encode("utf-8")
        
        # Derive chunk key using HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=user_key[:16],  # Use first 16 bytes of user key as salt
            info=info,
            backend=default_backend(),
        )
        chunk_key = hkdf.derive(user_key)
        
        return chunk_key

    # File Chunking - Aligned with Contract

    def chunk_file(
        self, file_data: bytes, chunk_size: int = 10 * 1024 * 1024
    ) -> list[bytes]:
        """
        Split file into chunks
        
        Args:
            file_data: File data to chunk
            chunk_size: Size of each chunk in bytes (default: 10MB)
            
        Returns:
            List of chunk bytes
        """
        chunks = []
        for i in range(0, len(file_data), chunk_size):
            chunks.append(file_data[i : i + chunk_size])
        return chunks

    # Chunk Encryption/Decryption - Aligned with Contract

    def encrypt_file_chunk(
        self, chunk_data: bytes, chunk_key: bytes
    ) -> tuple[bytes, bytes, bytes]:
        """
        Encrypt a file chunk using AES-256-GCM
        
        Args:
            chunk_data: Chunk data to encrypt
            chunk_key: Encryption key for this chunk
            
        Returns:
            (encrypted_data, iv, checksum) tuple
            - encrypted_data: Ciphertext with GCM tag appended (last 16 bytes)
            - iv: Initialization vector (12 bytes)
            - checksum: GCM authentication tag (16 bytes, same as last 16 bytes of encrypted_data)
        """
        # Generate IV (96 bits for GCM)
        iv = os.urandom(12)
        
        # Encrypt chunk (GCM automatically appends tag)
        aesgcm = AESGCM(chunk_key)
        ciphertext = aesgcm.encrypt(iv, chunk_data, None)
        
        # GCM tag is automatically appended to ciphertext (last 16 bytes)
        # Extract tag for checksum
        encrypted_data = ciphertext  # Full ciphertext with tag
        checksum = ciphertext[-16:]  # GCM tag (last 16 bytes)
        
        return (encrypted_data, iv, checksum)

    def decrypt_file_chunk(
        self, encrypted_data: bytes, chunk_key: bytes, iv: bytes
    ) -> bytes:
        """
        Decrypt a file chunk using AES-256-GCM
        
        Args:
            encrypted_data: Encrypted chunk data (ciphertext + GCM tag)
            chunk_key: Decryption key for this chunk
            iv: Initialization vector
            
        Returns:
            Decrypted chunk data
            
        Note: 
            - GCM tag (checksum) is embedded at the end of encrypted_data
            - Checksum verification is automatic with GCM (raises exception if invalid)
        """
        aesgcm = AESGCM(chunk_key)
        # GCM decrypt automatically verifies the tag (checksum)
        # Tag is the last 16 bytes of encrypted_data
        decrypted_data = aesgcm.decrypt(iv, encrypted_data, None)
        return decrypted_data

    # Token Encryption (for OAuth tokens) - Aligned with Contract

    def encrypt_token(self, token: str, key: bytes) -> bytes:
        """
        Encrypt OAuth token using AES-256-GCM
        
        Args:
            token: Token string to encrypt
            key: Encryption key
            
        Returns:
            Encrypted token bytes
        """
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        token_bytes = token.encode("utf-8")
        ciphertext = aesgcm.encrypt(nonce, token_bytes, None)
        return nonce + ciphertext

    def decrypt_token(self, encrypted_token: bytes, key: bytes) -> str:
        """
        Decrypt OAuth token using AES-256-GCM
        
        Args:
            encrypted_token: Encrypted token bytes
            key: Decryption key
            
        Returns:
            Decrypted token string
        """
        nonce = encrypted_token[:12]
        ciphertext = encrypted_token[12:]
        aesgcm = AESGCM(key)
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_bytes.decode("utf-8")

    # Legacy methods for backward compatibility (will be removed)

    def generate_user_key(self) -> bytes:
        """Legacy method - use generate_user_encryption_key() instead"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.generate_user_encryption_key())
        except RuntimeError:
            # Create new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.generate_user_encryption_key())
            loop.close()
            return result

    def encrypt_file(self, file_data: bytes, user_key: bytes) -> Tuple[bytes, bytes]:
        """
        Legacy method for file encryption (non-chunked)
        For chunked encryption, use chunk_file() + encrypt_file_chunk()

        Returns:
            (encrypted_data, nonce)
        """
        nonce = os.urandom(12)
        aesgcm = AESGCM(user_key)
        ciphertext = aesgcm.encrypt(nonce, file_data, None)
        return ciphertext, nonce

    def decrypt_file(
        self, encrypted_data: bytes, nonce: bytes, user_key: bytes
    ) -> bytes:
        """Legacy method for file decryption (non-chunked)"""
        aesgcm = AESGCM(user_key)
        return aesgcm.decrypt(nonce, encrypted_data, None)

    def calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data).hexdigest()


# Create singleton instance
encryption_service = EncryptionService()
