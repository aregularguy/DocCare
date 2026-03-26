"""Settings widget - Placeholder."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class SettingsWidget(QWidget):
    """Settings widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Settings")
        title.setObjectName("page_title")
        layout.addWidget(title)

        placeholder = QLabel("Application settings coming soon...")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #86868B; padding: 100px; font-size: 16px;")
        layout.addWidget(placeholder)

    def refresh_data(self):
        """Refresh data."""
        pass
