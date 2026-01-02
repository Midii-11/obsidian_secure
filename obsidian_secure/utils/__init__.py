"""
Utility functions for ObsidianSecure.
"""

from .hashing import compute_file_hash
from .logging import setup_logging

__all__ = [
    "compute_file_hash",
    "setup_logging",
]
