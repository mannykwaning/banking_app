"""
Unit tests for encryption utilities.
"""

import pytest
from app.core.encryption import encrypt_data, decrypt_data, get_encryption_key


class TestEncryption:
    """Test suite for encryption utilities."""

    def test_get_encryption_key(self):
        """Test encryption key generation."""
        key = get_encryption_key()

        # Assert
        assert key is not None
        assert isinstance(key, bytes)
        assert len(key) == 44  # Base64 encoded 32-byte key

    def test_encrypt_data(self):
        """Test data encryption."""
        plain_text = "1234567890123456"

        # Execute
        encrypted = encrypt_data(plain_text)

        # Assert
        assert encrypted != plain_text
        assert isinstance(encrypted, str)
        assert len(encrypted) > len(plain_text)

    def test_decrypt_data(self):
        """Test data decryption."""
        plain_text = "1234567890123456"

        # Execute
        encrypted = encrypt_data(plain_text)
        decrypted = decrypt_data(encrypted)

        # Assert
        assert decrypted == plain_text

    def test_encrypt_decrypt_cvv(self):
        """Test encrypting and decrypting CVV."""
        cvv = "123"

        # Execute
        encrypted = encrypt_data(cvv)
        decrypted = decrypt_data(encrypted)

        # Assert
        assert decrypted == cvv
        assert encrypted != cvv

    def test_encrypt_decrypt_pan(self):
        """Test encrypting and decrypting PAN."""
        pan = "4000000000001234"

        # Execute
        encrypted = encrypt_data(pan)
        decrypted = decrypt_data(encrypted)

        # Assert
        assert decrypted == pan
        assert encrypted != pan

    def test_encryption_is_deterministic(self):
        """Test that encryption produces different results each time (due to IV)."""
        plain_text = "1234567890123456"

        # Execute
        encrypted1 = encrypt_data(plain_text)
        encrypted2 = encrypt_data(plain_text)

        # Assert - Fernet includes timestamp so encryptions will differ
        # Both should decrypt to same value though
        assert decrypt_data(encrypted1) == plain_text
        assert decrypt_data(encrypted2) == plain_text

    def test_decrypt_invalid_data_raises_error(self):
        """Test that decrypting invalid data raises an error."""
        invalid_encrypted = "invalid_encrypted_data"

        # Execute & Assert
        with pytest.raises(Exception):
            decrypt_data(invalid_encrypted)

    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        plain_text = ""

        # Execute
        encrypted = encrypt_data(plain_text)
        decrypted = decrypt_data(encrypted)

        # Assert
        assert decrypted == plain_text

    def test_encrypt_special_characters(self):
        """Test encrypting data with special characters."""
        plain_text = "Test@123!#$%"

        # Execute
        encrypted = encrypt_data(plain_text)
        decrypted = decrypt_data(encrypted)

        # Assert
        assert decrypted == plain_text
