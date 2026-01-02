"""
Configuration constants for ObsidianSecure.
"""

import os
from pathlib import Path

# Application metadata
APP_NAME = "ObsidianSecure"
APP_VERSION = "0.1.0"
FILE_MAGIC = "OBSEC1"
FORMAT_VERSION = 1

# Cryptographic parameters
KDF_ALGORITHM = "argon2id"
ARGON2_MEMORY_COST = 65536  # 64 MB in KiB
ARGON2_TIME_COST = 3  # iterations
ARGON2_PARALLELISM = 4  # threads

CIPHER_ALGORITHM = "AES-256-GCM"
AES_KEY_SIZE = 32  # 256 bits
SALT_SIZE = 16  # bytes
NONCE_SIZE = 12  # bytes for GCM
TAG_SIZE = 16  # bytes for GCM authentication tag

# HKDF parameters
HKDF_INFO_VAULT = b"ObsidianSecure.Vault.Key"
HKDF_INFO_FILE = b"ObsidianSecure.File.Key"

# File extensions
ENCRYPTED_FILE_EXT = ".enc"
INDEX_FILENAME = "index.enc"
MARKDOWN_EXT = ".md"

# Workspace configuration
WORKSPACE_BASE = Path(os.getenv("LOCALAPPDATA", os.path.expanduser("~"))) / APP_NAME / "workspace"
WORKSPACE_PREFIX = "workspace_"

# Security settings
SECURE_DELETE_PASSES = 3  # Number of overwrite passes for secure deletion
AUTO_LOCK_TIMEOUT = 30 * 60  # 30 minutes in seconds (0 = disabled)

# Obsidian configuration
OBSIDIAN_CONFIG_FOLDER = ".obsidian"
OBSIDIAN_EXECUTABLE = os.path.expandvars(
    r"%LOCALAPPDATA%\Programs\Obsidian\Obsidian.exe"
)

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
