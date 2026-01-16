"""
Encryption utilities for sensitive card data.
Uses Fernet symmetric encryption for PAN and CVV data.
"""

from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """
    Derive a consistent encryption key from the application secret key.
    Uses SHA256 to create a properly formatted key for Fernet.
    """
    # Derive a 32-byte key from the secret key using SHA256
    key = hashlib.sha256(settings.secret_key.encode()).digest()
    # Fernet requires a base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key)


def get_cipher():
    """Get a Fernet cipher instance with the encryption key."""
    return Fernet(get_encryption_key())


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive string data.

    Args:
        data: Plain text data to encrypt

    Returns:
        Base64-encoded encrypted data as string
    """
    cipher = get_cipher()
    encrypted = cipher.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt encrypted string data.

    Args:
        encrypted_data: Base64-encoded encrypted data

    Returns:
        Decrypted plain text data
    """
    cipher = get_cipher()
    decrypted = cipher.decrypt(encrypted_data.encode())
    return decrypted.decode()
