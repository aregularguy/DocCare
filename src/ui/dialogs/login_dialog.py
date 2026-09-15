"""App login screen — shown on startup when a password is configured."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from ...services.settings_service import SettingsService


class LoginDialog(QDialog):
    """Full-screen login dialog shown before the main window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = SettingsService()
        self._attempts = 0
        self.setWindowTitle("DentNest — Login")
        self.setModal(True)
        self.setFixedSize(420, 380)
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
            "stop:0 #1F4E5A, stop:1 #2A6674); }"
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
        body.setStyleSheet("background:#F4F7F8;")
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
            "QLineEdit { border:2px solid #CFDADE; border-radius:8px;"
            " padding:0 14px; font-size:14px; background:white; }"
            "QLineEdit:focus { border:2px solid #1F4E5A; }"
        )
        self.password_input.returnPressed.connect(self._on_unlock)
        vl.addWidget(self.password_input)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color:#DC2626; font-size:12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        vl.addWidget(self.error_label)

        unlock_btn = QPushButton("Unlock")
        unlock_btn.setFixedHeight(46)
        unlock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        unlock_btn.setStyleSheet(
            "QPushButton { background:#1F4E5A; color:white; border:none;"
            " border-radius:8px; font-size:14px; font-weight:700; }"
            "QPushButton:hover { background:#2A6674; }"
        )
        unlock_btn.clicked.connect(self._on_unlock)
        vl.addWidget(unlock_btn)

        # ── Forgot Password link ──
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_btn.setStyleSheet(
            "QPushButton { background:transparent; border:none;"
            " color:#1F8A9E; font-size:12px; font-weight:600; text-decoration:underline; }"
            "QPushButton:hover { color:#16707F; }"
        )
        forgot_btn.clicked.connect(self._on_forgot_password)
        vl.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignCenter)

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
            msg = "Incorrect password. Please try again."
            if self._attempts >= 3:
                msg = f"Incorrect password ({self._attempts} attempts)."
            self.error_label.setText(msg)
            self.error_label.setVisible(True)
            # Red border flash
            self.password_input.setStyleSheet(
                "QLineEdit { border:2px solid #DC2626; border-radius:8px;"
                " padding:0 14px; font-size:14px; background:#FBEBEA; }"
            )
            QTimer.singleShot(800, self._reset_input_style)

    def _reset_input_style(self):
        self.password_input.setStyleSheet(
            "QLineEdit { border:2px solid #CFDADE; border-radius:8px;"
            " padding:0 14px; font-size:14px; background:white; }"
            "QLineEdit:focus { border:2px solid #1F4E5A; }"
        )

    def _on_forgot_password(self):
        """Handle Forgot Password — recovery key flow."""
        if not self.service.get("recovery_key_hash"):
            QMessageBox.warning(
                self, "No Recovery Key",
                "No recovery key has been configured.\n\n"
                "A recovery key is generated when you set a password in Settings.\n"
                "If you cannot remember your password, you may need to manually "
                "delete the app_password_hash from data/settings.json."
            )
            return

        # Step 1: Ask for recovery key
        dialog = _RecoveryKeyDialog(self.service, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Step 2: Set new password
            pw_dialog = _SetNewPasswordDialog(self.service, self)
            if pw_dialog.exec() == QDialog.DialogCode.Accepted:
                # Password has been reset, accept login
                self.accept()


class _RecoveryKeyDialog(QDialog):
    """Dialog that asks for the recovery key."""

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Recovery Key")
        self.setFixedSize(400, 240)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Enter Recovery Key")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color:#1F4E5A;")
        layout.addWidget(title)

        info = QLabel("Enter the recovery key that was shown when you set your password.")
        info.setStyleSheet("color:#5B6B73; font-size:12px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXX-XXX-XXX-XXX")
        self.key_input.setFixedHeight(44)
        self.key_input.setStyleSheet(
            "QLineEdit { border:2px solid #CFDADE; border-radius:8px;"
            " padding:0 14px; font-size:16px; font-family:monospace;"
            " letter-spacing:2px; background:white; }"
            "QLineEdit:focus { border:2px solid #1F4E5A; }"
        )
        self.key_input.returnPressed.connect(self._on_verify)
        layout.addWidget(self.key_input)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color:#DC2626; font-size:12px;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(
            "QPushButton { background:#F3F4F6; color:#374151; border:1px solid #CFDADE;"
            " border-radius:8px; padding:8px 20px; font-size:13px; font-weight:600; }"
            "QPushButton:hover { background:#DDE5E8; }"
        )
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        verify_btn = QPushButton("Verify")
        verify_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        verify_btn.setStyleSheet(
            "QPushButton { background:#1F4E5A; color:white; border:none;"
            " border-radius:8px; padding:8px 20px; font-size:13px; font-weight:700; }"
            "QPushButton:hover { background:#2A6674; }"
        )
        verify_btn.clicked.connect(self._on_verify)
        btn_layout.addWidget(verify_btn)

        layout.addLayout(btn_layout)
        self.key_input.setFocus()

    def _on_verify(self):
        key = self.key_input.text().strip()
        if not key:
            self.error_label.setText("Please enter the recovery key.")
            self.error_label.setVisible(True)
            return

        if self.service.verify_recovery_key(key):
            self.accept()
        else:
            self.error_label.setText("Invalid recovery key. Please try again.")
            self.error_label.setVisible(True)
            self.key_input.selectAll()
            self.key_input.setFocus()


