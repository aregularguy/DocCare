"""Patient list and management widget with inline form."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QStackedWidget, QMessageBox,
    QSpinBox, QTextEdit, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ...services.patient_service import PatientService
from ...services.treatment_service import TreatmentService
from ...models.patient import Patient


class PatientFormView(QWidget):
    """Inline patient form (not a dialog)."""

    def __init__(self, patient_service, treatment_service, parent_widget, patient: Patient = None):
        super().__init__()
        self.patient_service = patient_service
        self.treatment_service = treatment_service
        self.parent_widget = parent_widget
        self.patient = patient
        self.is_edit_mode = patient is not None
        self.init_ui()

        if self.is_edit_mode:
            self.load_patient_data()

    def init_ui(self):
        """Initialize the form UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Edit Patient" if self.is_edit_mode else "Add New Patient")
        title.setObjectName("page_title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("← Back to Patients")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.on_cancel)
        header_layout.addWidget(cancel_btn)

        layout.addLayout(header_layout)

        # Form card
        form_frame = QFrame()
        form_frame.setObjectName("card")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(24, 24, 24, 24)

        # Patient Basic Info Section
        section_label = QLabel("Patient Information")
        section_label.setObjectName("section_title")
        form_layout.addRow(section_label)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        form_layout.addRow("Name *:", self.name_input)

        # Mobile
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("10-digit mobile number")
        self.mobile_input.setMaxLength(10)
        form_layout.addRow("Mobile *:", self.mobile_input)

        # Age
        self.age_input = QSpinBox()
        self.age_input.setMinimum(1)
        self.age_input.setMaximum(120)
        self.age_input.setValue(30)
        form_layout.addRow("Age *:", self.age_input)

        # City
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city")
        form_layout.addRow("City *:", self.city_input)

        # Address
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter full address (optional)")
        self.address_input.setMaximumHeight(80)
        form_layout.addRow("Address:", self.address_input)

        layout.addWidget(form_frame)

        # Error label
        self.error_label = QLabel()
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Success label
        self.success_label = QLabel()
        self.success_label.setObjectName("success_label")
        self.success_label.setWordWrap(True)
        self.success_label.setVisible(False)
        layout.addWidget(self.success_label)

        # Save button (not full width)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("💾 Save Patient" if not self.is_edit_mode else "💾 Update Patient")
        save_btn.setObjectName("primary_button")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.on_save)
        save_btn.setMinimumHeight(44)
        save_btn.setMinimumWidth(200)
        button_layout.addWidget(save_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()

    def load_patient_data(self):
        """Load patient data into form."""
        if not self.patient:
            return

        self.name_input.setText(self.patient.name)
        self.mobile_input.setText(self.patient.mobile_number)
        self.age_input.setValue(self.patient.age)
        self.city_input.setText(self.patient.city)
        if self.patient.address:
            self.address_input.setPlainText(self.patient.address)

    def on_save(self):
        """Save patient."""
        # Hide previous messages
        self.error_label.setVisible(False)
        self.success_label.setVisible(False)

        # Get form data
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()
        age = self.age_input.value()
        city = self.city_input.text().strip()
        address = self.address_input.toPlainText().strip()

        # Save
        if self.is_edit_mode:
            success, message = self.patient_service.update_patient(
                self.patient.id, name=name, mobile_number=mobile,
                age=age, city=city, address=address if address else None
            )
        else:
            success, message, patient_id = self.patient_service.create_patient(
                name=name, mobile_number=mobile, age=age, city=city,
                address=address if address else None
            )

        if success:
            self.success_label.setText(f"✅ {message}")
            self.success_label.setVisible(True)
            # Go back to list after 1 second (guard against deleted widget)
            from PyQt6.QtCore import QTimer
            def _safe_cancel():
                try:
                    if self and self.parent_widget:
                        self.on_cancel()
                except RuntimeError:
                    pass  # widget already deleted
            QTimer.singleShot(1000, _safe_cancel)
        else:
            self.error_label.setText(f"❌ {message}")
            self.error_label.setVisible(True)

    def on_cancel(self):
        """Cancel and go back."""
        self.parent_widget.show_list_view()


class PatientListWidget(QWidget):
    """Patient list and management with inline form."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_service = PatientService()
        self.treatment_service = TreatmentService()
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        # Stack widget to switch between list and form
        self.stack = QStackedWidget()

        # Create list view
        self.list_view = self.create_list_view()
        self.stack.addWidget(self.list_view)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

    def create_list_view(self):
        """Create the patient list view."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # Hero banner
        banner = QFrame()
        banner.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #0F2942, stop:0.6 #1A4A7A, stop:1 #1E6FA8);"
            " border-radius: 14px; }"
        )
        banner.setFixedHeight(110)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(28, 0, 28, 0)

        banner_title = QLabel("🦷  All Patients")
        banner_title.setStyleSheet(
            "color: white; font-size: 22px; font-weight: 700; background: transparent;"
        )
        banner_layout.addWidget(banner_title)
        banner_layout.addStretch()

        add_btn = QPushButton("➕  Add New Patient")
        add_btn.setObjectName("primary_button")
        add_btn.setStyleSheet(
            "QPushButton { background: white; color: #0F2942; border: none;"
            " border-radius: 8px; padding: 10px 20px; font-weight: 600; font-size: 13px; }"
            "QPushButton:hover { background: #E0F2FE; }"
        )
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.show_add_form)
        banner_layout.addWidget(add_btn)

        layout.addWidget(banner)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name, mobile, or city...")
        self.search_input.setMinimumWidth(400)
        self.search_input.textChanged.connect(self.on_search)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Mobile", "Age", "City", "Actions"
        ])

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 60)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 120)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 60)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 280)

        self.table.verticalHeader().setDefaultSectionSize(46)
        layout.addWidget(self.table)

        self.load_patients()

        return widget

    def load_patients(self, search_query: str = ""):
        """Load patients."""
        if search_query:
            patients = self.patient_service.search_patients(search_query)
        else:
            patients = self.patient_service.get_all_patients()

        self.table.setRowCount(0)

        for patient in patients:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(patient.id)))
            name_item = QTableWidgetItem(patient.name)
            name_item.setFont(QFont("Inter", 13, QFont.Weight.Bold))
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, QTableWidgetItem(patient.mobile_number))
            self.table.setItem(row, 3, QTableWidgetItem(str(patient.age)))
            self.table.setItem(row, 4, QTableWidgetItem(patient.city))

            # Actions with better buttons
            actions = self.create_action_buttons(patient.id)
            self.table.setCellWidget(row, 5, actions)

    def create_action_buttons(self, patient_id: int):
        """Create compact, clearly visible action buttons."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        _btn_style = (
            "QPushButton {{ background:{bg}; color:{fg}; border:none; border-radius:6px;"
            " padding:0 10px; font-size:11px; font-weight:600; font-family:'Ubuntu',sans-serif; }}"
            "QPushButton:hover {{ background:{hv}; }}"
        )

        view_btn = QPushButton("📋 History")
        view_btn.setFixedHeight(30)
        view_btn.setMinimumWidth(82)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setStyleSheet(_btn_style.format(bg="#EFF6FF", fg="#1A4A7A", hv="#DBEAFE"))
        view_btn.clicked.connect(lambda: self.on_view_patient(patient_id))
        layout.addWidget(view_btn)

        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setFixedHeight(30)
        edit_btn.setMinimumWidth(64)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(_btn_style.format(bg="#F0FDF4", fg="#166534", hv="#DCFCE7"))
        edit_btn.clicked.connect(lambda: self.show_edit_form(patient_id))
        layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet(_btn_style.format(bg="#FEF2F2", fg="#991B1B", hv="#FEE2E2"))
        delete_btn.clicked.connect(lambda: self.on_delete_patient(patient_id))
        layout.addWidget(delete_btn)

        return widget

    def on_search(self):
        """Handle search."""
        self.load_patients(self.search_input.text())

    def show_add_form(self):
        """Show add patient form."""
        form = PatientFormView(self.patient_service, self.treatment_service, self)
        self.stack.addWidget(form)
        self.stack.setCurrentWidget(form)

    def show_edit_form(self, patient_id: int):
        """Show edit form."""
        patient = self.patient_service.get_patient(patient_id)
        if patient:
            form = PatientFormView(self.patient_service, self.treatment_service, self, patient)
            self.stack.addWidget(form)
            self.stack.setCurrentWidget(form)

    def show_list_view(self):
        """Show patient list."""
        self.stack.setCurrentWidget(self.list_view)
        self.load_patients()
        # Remove old form widgets
        while self.stack.count() > 1:
            widget = self.stack.widget(1)
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def on_view_patient(self, patient_id: int):
        """Show patient details as embedded page in the same window."""
        patient = self.patient_service.get_patient(patient_id)
        if patient:
            self.show_patient_details(patient)

    def show_patient_details(self, patient):
        """Push patient details widget onto the stack."""
        from ..dialogs.patient_details import PatientDetailsWidget
        # Remove any previously pushed detail pages
        while self.stack.count() > 1:
            w = self.stack.widget(1)
            self.stack.removeWidget(w)
            w.deleteLater()

        details = PatientDetailsWidget(patient, self)
        self.stack.addWidget(details)
        self.stack.setCurrentWidget(details)

    def on_delete_patient(self, patient_id: int):
        """Delete patient."""
        patient = self.patient_service.get_patient(patient_id)
        if not patient:
            return

        reply = QMessageBox.question(
            self, 'Delete Patient',
            f'Delete patient "{patient.name}"?\n\nThis will delete all treatments, payments, and prescriptions.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.patient_service.delete_patient(patient_id)
            if success:
                QMessageBox.information(self, 'Success', message)
                self.load_patients()
            else:
                QMessageBox.warning(self, 'Error', message)

    def refresh_data(self):
        """Refresh data."""
        if self.stack.currentWidget() == self.list_view:
            self.load_patients()
