"""
Vault discovery and validation.
"""

from pathlib import Path
from .layout import VaultLayout
from ..config import INDEX_FILENAME


def is_valid_vault(vault_path: str | Path) -> bool:
    """
    Check if a directory is a valid ObsidianSecure vault.

    Args:
        vault_path: Path to potential vault

    Returns:
        bool: True if valid vault
    """
    vault_path = Path(vault_path)

    if not vault_path.exists() or not vault_path.is_dir():
        return False

    # Check for vault metadata
    if not (vault_path / ".vault_id").exists():
        return False

    # Check for encrypted index
    if not (vault_path / INDEX_FILENAME).exists():
        return False

    return True


def discover_vaults(search_path: str | Path) -> list[Path]:
    """
    Discover all valid vaults in a directory tree.

    Args:
        search_path: Root path to search

    Returns:
        list[Path]: List of vault paths
    """
    search_path = Path(search_path)
    vaults = []

    if not search_path.exists():
        return vaults

    # Search recursively
    for path in search_path.rglob(".vault_id"):
        vault_path = path.parent
        if is_valid_vault(vault_path):
            vaults.append(vault_path)

    return vaults
