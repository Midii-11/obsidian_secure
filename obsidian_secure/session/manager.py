"""
Session manager for coordinating vault unlock/lock operations.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from ..crypto import (
    derive_master_key,
    derive_vault_key,
    derive_file_key,
    encrypt_data,
    decrypt_data,
    read_encrypted_file,
    create_encrypted_file,
)
from ..vault import VaultIndex, VaultLayout
from ..io import atomic_write
from ..config import OBSIDIAN_EXECUTABLE
from .workspace import Workspace
from .watcher import FileWatcher


class SessionManager:
    """Manages unlock/lock sessions for encrypted vaults."""

    def __init__(self, vault_path: str | Path):
        """
        Initialize session manager.

        Args:
            vault_path: Path to encrypted vault
        """
        self.vault_path = Path(vault_path)
        self.layout = VaultLayout(vault_path)
        self.workspace: Optional[Workspace] = None
        self.index: Optional[VaultIndex] = None
        self.vault_key: Optional[bytes] = None
        self.master_key: Optional[bytes] = None
        self.salt: Optional[bytes] = None
        self.watcher: Optional[FileWatcher] = None
        self.vault_id: Optional[str] = None

    def unlock(self, password: str) -> Workspace:
        """
        Unlock the vault and create a workspace.

        Args:
            password: Master password

        Returns:
            Workspace: Created workspace

        Raises:
            ValueError: If password is incorrect or vault is invalid
            FileNotFoundError: If vault doesn't exist
        """
        if not self.layout.exists():
            raise FileNotFoundError(f"Vault not found: {self.vault_path}")

        # Get vault ID
        self.vault_id = self.layout.get_vault_id()

        # Load and decrypt index to verify password
        index_path = self.layout.get_index_path()
        enc_index = read_encrypted_file(str(index_path))

        # Derive master key from password
        self.master_key, self.salt = derive_master_key(password, enc_index.salt)

        # Derive vault key
        self.vault_key = derive_vault_key(self.master_key, self.vault_id)

        # Decrypt index
        try:
            self.index = VaultIndex.decrypt(
                enc_index.ciphertext,
                self.vault_key,
                enc_index.nonce
            )
        except Exception as e:
            raise ValueError(f"Failed to decrypt vault (incorrect password?): {e}")

        # Create workspace
        self.workspace = Workspace()
        self.workspace.create()

        # Build folder structure
        self.workspace.build_tree(self.index)

        # Decrypt all files
        for node in self.index.nodes.values():
            if node.node_type == "file":
                self._decrypt_file_to_workspace(node.node_id)

        # Track initial file hashes
        for file_path in self.workspace.list_files():
            self.workspace.track_file(file_path)

        # Start file watcher
        self.watcher = FileWatcher(self.workspace.workspace_path)
        self.watcher.start()

        return self.workspace

    def lock(self) -> None:
        """
        Lock the vault and destroy the workspace.

        This encrypts any modified files and securely deletes the workspace.
        """
        if self.workspace is None:
            return

        # Stop file watcher
        if self.watcher:
            self.watcher.stop()

        # Get ALL files currently in workspace
        all_files = self.workspace.list_files()

        # Process all files (new, modified, or unchanged)
        for file_path in all_files:
            # Convert to path string with forward slashes
            full_path = str(file_path).replace(os.sep, "/")

            # Check if file exists in index
            node_id = self.index.find_by_path(full_path)

            if node_id:
                # Existing file - check if modified
                tracked_hash = self.workspace.file_hashes.get(str(file_path))
                if tracked_hash:
                    current_hash = self.workspace.compute_file_hash(file_path)
                    if current_hash != tracked_hash:
                        # File was modified - re-encrypt it
                        self._encrypt_file_from_workspace(node_id)
                else:
                    # File wasn't tracked (shouldn't happen, but re-encrypt to be safe)
                    self._encrypt_file_from_workspace(node_id)
            else:
                # NEW file - add to index and encrypt
                self._add_new_file_to_vault(file_path)

        # Handle deleted files (in index but not in workspace)
        workspace_file_paths = set(str(f).replace(os.sep, "/") for f in all_files)

        for node_id, node in list(self.index.nodes.items()):
            if node.node_type == "file":
                node_path = self.index.get_path(node_id)

                if node_path not in workspace_file_paths:
                    # File was deleted - remove from index and vault
                    enc_file_path = self.layout.get_encrypted_file_path(node_id)
                    if enc_file_path.exists():
                        enc_file_path.unlink()
                    self.index.remove_node(node_id)

        # Save updated index
        if self.index and self.vault_key and self.salt:
            nonce = os.urandom(12)
            self.index.save(self.vault_path, self.vault_key, self.salt, nonce)

        # Securely delete workspace
        self.workspace.destroy()

        # Clear sensitive data
        self._clear_sensitive_data()

    def _decrypt_file_to_workspace(self, node_id: str) -> None:
        """
        Decrypt a file and write it to the workspace.

        Args:
            node_id: File node ID
        """
        if self.vault_key is None or self.workspace is None or self.index is None:
            raise RuntimeError("Session not initialized")

        # Read encrypted file
        enc_file_path = self.layout.get_encrypted_file_path(node_id)

        if not enc_file_path.exists():
            # File doesn't exist yet (new file in index)
            return

        enc_file = read_encrypted_file(str(enc_file_path))

        # Derive file key
        file_key = derive_file_key(self.vault_key, node_id)

        # Decrypt
        plaintext = decrypt_data(enc_file.ciphertext, file_key, enc_file.nonce)

        # Write to workspace
        self.workspace.write_file(self.index, node_id, plaintext)

    def _encrypt_file_from_workspace(self, node_id: str) -> None:
        """
        Encrypt a file from the workspace and save to vault.

        Args:
            node_id: File node ID
        """
        if self.vault_key is None or self.workspace is None or self.index is None:
            raise RuntimeError("Session not initialized")

        # Read from workspace
        plaintext = self.workspace.read_file(self.index, node_id)

        # Derive file key
        file_key = derive_file_key(self.vault_key, node_id)

        # Encrypt
        ciphertext, nonce = encrypt_data(plaintext, file_key)

        # Create encrypted file
        enc_file = create_encrypted_file(
            plaintext=plaintext,
            file_id=node_id,
            file_type="file",
            ciphertext=ciphertext,
            salt=self.salt,
            nonce=nonce,
        )

        # Save to vault
        enc_file_path = self.layout.get_encrypted_file_path(node_id)
        atomic_write(enc_file_path, enc_file.to_bytes())

    def _add_new_file_to_vault(self, file_path: Path) -> None:
        """
        Add a new file to the vault (created during session).

        Args:
            file_path: Relative path to the new file in workspace
        """
        if self.vault_key is None or self.workspace is None or self.index is None:
            raise RuntimeError("Session not initialized")

        # Convert path to string with forward slashes
        path_str = str(file_path).replace(os.sep, "/")

        # Parse path to find parent folder
        parts = path_str.split("/")
        filename = parts[-1]

        # Find or create parent folder in index
        parent_id = "root"  # Default to root
        if len(parts) > 1:
            # Navigate through folder structure
            current_id = None
            for folder_name in parts[:-1]:
                # Try to find existing folder
                found_id = None
                for node in self.index.nodes.values():
                    if (node.parent_id == current_id and
                        node.name == folder_name and
                        node.node_type == "folder"):
                        found_id = node.node_id
                        break

                if found_id:
                    current_id = found_id
                else:
                    # Create new folder
                    current_id = self.index.add_node(
                        name=folder_name,
                        node_type="folder",
                        parent_id=current_id
                    )

            parent_id = current_id if current_id else "root"

        # Add file to index
        node_id = self.index.add_node(
            name=filename,
            node_type="file",
            parent_id=parent_id
        )

        # Encrypt and save the file
        self._encrypt_file_from_workspace(node_id)

    def _clear_sensitive_data(self) -> None:
        """Clear sensitive data from memory (best-effort)."""
        if self.master_key:
            # Overwrite with zeros
            for i in range(len(self.master_key)):
                self.master_key = None

        if self.vault_key:
            self.vault_key = None

        self.workspace = None
        self.index = None
        self.salt = None

    def launch_obsidian(self, obsidian_path: str | None = None) -> subprocess.Popen:
        """
        Launch Obsidian with the workspace.

        Args:
            obsidian_path: Optional path to Obsidian executable

        Returns:
            subprocess.Popen: Obsidian process

        Raises:
            RuntimeError: If workspace is not unlocked
        """
        if self.workspace is None:
            raise RuntimeError("Workspace is not unlocked")

        if obsidian_path is None:
            # Default Obsidian path from config
            obsidian_path = OBSIDIAN_EXECUTABLE

        if not os.path.exists(obsidian_path):
            raise FileNotFoundError(f"Obsidian not found at: {obsidian_path}")

        # Launch Obsidian
        process = subprocess.Popen(
            [obsidian_path, str(self.workspace.workspace_path)],
            shell=False
        )

        return process
