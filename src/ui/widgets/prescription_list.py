"""Prescription list and management widget."""
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QDialog, QFormLayout, QComboBox,
    QMessageBox, QCompleter, QDialogButtonBox, QScrollArea,
    QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QFont, QColor
from ...services.patient_service import PatientService
from ...services.treatment_service import TreatmentService
from ...services.prescription_service import PrescriptionService


class AddPrescriptionDialog(QDialog):
    """Dialog for adding a new prescription."""

    def __init__(self, patient_service, treatment_service, prescription_service, parent=None):
        super().__init__(parent)
        self.patient_service = patient_service
        self.treatment_service = treatment_service
        self.prescription_service = prescription_service
        self.selected_patient = None
        self.selected_treatment = None
        self.setWindowTitle("Add Prescription")
        self.setMinimumWidth(520)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        # Title
        title = QLabel("💊 New Prescription")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1F4E5A; margin-bottom: 4px;")
        layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #DDE5E8; max-height: 1px;")
        layout.addWidget(separator)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # --- Patient search ---
        patient_search_layout = QVBoxLayout()
        patient_search_layout.setSpacing(4)

        self.patient_search = QLineEdit()
        self.patient_search.setPlaceholderText("Type patient name or mobile…")
        self.patient_search.textChanged.connect(self._on_patient_search)
        patient_search_layout.addWidget(self.patient_search)

        self.patient_results = QTableWidget(0, 2)
        self.patient_results.setHorizontalHeaderLabels(["Name", "Mobile"])
        self.patient_results.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.patient_results.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.patient_results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.patient_results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.patient_results.setMaximumHeight(130)
        self.patient_results.setVisible(False)
        self.patient_results.itemSelectionChanged.connect(self._on_patient_selected)
        patient_search_layout.addWidget(self.patient_results)

        self.selected_patient_label = QLabel("No patient selected")
        self.selected_patient_label.setStyleSheet("color: #5B6B73; font-size: 12px;")
        patient_search_layout.addWidget(self.selected_patient_label)

        patient_container = QWidget()
        patient_container.setLayout(patient_search_layout)
        form.addRow("Patient *:", patient_container)

        # --- Treatment ---
        self.treatment_combo = QComboBox()
        self.treatment_combo.setPlaceholderText("Select patient first")
        self.treatment_combo.setEnabled(False)
        form.addRow("Treatment *:", self.treatment_combo)

        # --- Medicine ---
        medicine_layout = QVBoxLayout()
        medicine_layout.setSpacing(4)

        self.medicine_combo = QComboBox()
        self.medicine_combo.setEditable(True)
        self.medicine_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.medicine_combo.lineEdit().setPlaceholderText("Search or select medicine…")

        medicines = self.prescription_service.get_all_medicines()
        self._medicine_map = {}
        medicine_names = []
        for m in medicines:
            display = f"{m.name}  [{m.category or ''}]" if m.category else m.name
            self.medicine_combo.addItem(display, userData=m.name)
            medicine_names.append(display)
            self._medicine_map[display] = m.name

        completer = QCompleter(medicine_names, self)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.medicine_combo.setCompleter(completer)
        medicine_layout.addWidget(self.medicine_combo)

        medicine_container = QWidget()
        medicine_container.setLayout(medicine_layout)
        form.addRow("Medicine *:", medicine_container)

        # --- Dosage ---
        self.dosage_input = QLineEdit()
        self.dosage_input.setPlaceholderText("e.g. 500mg, 1 tablet")
        form.addRow("Dosage:", self.dosage_input)

        # --- Frequency ---
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems([
            "Once daily",
            "Twice daily",
            "Three times daily",
            "Four times daily",
            "As needed",
            "Before meals",
            "After meals",
            "At bedtime",
        ])
        form.addRow("Frequency:", self.frequency_combo)

        # --- Duration ---
        self.duration_combo = QComboBox()
        self.duration_combo.addItems([
            "3 days",
            "5 days",
            "7 days",
            "10 days",
            "14 days",
            "21 days",
            "1 month",
            "As directed",
        ])
        form.addRow("Duration:", self.duration_combo)

        # --- Notes ---
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Additional notes (optional)")
        form.addRow("Notes:", self.notes_input)

        layout.addLayout(form)

        # Error label
        self.error_label = QLabel()
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾  Save Prescription")
        save_btn.setObjectName("primary_button")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_patient_search(self, text: str):
        """Filter patients as user types."""
        if not text.strip():
            self.patient_results.setVisible(False)
            return

        patients = self.patient_service.search_patients(text.strip())
        self.patient_results.setRowCount(0)
        for p in patients[:8]:
            row = self.patient_results.rowCount()
            self.patient_results.insertRow(row)
            name_item = QTableWidgetItem(p.name)
            name_item.setData(Qt.ItemDataRole.UserRole, p)
            self.patient_results.setItem(row, 0, name_item)
            self.patient_results.setItem(row, 1, QTableWidgetItem(p.mobile_number or ""))

        self.patient_results.setVisible(len(patients) > 0)

    def _on_patient_selected(self):
        """Handle patient selection from results table."""
        rows = self.patient_results.selectedItems()
        if not rows:
            return

        row = self.patient_results.currentRow()
        item = self.patient_results.item(row, 0)
        if not item:
            return

        patient = item.data(Qt.ItemDataRole.UserRole)
        self.selected_patient = patient
        self.patient_search.setText(patient.name)
        self.patient_results.setVisible(False)
        self.selected_patient_label.setText(
            f"✓ {patient.name}  |  📱 {patient.mobile_number or 'N/A'}"
        )
        self.selected_patient_label.setStyleSheet("color: #2E9E6B; font-size: 12px; font-weight: 600;")

        # Load treatments for this patient
        self._load_treatments(patient.id)

    def _load_treatments(self, patient_id: int):
        """Load treatments for the selected patient."""
        self.treatment_combo.clear()
        self._treatment_list = []
        treatments = self.treatment_service.get_patient_treatments(patient_id)
        if treatments:
            for t in treatments:
                label = t.treatment_type_name or f"Treatment #{t.id}"
                if t.start_date:
                    label += f"  ({t.start_date.strftime('%d %b %Y')})"
                self.treatment_combo.addItem(label, userData=t)
                self._treatment_list.append(t)
            self.treatment_combo.setEnabled(True)
        else:
            self.treatment_combo.addItem("No treatments found")
            self.treatment_combo.setEnabled(False)

    def _get_selected_medicine_name(self) -> str:
        """Extract raw medicine name from combo selection."""
        idx = self.medicine_combo.currentIndex()
        if idx >= 0:
            user_data = self.medicine_combo.itemData(idx)
            if user_data:
                return user_data
        # Fallback: use typed text, strip category suffix
        text = self.medicine_combo.currentText().strip()
        if "  [" in text:
            return text.split("  [")[0].strip()
        return text

    def _on_save(self):
        """Validate and save the prescription."""
        # Validate patient
        if not self.selected_patient:
            self._show_error("Please select a patient.")
            return

        # Validate treatment
        if not self.treatment_combo.isEnabled() or self.treatment_combo.count() == 0:
            self._show_error("No treatment available for this patient.")
            return

        treatment = self.treatment_combo.currentData()
        if not treatment:
            self._show_error("Please select a valid treatment.")
            return

        # Validate medicine
        medicine_name = self._get_selected_medicine_name()
        if not medicine_name:
            self._show_error("Please select or enter a medicine.")
            return

        dosage = self.dosage_input.text().strip() or None
        frequency = self.frequency_combo.currentText()
        duration = self.duration_combo.currentText()
        notes = self.notes_input.text().strip() or None

        success, message, _ = self.prescription_service.add_prescription(
            treatment_id=treatment.id,
            medicine_name=medicine_name,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
            prescribed_date=date.today(),
            notes=notes,
        )

        if success:
            self.accept()
        else:
            self._show_error(message)

    def _show_error(self, message: str):
        self.error_label.setText(f"⚠  {message}")
        self.error_label.setVisible(True)


