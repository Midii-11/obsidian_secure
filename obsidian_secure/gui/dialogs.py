"""
Dialogs for vault operations.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt


class PasswordDialog(QDialog):
    """Dialog for entering vault password."""

    def __init__(self, parent=None, title="Unlock Vault"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.password = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout()

        # Password label
        label = QLabel("Enter master password:")
        layout.addWidget(label)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.accept)
        layout.addWidget(self.password_input)

        # Buttons
        button_layout = QHBoxLayout()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setMinimumWidth(300)

    def accept(self):
        """Accept the dialog and store the password."""
        self.password = self.password_input.text()
        super().accept()

    def get_password(self) -> str | None:
        """
        Show dialog and get password.

        Returns:
            str | None: Password if OK was clicked, None if cancelled
        """
        result = self.exec()
        if result == QDialog.DialogCode.Accepted:
            return self.password
        return None


class CreateVaultDialog(QDialog):
    """Dialog for creating a new vault."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Vault")
        self.setModal(True)

        self.vault_path = None
        self.vault_name = None
        self.password = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout()

        # Vault location
        location_label = QLabel("Vault Location:")
        layout.addWidget(location_label)

        location_layout = QHBoxLayout()
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Select vault directory...")
        location_layout.addWidget(self.location_input)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_location)
        location_layout.addWidget(self.browse_button)

        layout.addLayout(location_layout)

        # Vault name
        name_label = QLabel("Vault Name:")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Secure Vault")
        layout.addWidget(self.name_input)

        # Password
        password_label = QLabel("Master Password:")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Confirm password
        confirm_label = QLabel("Confirm Password:")
        layout.addWidget(confirm_label)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_input)

        # Buttons
        button_layout = QHBoxLayout()

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self._validate_and_accept)
        button_layout.addWidget(self.create_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setMinimumWidth(400)

    def _browse_location(self):
        """Open file dialog to select vault location."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Vault Directory",
            str(Path.home()),
        )

        if directory:
            self.location_input.setText(directory)

    def _validate_and_accept(self):
        """Validate inputs and accept dialog."""
        # Validate location
        location = self.location_input.text().strip()
        if not location:
            QMessageBox.warning(self, "Invalid Input", "Please select a vault location.")
            return

        # Validate vault name
        name = self.name_input.text().strip()
        if not name:
            name = "My Vault"  # Default name

        # Validate password
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not password:
            QMessageBox.warning(self, "Invalid Input", "Password cannot be empty.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return

        if len(password) < 8:
            QMessageBox.warning(
                self,
                "Weak Password",
                "Password should be at least 8 characters long.",
            )
            return

        # Store values
        self.vault_path = Path(location)
        self.vault_name = name
        self.password = password

        self.accept()

    def get_values(self) -> tuple[Path, str, str] | None:
        """
        Show dialog and get values.

        Returns:
            tuple | None: (vault_path, vault_name, password) if OK, None if cancelled
        """
        result = self.exec()
        if result == QDialog.DialogCode.Accepted:
            return (self.vault_path, self.vault_name, self.password)
        return None
