"""
Simplified Encryption Service for MVP - AES-256-GCM
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import hashlib
from typing import Tuple
from app.core.config import settings


class EncryptionService:
    """Simplified encryption service - per-user keys, file-level encryption"""

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

    def generate_user_key(self) -> bytes:
        """Generate a new user encryption key"""
        return os.urandom(32)  # 256-bit key

    def encrypt_user_key(self, user_key: bytes) -> str:
        """Encrypt a user's encryption key with master key"""
        nonce = os.urandom(12)
        ciphertext = self.master_aesgcm.encrypt(nonce, user_key, None)
        encrypted = nonce + ciphertext
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt_user_key(self, encrypted_user_key: str) -> bytes:
        """Decrypt a user's encryption key"""
        encrypted_bytes = base64.b64decode(encrypted_user_key.encode("utf-8"))
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        return self.master_aesgcm.decrypt(nonce, ciphertext, None)

    def encrypt_file(self, file_data: bytes, user_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypt file data with user's key

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
        """Decrypt file data"""
        aesgcm = AESGCM(user_key)
        return aesgcm.decrypt(nonce, encrypted_data, None)

    def calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data).hexdigest()


# Create singleton instance
encryption_service = EncryptionService()
