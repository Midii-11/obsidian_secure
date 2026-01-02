"""
Tests for vault management.
"""

import pytest
import tempfile
from pathlib import Path

from obsidian_secure.vault import VaultIndex, VaultLayout, VaultManager


class TestVaultIndex:
    """Tests for vault index."""

    def test_create_index(self):
        """Test creating a new index."""
        index = VaultIndex("test_vault")
        assert index.vault_id == "test_vault"
        assert len(index.nodes) == 0

    def test_add_folder(self):
        """Test adding a folder."""
        index = VaultIndex("test_vault")
        folder_id = index.add_node("Documents", "folder")

        assert folder_id in index.nodes
        assert index.nodes[folder_id].name == "Documents"
        assert index.nodes[folder_id].node_type == "folder"

    def test_add_file(self):
        """Test adding a file."""
        index = VaultIndex("test_vault")
        folder_id = index.add_node("Folder", "folder")
        file_id = index.add_node("notes.md", "file", parent_id=folder_id)

        assert file_id in index.nodes
        assert index.nodes[file_id].name == "notes.md"
        assert index.nodes[file_id].parent_id == folder_id

    def test_get_path(self):
        """Test getting full path of a node."""
        index = VaultIndex("test_vault")
        # Create root folder (excluded from paths)
        root_id = index.add_node("VaultRoot", "folder")
        # Create nested structure
        folder_id = index.add_node("Secrets", "folder", parent_id=root_id)
        file_id = index.add_node("password.md", "file", parent_id=folder_id)

        path = index.get_path(file_id)
        assert path == "Secrets/password.md"

    def test_find_by_path(self):
        """Test finding a node by path."""
        index = VaultIndex("test_vault")
        # Create root folder (excluded from paths)
        root_id = index.add_node("VaultRoot", "folder")
        # Create nested structure
        folder_id = index.add_node("Secrets", "folder", parent_id=root_id)
        file_id = index.add_node("password.md", "file", parent_id=folder_id)

        found_id = index.find_by_path("Secrets/password.md")
        assert found_id == file_id

    def test_remove_node(self):
        """Test removing a node."""
        index = VaultIndex("test_vault")
        folder_id = index.add_node("Folder", "folder")

        index.remove_node(folder_id)
        assert folder_id not in index.nodes

    def test_cannot_remove_node_with_children(self):
        """Test that removing a node with children fails."""
        index = VaultIndex("test_vault")
        folder_id = index.add_node("Folder", "folder")
        file_id = index.add_node("file.md", "file", parent_id=folder_id)

        with pytest.raises(ValueError):
            index.remove_node(folder_id)

    def test_serialization(self):
        """Test index serialization."""
        index = VaultIndex("test_vault")
        folder_id = index.add_node("Folder", "folder")
        file_id = index.add_node("file.md", "file", parent_id=folder_id)

        data = index.to_dict()

        assert data["vault_id"] == "test_vault"
        assert folder_id in data["nodes"]
        assert file_id in data["nodes"]

    def test_deserialization(self):
        """Test index deserialization."""
        index = VaultIndex("test_vault")
        # Create root folder (excluded from paths)
        root_id = index.add_node("VaultRoot", "folder")
        # Create nested structure
        folder_id = index.add_node("Folder", "folder", parent_id=root_id)
        file_id = index.add_node("file.md", "file", parent_id=folder_id)

        data = index.to_dict()
        loaded = VaultIndex.from_dict(data)

        assert loaded.vault_id == "test_vault"
        assert len(loaded.nodes) == 3  # root + folder + file
        assert loaded.get_path(file_id) == "Folder/file.md"


class TestVaultLayout:
    """Tests for vault layout."""

    def test_initialize_vault(self):
        """Test initializing a new vault."""
        with tempfile.TemporaryDirectory() as tmpdir:
            layout = VaultLayout(tmpdir)
            vault_id = layout.initialize()

            assert layout.exists()
            assert len(vault_id) > 0
            assert layout.get_vault_id() == vault_id

    def test_get_encrypted_file_path(self):
        """Test getting encrypted file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            layout = VaultLayout(tmpdir)
            layout.initialize()

            file_path = layout.get_encrypted_file_path("abc123")
            assert file_path.name == "abc123.enc"


class TestVaultManager:
    """Tests for vault manager."""

    def test_create_vault(self):
        """Test creating a new vault."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            password = "test_password_123"

            vault_id = VaultManager.create_vault(vault_path, password, "Test Vault")

            assert len(vault_id) > 0
            assert vault_path.exists()
            assert (vault_path / ".vault_id").exists()
            assert (vault_path / "index.enc").exists()

    def test_create_vault_empty_password_fails(self):
        """Test that empty password fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"

            with pytest.raises(ValueError):
                VaultManager.create_vault(vault_path, "", "Test Vault")
