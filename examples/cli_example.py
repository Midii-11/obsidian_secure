"""
CLI Example - Using ObsidianSecure programmatically

This example shows how to use the ObsidianSecure library without the GUI.
"""

import sys
from pathlib import Path

# Add parent directory to path to import obsidian_secure
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_secure.vault import VaultManager
from obsidian_secure.session import SessionManager


def create_example_vault():
    """Create an example vault with some test files."""
    print("=== Creating Example Vault ===\n")

    vault_path = Path("example_vault")
    password = "example_password_123"

    # Create vault
    print(f"Creating vault at: {vault_path}")
    vault_id = VaultManager.create_vault(vault_path, password, "Example Vault")
    print(f"✓ Vault created with ID: {vault_id}\n")

    return vault_path, password


def unlock_and_add_note(vault_path: Path, password: str):
    """Unlock vault and add a sample note."""
    print("=== Unlocking Vault ===\n")

    # Create session manager
    session = SessionManager(vault_path)

    # Unlock vault
    print("Unlocking vault...")
    workspace = session.unlock(password)
    print(f"✓ Vault unlocked! Workspace: {workspace.workspace_path}\n")

    # Add a sample note
    print("=== Adding Sample Note ===\n")

    sample_note = """# Welcome to ObsidianSecure!

This is a test note created programmatically.

## Features

- Complete encryption
- Secure storage
- Easy to use

## Next Steps

1. Edit this note in Obsidian
2. Add your own notes
3. Lock the vault when done

---

*This note is encrypted when the vault is locked.*
"""

    # Write note to workspace
    note_path = workspace.workspace_path / "Welcome.md"
    note_path.write_text(sample_note, encoding='utf-8')
    print(f"✓ Created note: Welcome.md\n")

    # Track the file
    workspace.track_file(Path("Welcome.md"))

    print(f"Workspace location: {workspace.workspace_path}")
    print("You can now open this folder in Obsidian!\n")

    input("Press Enter when you're done editing notes...")

    # Lock vault
    print("\n=== Locking Vault ===\n")
    print("Re-encrypting modified files...")
    session.lock()
    print("✓ Vault locked and workspace deleted!\n")


def verify_encryption(vault_path: Path):
    """Verify that the vault is properly encrypted."""
    print("=== Verifying Encryption ===\n")

    # List encrypted files
    enc_files = list(vault_path.glob("*.enc"))
    print(f"Encrypted files in vault: {len(enc_files)}")

    for enc_file in enc_files:
        print(f"  - {enc_file.name}")

    print("\n✓ All files are encrypted on disk!")
    print(f"Vault location: {vault_path}")
    print("This folder is safe to backup or sync.\n")


def main():
    """Main example workflow."""
    print("\n" + "=" * 60)
    print("ObsidianSecure - CLI Example")
    print("=" * 60 + "\n")

    print("This example demonstrates:")
    print("1. Creating a new encrypted vault")
    print("2. Unlocking and adding notes")
    print("3. Locking and re-encrypting")
    print("4. Verifying encryption\n")

    input("Press Enter to continue...")
    print()

    # Create vault
    vault_path, password = create_example_vault()

    # Unlock and add content
    unlock_and_add_note(vault_path, password)

    # Verify
    verify_encryption(vault_path)

    print("=" * 60)
    print("Example complete!")
    print("=" * 60)
    print(f"\nYour encrypted vault is at: {vault_path.absolute()}")
    print(f"Password: {password}")
    print("\nYou can now use the GUI to interact with this vault:")
    print("  python main.py")
    print()


if __name__ == "__main__":
    main()
