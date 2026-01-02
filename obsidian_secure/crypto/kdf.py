"""
Key Derivation Functions using Argon2id.
"""

import os
from argon2 import PasswordHasher, low_level
from argon2.low_level import Type
from ..config import (
    ARGON2_MEMORY_COST,
    ARGON2_TIME_COST,
    ARGON2_PARALLELISM,
    SALT_SIZE,
    AES_KEY_SIZE,
)


def derive_master_key(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """
    Derive a master key from a password using Argon2id.

    Args:
        password: The master password
        salt: Optional salt (if None, generates new random salt)

    Returns:
        tuple: (master_key, salt)

    Raises:
        ValueError: If password is empty
    """
    if not password:
        raise ValueError("Password cannot be empty")

    if salt is None:
        salt = os.urandom(SALT_SIZE)

    if len(salt) != SALT_SIZE:
        raise ValueError(f"Salt must be {SALT_SIZE} bytes")

    # Derive key using Argon2id
    master_key = low_level.hash_secret_raw(
        secret=password.encode('utf-8'),
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=AES_KEY_SIZE,
        type=Type.ID  # Argon2id
    )

    return master_key, salt


def verify_password(password: str, salt: bytes, expected_key: bytes) -> bool:
    """
    Verify a password by re-deriving the key and comparing.

    Args:
        password: The password to verify
        salt: The salt used during key derivation
        expected_key: The expected master key

    Returns:
        bool: True if password is correct
    """
    try:
        derived_key, _ = derive_master_key(password, salt)
        # Constant-time comparison
        return low_level.verify_secret(expected_key, derived_key, Type.ID)
    except Exception:
        return False
