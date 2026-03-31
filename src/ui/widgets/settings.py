"""Settings page — clinic info, doctor details, logo upload."""
import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from ...services.settings_service import SettingsService


class SettingsWidget(QWidget):
    """Settings page with clinic + doctor info."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = SettingsService()
        self._logo_preview = None
        self.init_ui()

    # ── init ─────────────────────────────────────────────────────────────

    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_banner())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #F8FAFC; }")

        body = QWidget()
        body.setStyleSheet("background: #F8FAFC;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(40, 32, 40, 40)
        bl.setSpacing(24)

        bl.addWidget(self._build_section("🏥  Clinic Information", [
            ("clinic_name_english", "Clinic Name (English)", "e.g. Dr. Abrar's Dental Care and Implant Centre"),
            ("clinic_name_marathi", "Clinic Name (Marathi)", "e.g. दातांचा दवाखाना  (optional)"),
            ("clinic_address",      "Address",               "e.g. Plot 12, Main Road, Phaltan, Maharashtra"),
            ("clinic_phone",        "Phone / Mobile",        "e.g. 7620962937 / 7588606132"),
            ("clinic_timing",       "Clinic Timing",         "e.g. सकाळी ९ ते दुपारी २  |  सायं. ५ ते रात्री ८  (optional)"),
        ]))

        bl.addWidget(self._build_section("👨‍⚕️  Doctor Information", [
            ("doctor_name", "Doctor Full Name", "e.g. Dr. Abrar Pharuk Shaikh"),
            ("degree",      "Degree",           "e.g. B.D.S (RGUHS)"),
            ("reg_number",  "Registration No.", "e.g. A-51710"),
        ]))

        bl.addWidget(self._build_logo_section())
        bl.addStretch()

        save_btn = QPushButton("💾  Save Settings")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(44)
        save_btn.setStyleSheet(
            "QPushButton { background:#0F2942; color:white; border:none;"
            " border-radius:8px; font-size:14px; font-weight:700; padding:0 32px; }"
            "QPushButton:hover { background:#1A4A7A; }"
        )
        save_btn.clicked.connect(self._save)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        bl.addLayout(btn_row)

        scroll.setWidget(body)
        root.addWidget(scroll)

        self._load_values()

    def _build_banner(self):
        banner = QFrame()
        banner.setFixedHeight(100)
        banner.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #0F2942, stop:1 #1A4A7A); }"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(32, 0, 32, 0)

        title = QLabel("⚙️  Settings")
        title.setFont(QFont("Ubuntu", 22, QFont.Weight.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        bl.addWidget(title)
        bl.addStretch()

        sub = QLabel("Clinic & Doctor details auto-populate the prescription PDF")
        sub.setStyleSheet("color:#93C5FD; font-size:13px; background:transparent;")
        bl.addWidget(sub)
        return banner

    def _build_section(self, title: str, fields: list) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:white; border:1px solid #E2E8F0;"
            " border-radius:12px; }"
        )
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(16)

        hdr = QLabel(title)
        hdr.setFont(QFont("Ubuntu", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#0F2942; border:none;")
        vl.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#E2E8F0; border:none; border-top:1px solid #E2E8F0;")
        vl.addWidget(sep)

        self._fields = getattr(self, '_fields', {})
        for key, label, placeholder in fields:
            row = QVBoxLayout()
            row.setSpacing(4)

            lbl = QLabel(label)
            lbl.setStyleSheet("color:#374151; font-size:13px; font-weight:600; border:none;")
            row.addWidget(lbl)

            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(40)
            inp.setStyleSheet(
                "QLineEdit { border:1px solid #D1D5DB; border-radius:7px;"
                " padding:0 12px; font-size:13px; background:white; }"
                "QLineEdit:focus { border:2px solid #0F2942; }"
            )
            self._fields[key] = inp
            row.addWidget(inp)
            vl.addLayout(row)

        return card

    def _build_logo_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:white; border:1px solid #E2E8F0;"
            " border-radius:12px; }"
        )
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(16)

        hdr = QLabel("🖼️  Clinic Logo")
        hdr.setFont(QFont("Ubuntu", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#0F2942; border:none;")
        vl.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#E2E8F0; border:none; border-top:1px solid #E2E8F0;")
        vl.addWidget(sep)

        row = QHBoxLayout()
        row.setSpacing(20)

        self._logo_preview = QLabel()
        self._logo_preview.setFixedSize(90, 90)
        self._logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_preview.setStyleSheet(
            "QLabel { border:2px dashed #CBD5E1; border-radius:45px;"
            " background:#F8FAFC; color:#94A3B8; font-size:28px; }"
        )
        self._logo_preview.setText("🏥")
        row.addWidget(self._logo_preview)

        right = QVBoxLayout()
        right.setSpacing(8)

        info = QLabel("Upload a clinic logo — appears top-right of prescription PDF.\nRecommended: square image (PNG or JPG), min 200×200px.")
        info.setStyleSheet("color:#64748B; font-size:12px; border:none;")
        info.setWordWrap(True)
        right.addWidget(info)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        upload_btn = QPushButton("📁  Upload Logo")
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.setFixedHeight(36)
        upload_btn.setStyleSheet(
            "QPushButton { background:#EFF6FF; color:#1A4A7A; border:1px solid #BFDBFE;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 16px; }"
            "QPushButton:hover { background:#DBEAFE; }"
        )
        upload_btn.clicked.connect(self._upload_logo)
        btns.addWidget(upload_btn)

        remove_btn = QPushButton("🗑  Remove")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setFixedHeight(36)
        remove_btn.setStyleSheet(
            "QPushButton { background:#FEF2F2; color:#991B1B; border:1px solid #FECACA;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 16px; }"
            "QPushButton:hover { background:#FEE2E2; }"
        )
        remove_btn.clicked.connect(self._remove_logo)
        btns.addWidget(remove_btn)
        btns.addStretch()

        right.addLayout(btns)
        row.addLayout(right)
        vl.addLayout(row)
        return card

    # ── data ─────────────────────────────────────────────────────────────

    def _load_values(self):
        data = self.service.get_all()
        for key, inp in self._fields.items():
            inp.setText(data.get(key, ""))
        logo = data.get("logo_path", "")
        if logo and os.path.exists(logo):
            self._set_logo_preview(logo)

    def _save(self):
        data = {key: inp.text().strip() for key, inp in self._fields.items()}
        # keep existing logo_path
        data["logo_path"] = self.service.get("logo_path")
        if self.service.save(data):
            QMessageBox.information(self, "Saved", "✅ Settings saved successfully!\nPrescription PDFs will now use these details.")
        else:
            QMessageBox.warning(self, "Error", "❌ Failed to save settings.")

    def _upload_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Clinic Logo", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return
        dest_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))))), "data"
        )
        os.makedirs(dest_dir, exist_ok=True)
        ext = os.path.splitext(path)[1]
        dest = os.path.join(dest_dir, f"clinic_logo{ext}")
        shutil.copy2(path, dest)
        current = {k: v.text().strip() for k, v in self._fields.items()}
        current["logo_path"] = dest
        self.service.save(current)
        self._set_logo_preview(dest)
        QMessageBox.information(self, "Logo Uploaded", "✅ Logo saved! It will appear on your prescription PDFs.")

    def _remove_logo(self):
        current = {k: v.text().strip() for k, v in self._fields.items()}
        current["logo_path"] = ""
        self.service.save(current)
        self._logo_preview.setPixmap(QPixmap())
        self._logo_preview.setText("🏥")

    def _set_logo_preview(self, path: str):
        pix = QPixmap(path).scaled(
            86, 86,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._logo_preview.setPixmap(pix)
        self._logo_preview.setStyleSheet(
            "QLabel { border:2px solid #BFDBFE; border-radius:45px; background:#F0F9FF; }"
        )

    def refresh_data(self):
        self._load_values()
