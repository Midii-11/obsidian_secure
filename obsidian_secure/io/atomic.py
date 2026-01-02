"""
Atomic file write operations to prevent corruption.
"""

import os
import tempfile
from pathlib import Path


def atomic_write(file_path: str | Path, data: bytes) -> None:
    """
    Write data to a file atomically using write-then-rename.

    This ensures the file is never in a partially written state.

    Args:
        file_path: Target file path
        data: Data to write

    Raises:
        OSError: If write or rename fails
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary file in the same directory to ensure same filesystem
    fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=".tmp_",
        suffix=file_path.suffix
    )

    try:
        # Write data to temporary file
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk

        # Atomic rename (Windows: replace existing file)
        if os.name == 'nt':  # Windows
            # On Windows, we need to remove the target first if it exists
            if file_path.exists():
                os.replace(temp_path, file_path)
            else:
                os.rename(temp_path, file_path)
        else:  # Unix-like
            os.rename(temp_path, file_path)

    except Exception:
        # Clean up temporary file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise
