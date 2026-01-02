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
   - Close Obsidian
   - Click "Lock" in ObsidianSecure
   - Your notes are re-encrypted and the workspace is securely deleted

## Daily Workflow

1. Start ObsidianSecure: `python main.py`
2. Select your vault
3. Unlock with password
4. Launch Obsidian
5. Work on your notes
6. Lock the vault when finished

## Important Notes

- **NEVER forget your password** - there's no recovery method!
- **Always lock** before shutting down
- **Keep backups** of your encrypted vault folder
- The encrypted vault folder (e.g., `C:\MySecrets\vault`) is safe to backup/sync
- The temporary workspace is automatically deleted on lock

## Troubleshooting

### "Obsidian not found"
- Install Obsidian from [obsidian.md](https://obsidian.md/)
- Default location: `%LOCALAPPDATA%\Obsidian\Obsidian.exe`

### "Invalid password"
- Double-check your password (case-sensitive!)
- If truly forgotten, your vault cannot be recovered

### Leftover workspace warning
- This happens if the app crashed
- Click "Yes" to clean up the leftover decrypted files

## Advanced Usage

For programmatic access, see [examples/cli_example.py](examples/cli_example.py)
