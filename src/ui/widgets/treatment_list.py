"""Treatment workflow with patient search and treatment queue."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QStackedWidget, QMessageBox,
    QFormLayout, QComboBox, QDoubleSpinBox, QTextEdit,
    QCompleter, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from ...services.patient_service import PatientService
from ...services.treatment_service import TreatmentService
from datetime import date


class TreatmentFormView(QWidget):
    """Add treatment with patient search/create."""

    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.patient_service = PatientService()
        self.treatment_service = TreatmentService()
        self.selected_patient = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("New Treatment")
        title.setObjectName("page_title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        cancel_btn = QPushButton("← Back")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.on_cancel)
        header_layout.addWidget(cancel_btn)

        layout.addLayout(header_layout)

        # Step 1: Search or Create Patient
        patient_frame = QFrame()
        patient_frame.setObjectName("card")
        patient_layout = QVBoxLayout(patient_frame)
        patient_layout.setContentsMargins(24, 24, 24, 24)
        patient_layout.setSpacing(16)

        step1_label = QLabel("Step 1: Select Patient")
        step1_label.setObjectName("section_title")
        patient_layout.addWidget(step1_label)

        # Search existing patient
        search_layout = QHBoxLayout()

        self.patient_search = QLineEdit()
        self.patient_search.setPlaceholderText("🔍 Type patient name or mobile number to search...")
        self.patient_search.textChanged.connect(self.on_patient_search)
        self.patient_search.setMinimumHeight(44)
        search_layout.addWidget(self.patient_search)

        show_all_btn = QPushButton("Show All")
        show_all_btn.setObjectName("secondary_button")
        show_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        show_all_btn.clicked.connect(self.show_all_patients)
        show_all_btn.setMaximumWidth(120)
        search_layout.addWidget(show_all_btn)

        patient_layout.addLayout(search_layout)

        # Search results
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(4)
        self.search_results.setHorizontalHeaderLabels(["Name", "Mobile", "Age", "City"])
        self.search_results.setMinimumHeight(150)
        self.search_results.setMaximumHeight(200)
        self.search_results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.search_results.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.search_results.cellClicked.connect(self.on_patient_selected)
        self.search_results.verticalHeader().setVisible(False)
        self.search_results.setAlternatingRowColors(True)

        # Set column widths
        header = self.search_results.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 120)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 60)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        patient_layout.addWidget(self.search_results)

        # Selected patient display
        self.selected_patient_label = QLabel("No patient selected")
        self.selected_patient_label.setStyleSheet("color: #86868B; font-style: italic;")
        patient_layout.addWidget(self.selected_patient_label)

        # OR create new patient
        or_label = QLabel("— OR —")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_label.setStyleSheet("color: #86868B; margin: 10px 0;")
        patient_layout.addWidget(or_label)

        create_new_btn = QPushButton("➕ Create New Patient")
        create_new_btn.setObjectName("secondary_button")
        create_new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_new_btn.clicked.connect(self.on_create_new_patient)
        patient_layout.addWidget(create_new_btn)

        layout.addWidget(patient_frame)

        # Step 2: Treatment Details
        treatment_frame = QFrame()
        treatment_frame.setObjectName("card")
        treatment_layout = QFormLayout(treatment_frame)
        treatment_layout.setContentsMargins(24, 24, 24, 24)
        treatment_layout.setSpacing(16)

        step2_label = QLabel("Step 2: Treatment Details")
        step2_label.setObjectName("section_title")
        treatment_layout.addRow(step2_label)

        # Treatment type
        self.treatment_type = QComboBox()
        self.load_treatment_types()
        treatment_layout.addRow("Treatment Type *:", self.treatment_type)

        # Cost
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMinimum(0)
        self.cost_input.setMaximum(1000000)
        self.cost_input.setPrefix("₹ ")
        self.cost_input.setValue(0)
        treatment_layout.addRow("Total Cost *:", self.cost_input)

        # Start date
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        treatment_layout.addRow("Start Date:", self.start_date)

        # Status
        self.status = QComboBox()
        self.status.addItems(["Planned", "In Progress", "Completed"])
        treatment_layout.addRow("Status:", self.status)

        # Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Add any notes about the treatment...")
        self.notes.setMaximumHeight(100)
        treatment_layout.addRow("Notes:", self.notes)

        layout.addWidget(treatment_frame)

        # Error/Success messages
        self.error_label = QLabel()
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        self.success_label = QLabel()
        self.success_label.setObjectName("success_label")
        self.success_label.setWordWrap(True)
        self.success_label.setVisible(False)
        layout.addWidget(self.success_label)

        # Add to Queue button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        add_queue_btn = QPushButton("➕ Add to Treatment Queue")
        add_queue_btn.setObjectName("primary_button")
        add_queue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_queue_btn.clicked.connect(self.on_add_treatment)
        add_queue_btn.setMinimumHeight(44)
        add_queue_btn.setMinimumWidth(250)
        button_layout.addWidget(add_queue_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()

        # Load all patients by default
        self.show_all_patients()

    def load_treatment_types(self):
        """Load treatment types into dropdown."""
        treatment_types = self.treatment_service.get_all_treatment_types()
        self.treatment_type.clear()
        for tt in treatment_types:
            self.treatment_type.addItem(tt.name, tt.id)

    def show_all_patients(self):
        """Show all patients in the results table."""
        self.patient_search.clear()
        patients = self.patient_service.get_all_patients()

        self.search_results.setRowCount(0)

        if not patients:
            # Show "no patients" message
            self.search_results.insertRow(0)
            no_results = QTableWidgetItem("No patients in database yet. Click 'Create New Patient' below.")
            no_results.setForeground(Qt.GlobalColor.gray)
            self.search_results.setItem(0, 0, no_results)
            self.search_results.setSpan(0, 0, 1, 4)
            return

        # Show all patients
        for patient in patients[:20]:  # Show top 20
            row = self.search_results.rowCount()
            self.search_results.insertRow(row)

            name_item = QTableWidgetItem(patient.name)
            name_item.setData(Qt.ItemDataRole.UserRole, patient.id)
            self.search_results.setItem(row, 0, name_item)

            self.search_results.setItem(row, 1, QTableWidgetItem(patient.mobile_number))
            self.search_results.setItem(row, 2, QTableWidgetItem(str(patient.age)))
            self.search_results.setItem(row, 3, QTableWidgetItem(patient.city))

    def on_patient_search(self):
        """Search for patients."""
        query = self.patient_search.text().strip()

        # Clear previous results
        self.search_results.setRowCount(0)

        if not query or len(query) < 1:
            return

        # Search for patients
        patients = self.patient_service.search_patients(query)

        if not patients:
            # Show "no results" message
            self.search_results.insertRow(0)
            no_results = QTableWidgetItem(f'No patients found matching "{query}"')
            no_results.setForeground(Qt.GlobalColor.gray)
            self.search_results.setItem(0, 0, no_results)
            self.search_results.setSpan(0, 0, 1, 4)
            return

        # Show results
        for patient in patients[:10]:  # Show top 10 results
            row = self.search_results.rowCount()
            self.search_results.insertRow(row)

            name_item = QTableWidgetItem(patient.name)
            name_item.setData(Qt.ItemDataRole.UserRole, patient.id)
            self.search_results.setItem(row, 0, name_item)

            self.search_results.setItem(row, 1, QTableWidgetItem(patient.mobile_number))
            self.search_results.setItem(row, 2, QTableWidgetItem(str(patient.age)))
            self.search_results.setItem(row, 3, QTableWidgetItem(patient.city))

    def on_patient_selected(self, row, col):
        """Patient selected from search results."""
        item = self.search_results.item(row, 0)
        patient_id = item.data(Qt.ItemDataRole.UserRole)

        self.selected_patient = self.patient_service.get_patient(patient_id)
        if self.selected_patient:
            self.selected_patient_label.setText(
                f"✅ Selected: {self.selected_patient.name} ({self.selected_patient.mobile_number})"
            )
            self.selected_patient_label.setStyleSheet("color: #34C759; font-weight: 500;")

    def on_create_new_patient(self):
        """Navigate to create new patient."""
        # Navigate to patients page
        main_window = self.window()
        if hasattr(main_window, 'sidebar'):
            main_window.sidebar.on_nav_clicked('patients')

    def on_add_treatment(self):
        """Add treatment to queue."""
        self.error_label.setVisible(False)
        self.success_label.setVisible(False)

        # Validate patient selected
        if not self.selected_patient:
            self.error_label.setText("❌ Please select a patient first")
            self.error_label.setVisible(True)
            return

        # Validate cost
        cost = self.cost_input.value()
        if cost <= 0:
            self.error_label.setText("❌ Please enter a valid cost")
            self.error_label.setVisible(True)
            return

        # Get treatment data
        treatment_type_id = self.treatment_type.currentData()
        status_map = {"Planned": "planned", "In Progress": "in_progress", "Completed": "completed"}
        status = status_map[self.status.currentText()]
        start_date_py = self.start_date.date().toPyDate()
        notes_text = self.notes.toPlainText().strip()

        # Create treatment
        success, message, treatment_id = self.treatment_service.create_treatment(
            patient_id=self.selected_patient.id,
            treatment_type_id=treatment_type_id,
            total_cost=cost,
            status=status,
            start_date=start_date_py,
            notes=notes_text if notes_text else None
        )

        if success:
            self.success_label.setText(f"✅ {message} - Added to queue!")
            self.success_label.setVisible(True)

            # Reset form
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, self.reset_form)
        else:
            self.error_label.setText(f"❌ {message}")
            self.error_label.setVisible(True)

    def reset_form(self):
        """Reset form after successful add."""
        self.selected_patient = None
        self.patient_search.clear()
        self.search_results.setRowCount(0)
        self.selected_patient_label.setText("No patient selected")
        self.selected_patient_label.setStyleSheet("color: #86868B; font-style: italic;")
        self.cost_input.setValue(0)
        self.notes.clear()
        self.status.setCurrentIndex(0)
        self.success_label.setVisible(False)

    def on_cancel(self):
        """Go back."""
        self.parent_widget.show_queue_view()


class TreatmentQueueView(QWidget):
    """View showing treatment queue."""

    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.treatment_service = TreatmentService()
        self.patient_service = PatientService()
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Treatment Queue")
        title.setObjectName("page_title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        add_btn = QPushButton("➕ Add New Treatment")
        add_btn.setObjectName("primary_button")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.on_add_new_treatment)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Queue table
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(7)
        self.queue_table.setHorizontalHeaderLabels([
            "Patient", "Mobile", "Treatment", "Cost", "Status", "Date", "Actions"
        ])

        self.queue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.queue_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.queue_table.setAlternatingRowColors(True)
        self.queue_table.verticalHeader().setVisible(False)
        self.queue_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Column widths
        header = self.queue_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 120)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 100)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 120)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 100)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 150)

        layout.addWidget(self.queue_table)

        self.load_queue()

    def load_queue(self):
        """Load treatment queue."""
        # Get all pending treatments
        all_patients = self.patient_service.get_all_patients()

        self.queue_table.setRowCount(0)

        for patient in all_patients:
            treatments = self.treatment_service.get_patient_treatments(patient.id)

            for treatment in treatments:
                row = self.queue_table.rowCount()
                self.queue_table.insertRow(row)

                self.queue_table.setItem(row, 0, QTableWidgetItem(patient.name))
                self.queue_table.setItem(row, 1, QTableWidgetItem(patient.mobile_number))
                self.queue_table.setItem(row, 2, QTableWidgetItem(treatment.treatment_type_name or "N/A"))
                self.queue_table.setItem(row, 3, QTableWidgetItem(f"₹{treatment.total_cost:.2f}"))
                self.queue_table.setItem(row, 4, QTableWidgetItem(treatment.status.upper()))

                date_str = treatment.start_date.strftime('%Y-%m-%d') if treatment.start_date else "N/A"
                self.queue_table.setItem(row, 5, QTableWidgetItem(date_str))

                # Action buttons
                actions = self.create_action_buttons(treatment.id)
                self.queue_table.setCellWidget(row, 6, actions)

    def create_action_buttons(self, treatment_id: int):
        """Create action buttons."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        view_btn = QPushButton("👁️ View")
        view_btn.setObjectName("secondary_button")
        view_btn.setMinimumWidth(70)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(view_btn)

        return widget

    def on_add_new_treatment(self):
        """Show add treatment form."""
        self.parent_widget.show_add_form()

    def refresh(self):
        """Refresh queue."""
        self.load_queue()


class TreatmentListWidget(QWidget):
    """Main treatment widget with stack."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        self.stack = QStackedWidget()

        # Create views
        self.queue_view = TreatmentQueueView(self)
        self.stack.addWidget(self.queue_view)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

    def show_queue_view(self):
        """Show queue view."""
        self.stack.setCurrentWidget(self.queue_view)
        self.queue_view.refresh()

        # Remove old forms
        while self.stack.count() > 1:
            widget = self.stack.widget(1)
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def show_add_form(self):
        """Show add form."""
        form = TreatmentFormView(self)
        self.stack.addWidget(form)
        self.stack.setCurrentWidget(form)

    def refresh_data(self):
        """Refresh data."""
        if self.stack.currentWidget() == self.queue_view:
            self.queue_view.refresh()
