"""
Temporary decrypted workspace management.
"""

import uuid
import shutil
from pathlib import Path
from typing import Dict

from ..config import WORKSPACE_BASE, WORKSPACE_PREFIX, MARKDOWN_EXT, OBSIDIAN_CONFIG_FOLDER
from ..io import secure_delete_directory
from ..vault import VaultIndex, IndexNode


class Workspace:
    """Manages a temporary decrypted workspace for Obsidian."""

    def __init__(self, workspace_id: str | None = None):
        """
        Initialize a workspace.

        Args:
            workspace_id: Optional workspace ID (generates random if None)
        """
        if workspace_id is None:
            workspace_id = uuid.uuid4().hex[:8]

        self.workspace_id = workspace_id
        self.workspace_path = WORKSPACE_BASE / f"{WORKSPACE_PREFIX}{workspace_id}"
        self.file_hashes: Dict[str, str] = {}  # Track file hashes for change detection

    def create(self) -> None:
        """
        Create the workspace directory.

        Raises:
            FileExistsError: If workspace already exists
        """
        if self.workspace_path.exists():
            raise FileExistsError(f"Workspace already exists: {self.workspace_path}")

        self.workspace_path.mkdir(parents=True, exist_ok=True)

        # Create basic Obsidian config
        self._create_obsidian_config()

    def destroy(self) -> None:
        """Securely delete the workspace."""
        if self.workspace_path.exists():
            secure_delete_directory(self.workspace_path)

    def exists(self) -> bool:
        """Check if workspace exists."""
        return self.workspace_path.exists()

    def _create_obsidian_config(self) -> None:
        """Create minimal Obsidian configuration."""
        config_dir = self.workspace_path / OBSIDIAN_CONFIG_FOLDER
        config_dir.mkdir(exist_ok=True)

        # Create app.json with basic settings
        app_config = {
            "vimMode": False,
            "showLineNumber": True,
        }

        import json
        app_json_path = config_dir / "app.json"
        app_json_path.write_text(json.dumps(app_config, indent=2), encoding='utf-8')

    def build_tree(self, index: VaultIndex) -> None:
        """
        Build the folder structure in the workspace from the index.

        Args:
            index: Vault index containing the tree structure
        """
        # Create all folders first
        for node in index.nodes.values():
            if node.node_type == "folder":
                folder_path = self._get_node_path(index, node.node_id)
                folder_path.mkdir(parents=True, exist_ok=True)

    def _get_node_path(self, index: VaultIndex, node_id: str) -> Path:
        """
        Get the workspace path for a node.

        Args:
            index: Vault index
            node_id: Node ID

        Returns:
            Path: Workspace path for the node
        """
        node = index.get_node(node_id)
        if node is None:
            raise ValueError(f"Node {node_id} not found in index")

        # Build path from root, excluding the root folder itself
        # The workspace directory represents the root folder, so we don't include it in the path
        parts = []
        current_id = node_id

        while current_id is not None:
            current_node = index.nodes[current_id]

            # Only add to path if this node has a parent (i.e., not the root folder)
            if current_node.parent_id is not None:
                parts.insert(0, current_node.name)

            current_id = current_node.parent_id

        if not parts:
            # This is the root node itself
            return self.workspace_path

        return self.workspace_path / Path(*parts)

    def write_file(self, index: VaultIndex, node_id: str, content: bytes) -> None:
        """
        Write a decrypted file to the workspace.

        Args:
            index: Vault index
            node_id: File node ID
            content: Decrypted file content
        """
        file_path = self._get_node_path(index, node_id)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content)

    def read_file(self, index: VaultIndex, node_id: str) -> bytes:
        """
        Read a file from the workspace.

        Args:
            index: Vault index
            node_id: File node ID

        Returns:
            bytes: File content
        """
        file_path = self._get_node_path(index, node_id)
        return file_path.read_bytes()

    def list_files(self) -> list[Path]:
        """
        List all markdown files in the workspace.

        Returns:
            list[Path]: List of file paths relative to workspace
        """
        if not self.workspace_path.exists():
            return []

        files = []
        for file_path in self.workspace_path.rglob(f"*{MARKDOWN_EXT}"):
            # Skip Obsidian config directory
            if OBSIDIAN_CONFIG_FOLDER in file_path.parts:
                continue
            files.append(file_path.relative_to(self.workspace_path))

        return files

    def compute_file_hash(self, file_path: Path) -> str:
        """
        Compute hash of a file in the workspace.

        Args:
            file_path: Path relative to workspace

        Returns:
            str: SHA-256 hash
        """
        from ..utils import compute_file_hash

        full_path = self.workspace_path / file_path
        return compute_file_hash(full_path)

    def track_file(self, file_path: Path) -> None:
        """
        Track a file for change detection.

        Args:
            file_path: Path relative to workspace
        """
        file_hash = self.compute_file_hash(file_path)
        self.file_hashes[str(file_path)] = file_hash

    def get_modified_files(self) -> list[Path]:
        """
        Get list of files that have been modified since tracking started.

        Returns:
            list[Path]: List of modified file paths
        """
        modified = []

        for file_path_str, original_hash in self.file_hashes.items():
            file_path = Path(file_path_str)
            full_path = self.workspace_path / file_path

            if not full_path.exists():
                # File was deleted
                modified.append(file_path)
                continue

            current_hash = self.compute_file_hash(file_path)
            if current_hash != original_hash:
                modified.append(file_path)

        return modified

    @staticmethod
    def find_existing_workspaces() -> list[Path]:
        """
        Find existing workspace directories (for crash recovery).

        Returns:
            list[Path]: List of workspace paths
        """
        if not WORKSPACE_BASE.exists():
            return []

        return list(WORKSPACE_BASE.glob(f"{WORKSPACE_PREFIX}*"))
