"""
Tests for cryptographic primitives.
"""

import pytest
from obsidian_secure.crypto import (
    derive_master_key,
    encrypt_data,
    decrypt_data,
    derive_vault_key,
    derive_file_key,
    create_encrypted_file,
    EncryptedFile,
)


class TestKDF:
    """Tests for key derivation."""

    def test_derive_master_key(self):
        """Test master key derivation."""
        password = "test_password_123"
        master_key, salt = derive_master_key(password)

        assert len(master_key) == 32  # 256 bits
        assert len(salt) == 16  # 128 bits

    def test_derive_master_key_deterministic(self):
        """Test that same password + salt gives same key."""
        password = "test_password_123"
        master_key1, salt = derive_master_key(password)
        master_key2, _ = derive_master_key(password, salt)

        assert master_key1 == master_key2

    def test_derive_master_key_different_passwords(self):
        """Test that different passwords give different keys."""
        password1 = "password1"
        password2 = "password2"

        key1, salt = derive_master_key(password1)
        key2, _ = derive_master_key(password2, salt)

        assert key1 != key2

    def test_derive_master_key_empty_password(self):
        """Test that empty password raises error."""
        with pytest.raises(ValueError):
            derive_master_key("")


class TestEncryption:
    """Tests for encryption/decryption."""

    def test_encrypt_decrypt(self):
        """Test basic encryption and decryption."""
        plaintext = b"Hello, World! This is a test message."
        key = b"x" * 32  # 256-bit key

        ciphertext, nonce = encrypt_data(plaintext, key)
        decrypted = decrypt_data(ciphertext, key, nonce)

        assert decrypted == plaintext

    def test_different_plaintexts_different_ciphertexts(self):
        """Test that different plaintexts produce different ciphertexts."""
        key = b"x" * 32

        plaintext1 = b"message1"
        plaintext2 = b"message2"

        ciphertext1, nonce1 = encrypt_data(plaintext1, key)
        ciphertext2, nonce2 = encrypt_data(plaintext2, key)

        assert ciphertext1 != ciphertext2

    def test_wrong_key_fails(self):
        """Test that wrong key fails decryption."""
        plaintext = b"secret message"
        key1 = b"a" * 32
        key2 = b"b" * 32

        ciphertext, nonce = encrypt_data(plaintext, key1)

        with pytest.raises(Exception):  # InvalidTag
            decrypt_data(ciphertext, key2, nonce)

    def test_tampered_ciphertext_fails(self):
        """Test that tampered ciphertext fails authentication."""
        plaintext = b"secret message"
        key = b"x" * 32

        ciphertext, nonce = encrypt_data(plaintext, key)

        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0xFF
        tampered = bytes(tampered)

        with pytest.raises(Exception):  # InvalidTag
            decrypt_data(tampered, key, nonce)


class TestHKDF:
    """Tests for HKDF key derivation."""

    def test_derive_vault_key(self):
        """Test vault key derivation."""
        master_key = b"x" * 32
        vault_id = "test_vault_123"

        vault_key = derive_vault_key(master_key, vault_id)

        assert len(vault_key) == 32

    def test_derive_file_key(self):
        """Test file key derivation."""
        vault_key = b"y" * 32
        file_id = "file_abc"

        file_key = derive_file_key(vault_key, file_id)

        assert len(file_key) == 32

    def test_different_vault_ids_different_keys(self):
        """Test that different vault IDs produce different keys."""
        master_key = b"x" * 32

        key1 = derive_vault_key(master_key, "vault1")
        key2 = derive_vault_key(master_key, "vault2")

        assert key1 != key2


class TestEncryptedFileFormat:
    """Tests for encrypted file format."""

    def test_encrypted_file_serialization(self):
        """Test encrypting and serializing a file."""
        plaintext = b"Test file content"
        key = b"x" * 32
        file_id = "test_file"

        # Encrypt
        ciphertext, nonce = encrypt_data(plaintext, key)

        # Create encrypted file
        enc_file = create_encrypted_file(
            plaintext=plaintext,
            file_id=file_id,
            file_type="file",
            ciphertext=ciphertext,
            salt=b"0" * 16,
            nonce=nonce,
        )

        # Serialize
        data = enc_file.to_bytes()

        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_encrypted_file_deserialization(self):
        """Test deserializing an encrypted file."""
        plaintext = b"Test file content"
        key = b"x" * 32
        file_id = "test_file"

        # Encrypt
        ciphertext, nonce = encrypt_data(plaintext, key)

        # Create encrypted file
        enc_file = create_encrypted_file(
            plaintext=plaintext,
            file_id=file_id,
            file_type="file",
            ciphertext=ciphertext,
            salt=b"0" * 16,
            nonce=nonce,
        )

        # Serialize and deserialize
        data = enc_file.to_bytes()
        loaded = EncryptedFile.from_bytes(data)

        assert loaded.file_id == file_id
        assert loaded.file_type == "file"
        assert loaded.ciphertext == ciphertext
        assert loaded.nonce == nonce

    def test_encrypted_file_round_trip(self):
        """Test full encryption round trip."""
        plaintext = b"Secret data that needs encryption"
        key = b"x" * 32
        file_id = "test_123"

        # Encrypt
        ciphertext, nonce = encrypt_data(plaintext, key)

        # Create encrypted file
        enc_file = create_encrypted_file(
            plaintext=plaintext,
            file_id=file_id,
            file_type="file",
            ciphertext=ciphertext,
            salt=b"s" * 16,
            nonce=nonce,
        )

        # Serialize
        data = enc_file.to_bytes()

        # Deserialize
        loaded = EncryptedFile.from_bytes(data)

        # Decrypt
        decrypted = decrypt_data(loaded.ciphertext, key, loaded.nonce)

        assert decrypted == plaintext
