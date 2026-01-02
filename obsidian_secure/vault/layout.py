"""
Vault directory layout management.
"""

import uuid
from pathlib import Path
from ..config import ENCRYPTED_FILE_EXT, INDEX_FILENAME


class VaultLayout:
    """Manages the physical layout of an encrypted vault."""

    def __init__(self, vault_path: str | Path):
        """
        Initialize vault layout.

        Args:
            vault_path: Path to vault root directory
        """
        self.vault_path = Path(vault_path)

    def initialize(self) -> str:
        """
        Initialize a new vault directory structure.

        Returns:
            str: Vault ID

        Raises:
            FileExistsError: If vault already exists
        """
        if self.vault_path.exists() and any(self.vault_path.iterdir()):
            raise FileExistsError(f"Vault directory is not empty: {self.vault_path}")

        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Generate vault ID
        vault_id = uuid.uuid4().hex

        # Create vault metadata file
        metadata = {
            "vault_id": vault_id,
            "version": 1,
        }

        metadata_path = self.vault_path / ".vault_id"
        metadata_path.write_text(vault_id, encoding='utf-8')

        return vault_id

    def get_vault_id(self) -> str:
        """
        Get the vault ID from metadata.

        Returns:
            str: Vault ID

        Raises:
            FileNotFoundError: If vault metadata doesn't exist
        """
        metadata_path = self.vault_path / ".vault_id"

        if not metadata_path.exists():
            raise FileNotFoundError(f"Vault metadata not found: {metadata_path}")

        return metadata_path.read_text(encoding='utf-8').strip()

    def get_encrypted_file_path(self, file_id: str) -> Path:
        """
        Get the path to an encrypted file.

        Args:
            file_id: File node ID

        Returns:
            Path: Path to encrypted file
        """
        return self.vault_path / f"{file_id}{ENCRYPTED_FILE_EXT}"

    def get_index_path(self) -> Path:
        """Get the path to the encrypted index."""
        return self.vault_path / INDEX_FILENAME

    def list_encrypted_files(self) -> list[Path]:
        """
        List all encrypted files in the vault.

        Returns:
            list[Path]: List of encrypted file paths
        """
        if not self.vault_path.exists():
            return []

        return list(self.vault_path.glob(f"*{ENCRYPTED_FILE_EXT}"))

    def exists(self) -> bool:
        """Check if vault exists."""
        return self.vault_path.exists() and (self.vault_path / ".vault_id").exists()
