"""
HKDF-based key hierarchy for deriving vault and file keys.
"""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from ..config import HKDF_INFO_VAULT, HKDF_INFO_FILE, AES_KEY_SIZE


def derive_vault_key(master_key: bytes, vault_id: str) -> bytes:
    """
    Derive a vault-specific key from the master key.

    Args:
        master_key: The master key derived from password
        vault_id: Unique identifier for the vault

    Returns:
        bytes: Vault-specific key
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=vault_id.encode('utf-8'),
        info=HKDF_INFO_VAULT,
    )
    return hkdf.derive(master_key)


def derive_file_key(vault_key: bytes, file_id: str) -> bytes:
    """
    Derive a file-specific key from the vault key.

    Args:
        vault_key: The vault-specific key
        file_id: Unique identifier for the file

    Returns:
        bytes: File-specific key
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=file_id.encode('utf-8'),
        info=HKDF_INFO_FILE,
    )
    return hkdf.derive(vault_key)
