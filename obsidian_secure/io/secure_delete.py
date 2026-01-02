"""
Secure file and directory deletion with overwriting.
"""

import os
import shutil
from pathlib import Path
from ..config import SECURE_DELETE_PASSES


def secure_delete_file(file_path: str | Path) -> None:
    """
    Securely delete a file by overwriting it before deletion.

    Args:
        file_path: Path to file to delete

    Note:
        On SSDs with wear leveling, this may not guarantee complete erasure,
        but it provides defense-in-depth against casual recovery attempts.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return

    if not file_path.is_file():
        raise ValueError(f"{file_path} is not a file")

    file_size = file_path.stat().st_size

    try:
        # Overwrite file multiple times
        with open(file_path, 'r+b') as f:
            for _ in range(SECURE_DELETE_PASSES):
                f.seek(0)
                # Write random data
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

            # Final pass with zeros
            f.seek(0)
            f.write(b'\x00' * file_size)
            f.flush()
            os.fsync(f.fileno())

    finally:
        # Delete the file
        file_path.unlink(missing_ok=True)


def secure_delete_directory(dir_path: str | Path) -> None:
    """
    Securely delete a directory and all its contents.

    Args:
        dir_path: Path to directory to delete

    Raises:
        OSError: If files cannot be deleted (e.g., locked by another process)
    """
    dir_path = Path(dir_path)

    if not dir_path.exists():
        return

    if not dir_path.is_dir():
        raise ValueError(f"{dir_path} is not a directory")

    failed_files = []

    # Recursively delete all files
    for root, dirs, files in os.walk(dir_path, topdown=False):
        root_path = Path(root)

        # Securely delete all files
        for name in files:
            file_path = root_path / name
            try:
                secure_delete_file(file_path)
            except Exception as e:
                # Track failed files
                failed_files.append((file_path, str(e)))
                print(f"Warning: Failed to securely delete {file_path}: {e}")

        # Remove empty directories
        for name in dirs:
            dir_to_remove = root_path / name
            try:
                dir_to_remove.rmdir()
            except OSError:
                pass

    # If some files failed, raise an error
    if failed_files:
        error_msg = f"Failed to delete {len(failed_files)} file(s). They may be locked by another process:\n"
        for file_path, error in failed_files[:5]:  # Show first 5
            error_msg += f"  - {file_path.name}: {error}\n"
        if len(failed_files) > 5:
            error_msg += f"  ... and {len(failed_files) - 5} more\n"
        error_msg += "\nPlease close Obsidian and any other programs that may have these files open, then try locking again."
        raise OSError(error_msg)

    # Remove the root directory
    try:
        dir_path.rmdir()
    except OSError as e:
        # If rmdir fails, try shutil.rmtree as fallback
        try:
            shutil.rmtree(dir_path, ignore_errors=False)
        except Exception as e2:
            raise OSError(
                f"Failed to delete workspace directory: {e}\n"
                f"Please close Obsidian and try again."
            ) from e2
