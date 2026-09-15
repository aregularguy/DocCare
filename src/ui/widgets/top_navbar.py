"""Top navigation bar widget."""
import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QFileDialog, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QFont


LOGO_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'clinic_logo.png')
)


class LogoButton(QLabel):
    """Clickable logo — shows image or purple initials placeholder."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to upload clinic logo")
        self._load_logo()

    def _load_logo(self):
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH).scaled(
                40, 40,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._set_rounded(pix)
        else:
            self._set_placeholder()

    def _set_rounded(self, pix):
        rounded = QPixmap(40, 40)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, 40, 40, 8, 8)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pix)
        painter.end()
        self.setPixmap(rounded)

    def _set_placeholder(self):
        pix = QPixmap(40, 40)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#4E4F8F")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 40, 40, 8, 8)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "DN")
        painter.end()
        self.setPixmap(pix)

    def mousePressEvent(self, event):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Clinic Logo", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            os.makedirs(os.path.dirname(LOGO_PATH), exist_ok=True)
            shutil.copy(path, LOGO_PATH)
            self._load_logo()


class TopNavBar(QFrame):
    """Top navigation bar for DentNest."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setStyleSheet(
            "QFrame { background: #FFFFFF;"
            " border-bottom: 1px solid #DDE5E8; }"
        )
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # ── Left: logo + app name ──
        self.logo_btn = LogoButton()
        layout.addWidget(self.logo_btn)

        app_name = QLabel("DentNest")
        app_name.setStyleSheet(
            "color: #1E2B32; font-size: 16px; font-weight: 700;"
            " background: transparent; border: none;"
        )
        layout.addWidget(app_name)

        layout.addSpacing(20)

        # ── Center: search ──
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍   Search patients...")
        self.search.setFixedHeight(36)
        self.search.setMaximumWidth(340)
        self.search.setStyleSheet(
            "QLineEdit { background: #EEF3F4; border: 1px solid #DDE5E8;"
            " border-radius: 8px; padding: 0 14px; font-size: 13px;"
            " color: #1E2B32; }"
            "QLineEdit:focus { border: 1.5px solid #1F8A9E; background: white; }"
        )
        layout.addWidget(self.search, stretch=1)

        layout.addStretch()

        # ── Right: doctor profile button ──
        self.profile_btn = QPushButton("👤   Dr. Name  ▾")
        self.profile_btn.setStyleSheet(
            "QPushButton { background: #EEEFF8; color: #4E4F8F;"
            " border: 1px solid #D6D8EE; border-radius: 8px;"
            " padding: 6px 14px; font-size: 13px; font-weight: 600; }"
            "QPushButton:hover { background: #E3F3F6; }"
            "QPushButton::menu-indicator { image: none; }"
        )
        self.profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.profile_btn.clicked.connect(self._show_profile_menu)
        layout.addWidget(self.profile_btn)

    def _show_profile_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background: white; border: 1px solid #DDE5E8;"
            " border-radius: 8px; padding: 4px; }"
            "QMenu::item { padding: 10px 20px; font-size: 13px;"
            " color: #1E2B32; border-radius: 4px; }"
            "QMenu::item:selected { background: #EEEFF8; color: #4E4F8F; }"
        )
        menu.addAction("👤  Profile")
        menu.addAction("⚙️  Settings")
        menu.addSeparator()
        menu.addAction("🚪  Exit")
        menu.exec(self.profile_btn.mapToGlobal(
            self.profile_btn.rect().bottomLeft()
        ))
