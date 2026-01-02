"""
Cryptographic primitives for ObsidianSecure.
"""

from .kdf import derive_master_key
from .cipher import encrypt_data, decrypt_data
from .hkdf import derive_vault_key, derive_file_key
from .formats import EncryptedFile, create_encrypted_file, read_encrypted_file

__all__ = [
    "derive_master_key",
    "encrypt_data",
    "decrypt_data",
    "derive_vault_key",
    "derive_file_key",
    "EncryptedFile",
    "create_encrypted_file",
    "read_encrypted_file",
]
