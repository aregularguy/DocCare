"""Settings page — clinic info, doctor details, logo upload, backup, security."""
import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from ...services.settings_service import SettingsService
from ...services.backup_service import BackupService


class SettingsWidget(QWidget):
    """Settings page with clinic + doctor info."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = SettingsService()
        self.backup_service = BackupService()
        self._logo_preview = None
        self._backup_status_label = None
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
        scroll.setStyleSheet("QScrollArea { background: #F4F7F8; }")

        body = QWidget()
        body.setStyleSheet("background: #F4F7F8;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(40, 32, 40, 40)
        bl.setSpacing(24)

        bl.addWidget(self._build_section("Clinic Information", [
            ("clinic_name_english", "Clinic Name (English)", "Enter clinic name in English"),
            ("clinic_name_marathi", "Clinic Name (Marathi)", "Enter clinic name in Marathi (optional)"),
            ("clinic_address",      "Address",               "Enter full clinic address"),
            ("clinic_phone",        "Phone / Mobile",        "Enter phone or mobile number"),
            ("clinic_timing",       "Clinic Timing",         "Enter clinic hours (optional)"),
        ]))

        bl.addWidget(self._build_section("Doctor Information", [
            ("doctor_name", "Doctor Full Name", "Enter doctor's full name"),
            ("degree",      "Degree",           "Enter degree (e.g. B.D.S)"),
            ("reg_number",  "Registration No.", "Enter registration number"),
        ]))

        bl.addWidget(self._build_logo_section())
        bl.addWidget(self._build_backup_section())
        bl.addWidget(self._build_cloud_backup_section())
        bl.addWidget(self._build_security_section())
        bl.addStretch()

        save_btn = QPushButton("💾  Save Settings")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(44)
        save_btn.setStyleSheet(
            "QPushButton { background:#1F4E5A; color:white; border:none;"
            " border-radius:8px; font-size:14px; font-weight:700; padding:0 32px; }"
            "QPushButton:hover { background:#2A6674; }"
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
            "stop:0 #1F4E5A, stop:1 #2A6674); }"
        )
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(32, 0, 32, 0)

        title = QLabel("⚙️  Settings")
        title.setFont(QFont("Ubuntu", 22, QFont.Weight.Bold))
        title.setStyleSheet("color:white; background:transparent;")
        bl.addWidget(title)
        bl.addStretch()

        sub = QLabel("Clinic & Doctor details auto-populate the prescription PDF")
        sub.setStyleSheet("color:#A9CBD2; font-size:13px; background:transparent;")
        bl.addWidget(sub)
        return banner

    def _build_section(self, title: str, fields: list) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:white; border:1px solid #DDE5E8;"
            " border-radius:12px; }"
        )
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(16)

        hdr = QLabel(title)
        hdr.setFont(QFont("Ubuntu", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#1F4E5A; border:none;")
        vl.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#DDE5E8; border:none; border-top:1px solid #DDE5E8;")
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
                "QLineEdit { border:1px solid #CFDADE; border-radius:7px;"
                " padding:0 12px; font-size:13px; background:white; }"
                "QLineEdit:focus { border:2px solid #1F4E5A; }"
            )
            self._fields[key] = inp
            row.addWidget(inp)
            vl.addLayout(row)

        return card

    def _build_logo_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:white; border:1px solid #DDE5E8;"
            " border-radius:12px; }"
        )
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(16)

        hdr = QLabel("🖼️  Clinic Logo")
        hdr.setFont(QFont("Ubuntu", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#1F4E5A; border:none;")
        vl.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#DDE5E8; border:none; border-top:1px solid #DDE5E8;")
        vl.addWidget(sep)

        row = QHBoxLayout()
        row.setSpacing(20)

        self._logo_preview = QLabel()
        self._logo_preview.setFixedSize(90, 90)
        self._logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_preview.setStyleSheet(
            "QLabel { border:2px dashed #C5D2D7; border-radius:45px;"
            " background:#F4F7F8; color:#8A989F; font-size:28px; }"
        )
        self._logo_preview.setText("🏥")
        row.addWidget(self._logo_preview)

        right = QVBoxLayout()
        right.setSpacing(8)

        info = QLabel("Upload a clinic logo — appears top-right of prescription PDF.\nRecommended: square image (PNG or JPG), min 200×200px.")
        info.setStyleSheet("color:#5B6B73; font-size:12px; border:none;")
        info.setWordWrap(True)
        right.addWidget(info)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        upload_btn = QPushButton("📁  Upload Logo")
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.setFixedHeight(36)
        upload_btn.setStyleSheet(
            "QPushButton { background:#E3F3F6; color:#2A6674; border:1px solid #B9DCE4;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 16px; }"
            "QPushButton:hover { background:#CDEAF0; }"
        )
        upload_btn.clicked.connect(self._upload_logo)
        btns.addWidget(upload_btn)

        remove_btn = QPushButton("🗑  Remove")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setFixedHeight(36)
        remove_btn.setStyleSheet(
            "QPushButton { background:#FBEBEA; color:#9E3B38; border:1px solid #FECACA;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 16px; }"
            "QPushButton:hover { background:#F8DEDD; }"
        )
        remove_btn.clicked.connect(self._remove_logo)
        btns.addWidget(remove_btn)
        btns.addStretch()

        right.addLayout(btns)
        row.addLayout(right)
        vl.addLayout(row)
        return card

    def _build_backup_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:white; border:1px solid #DDE5E8; border-radius:12px; }"
        )
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(14)

        hdr = QLabel("🗄️  Database Backup")
        hdr.setFont(QFont("Ubuntu", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#1F4E5A; border:none;")
        vl.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border:none; border-top:1px solid #DDE5E8;")
        vl.addWidget(sep)

        info = QLabel(
            "Keep your patient data safe. Backup creates a copy of your database file.\n"
            "Auto-backup runs every time the app starts (last 7 kept automatically)."
        )
        info.setStyleSheet("color:#5B6B73; font-size:12px; border:none;")
        info.setWordWrap(True)
        vl.addWidget(info)

        # DB size + last backup info
        db_size = self.backup_service.get_db_size()
        last = self.backup_service.get_last_backup_info()
        last_text = f"Last backup: {last['time']}" if last["exists"] else "Last backup: Never"

        self._backup_status_label = QLabel(f"Database size: {db_size}   ·   {last_text}")
        self._backup_status_label.setStyleSheet("color:#374151; font-size:12px; border:none;")
        vl.addWidget(self._backup_status_label)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        backup_btn = QPushButton("💾  Backup Now")
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.setFixedHeight(38)
        backup_btn.setStyleSheet(
            "QPushButton { background:#1F4E5A; color:white; border:none;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 18px; }"
            "QPushButton:hover { background:#2A6674; }"
        )
        backup_btn.clicked.connect(self._do_backup)
        btns.addWidget(backup_btn)

        open_folder_btn = QPushButton("📂  Open Backup Folder")
        open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_folder_btn.setFixedHeight(38)
        open_folder_btn.setStyleSheet(
            "QPushButton { background:#E3F3F6; color:#2A6674; border:1px solid #B9DCE4;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 16px; }"
            "QPushButton:hover { background:#CDEAF0; }"
        )
        open_folder_btn.clicked.connect(self._open_backup_folder)
        btns.addWidget(open_folder_btn)
        btns.addStretch()
        vl.addLayout(btns)

        # ── Restore & Merge row ──────────────────────────────────────
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("border:none; border-top:1px solid #DDE5E8;")
        vl.addWidget(sep2)

        restore_info = QLabel(
            "Restore a backup to replace current data, or import & merge "
            "records from another machine without losing existing data."
        )
        restore_info.setStyleSheet("color:#5B6B73; font-size:12px; border:none;")
        restore_info.setWordWrap(True)
        vl.addWidget(restore_info)

        btns2 = QHBoxLayout()
        btns2.setSpacing(10)

        restore_btn = QPushButton("Restore Backup")
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.setFixedHeight(38)
        restore_btn.setStyleSheet(
            "QPushButton { background:#FBEBEA; color:#9E3B38; border:1px solid #FECACA;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 18px; }"
            "QPushButton:hover { background:#F8DEDD; }"
        )
        restore_btn.clicked.connect(self._do_restore)
        btns2.addWidget(restore_btn)

        merge_btn = QPushButton("Import && Merge")
        merge_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        merge_btn.setFixedHeight(38)
        merge_btn.setStyleSheet(
            "QPushButton { background:#E3F3F6; color:#2A6674; border:1px solid #B9DCE4;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 18px; }"
            "QPushButton:hover { background:#CDEAF0; }"
        )
        merge_btn.clicked.connect(self._do_merge)
        btns2.addWidget(merge_btn)

        btns2.addStretch()
        vl.addLayout(btns2)
        return card

    def _build_cloud_backup_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:white; border:1px solid #DDE5E8; border-radius:12px; }"
        )
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(14)

        hdr = QLabel("Cloud Backup")
        hdr.setFont(QFont("Ubuntu", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#1F4E5A; border:none;")
        vl.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border:none; border-top:1px solid #DDE5E8;")
        vl.addWidget(sep)

        info = QLabel(
            "Choose a cloud-synced folder (Google Drive, OneDrive, Dropbox) for automatic backup.\n"
            "The app will copy the database to this folder every time it starts."
        )
        info.setStyleSheet("color:#5B6B73; font-size:12px; border:none;")
        info.setWordWrap(True)
        vl.addWidget(info)

        # Current folder status
        current_folder = self.service.get("cloud_backup_folder")
        if current_folder and os.path.isdir(current_folder):
            status_text = f"Folder: {current_folder}"
            status_color, status_bg, status_border = "#166534", "#F0FDF4", "#BBF7D0"
        elif current_folder:
            status_text = f"Folder not found: {current_folder}"
            status_color, status_bg, status_border = "#92400E", "#FFFBEB", "#FDE68A"
        else:
            status_text = "Not configured"
            status_color, status_bg, status_border = "#5B6B73", "#F4F7F8", "#DDE5E8"

        self._cloud_status = QLabel(status_text)
        self._cloud_status.setStyleSheet(
            f"color:{status_color}; background:{status_bg}; border:1px solid {status_border};"
            " border-radius:7px; padding:8px 12px; font-size:12px; font-weight:600;"
        )
        self._cloud_status.setWordWrap(True)
        vl.addWidget(self._cloud_status)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        choose_btn = QPushButton("Choose Folder")
        choose_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        choose_btn.setFixedHeight(38)
        choose_btn.setStyleSheet(
            "QPushButton { background:#1F4E5A; color:white; border:none;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 18px; }"
            "QPushButton:hover { background:#2A6674; }"
        )
        choose_btn.clicked.connect(self._choose_cloud_folder)
        btns.addWidget(choose_btn)

        if current_folder:
            remove_btn = QPushButton("Remove")
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setFixedHeight(38)
            remove_btn.setStyleSheet(
                "QPushButton { background:#FBEBEA; color:#9E3B38; border:1px solid #FECACA;"
                " border-radius:7px; font-size:13px; font-weight:600; padding:0 16px; }"
                "QPushButton:hover { background:#F8DEDD; }"
            )
            remove_btn.clicked.connect(self._remove_cloud_folder)
            btns.addWidget(remove_btn)

        btns.addStretch()
        vl.addLayout(btns)
        return card

    def _choose_cloud_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Cloud Backup Folder")
        if not folder:
            return
        self.service.save({"cloud_backup_folder": folder})
        QMessageBox.information(
            self, "Cloud Backup Configured",
            f"Cloud backup folder set to:\n{folder}\n\n"
            "The database will be backed up here on every app startup."
        )
        self.refresh_data()

    def _remove_cloud_folder(self):
        self.service.save({"cloud_backup_folder": ""})
        QMessageBox.information(self, "Removed", "Cloud backup folder has been removed.")
        self.refresh_data()

    def _build_security_section(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:white; border:1px solid #DDE5E8; border-radius:12px; }"
        )
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(14)

        hdr = QLabel("🔐  App Security")
        hdr.setFont(QFont("Ubuntu", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#1F4E5A; border:none;")
        vl.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border:none; border-top:1px solid #DDE5E8;")
        vl.addWidget(sep)

        is_set = self.service.is_password_set()
        status_text = "🔒 Password is set — app is locked on startup." if is_set else "🔓 No password set — anyone can open the app."
        status_color = "#166534" if is_set else "#92400E"
        status_bg    = "#F0FDF4" if is_set else "#FFFBEB"
        status_border = "#BBF7D0" if is_set else "#FDE68A"

        self._security_status = QLabel(status_text)
        self._security_status.setStyleSheet(
            f"color:{status_color}; background:{status_bg}; border:1px solid {status_border};"
            " border-radius:7px; padding:8px 12px; font-size:12px; font-weight:600;"
        )
        vl.addWidget(self._security_status)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        set_btn = QPushButton("🔑  Set / Change Password")
        set_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        set_btn.setFixedHeight(38)
        set_btn.setStyleSheet(
            "QPushButton { background:#1F4E5A; color:white; border:none;"
            " border-radius:7px; font-size:13px; font-weight:600; padding:0 18px; }"
            "QPushButton:hover { background:#2A6674; }"
        )
        set_btn.clicked.connect(self._set_password)
        btns.addWidget(set_btn)

        if is_set:
            remove_btn = QPushButton("🗑  Remove Password")
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setFixedHeight(38)
            remove_btn.setStyleSheet(
                "QPushButton { background:#FBEBEA; color:#9E3B38; border:1px solid #FECACA;"
                " border-radius:7px; font-size:13px; font-weight:600; padding:0 16px; }"
                "QPushButton:hover { background:#F8DEDD; }"
            )
            remove_btn.clicked.connect(self._remove_password)
            btns.addWidget(remove_btn)

        btns.addStretch()
        vl.addLayout(btns)
        return card

    # ── backup actions ────────────────────────────────────────────────────

    def _do_backup(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Backup Location")
        if not folder:
            return
        success, result = self.backup_service.backup_now(folder)
        if success:
            # Update status label
            last = self.backup_service.get_last_backup_info()
            db_size = self.backup_service.get_db_size()
            if self._backup_status_label:
                last_text = f"Last backup: {last['time']}" if last["exists"] else "Last backup: Never"
                self._backup_status_label.setText(f"Database size: {db_size}   ·   {last_text}")
            QMessageBox.information(
                self, "Backup Successful",
                f"✅ Backup saved to:\n{result}"
            )
        else:
            QMessageBox.warning(self, "Backup Failed", f"❌ {result}")

    def _open_backup_folder(self):
        import sys
        if getattr(sys, 'frozen', False):
            data_dir = os.path.join(os.path.dirname(sys.executable), "data")
        else:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))))), "data"
            )
        backup_dir = os.path.join(data_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        import subprocess, sys as _sys
        if _sys.platform == "win32":
            os.startfile(backup_dir)
        elif _sys.platform == "darwin":
            subprocess.Popen(["open", backup_dir])
        else:
            subprocess.Popen(["xdg-open", backup_dir])

    # ── restore & merge actions ──────────────────────────────────────────

    def _do_restore(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "SQLite Database (*.db)"
        )
        if not path:
            return

        ok, msg = BackupService._validate_dentnest_db(path)
        if not ok:
            QMessageBox.warning(self, "Invalid File", f"Cannot restore:\n{msg}")
            return

        counts = BackupService._get_record_counts(path)
        preview = "\n".join(f"  {t}: {c} records" for t, c in counts.items())

        reply = QMessageBox.warning(
            self, "Confirm Restore",
            f"This will REPLACE all current data with:\n\n{preview}\n\n"
            "A safety backup of your current database will be created first.\n\n"
            "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success, result = self.backup_service.restore_backup(path)
        if success:
            QMessageBox.information(
                self, "Restore Successful",
                "Database restored successfully!\nAll pages will now refresh."
            )
            self._refresh_all_app_pages()
        else:
            QMessageBox.critical(self, "Restore Failed", f"Error: {result}")

    def _do_merge(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Database to Import", "", "SQLite Database (*.db)"
        )
        if not path:
            return

        ok, msg = BackupService._validate_dentnest_db(path)
        if not ok:
            QMessageBox.warning(self, "Invalid File", f"Cannot import:\n{msg}")
            return

        counts = BackupService._get_record_counts(path)
        preview = "\n".join(f"  {t}: {c} records" for t, c in counts.items())

        reply = QMessageBox.question(
            self, "Confirm Import & Merge",
            f"Source database contains:\n\n{preview}\n\n"
            "Only NEW records will be imported. Existing data will NOT be changed.\n"
            "A safety backup will be created first.\n\n"
            "Proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success, result = self.backup_service.smart_merge(path)
        if success:
            summary = "\n".join(
                f"  {t}: {c} imported" for t, c in result.items() if c > 0
            )
            if not summary:
                summary = "  No new records found — databases already in sync."
            QMessageBox.information(
                self, "Import Complete",
                f"Merge finished!\n\n{summary}"
            )
            self._refresh_all_app_pages()
        else:
            QMessageBox.critical(
                self, "Import Failed",
                f"Error: {result.get('error', 'Unknown error')}"
            )

    def _refresh_all_app_pages(self):
        main_window = self.window()
        if hasattr(main_window, 'refresh_all_pages'):
            main_window.refresh_all_pages()

    # ── security actions ──────────────────────────────────────────────────

    def _set_password(self):
        new_pw, ok = QInputDialog.getText(
            self, "Set Password", "Enter new password:",
            QLineEdit.EchoMode.Password
        )
        if not ok or not new_pw.strip():
            return
        confirm, ok2 = QInputDialog.getText(
            self, "Confirm Password", "Re-enter new password:",
            QLineEdit.EchoMode.Password
        )
        if not ok2:
            return
        if new_pw != confirm:
            QMessageBox.warning(self, "Mismatch", "Passwords do not match.")
            return
        if len(new_pw) < 4:
            QMessageBox.warning(self, "Too Short", "Password must be at least 4 characters.")
            return
        self.service.set_password(new_pw)
        recovery_key = self.service.generate_recovery_key()
        QMessageBox.information(
            self, "Password Set",
            f"Password set successfully!\n"
            f"The app will ask for this password on next startup.\n\n"
            f"Your recovery key:\n\n"
            f"    {recovery_key}\n\n"
            f"Write this down and keep it safe.\n"
            f"You will need it if you forget your password."
        )
        self.refresh_data()

    def _remove_password(self):
        current, ok = QInputDialog.getText(
            self, "Remove Password", "Enter current password to confirm removal:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return
        if not self.service.verify_password(current):
            QMessageBox.warning(self, "Wrong Password", "❌ Incorrect password.")
            return
        self.service.set_password("")
        QMessageBox.information(self, "Password Removed", "🔓 Password removed. App will open without a lock.")
        self.refresh_data()

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
            "QLabel { border:2px solid #B9DCE4; border-radius:45px; background:#EEF7F9; }"
        )

    def refresh_data(self):
        self._load_values()
