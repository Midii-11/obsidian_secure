# Contributing to ObsidianSecure

Thank you for your interest in contributing to ObsidianSecure!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Lock_Notes_Obsidian
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests**
   ```bash
   pytest
   ```

## Project Structure

```
obsidian_secure/
├── crypto/          # Cryptographic primitives
│   ├── kdf.py       # Argon2 key derivation
│   ├── cipher.py    # AES-256-GCM encryption
│   ├── hkdf.py      # Key hierarchy
│   └── formats.py   # Encrypted file format
├── vault/           # Vault management
│   ├── index.py     # Encrypted index (filename mapping)
│   ├── layout.py    # Vault directory layout
│   ├── discovery.py # Vault discovery
│   └── manager.py   # High-level vault operations
├── session/         # Session management
│   ├── manager.py   # Session lifecycle
│   ├── workspace.py # Temporary workspace
│   └── watcher.py   # File change monitoring
├── io/              # I/O utilities
│   ├── atomic.py    # Atomic file writes
│   └── secure_delete.py  # Secure deletion
├── gui/             # GUI components
│   ├── main_window.py    # Main application window
│   ├── dialogs.py        # Dialogs (password, create vault)
│   └── vault_tree.py     # Tree view widget
└── utils/           # Utilities
    ├── hashing.py   # File hashing
    └── logging.py   # Logging setup
```

## Coding Guidelines

### Security Considerations

1. **Never log sensitive data**
   - No passwords, keys, or plaintext content in logs
   - Use the SensitiveDataFilter

2. **Memory safety**
   - Clear sensitive data from memory when done
   - Use best-effort memory zeroing

3. **File operations**
   - Always use atomic writes for encrypted files
   - Use secure deletion for temporary files

4. **Cryptography**
   - Don't implement your own crypto primitives
   - Use established libraries (cryptography, argon2-cffi)
   - Follow current best practices

### Code Style

1. **Follow PEP 8**
   - Use `black` for formatting: `black obsidian_secure/`

2. **Type hints**
   - Use type hints for all functions
   - Example: `def func(param: str) -> int:`

3. **Docstrings**
   - Use Google-style docstrings
   - Document all public functions and classes

4. **Error handling**
   - Use specific exceptions
   - Provide helpful error messages

### Testing

1. **Write tests for new features**
   - Unit tests in `tests/`
   - Aim for high coverage

2. **Test security-critical code**
   - Encryption/decryption
   - Key derivation
   - Secure deletion

3. **Run tests before committing**
   ```bash
   pytest
   ```

## Adding New Features

### Example: Adding a New Encryption Algorithm

1. **Add to config.py**
   ```python
   CIPHER_ALGORITHM = "AES-256-GCM"  # or new algorithm
   ```

2. **Implement in crypto/cipher.py**
   ```python
   def encrypt_data_new(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
       # Implementation
       pass
   ```

3. **Add tests**
   ```python
   # tests/test_crypto.py
   def test_new_encryption():
       # Test implementation
       pass
   ```

4. **Update documentation**
   - Update README.md
   - Update docstrings

### Example: Adding GUI Feature

1. **Add UI components in gui/**
   ```python
   # gui/new_dialog.py
   class NewDialog(QDialog):
       # Implementation
       pass
   ```

2. **Integrate with MainWindow**
   ```python
   # gui/main_window.py
   def _new_feature(self):
       dialog = NewDialog(self)
       # ...
   ```

3. **Add tests if applicable**

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests and linting**
   ```bash
   pytest
   black obsidian_secure/
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/my-feature
   ```

## Security Vulnerability Reporting

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email the maintainer privately
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Questions?

Feel free to open an issue for:
- Feature requests
- Bug reports
- Documentation improvements
- General questions

Thank you for contributing!
