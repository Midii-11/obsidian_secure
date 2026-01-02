# Changelog

All notable changes to ObsidianSecure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-02

### Added
- Initial release of ObsidianSecure
- Complete vault encryption using AES-256-GCM
- Argon2id password-based key derivation
- HKDF key hierarchy (Master → Vault → File keys)
- Encrypted index for filename/folder name protection
- Temporary workspace management
- Automatic file change detection
- Secure file and directory deletion
- PySide6 GUI application
- Crash recovery system
- Obsidian launcher integration
- Comprehensive test suite (27 tests)
- Documentation (README, QUICKSTART, CONTRIBUTING)
- CLI example for programmatic usage

### Security Features
- Data-at-rest encryption
- Filename and folder name encryption
- Authenticated encryption (GCM mode)
- Memory-hard key derivation (Argon2id)
- Atomic file writes
- Multi-pass secure deletion
- No password storage
- No plaintext logs

### Platform Support
- Windows (primary target)
- Python 3.9+ compatible

## [0.1.1] - 2026-01-02

### Fixed
- **Critical**: Fixed new files not persisting across lock/unlock cycles
  - Completely rewrote `lock()` method to process all workspace files (new, modified, and unchanged)
  - Added comprehensive file lifecycle management (create, modify, delete)
  - Files created in Obsidian now properly persist after locking
- **Critical**: Fixed subdirectory file handling
  - Updated `_add_new_file_to_vault()` to correctly navigate from root folder
  - New directories and files within them now work correctly
  - Fixed path resolution for nested folder structures
- **Critical**: Fixed workspace not being deleted when files are locked by other processes
  - Updated `secure_delete_directory()` to raise descriptive errors instead of failing silently
  - Added user warnings about closing Obsidian before locking
  - Improved error messages with troubleshooting guidance
- Fixed salt validation error on vault unlock
  - Updated `VaultIndex.save()` signature to accept salt parameter
  - Vault now unlocks correctly after being locked
- Fixed duplicate notes appearing in GUI tree view
  - Updated `VaultIndex.find_by_path()` to search from root folder's children
  - Proper path resolution prevents duplicate entries
- Fixed Obsidian executable path configuration
  - Updated default path to `%LOCALAPPDATA%\Programs\Obsidian\Obsidian.exe`
  - Configurable via `config.py`

### Improved
- Enhanced error messages for file locking issues
- Added confirmation dialogs with security reminders
- Better user guidance in lock/unlock workflow
- Improved path normalization across all file operations
- Updated test suite to match new path handling behavior (27 tests passing)

### Documentation
- Added IMPORTANT_WORKFLOW.md with detailed lock/unlock instructions
- Updated README with corrected Obsidian path
- Enhanced troubleshooting section

## [Unreleased]

### Planned Features
- macOS and Linux support
- Vault backup/restore
- Password change functionality
- Import existing Obsidian vaults
- Auto-lock timer
- System tray integration
- Multi-vault management
- Vault statistics
- Export to plaintext
