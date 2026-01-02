"""
Encrypted index for mapping file IDs to real names and structure.
"""

import json
import uuid
from dataclasses import dataclass, field
from typing import Literal, Dict, Optional
from pathlib import Path

from ..crypto import encrypt_data, decrypt_data
from ..io import atomic_write
from ..config import INDEX_FILENAME


@dataclass
class IndexNode:
    """Represents a file or folder in the vault index."""

    node_id: str  # Unique ID (used as encrypted filename)
    name: str  # Real name (encrypted in index.enc)
    parent_id: Optional[str]  # Parent folder ID (None for root)
    node_type: Literal["file", "folder"]
    metadata: Dict = field(default_factory=dict)  # Additional metadata

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "parent": self.parent_id,
            "type": self.node_type,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, node_id: str, data: dict) -> "IndexNode":
        """Create IndexNode from dictionary."""
        return cls(
            node_id=node_id,
            name=data["name"],
            parent_id=data.get("parent"),
            node_type=data["type"],
            metadata=data.get("metadata", {}),
        )


class VaultIndex:
    """Manages the encrypted index mapping file IDs to real names."""

    def __init__(self, vault_id: str):
        """
        Initialize a vault index.

        Args:
            vault_id: Unique identifier for the vault
        """
        self.vault_id = vault_id
        self.nodes: Dict[str, IndexNode] = {}

    def add_node(
        self,
        name: str,
        node_type: Literal["file", "folder"],
        parent_id: Optional[str] = None,
        node_id: Optional[str] = None,
    ) -> str:
        """
        Add a new node to the index.

        Args:
            name: Real name of the file/folder
            node_type: Type of node ("file" or "folder")
            parent_id: ID of parent folder (None for root)
            node_id: Optional specific ID (generates UUID if None)

        Returns:
            str: Node ID

        Raises:
            ValueError: If parent doesn't exist or is not a folder
        """
        if node_id is None:
            node_id = uuid.uuid4().hex[:8]  # Short ID for filenames

        # Validate parent exists and is a folder
        if parent_id is not None:
            if parent_id not in self.nodes:
                raise ValueError(f"Parent node {parent_id} does not exist")
            if self.nodes[parent_id].node_type != "folder":
                raise ValueError(f"Parent node {parent_id} is not a folder")

        # Check for duplicate ID
        if node_id in self.nodes:
            raise ValueError(f"Node ID {node_id} already exists")

        node = IndexNode(
            node_id=node_id,
            name=name,
            parent_id=parent_id,
            node_type=node_type,
        )

        self.nodes[node_id] = node
        return node_id

    def remove_node(self, node_id: str) -> None:
        """
        Remove a node from the index.

        Args:
            node_id: ID of node to remove

        Raises:
            ValueError: If node doesn't exist or has children
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")

        # Check for children
        children = self.get_children(node_id)
        if children:
            raise ValueError(f"Cannot remove node {node_id} with children")

        del self.nodes[node_id]

    def get_node(self, node_id: str) -> Optional[IndexNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_children(self, parent_id: str) -> list[IndexNode]:
        """Get all children of a parent node."""
        return [
            node for node in self.nodes.values()
            if node.parent_id == parent_id
        ]

    def get_path(self, node_id: str) -> str:
        """
        Get the full path of a node.

        Args:
            node_id: Node ID

        Returns:
            str: Full path (e.g., "Secrets/AWS Root.md")

        Raises:
            ValueError: If node doesn't exist
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")

        parts = []
        current_id = node_id

        while current_id is not None:
            node = self.nodes[current_id]
            # Only include nodes that have a parent (exclude root folder)
            if node.parent_id is not None:
                parts.insert(0, node.name)
            current_id = node.parent_id

        return "/".join(parts) if parts else ""

    def find_by_path(self, path: str) -> Optional[str]:
        """
        Find a node by its path.

        Args:
            path: Path to search for (e.g., "Secrets/AWS Root.md" or "file.md")
                 Note: Path should NOT include the root folder name

        Returns:
            Optional[str]: Node ID if found, None otherwise
        """
        if not path:
            # Empty path refers to root folder
            for node in self.nodes.values():
                if node.parent_id is None:
                    return node.node_id
            return None

        parts = path.split("/") if path else []

        # Find the root folder first
        root_id = None
        for node in self.nodes.values():
            if node.parent_id is None:
                root_id = node.node_id
                break

        if root_id is None:
            return None

        # Start searching from root folder's children
        current_id = root_id

        for part in parts:
            # Find child with matching name
            found = False
            for node in self.nodes.values():
                if node.parent_id == current_id and node.name == part:
                    current_id = node.node_id
                    found = True
                    break

            if not found:
                return None

        return current_id

    def to_dict(self) -> dict:
        """Serialize index to dictionary."""
        return {
            "vault_id": self.vault_id,
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in self.nodes.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VaultIndex":
        """Deserialize index from dictionary."""
        index = cls(vault_id=data["vault_id"])

        for node_id, node_data in data.get("nodes", {}).items():
            index.nodes[node_id] = IndexNode.from_dict(node_id, node_data)

        return index

    def encrypt(self, key: bytes, nonce: bytes) -> bytes:
        """
        Encrypt the index.

        Args:
            key: Encryption key
            nonce: Nonce for encryption

        Returns:
            bytes: Encrypted index data
        """
        plaintext = json.dumps(self.to_dict(), indent=2).encode('utf-8')
        ciphertext, _ = encrypt_data(plaintext, key, nonce)
        return ciphertext

    @classmethod
    def decrypt(cls, ciphertext: bytes, key: bytes, nonce: bytes) -> "VaultIndex":
        """
        Decrypt and deserialize an index.

        Args:
            ciphertext: Encrypted index data
            key: Decryption key
            nonce: Nonce used during encryption

        Returns:
            VaultIndex: Decrypted index

        Raises:
            ValueError: If decryption fails or data is invalid
        """
        plaintext = decrypt_data(ciphertext, key, nonce)
        data = json.loads(plaintext.decode('utf-8'))
        return cls.from_dict(data)

    def save(self, vault_path: Path, key: bytes, salt: bytes, nonce: bytes) -> None:
        """
        Save encrypted index to disk.

        Args:
            vault_path: Path to vault directory
            key: Encryption key
            salt: Salt used for key derivation
            nonce: Nonce for encryption
        """
        from ..crypto.formats import create_encrypted_file

        # Encrypt index
        plaintext = json.dumps(self.to_dict(), indent=2).encode('utf-8')
        ciphertext, actual_nonce = encrypt_data(plaintext, key, nonce)

        # Create encrypted file
        enc_file = create_encrypted_file(
            plaintext=plaintext,
            file_id=self.vault_id,
            file_type="index",
            ciphertext=ciphertext,
            salt=salt,
            nonce=actual_nonce,
        )

        # Save to disk
        index_path = vault_path / INDEX_FILENAME
        atomic_write(index_path, enc_file.to_bytes())

    @classmethod
    def load(cls, vault_path: Path, key: bytes) -> "VaultIndex":
        """
        Load and decrypt index from disk.

        Args:
            vault_path: Path to vault directory
            key: Decryption key

        Returns:
            VaultIndex: Loaded index

        Raises:
            FileNotFoundError: If index doesn't exist
            ValueError: If decryption fails
        """
        from ..crypto.formats import read_encrypted_file

        index_path = vault_path / INDEX_FILENAME

        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")

        # Read encrypted file
        enc_file = read_encrypted_file(str(index_path))

        # Decrypt
        return cls.decrypt(enc_file.ciphertext, key, enc_file.nonce)
