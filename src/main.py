import sys
import os
import ctypes
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from .database.migrations import create_tables
from .database.seed_data import seed_all
from .ui.main_window import MainWindow


def setup_logging():
    """Setup application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def initialize_database():
    """Initialize database schema and seed data."""
    logger = logging.getLogger(__name__)

    try:
        logger.info("Initializing database...")
        create_tables()
        logger.info("Database tables created successfully")

        logger.info("Seeding initial data...")
        seed_all()
        logger.info("Database seeded successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting DentNest application...")

    # Initialize database
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("DentNest")
    app.setOrganizationName("DentNest")

    # Fix for taskbar icon on Windows
    if sys.platform == 'win32':
        myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Set Application Icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "dentnest.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Set application style
    app.setStyle('Fusion')

    # Force light theme palette (override system dark theme)
    from PyQt6.QtGui import QPalette, QColor
    from PyQt6.QtCore import Qt

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(29, 29, 31))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(250, 250, 250))
    palette.setColor(QPalette.ColorRole.Text, QColor(29, 29, 31))
    palette.setColor(QPalette.ColorRole.Button, QColor(245, 245, 247))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(29, 29, 31))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("Application started successfully")

    # Run event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
