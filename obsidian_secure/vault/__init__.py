"""
Vault management for encrypted Obsidian vaults.
"""

from .index import VaultIndex, IndexNode
from .layout import VaultLayout
from .discovery import discover_vaults, is_valid_vault
from .manager import VaultManager

__all__ = [
    "VaultIndex",
    "IndexNode",
    "VaultLayout",
    "VaultManager",
    "discover_vaults",
    "is_valid_vault",
]
