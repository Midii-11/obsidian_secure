"""
Main application window for ObsidianSecure.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTextEdit,
    QMessageBox,
    QProgressBar,
    QSplitter,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from .dialogs import PasswordDialog, CreateVaultDialog
from .vault_tree import VaultTreeWidget
from ..session import SessionManager
from ..vault import VaultManager, is_valid_vault
from ..config import APP_NAME, APP_VERSION


class WorkerThread(QThread):
    """Worker thread for long-running operations."""

    finished = Signal(object)  # Result
    error = Signal(str)  # Error message
    progress = Signal(str)  # Progress message

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Run the worker function."""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(800, 600)

        self.vault_path: Path | None = None
        self.session_manager: SessionManager | None = None
        self.is_unlocked = False

        self._setup_ui()
        self._check_crash_recovery()

    def _setup_ui(self):
        """Set up the UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Top section: Vault info and actions
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)

        # Vault path display
        vault_info_layout = QHBoxLayout()

        vault_label = QLabel("Current Vault:")
        vault_info_layout.addWidget(vault_label)

        self.vault_path_label = QLabel("No vault selected")
        self.vault_path_label.setStyleSheet("font-weight: bold;")
        vault_info_layout.addWidget(self.vault_path_label)

        vault_info_layout.addStretch()

        top_layout.addLayout(vault_info_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.select_vault_button = QPushButton("Select Vault")
        self.select_vault_button.clicked.connect(self._select_vault)
        button_layout.addWidget(self.select_vault_button)

        self.create_vault_button = QPushButton("Create New Vault")
        self.create_vault_button.clicked.connect(self._create_vault)
        button_layout.addWidget(self.create_vault_button)

        self.unlock_button = QPushButton("Unlock")
        self.unlock_button.clicked.connect(self._unlock_vault)
        self.unlock_button.setEnabled(False)
        button_layout.addWidget(self.unlock_button)

        self.lock_button = QPushButton("Lock")
        self.lock_button.clicked.connect(self._lock_vault)
        self.lock_button.setEnabled(False)
        button_layout.addWidget(self.lock_button)

        self.launch_obsidian_button = QPushButton("Launch Obsidian")
        self.launch_obsidian_button.clicked.connect(self._launch_obsidian)
        self.launch_obsidian_button.setEnabled(False)
        button_layout.addWidget(self.launch_obsidian_button)

        button_layout.addStretch()

        top_layout.addLayout(button_layout)

        layout.addWidget(top_section)

        # Splitter for tree and log
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Tree view
        self.tree_widget = VaultTreeWidget()
        splitter.addWidget(self.tree_widget)

        # Log panel
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(0, 0, 0, 0)

        log_label = QLabel("Log:")
        log_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        font = QFont("Courier New", 9)
        self.log_text.setFont(font)
        log_layout.addWidget(self.log_text)

        splitter.addWidget(log_widget)

        layout.addWidget(splitter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def _check_crash_recovery(self):
        """Check for leftover workspaces and prompt for recovery."""
        from ..session.workspace import Workspace

        existing = Workspace.find_existing_workspaces()

        if existing:
            reply = QMessageBox.question(
                self,
                "Crash Recovery",
                f"Found {len(existing)} leftover workspace(s) from a previous session.\n\n"
                "These may contain decrypted data and should be cleaned up.\n\n"
                "Delete them now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._log("Cleaning up leftover workspaces...")
                from ..io import secure_delete_directory

                for workspace_path in existing:
                    try:
                        secure_delete_directory(workspace_path)
                        self._log(f"Deleted: {workspace_path.name}")
                    except Exception as e:
                        self._log(f"Error deleting {workspace_path.name}: {e}")

                self._log("Cleanup complete.")

    def _select_vault(self):
        """Open dialog to select an existing vault."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Vault Directory",
            str(Path.home()),
        )

        if not directory:
            return

        vault_path = Path(directory)

        if not is_valid_vault(vault_path):
            QMessageBox.warning(
                self,
                "Invalid Vault",
                "The selected directory is not a valid ObsidianSecure vault.",
            )
            return

        self.vault_path = vault_path
        self.vault_path_label.setText(str(vault_path))
        self.unlock_button.setEnabled(True)
        self._log(f"Selected vault: {vault_path}")

    def _create_vault(self):
        """Create a new vault."""
        dialog = CreateVaultDialog(self)
        result = dialog.get_values()

        if result is None:
            return

        vault_path, vault_name, password = result

        # Create vault in worker thread
        self._log(f"Creating vault at {vault_path}...")
        self._show_progress("Creating vault...")

        def create():
            return VaultManager.create_vault(vault_path, password, vault_name)

        worker = WorkerThread(create)
        worker.finished.connect(lambda vault_id: self._on_vault_created(vault_path, vault_id))
        worker.error.connect(self._on_operation_error)
        worker.start()

        # Store worker to prevent garbage collection
        self._worker = worker

    def _on_vault_created(self, vault_path: Path, vault_id: str):
        """Handle vault creation completion."""
        self._hide_progress()
        self._log(f"Vault created successfully! ID: {vault_id}")

        QMessageBox.information(
            self,
            "Vault Created",
            f"Vault created successfully at:\n{vault_path}\n\nVault ID: {vault_id}",
        )

        # Auto-select the new vault
        self.vault_path = vault_path
        self.vault_path_label.setText(str(vault_path))
        self.unlock_button.setEnabled(True)

    def _unlock_vault(self):
        """Unlock the selected vault."""
        if self.vault_path is None:
            return

        # Get password
        dialog = PasswordDialog(self, title="Unlock Vault")
        password = dialog.get_password()

        if password is None:
            return

        # Unlock in worker thread
        self._log("Unlocking vault...")
        self._show_progress("Unlocking vault...")

        def unlock():
            self.session_manager = SessionManager(self.vault_path)
            workspace = self.session_manager.unlock(password)
            return workspace

        worker = WorkerThread(unlock)
        worker.finished.connect(self._on_vault_unlocked)
        worker.error.connect(self._on_operation_error)
        worker.start()

        self._worker = worker

    def _on_vault_unlocked(self, workspace):
        """Handle vault unlock completion."""
        self._hide_progress()
        self._log(f"Vault unlocked! Workspace: {workspace.workspace_path}")

        self.is_unlocked = True
        self.unlock_button.setEnabled(False)
        self.lock_button.setEnabled(True)
        self.launch_obsidian_button.setEnabled(True)

        # Load tree
        if self.session_manager and self.session_manager.index:
            self.tree_widget.load_index(self.session_manager.index)

        QMessageBox.information(
            self,
            "Vault Unlocked",
            f"Vault unlocked successfully!\n\nWorkspace: {workspace.workspace_path}",
        )

    def _lock_vault(self):
        """Lock the vault."""
        if self.session_manager is None:
            return

        reply = QMessageBox.question(
            self,
            "Lock Vault",
            "Lock the vault and securely delete the workspace?\n\n"
            "Any modified files will be encrypted and saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self._log("Locking vault...")
        self._show_progress("Locking vault...")

        def lock():
            self.session_manager.lock()

        worker = WorkerThread(lock)
        worker.finished.connect(self._on_vault_locked)
        worker.error.connect(self._on_operation_error)
        worker.start()

        self._worker = worker

    def _on_vault_locked(self, _):
        """Handle vault lock completion."""
        self._hide_progress()
        self._log("Vault locked successfully.")

        self.is_unlocked = False
        self.unlock_button.setEnabled(True)
        self.lock_button.setEnabled(False)
        self.launch_obsidian_button.setEnabled(False)

        self.tree_widget.clear()

        QMessageBox.information(self, "Vault Locked", "Vault locked and workspace deleted.")

    def _launch_obsidian(self):
        """Launch Obsidian with the unlocked workspace."""
        if self.session_manager is None:
            return

        try:
            process = self.session_manager.launch_obsidian()
            self._log(f"Launched Obsidian (PID: {process.pid})")

            QMessageBox.information(
                self,
                "Obsidian Launched",
                "Obsidian has been launched with the decrypted workspace.",
            )
        except FileNotFoundError as e:
            QMessageBox.warning(
                self,
                "Obsidian Not Found",
                f"Could not find Obsidian:\n\n{e}\n\n"
                "You can manually open the workspace folder:\n"
                f"{self.session_manager.workspace.workspace_path}",
            )
        except Exception as e:
            self._log(f"Error launching Obsidian: {e}")
            QMessageBox.critical(self, "Error", f"Failed to launch Obsidian:\n\n{e}")

    def _on_operation_error(self, error_msg: str):
        """Handle operation errors."""
        self._hide_progress()
        self._log(f"ERROR: {error_msg}")
        QMessageBox.critical(self, "Error", f"Operation failed:\n\n{error_msg}")

    def _show_progress(self, message: str):
        """Show progress bar with message."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self._log(message)

    def _hide_progress(self):
        """Hide progress bar."""
        self.progress_bar.setVisible(False)

    def _log(self, message: str):
        """Add message to log."""
        self.log_text.append(message)

    def closeEvent(self, event):
        """Handle window close event."""
        if self.is_unlocked:
            reply = QMessageBox.warning(
                self,
                "Vault Still Unlocked",
                "The vault is still unlocked. Lock it before closing?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._lock_vault()
                # Wait for lock to complete
                if hasattr(self, "_worker"):
                    self._worker.wait()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                # Clean up resources without locking
                self._cleanup_resources()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def _cleanup_resources(self):
        """Clean up resources (watcher, threads) without locking vault."""
        if self.session_manager and self.session_manager.watcher:
            self.session_manager.watcher.stop()
            self.session_manager.watcher = None
