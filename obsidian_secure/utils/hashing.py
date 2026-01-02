"""
File hashing utilities for change detection.
"""

import hashlib
from pathlib import Path


def compute_file_hash(file_path: str | Path, algorithm: str = "sha256") -> str:
    """
    Compute cryptographic hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, sha512, etc.)

    Returns:
        str: Hexadecimal hash digest

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    hasher = hashlib.new(algorithm)

    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()
