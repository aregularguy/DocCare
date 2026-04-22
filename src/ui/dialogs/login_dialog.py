"""App login screen — shown on startup when a password is configured."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeyEvent
from ...services.settings_service import SettingsService


class LoginDialog(QDialog):
    """Full-screen login dialog shown before the main window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = SettingsService()
        self._attempts = 0
        self.setWindowTitle("DentNest — Login")
        self.setModal(True)
        self.setFixedSize(420, 340)
        # Remove the close (X) button so the user can't bypass login
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Top banner ──
        banner = QFrame()
        banner.setFixedHeight(100)
        banner.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #0F2942, stop:1 #1A4A7A); }"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(28, 0, 28, 0)
        icon = QLabel("🦷")
        icon.setStyleSheet("font-size:32px; background:transparent;")
        bl.addWidget(icon)
        title = QLabel("DentNest")
        title.setFont(QFont("Ubuntu", 22, QFont.Weight.Bold))
        title.setStyleSheet("color:white; background:transparent; margin-left:10px;")
        bl.addWidget(title)
        bl.addStretch()
        layout.addWidget(banner)

        # ── Body ──
        body = QFrame()
        body.setStyleSheet("background:#F8FAFC;")
        vl = QVBoxLayout(body)
        vl.setContentsMargins(40, 32, 40, 32)
        vl.setSpacing(16)

        subtitle = QLabel("Enter your password to continue")
        subtitle.setStyleSheet("color:#374151; font-size:14px; font-weight:600;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(subtitle)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setFixedHeight(46)
        self.password_input.setStyleSheet(
            "QLineEdit { border:2px solid #D1D5DB; border-radius:8px;"
            " padding:0 14px; font-size:14px; background:white; }"
            "QLineEdit:focus { border:2px solid #0F2942; }"
        )
        self.password_input.returnPressed.connect(self._on_unlock)
        vl.addWidget(self.password_input)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color:#DC2626; font-size:12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        vl.addWidget(self.error_label)

        unlock_btn = QPushButton("🔓  Unlock")
        unlock_btn.setFixedHeight(46)
        unlock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        unlock_btn.setStyleSheet(
            "QPushButton { background:#0F2942; color:white; border:none;"
            " border-radius:8px; font-size:14px; font-weight:700; }"
            "QPushButton:hover { background:#1A4A7A; }"
        )
        unlock_btn.clicked.connect(self._on_unlock)
        vl.addWidget(unlock_btn)

        vl.addStretch()
        layout.addWidget(body)

        self.password_input.setFocus()

    def _on_unlock(self):
        password = self.password_input.text()
        if self.service.verify_password(password):
            self.accept()
        else:
            self._attempts += 1
            self.password_input.clear()
            self.password_input.setFocus()
            msg = f"Incorrect password. Please try again."
            if self._attempts >= 3:
                msg = f"Incorrect password ({self._attempts} attempts)."
            self.error_label.setText(f"❌ {msg}")
            self.error_label.setVisible(True)
            # Shake animation — red border flash
            self.password_input.setStyleSheet(
                "QLineEdit { border:2px solid #DC2626; border-radius:8px;"
                " padding:0 14px; font-size:14px; background:#FEF2F2; }"
            )
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(800, self._reset_input_style)

    def _reset_input_style(self):
        self.password_input.setStyleSheet(
            "QLineEdit { border:2px solid #D1D5DB; border-radius:8px;"
            " padding:0 14px; font-size:14px; background:white; }"
            "QLineEdit:focus { border:2px solid #0F2942; }"
        )