class _SetNewPasswordDialog(QDialog):
    """Dialog to set a new password after successful recovery."""

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Set New Password")
        self.setFixedSize(400, 300)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Set New Password")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color:#1F4E5A;")
        layout.addWidget(title)

        info = QLabel("Recovery key verified. Enter your new password below.")
        info.setStyleSheet("color:#166534; font-size:12px; font-weight:600;")
        info.setWordWrap(True)
        layout.addWidget(info)

        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.setPlaceholderText("New password (min 4 characters)")
        self.pw_input.setFixedHeight(44)
        self.pw_input.setStyleSheet(
            "QLineEdit { border:2px solid #CFDADE; border-radius:8px;"
            " padding:0 14px; font-size:14px; background:white; }"
            "QLineEdit:focus { border:2px solid #1F4E5A; }"
        )
        layout.addWidget(self.pw_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm new password")
        self.confirm_input.setFixedHeight(44)
        self.confirm_input.setStyleSheet(
            "QLineEdit { border:2px solid #CFDADE; border-radius:8px;"
            " padding:0 14px; font-size:14px; background:white; }"
            "QLineEdit:focus { border:2px solid #1F4E5A; }"
        )
        self.confirm_input.returnPressed.connect(self._on_save)
        layout.addWidget(self.confirm_input)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color:#DC2626; font-size:12px;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(
            "QPushButton { background:#F3F4F6; color:#374151; border:1px solid #CFDADE;"
            " border-radius:8px; padding:8px 20px; font-size:13px; font-weight:600; }"
            "QPushButton:hover { background:#DDE5E8; }"
        )
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Set Password")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(
            "QPushButton { background:#1F4E5A; color:white; border:none;"
            " border-radius:8px; padding:8px 20px; font-size:13px; font-weight:700; }"
            "QPushButton:hover { background:#2A6674; }"
        )
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        self.pw_input.setFocus()

    def _on_save(self):
        pw = self.pw_input.text()
        confirm = self.confirm_input.text()

        if len(pw) < 4:
            self.error_label.setText("Password must be at least 4 characters.")
            self.error_label.setVisible(True)
            return

        if pw != confirm:
            self.error_label.setText("Passwords do not match.")
            self.error_label.setVisible(True)
            return

        self.service.set_password(pw)
        recovery_key = self.service.generate_recovery_key()

        QMessageBox.information(
            self,
            "Password Reset",
            f"Password has been reset successfully.\n\n"
            f"Your new recovery key:\n\n"
            f"    {recovery_key}\n\n"
            f"Write this down and keep it safe.\n"
            f"You will need it if you forget your password again."
        )
        self.accept()
