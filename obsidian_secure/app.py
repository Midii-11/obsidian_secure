"""
Main application entry point for ObsidianSecure.
"""

import sys
from PySide6.QtWidgets import QApplication
from .gui import MainWindow
from .utils import setup_logging


def main():
    """Main application entry point."""
    # Set up logging
    logger = setup_logging()
    logger.info("Starting ObsidianSecure...")

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ObsidianSecure")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
