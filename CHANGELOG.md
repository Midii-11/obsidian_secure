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
