"""
AES-256-GCM encryption and decryption.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from ..config import NONCE_SIZE, AES_KEY_SIZE


def encrypt_data(plaintext: bytes, key: bytes, nonce: bytes | None = None) -> tuple[bytes, bytes]:
    """
    Encrypt data using AES-256-GCM.

    Args:
        plaintext: Data to encrypt
        key: 256-bit encryption key
        nonce: Optional 12-byte nonce (generated if None)

    Returns:
        tuple: (ciphertext_with_tag, nonce)

    Raises:
        ValueError: If key is not 32 bytes
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"Key must be {AES_KEY_SIZE} bytes")

    if nonce is None:
        nonce = os.urandom(NONCE_SIZE)

    if len(nonce) != NONCE_SIZE:
        raise ValueError(f"Nonce must be {NONCE_SIZE} bytes")

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    return ciphertext, nonce


def decrypt_data(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    """
    Decrypt data using AES-256-GCM.

    Args:
        ciphertext: Encrypted data with authentication tag
        key: 256-bit encryption key
        nonce: 12-byte nonce used during encryption

    Returns:
        bytes: Decrypted plaintext

    Raises:
        ValueError: If key or nonce size is incorrect
        cryptography.exceptions.InvalidTag: If authentication fails
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"Key must be {AES_KEY_SIZE} bytes")

    if len(nonce) != NONCE_SIZE:
        raise ValueError(f"Nonce must be {NONCE_SIZE} bytes")

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    return plaintext