class PrescriptionListWidget(QWidget):
    """Full prescriptions management page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_service = PatientService()
        self.treatment_service = TreatmentService()
        self.prescription_service = PrescriptionService()
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Hero Banner ──────────────────────────────────────────────
        banner = QFrame()
        banner.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #1F4E5A, stop:0.6 #2A6674, stop:1 #3A8C99);"
            " border-radius: 14px; }"
        )
        banner.setFixedHeight(110)

        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(28, 0, 28, 0)

        # Left: icon + text
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)

        banner_title = QLabel("💊  Prescriptions")
        banner_title.setStyleSheet(
            "color: #FFFFFF; font-size: 22px; font-weight: 700; background: transparent;"
        )
        left_layout.addWidget(banner_title)

        banner_sub = QLabel("Manage patient prescriptions and medicines")
        banner_sub.setStyleSheet(
            "color: #A9CBD2; font-size: 13px; background: transparent;"
        )
        left_layout.addWidget(banner_sub)
        banner_layout.addLayout(left_layout)
        banner_layout.addStretch()

        # Right: stats badge
        self.total_badge = QLabel("0 prescriptions")
        self.total_badge.setStyleSheet(
            "color: #FFFFFF; font-size: 13px; font-weight: 600;"
            " background: rgba(255,255,255,0.12); border-radius: 8px;"
            " padding: 6px 14px;"
        )
        banner_layout.addWidget(self.total_badge)

        # Right: Add button
        add_btn = QPushButton("＋  Add Prescription")
        add_btn.setObjectName("primary_button")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(
            "QPushButton { background-color: #3AA9BA; color: #1F4E5A; border: none;"
            " border-radius: 8px; padding: 0 20px; font-weight: 700; font-size: 13px; }"
            "QPushButton:hover { background-color: #A9CBD2; }"
        )
        add_btn.clicked.connect(self._open_add_dialog)
        banner_layout.addWidget(add_btn)

        layout.addWidget(banner)

        # ── Table ────────────────────────────────────────────────────
        columns = ["Patient", "Treatment", "Medicine", "Dosage", "Frequency", "Duration", "Date"]
        self.table = QTableWidget(0, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.table)

        # ── Empty state label ────────────────────────────────────────
        self.empty_label = QLabel("No prescriptions yet.\nClick '＋ Add Prescription' to add one.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color: #5B6B73; font-size: 15px; padding: 60px;"
        )
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

    def refresh_data(self):
        """Load all prescriptions from all patients and treatments."""
        self.table.setRowCount(0)
        total = 0

        try:
            patients = self.patient_service.get_all_patients()
            for patient in patients:
                treatments = self.treatment_service.get_patient_treatments(patient.id)
                for treatment in treatments:
                    prescriptions = self.prescription_service.get_treatment_prescriptions(treatment.id)
                    for rx in prescriptions:
                        self._add_table_row(patient, treatment, rx)
                        total += 1
        except Exception:
            pass

        has_data = total > 0
        self.table.setVisible(has_data)
        self.empty_label.setVisible(not has_data)
        self.total_badge.setText(f"{total} prescription{'s' if total != 1 else ''}")

    def _add_table_row(self, patient, treatment, prescription):
        """Insert one row into the prescriptions table."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Patient name (bold)
        patient_item = QTableWidgetItem(patient.name)
        patient_item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        patient_item.setForeground(QColor("#1F4E5A"))
        self.table.setItem(row, 0, patient_item)

        # Treatment
        treatment_name = treatment.treatment_type_name or f"Treatment #{treatment.id}"
        self.table.setItem(row, 1, QTableWidgetItem(treatment_name))

        # Medicine
        med_item = QTableWidgetItem(prescription.medicine_name)
        med_item.setForeground(QColor("#2A6674"))
        self.table.setItem(row, 2, med_item)

        # Dosage
        self.table.setItem(row, 3, QTableWidgetItem(prescription.dosage or "—"))

        # Frequency
        self.table.setItem(row, 4, QTableWidgetItem(prescription.frequency or "—"))

        # Duration
        self.table.setItem(row, 5, QTableWidgetItem(prescription.duration or "—"))

        # Date
        date_str = (
            prescription.prescribed_date.strftime("%d %b %Y")
            if prescription.prescribed_date
            else "—"
        )
        self.table.setItem(row, 6, QTableWidgetItem(date_str))

    def _open_add_dialog(self):
        """Open the Add Prescription dialog."""
        dialog = AddPrescriptionDialog(
            self.patient_service,
            self.treatment_service,
            self.prescription_service,
            parent=self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            QMessageBox.information(self, "Success", "Prescription added successfully.")
