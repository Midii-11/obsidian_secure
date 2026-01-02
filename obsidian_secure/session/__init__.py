"""
Session management for workspace lifecycle.
"""

from .manager import SessionManager
from .workspace import Workspace
from .watcher import FileWatcher

__all__ = [
    "SessionManager",
    "Workspace",
    "FileWatcher",
]
