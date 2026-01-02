"""
File watcher for monitoring workspace changes.
"""

import time
from pathlib import Path
from typing import Callable, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class FileWatcher:
    """Monitors workspace for file changes."""

    def __init__(self, workspace_path: Path, on_change: Callable[[Path], None] | None = None):
        """
        Initialize file watcher.

        Args:
            workspace_path: Path to workspace to monitor
            on_change: Optional callback function called when files change
        """
        self.workspace_path = workspace_path
        self.on_change = on_change
        self.observer: Observer | None = None
        self.changed_files: Set[Path] = set()

    def start(self) -> None:
        """Start monitoring the workspace."""
        if self.observer is not None:
            return  # Already running

        event_handler = WorkspaceEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.workspace_path), recursive=True)
        self.observer.start()

    def stop(self) -> None:
        """Stop monitoring the workspace."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.observer = None

    def get_changed_files(self) -> list[Path]:
        """
        Get list of files that have changed.

        Returns:
            list[Path]: List of changed file paths relative to workspace
        """
        return list(self.changed_files)

    def clear_changes(self) -> None:
        """Clear the list of changed files."""
        self.changed_files.clear()

    def _on_file_changed(self, file_path: Path) -> None:
        """
        Internal callback when a file changes.

        Args:
            file_path: Absolute path to changed file
        """
        # Convert to relative path
        try:
            relative_path = file_path.relative_to(self.workspace_path)
        except ValueError:
            return  # Not in workspace

        # Skip Obsidian config files
        if ".obsidian" in relative_path.parts:
            return

        self.changed_files.add(relative_path)

        if self.on_change:
            self.on_change(relative_path)


class WorkspaceEventHandler(FileSystemEventHandler):
    """Event handler for workspace file system events."""

    def __init__(self, watcher: FileWatcher):
        """
        Initialize event handler.

        Args:
            watcher: FileWatcher instance
        """
        self.watcher = watcher
        super().__init__()

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            self.watcher._on_file_changed(Path(event.src_path))

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            self.watcher._on_file_changed(Path(event.src_path))

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        if not event.is_directory:
            self.watcher._on_file_changed(Path(event.src_path))
