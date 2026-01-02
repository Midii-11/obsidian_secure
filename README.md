# ObsidianSecure - Secure Obsidian Vault Encryption Tool

ObsidianSecure provides maximum security for storing credentials and confidential notes in Obsidian through complete vault encryption.

## Features

- **Complete Encryption**: Encrypts both file contents and filenames/folder names
- **Data-at-Rest Protection**: Vault is always encrypted on disk
- **Temporary Workspace**: Decrypted files only exist during active sessions
- **Strong Cryptography**:
  - Argon2id for password-based key derivation
  - AES-256-GCM for authenticated encryption
  - HKDF for key hierarchy
- **Crash Recovery**: Automatic detection and cleanup of leftover workspaces
- **User-Friendly GUI**: Easy-to-use interface built with PySide6

## Installation

### Requirements

- Python 3.13.5 or later
- Windows (primary target platform)

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Application

Run the application:
```bash
python main.py
```

### Creating a New Vault

1. Click **"Create New Vault"**
2. Choose a directory for the encrypted vault
3. Enter a vault name
4. Set a strong master password (minimum 8 characters)
5. Confirm the password

The vault will be created with encrypted storage.

### Unlocking a Vault

1. Click **"Select Vault"** and choose your encrypted vault directory
2. Click **"Unlock"**
3. Enter your master password
4. The vault will be decrypted to a temporary workspace

### Working with Your Notes

1. After unlocking, click **"Launch Obsidian"**
2. Obsidian will open with your decrypted workspace
3. Edit your notes as usual
4. Modified files are tracked automatically

### Locking the Vault

1. Close Obsidian
2. Click **"Lock"** in ObsidianSecure
3. All modified files will be re-encrypted
4. The temporary workspace will be securely deleted

**IMPORTANT**: Always lock the vault when finished to protect your data!

## Security Model

### What's Protected

- **Disk Theft**: Encrypted vault is useless without password
- **Unauthorized Local Access**: All data encrypted at rest
- **Filename Leakage**: Both filenames and folder names are encrypted
- **Crash Scenarios**: Leftover workspaces detected and cleaned on next startup

### What's NOT Protected

- **Memory Inspection**: Plaintext exists in memory during unlocked sessions
- **Active Monitoring**: If someone accesses your computer while vault is unlocked
- **Keylogging**: Hardware/software keyloggers can capture your password

### Best Practices

1. **Use a strong password**: At least 12 characters, mix of uppercase, lowercase, numbers, symbols
2. **Lock when away**: Always lock the vault when stepping away from your computer
3. **Secure your computer**: Use full-disk encryption, screen lock, etc.
4. **Regular backups**: Keep encrypted backups of your vault
5. **Don't share passwords**: Never share your master password

## Architecture

### Directory Structure

```
obsidian_secure/
├── crypto/          # Cryptographic primitives
├── vault/           # Vault management and index
├── session/         # Session and workspace management
├── io/              # Atomic writes and secure deletion
├── gui/             # PySide6 GUI components
└── utils/           # Utilities (logging, hashing)
```

### Encrypted Vault Layout

```
my_vault/
├── .vault_id        # Vault identifier
├── index.enc        # Encrypted index (filename mappings)
├── a3f2e1.enc       # Encrypted file
├── b8d4c9.enc       # Encrypted file
└── f1a2b3.enc       # Encrypted file
```

Real filenames are stored encrypted in `index.enc`.

### Temporary Workspace

During an unlocked session, a temporary workspace is created:

```
%LOCALAPPDATA%\ObsidianSecure\workspace_<random_id>\
├── .obsidian/       # Obsidian config
├── Secrets/         # Decrypted folders
│   ├── AWS.md
│   └── Passwords.md
└── Notes/
    └── Ideas.md
```

This workspace is **securely deleted** when you lock the vault.

## Cryptographic Details

### Key Derivation (Argon2id)

- Memory cost: 64 MB
- Time cost: 3 iterations
- Parallelism: 4 threads

### Encryption (AES-256-GCM)

- Key size: 256 bits
- Nonce size: 12 bytes (unique per file)
- Authentication tag: 16 bytes

### Key Hierarchy

```
Master Password
    ↓ (Argon2id + salt)
Master Key
    ↓ (HKDF + vault_id)
Vault Key
    ↓ (HKDF + file_id)
File Key → Encrypts individual files
```

Each file has a unique encryption key derived from the vault key.

## Troubleshooting

### Leftover Workspaces

If the application crashes, you may see a warning about leftover workspaces on next startup. Click "Yes" to securely delete them.

### Obsidian Not Found

If "Launch Obsidian" fails:
- Verify Obsidian is installed at: `%LOCALAPPDATA%\Obsidian\Obsidian.exe`
- Or manually open the workspace folder shown in the log

### Forgotten Password

**There is NO password recovery!** If you forget your password, your vault cannot be decrypted. Store your password securely (e.g., password manager).

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
black obsidian_secure/
```

## License

This project is for educational and personal use.

## Disclaimer

This software is provided as-is. While it uses industry-standard cryptography, it has not undergone a professional security audit. Use at your own risk for sensitive data.

Always maintain backups of important data!
