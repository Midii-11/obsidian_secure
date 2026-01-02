# Quick Start Guide

## Installation

1. **Install Python 3.13.5 or later**
   - Download from [python.org](https://www.python.org/downloads/)

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## First Time Setup

1. **Run the application**
   ```bash
   python main.py
   ```

2. **Create your first vault**
   - Click "Create New Vault"
   - Choose a directory (e.g., `C:\MySecrets\vault`)
   - Enter a vault name (e.g., "My Secure Notes")
   - Set a strong password (at least 12 characters recommended)
   - Click "Create"

3. **Unlock your vault**
   - Click "Unlock"
   - Enter your password
   - Your vault is now decrypted to a temporary workspace

4. **Launch Obsidian**
   - Click "Launch Obsidian"
   - Obsidian will open with your decrypted notes
   - Create and edit notes as usual

5. **Lock when done**
   - Click "Lock" in ObsidianSecure
   - Your notes are re-encrypted and the workspace is securely deleted
   - (Recommended: Close Obsidian first for clean shutdown)

## Daily Workflow

1. Start ObsidianSecure: `python main.py`
2. Select your vault
3. Unlock with password
4. Launch Obsidian
5. Work on your notes (create, edit, delete files and folders)
6. Lock the vault in ObsidianSecure

## Important Notes

- **NEVER forget your password** - there's no recovery method!
- **Close Obsidian before locking** (recommended) - prevents file locking errors
- **Always lock** before shutting down
- **Keep backups** of your encrypted vault folder
- The encrypted vault folder (e.g., `C:\MySecrets\vault`) is safe to backup/sync
- The temporary workspace is automatically deleted on lock
- You can create/edit/delete files and folders - all changes are saved when you lock
- If locking fails with an error, close Obsidian and try again

## Troubleshooting

### "Obsidian not found"
- Install Obsidian from [obsidian.md](https://obsidian.md/)
- Default location: `%LOCALAPPDATA%\Programs\Obsidian\Obsidian.exe`
- If installed elsewhere, update path in `obsidian_secure/config.py`

### "Invalid password"
- Double-check your password (case-sensitive!)
- If truly forgotten, your vault cannot be recovered

### Leftover workspace warning
- This happens if the app crashed
- Click "Yes" to clean up the leftover decrypted files

### "Failed to delete files" error
- **Cause**: Obsidian or another program has files open
- **Solution**: Close Obsidian completely, then try locking again
- Verify Obsidian is not in Task Manager or system tray

## Advanced Usage

For programmatic access, see [examples/cli_example.py](examples/cli_example.py)
