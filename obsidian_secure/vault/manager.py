"""
High-level vault management operations.
"""

import os
from pathlib import Path
from typing import Optional

from .layout import VaultLayout
from .index import VaultIndex
from ..crypto import derive_master_key, derive_vault_key


class VaultManager:
    """High-level vault management operations."""

    @staticmethod
    def create_vault(vault_path: str | Path, password: str, vault_name: str = "My Vault") -> str:
        """
        Create a new encrypted vault.

        Args:
            vault_path: Path where vault should be created
            password: Master password for the vault
            vault_name: Optional name for the vault

        Returns:
            str: Vault ID

        Raises:
            ValueError: If password is empty
            FileExistsError: If vault already exists
        """
        if not password:
            raise ValueError("Password cannot be empty")

        vault_path = Path(vault_path)

        # Initialize vault layout
        layout = VaultLayout(vault_path)
        vault_id = layout.initialize()

        # Derive encryption keys
        master_key, salt = derive_master_key(password)
        vault_key = derive_vault_key(master_key, vault_id)

        # Create empty index
        index = VaultIndex(vault_id)

        # Add root folder
        index.add_node(name=vault_name, node_type="folder", parent_id=None, node_id="root")

        # Save encrypted index
        nonce = os.urandom(12)

        # Create encrypted index file
        from ..crypto.formats import create_encrypted_file
        import json

        plaintext = json.dumps(index.to_dict(), indent=2).encode('utf-8')
        from ..crypto import encrypt_data
        ciphertext, actual_nonce = encrypt_data(plaintext, vault_key, nonce)

        enc_file = create_encrypted_file(
            plaintext=plaintext,
            file_id=vault_id,
            file_type="index",
            ciphertext=ciphertext,
            salt=salt,
            nonce=actual_nonce,
        )

        # Save to disk
        from ..io import atomic_write
        index_path = layout.get_index_path()
        atomic_write(index_path, enc_file.to_bytes())

        return vault_id

    @staticmethod
    def add_file_to_vault(
        vault_path: Path,
        vault_key: bytes,
        index: VaultIndex,
        file_path: Path,
        parent_id: str = "root",
        salt: bytes = b'',
    ) -> str:
        """
        Add a file to the vault.

        Args:
            vault_path: Path to vault
            vault_key: Vault encryption key
            index: Vault index
            file_path: Path to file to add
            parent_id: Parent folder node ID
            salt: Salt for encryption

        Returns:
            str: Node ID of added file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Add node to index
        node_id = index.add_node(
            name=file_path.name,
            node_type="file",
            parent_id=parent_id,
        )

        # Read and encrypt file
        plaintext = file_path.read_bytes()

        from ..crypto import encrypt_data, derive_file_key
        file_key = derive_file_key(vault_key, node_id)
        ciphertext, nonce = encrypt_data(plaintext, file_key)

        # Create encrypted file
        from ..crypto.formats import create_encrypted_file
        enc_file = create_encrypted_file(
            plaintext=plaintext,
            file_id=node_id,
            file_type="file",
            ciphertext=ciphertext,
            salt=salt,
            nonce=nonce,
        )

        # Save to vault
        layout = VaultLayout(vault_path)
        enc_file_path = layout.get_encrypted_file_path(node_id)

        from ..io import atomic_write
        atomic_write(enc_file_path, enc_file.to_bytes())

        return node_id

    @staticmethod
    def add_folder_to_vault(
        index: VaultIndex,
        folder_name: str,
        parent_id: str = "root",
    ) -> str:
        """
        Add a folder to the vault.

        Args:
            index: Vault index
            folder_name: Name of the folder
            parent_id: Parent folder node ID

        Returns:
            str: Node ID of added folder
        """
        return index.add_node(
            name=folder_name,
            node_type="folder",
            parent_id=parent_id,
        )
