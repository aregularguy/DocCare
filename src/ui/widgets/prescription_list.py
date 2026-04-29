"""Medicine catalog management widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QDialog, QFormLayout, QComboBox,
    QMessageBox, QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from ...services.prescription_service import PrescriptionService

MEDICINE_TYPES = [
    "Tablet", "Capsule", "Liquid", "Gel", "Mouthwash",
    "Drops", "Paste", "Powder", "Injection", "Other",
]


class AddMedicineDialog(QDialog):
    """Dialog for adding a new medicine."""

    def __init__(self, prescription_service, parent=None):
        super().__init__(parent)
        self.prescription_service = prescription_service
        self.setWindowTitle("Add Medicine")
        self.setMinimumWidth(440)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        title = QLabel("Add Medicine")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #0F2942; margin-bottom: 4px;")
        layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #E5E5EA; max-height: 1px;")
        layout.addWidget(separator)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Amoxicillin 500mg")
        form.addRow("Medicine Name *:", self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems(MEDICINE_TYPES)
        form.addRow("Type:", self.type_combo)

        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("Brand name (optional)")
        form.addRow("Brand Name:", self.brand_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("e.g. 500mg, 10ml")
        form.addRow("Quantity:", self.quantity_input)

        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Medicine")
        save_btn.setObjectName("primary_button")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            self._show_error("Medicine name is required.")
            return

        medicine_type = self.type_combo.currentText().lower()
        brand_name = self.brand_input.text().strip() or None
        quantity = self.quantity_input.text().strip() or None

        success, message, _ = self.prescription_service.add_medicine(
            name=name,
            medicine_type=medicine_type,
            brand_name=brand_name,
            common_dosage=quantity,
        )

        if success:
            self.accept()
        else:
            self._show_error(message)

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)


class EditMedicineDialog(QDialog):
    """Dialog for editing an existing medicine."""

    def __init__(self, prescription_service, medicine, parent=None):
        super().__init__(parent)
        self.prescription_service = prescription_service
        self.medicine = medicine
        self.setWindowTitle("Edit Medicine")
        self.setMinimumWidth(440)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        title = QLabel("Edit Medicine")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #0F2942; margin-bottom: 4px;")
        layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #E5E5EA; max-height: 1px;")
        layout.addWidget(separator)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setText(self.medicine.name)
        form.addRow("Medicine Name *:", self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems(MEDICINE_TYPES)
        # Pre-select matching type
        current_type = (self.medicine.medicine_type or "").capitalize()
        idx = self.type_combo.findText(current_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        form.addRow("Type:", self.type_combo)

        self.brand_input = QLineEdit()
        self.brand_input.setText(self.medicine.brand_name or "")
        form.addRow("Brand Name:", self.brand_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setText(self.medicine.common_dosage or "")
        form.addRow("Quantity:", self.quantity_input)

        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("primary_button")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            self._show_error("Medicine name is required.")
            return

        medicine_type = self.type_combo.currentText().lower()
        brand_name = self.brand_input.text().strip() or None
        quantity = self.quantity_input.text().strip() or None

        success, message = self.prescription_service.update_medicine(
            medicine_id=self.medicine.id,
            name=name,
            medicine_type=medicine_type,
            brand_name=brand_name,
            common_dosage=quantity,
        )

        if success:
            self.accept()
        else:
            self._show_error(message)

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)


class PrescriptionListWidget(QWidget):
    """Medicine catalog management page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prescription_service = PrescriptionService()
        self._all_medicines = []
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Banner
        banner = QFrame()
        banner.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #0F2942, stop:0.6 #1A4A7A, stop:1 #1E6FA8);"
            " border-radius: 14px; }"
        )
        banner.setFixedHeight(110)

        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(28, 0, 28, 0)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)

        banner_title = QLabel("Medicine Catalog")
        banner_title.setStyleSheet(
            "color: #FFFFFF; font-size: 22px; font-weight: 700; background: transparent;"
        )
        left_layout.addWidget(banner_title)

        banner_sub = QLabel("Manage your medicine inventory")
        banner_sub.setStyleSheet(
            "color: #94B8D4; font-size: 13px; background: transparent;"
        )
        left_layout.addWidget(banner_sub)
        banner_layout.addLayout(left_layout)
        banner_layout.addStretch()

        self.total_badge = QLabel("0 medicines")
        self.total_badge.setStyleSheet(
            "color: #FFFFFF; font-size: 13px; font-weight: 600;"
            " background: rgba(255,255,255,0.12); border-radius: 8px;"
            " padding: 6px 14px;"
        )
        banner_layout.addWidget(self.total_badge)

        add_btn = QPushButton("+  Add Medicine")
        add_btn.setObjectName("primary_button")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(
            "QPushButton { background-color: #38BDF8; color: #0F2942; border: none;"
            " border-radius: 8px; padding: 0 20px; font-weight: 700; font-size: 13px; }"
            "QPushButton:hover { background-color: #7DD3FC; }"
        )
        add_btn.clicked.connect(self._open_add_dialog)
        banner_layout.addWidget(add_btn)

        layout.addWidget(banner)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search medicines by name...")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(
            "QLineEdit { border: 1px solid #D2D2D7; border-radius: 8px;"
            " padding: 0 12px; font-size: 13px; }"
            "QLineEdit:focus { border-color: #007AFF; }"
        )
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        columns = ["Medicine Name", "Type", "Brand Name", "Quantity", "Actions"]
        self.table = QTableWidget(0, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.table)

        # Empty state
        self.empty_label = QLabel("No medicines found.\nClick '+ Add Medicine' to add one.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color: #86868B; font-size: 15px; padding: 60px;"
        )
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

    def refresh_data(self):
        """Load all medicines from the database."""
        self._all_medicines = self.prescription_service.get_all_medicines()
        self._render_table(self._all_medicines)

    def _render_table(self, medicines):
        """Render the given list of medicines into the table."""
        self.table.setRowCount(0)

        for med in medicines:
            self._add_table_row(med)

        total = len(medicines)
        has_data = total > 0
        self.table.setVisible(has_data)
        self.empty_label.setVisible(not has_data)
        self.total_badge.setText(f"{total} medicine{'s' if total != 1 else ''}")

    def _add_table_row(self, medicine):
        """Insert one row into the table."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Medicine Name (bold)
        name_item = QTableWidgetItem(medicine.name)
        name_item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        name_item.setForeground(QColor("#0F2942"))
        self.table.setItem(row, 0, name_item)

        # Type
        type_text = (medicine.medicine_type or "").capitalize()
        self.table.setItem(row, 1, QTableWidgetItem(type_text))

        # Brand Name
        self.table.setItem(row, 2, QTableWidgetItem(medicine.brand_name or ""))

        # Quantity (common_dosage)
        self.table.setItem(row, 3, QTableWidgetItem(medicine.common_dosage or ""))

        # Actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 2, 4, 2)
        actions_layout.setSpacing(6)

        edit_btn = QPushButton("Edit")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setFixedSize(60, 30)
        edit_btn.setStyleSheet(
            "QPushButton { background-color: #007AFF; color: white; border: none;"
            " border-radius: 6px; font-size: 12px; font-weight: 600; }"
            "QPushButton:hover { background-color: #0051D5; }"
        )
        edit_btn.clicked.connect(lambda checked, m=medicine: self._open_edit_dialog(m))
        actions_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setFixedSize(60, 30)
        delete_btn.setStyleSheet(
            "QPushButton { background-color: #FF3B30; color: white; border: none;"
            " border-radius: 6px; font-size: 12px; font-weight: 600; }"
            "QPushButton:hover { background-color: #D32F2F; }"
        )
        delete_btn.clicked.connect(lambda checked, m=medicine: self._on_delete(m))
        actions_layout.addWidget(delete_btn)

        self.table.setCellWidget(row, 4, actions_widget)

    def _on_search(self, text: str):
        """Filter table rows by medicine name."""
        query = text.strip().lower()
        if not query:
            self._render_table(self._all_medicines)
            return

        filtered = [m for m in self._all_medicines if query in m.name.lower()]
        self._render_table(filtered)

    def _open_add_dialog(self):
        dialog = AddMedicineDialog(self.prescription_service, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            QMessageBox.information(self, "Success", "Medicine added successfully.")

    def _open_edit_dialog(self, medicine):
        # Re-fetch to get latest data
        fresh = self.prescription_service.get_medicine(medicine.id)
        if not fresh:
            QMessageBox.warning(self, "Error", "Medicine not found.")
            return

        dialog = EditMedicineDialog(self.prescription_service, fresh, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            QMessageBox.information(self, "Success", "Medicine updated successfully.")

    def _on_delete(self, medicine):
        reply = QMessageBox.question(
            self,
            "Delete Medicine",
            f"Are you sure you want to delete '{medicine.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success, message = self.prescription_service.delete_medicine(medicine.id)
        if success:
            self.refresh_data()
        else:
            QMessageBox.warning(self, "Error", message)
