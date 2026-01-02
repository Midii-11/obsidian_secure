"""
Encrypted file format handling with JSON headers.
"""

import json
import base64
from dataclasses import dataclass
from typing import Literal
from ..config import (
    FILE_MAGIC,
    FORMAT_VERSION,
    KDF_ALGORITHM,
    CIPHER_ALGORITHM,
    ARGON2_MEMORY_COST,
    ARGON2_TIME_COST,
    ARGON2_PARALLELISM,
)


@dataclass
class EncryptedFile:
    """Represents an encrypted file with header and body."""

    # Header fields
    magic: str
    version: int
    kdf: str
    kdf_params: dict
    cipher: str
    salt: bytes
    nonce: bytes
    file_id: str
    file_type: Literal["file", "index"]

    # Body
    ciphertext: bytes

    def to_bytes(self) -> bytes:
        """
        Serialize the encrypted file to bytes.

        Returns:
            bytes: Complete encrypted file (header + body)
        """
        header = {
            "magic": self.magic,
            "version": self.version,
            "kdf": self.kdf,
            "kdf_params": self.kdf_params,
            "cipher": self.cipher,
            "salt": base64.b64encode(self.salt).decode('utf-8'),
            "nonce": base64.b64encode(self.nonce).decode('utf-8'),
            "file_id": self.file_id,
            "type": self.file_type,
        }

        header_json = json.dumps(header, indent=2)
        header_bytes = header_json.encode('utf-8')

        # Format: [4 bytes header length][header][body]
        header_length = len(header_bytes)
        length_prefix = header_length.to_bytes(4, byteorder='big')

        return length_prefix + header_bytes + self.ciphertext

    @classmethod
    def from_bytes(cls, data: bytes) -> "EncryptedFile":
        """
        Deserialize an encrypted file from bytes.

        Args:
            data: Complete encrypted file data

        Returns:
            EncryptedFile: Parsed encrypted file

        Raises:
            ValueError: If file format is invalid
        """
        if len(data) < 4:
            raise ValueError("File too short to contain header length")

        # Read header length
        header_length = int.from_bytes(data[0:4], byteorder='big')

        if len(data) < 4 + header_length:
            raise ValueError("File too short to contain header")

        # Parse header
        header_bytes = data[4:4 + header_length]
        try:
            header = json.loads(header_bytes.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Invalid header JSON: {e}")

        # Validate magic
        if header.get("magic") != FILE_MAGIC:
            raise ValueError(f"Invalid magic: expected {FILE_MAGIC}, got {header.get('magic')}")

        # Parse body
        ciphertext = data[4 + header_length:]

        return cls(
            magic=header["magic"],
            version=header["version"],
            kdf=header["kdf"],
            kdf_params=header["kdf_params"],
            cipher=header["cipher"],
            salt=base64.b64decode(header["salt"]),
            nonce=base64.b64decode(header["nonce"]),
            file_id=header["file_id"],
            file_type=header["type"],
            ciphertext=ciphertext,
        )


def create_encrypted_file(
    plaintext: bytes,
    file_id: str,
    file_type: Literal["file", "index"],
    ciphertext: bytes,
    salt: bytes,
    nonce: bytes,
) -> EncryptedFile:
    """
    Create an EncryptedFile object with standard parameters.

    Args:
        plaintext: Original plaintext (not stored, just for reference)
        file_id: Unique file identifier
        file_type: Type of file ("file" or "index")
        ciphertext: Encrypted data with authentication tag
        salt: Salt used for key derivation
        nonce: Nonce used for encryption

    Returns:
        EncryptedFile: Encrypted file object
    """
    kdf_params = {
        "memory_cost": ARGON2_MEMORY_COST,
        "time_cost": ARGON2_TIME_COST,
        "parallelism": ARGON2_PARALLELISM,
    }

    return EncryptedFile(
        magic=FILE_MAGIC,
        version=FORMAT_VERSION,
        kdf=KDF_ALGORITHM,
        kdf_params=kdf_params,
        cipher=CIPHER_ALGORITHM,
        salt=salt,
        nonce=nonce,
        file_id=file_id,
        file_type=file_type,
        ciphertext=ciphertext,
    )


def read_encrypted_file(file_path: str) -> EncryptedFile:
    """
    Read and parse an encrypted file from disk.

    Args:
        file_path: Path to encrypted file

    Returns:
        EncryptedFile: Parsed encrypted file

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    with open(file_path, 'rb') as f:
        data = f.read()

    return EncryptedFile.from_bytes(data)
