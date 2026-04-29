"""Treatment workflow with patient search and treatment queue."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QStackedWidget, QMessageBox,
    QFormLayout, QComboBox, QDoubleSpinBox, QTextEdit,
    QCompleter, QDateEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
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
        """Initialize UI — scrollable, non-overlapping layout."""
        # Outer layout just holds the scroll area
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(24)
        scroll.setWidget(container)

        # ── Header ──
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

        # ── Step 1: Select Patient ──
        patient_frame = QFrame()
        patient_frame.setObjectName("card")
        patient_frame.setStyleSheet(
            "QFrame#card { background:#FFFFFF; border:1px solid #E5E5EA;"
            " border-radius:12px; }"
        )
        pl = QVBoxLayout(patient_frame)
        pl.setContentsMargins(28, 24, 28, 24)
        pl.setSpacing(14)

        step1_row = QHBoxLayout()
        step1_badge = QLabel("1")
        step1_badge.setFixedSize(28, 28)
        step1_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step1_badge.setStyleSheet(
            "background:#007AFF; color:white; border-radius:14px;"
            " font-weight:700; font-size:13px;"
        )
        step1_row.addWidget(step1_badge)
        step1_lbl = QLabel("Select Patient")
        step1_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        step1_lbl.setStyleSheet("margin-left:8px;")
        step1_row.addWidget(step1_lbl)
        step1_row.addStretch()
        pl.addLayout(step1_row)

        # Search bar + Show All
        search_row = QHBoxLayout()
        self.patient_search = QLineEdit()
        self.patient_search.setPlaceholderText("🔍  Search by name or mobile number...")
        self.patient_search.setMinimumHeight(44)
        self.patient_search.textChanged.connect(self.on_patient_search)
        search_row.addWidget(self.patient_search)

        show_all_btn = QPushButton("Show All")
        show_all_btn.setObjectName("secondary_button")
        show_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        show_all_btn.clicked.connect(self.show_all_patients)
        show_all_btn.setFixedWidth(100)
        show_all_btn.setMinimumHeight(44)
        search_row.addWidget(show_all_btn)
        pl.addLayout(search_row)

        # Patient results table
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(4)
        self.search_results.setHorizontalHeaderLabels(["Name", "Mobile", "Age", "City"])
        self.search_results.setMinimumHeight(160)
        self.search_results.setMaximumHeight(220)
        self.search_results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.search_results.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.search_results.cellClicked.connect(self.on_patient_selected)
        self.search_results.verticalHeader().setVisible(False)
        self.search_results.setAlternatingRowColors(True)
        self.search_results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.search_results.verticalHeader().setDefaultSectionSize(40)
        h = self.search_results.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        h.resizeSection(1, 130)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        h.resizeSection(2, 60)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        pl.addWidget(self.search_results)

        # Selected patient banner
        self.selected_patient_label = QLabel("No patient selected")
        self.selected_patient_label.setStyleSheet(
            "color:#86868B; font-style:italic; padding:6px 0;"
        )
        pl.addWidget(self.selected_patient_label)

        # OR divider + create new
        or_row = QHBoxLayout()
        line_l = QFrame(); line_l.setFrameShape(QFrame.Shape.HLine)
        line_l.setStyleSheet("color:#E5E5EA;")
        or_row.addWidget(line_l)
        or_lbl = QLabel("  OR  ")
        or_lbl.setStyleSheet("color:#86868B; font-size:12px; font-weight:500;")
        or_row.addWidget(or_lbl)
        line_r = QFrame(); line_r.setFrameShape(QFrame.Shape.HLine)
        line_r.setStyleSheet("color:#E5E5EA;")
        or_row.addWidget(line_r)
        pl.addLayout(or_row)

        create_btn = QPushButton("➕  Create New Patient")
        create_btn.setObjectName("secondary_button")
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self.on_create_new_patient)
        create_btn.setMinimumHeight(40)
        pl.addWidget(create_btn)

        layout.addWidget(patient_frame)

        # ── Step 2: Treatment Details ──
        treatment_frame = QFrame()
        treatment_frame.setObjectName("card")
        treatment_frame.setStyleSheet(
            "QFrame#card { background:#FFFFFF; border:1px solid #E5E5EA;"
            " border-radius:12px; }"
        )
        tl = QVBoxLayout(treatment_frame)
        tl.setContentsMargins(28, 24, 28, 28)
        tl.setSpacing(20)

        step2_row = QHBoxLayout()
        step2_badge = QLabel("2")
        step2_badge.setFixedSize(28, 28)
        step2_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step2_badge.setStyleSheet(
            "background:#34C759; color:white; border-radius:14px;"
            " font-weight:700; font-size:13px;"
        )
        step2_row.addWidget(step2_badge)
        step2_lbl = QLabel("Treatment Details")
        step2_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        step2_lbl.setStyleSheet("margin-left:8px;")
        step2_row.addWidget(step2_lbl)
        step2_row.addStretch()
        tl.addLayout(step2_row)

        # Fields grid: 2 columns
        fields_row1 = QHBoxLayout()
        fields_row1.setSpacing(20)

        # Treatment Type
        type_col = QVBoxLayout()
        type_col.setSpacing(6)
        type_lbl = QLabel("Treatment Type *")
        type_lbl.setStyleSheet("font-weight:600; font-size:13px; color:#1D1D1F;")
        type_col.addWidget(type_lbl)
        self.treatment_type = QComboBox()
        self.treatment_type.setMinimumHeight(44)
        self.load_treatment_types()
        type_col.addWidget(self.treatment_type)
        fields_row1.addLayout(type_col)

        # Total Cost
        cost_col = QVBoxLayout()
        cost_col.setSpacing(6)
        cost_lbl = QLabel("Total Cost (Rs.) *")
        cost_lbl.setStyleSheet("font-weight:600; font-size:13px; color:#1D1D1F;")
        cost_col.addWidget(cost_lbl)
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMinimum(0)
        self.cost_input.setMaximum(1000000)
        self.cost_input.setPrefix("Rs. ")
        self.cost_input.setValue(0)
        self.cost_input.setMinimumHeight(44)
        cost_col.addWidget(self.cost_input)
        fields_row1.addLayout(cost_col)

        tl.addLayout(fields_row1)

        fields_row2 = QHBoxLayout()
        fields_row2.setSpacing(20)

        # Start Date
        date_col = QVBoxLayout()
        date_col.setSpacing(6)
        date_lbl = QLabel("Start Date")
        date_lbl.setStyleSheet("font-weight:600; font-size:13px; color:#1D1D1F;")
        date_col.addWidget(date_lbl)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setMinimumHeight(44)
        date_col.addWidget(self.start_date)
        fields_row2.addLayout(date_col)

        # Status
        status_col = QVBoxLayout()
        status_col.setSpacing(6)
        status_lbl = QLabel("Status")
        status_lbl.setStyleSheet("font-weight:600; font-size:13px; color:#1D1D1F;")
        status_col.addWidget(status_lbl)
        self.status = QComboBox()
        self.status.setMinimumHeight(44)
        self.status.addItem("📋  Planned")
        self.status.addItem("⚙️  In Progress")
        self.status.addItem("✅  Completed")
        self.status.setItemData(0, QColor("#FFF3E0"), Qt.ItemDataRole.BackgroundRole)
        self.status.setItemData(1, QColor("#E5F0FF"), Qt.ItemDataRole.BackgroundRole)
        self.status.setItemData(2, QColor("#E8F8EC"), Qt.ItemDataRole.BackgroundRole)
        self.status.setStyleSheet(
            "QComboBox QAbstractItemView::item { padding: 10px 14px; min-height:36px; }"
        )
        status_col.addWidget(self.status)
        fields_row2.addLayout(status_col)

        tl.addLayout(fields_row2)

        # Notes
        notes_lbl = QLabel("Notes (optional)")
        notes_lbl.setStyleSheet("font-weight:600; font-size:13px; color:#1D1D1F;")
        tl.addWidget(notes_lbl)
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Any additional notes about this treatment...")
        self.notes.setMinimumHeight(90)
        self.notes.setMaximumHeight(120)
        tl.addWidget(self.notes)

        layout.addWidget(treatment_frame)

        # ── Feedback labels ──
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

        # ── Submit button ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        add_queue_btn = QPushButton("🦷  Add to Treatment Queue")
        add_queue_btn.setObjectName("primary_button")
        add_queue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_queue_btn.clicked.connect(self.on_add_treatment)
        add_queue_btn.setMinimumHeight(48)
        add_queue_btn.setMinimumWidth(260)
        btn_row.addWidget(add_queue_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()

        # Load all patients by default
        self.show_all_patients()

    def load_treatment_types(self):
        """Load treatment types with icons and colors."""
        # icon, background color, text color
        TREATMENT_STYLE = {
            "Root Canal":   ("🦷", "#FFE5E5", "#CC0000"),
            "Filling":      ("🪨", "#FFF3E0", "#E65100"),
            "Cleaning":     ("✨", "#E5F0FF", "#0055CC"),
            "Extraction":   ("🔧", "#F3E5F5", "#7B1FA2"),
            "Crown":        ("👑", "#FFF8E1", "#F57F17"),
            "Implant":      ("🔩", "#E8F5E9", "#2E7D32"),
            "Whitening":    ("⬜", "#E5F0FF", "#1565C0"),
            "Braces":       ("📎", "#FCE4EC", "#880E4F"),
            "Denture":      ("🦴", "#F3E5F5", "#4A148C"),
            "Veneer":       ("💎", "#E0F7FA", "#00695C"),
            "Bridge":       ("🌉", "#FFF3E0", "#BF360C"),
            "Consultation": ("💬", "#E8F5E9", "#1B5E20"),
            "X-Ray":        ("🩻", "#F3E5F5", "#6A1B9A"),
        }

        treatment_types = self.treatment_service.get_all_treatment_types()
        self.treatment_type.clear()
        self.treatment_type.setStyleSheet(
            "QComboBox QAbstractItemView::item {"
            "  padding: 10px 14px;"
            "  min-height: 38px;"
            "  font-size: 13px;"
            "}"
            "QComboBox QAbstractItemView::item:selected {"
            "  background: #007AFF;"
            "  color: white;"
            "}"
        )

        for tt in treatment_types:
            style = TREATMENT_STYLE.get(tt.name, ("🦷", "#F5F5F7", "#1D1D1F"))
            icon, bg, fg = style
            label = f"{icon}  {tt.name}"
            self.treatment_type.addItem(label, tt.id)

            idx = self.treatment_type.count() - 1
            self.treatment_type.setItemData(idx, QColor(bg), Qt.ItemDataRole.BackgroundRole)
            self.treatment_type.setItemData(idx, QColor(fg), Qt.ItemDataRole.ForegroundRole)
            font = QFont("Segoe UI", 12)
            font.setWeight(QFont.Weight.Medium)
            self.treatment_type.setItemData(idx, font, Qt.ItemDataRole.FontRole)

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
        status_map = {
            "planned": "planned", "in progress": "in_progress", "completed": "completed"
        }
        raw_status = self.status.currentText().lower()
        # Strip emoji prefix if present
        for key in status_map:
            if key in raw_status:
                raw_status = key
                break
        status = status_map.get(raw_status, "planned")
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
    """View showing treatment queue with date filters."""

    STATUS_STYLE = {
        "planned":     ("PLANNED",     "#FFF3E0", "#E65100"),
        "in_progress": ("IN PROGRESS", "#E5F0FF", "#0055CC"),
        "completed":   ("COMPLETED",   "#E8F8EC", "#2E7D32"),
    }

    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.treatment_service = TreatmentService()
        self.patient_service = PatientService()
        self._current_filter = "today"
        self._hide_completed = True
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        # ── Header row ──
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

        # ── Filter bar ──
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)

        self._filter_btns = {}
        for key, label in [("today", "Today"), ("week", "This Week"), ("all", "All")]:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(34)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=key: self._set_filter(k))
            self._filter_btns[key] = btn
            filter_bar.addWidget(btn)

        filter_bar.addSpacing(16)

        self._completed_btn = QPushButton("Show Completed")
        self._completed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._completed_btn.setFixedHeight(34)
        self._completed_btn.setCheckable(True)
        self._completed_btn.setChecked(False)
        self._completed_btn.clicked.connect(self._toggle_completed)
        filter_bar.addWidget(self._completed_btn)

        filter_bar.addStretch()

        self._count_label = QLabel("")
        self._count_label.setStyleSheet("color:#86868B; font-size:12px;")
        filter_bar.addWidget(self._count_label)

        layout.addLayout(filter_bar)

        self._apply_filter_styles()

        # ── Queue table ──
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
        self.queue_table.verticalHeader().setDefaultSectionSize(48)

        header = self.queue_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 120)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 100)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 130)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 100)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 150)

        layout.addWidget(self.queue_table)

        self.load_queue()

    # ── filter helpers ────────────────────────────────────────────────────────

    def _set_filter(self, key: str):
        self._current_filter = key
        self._apply_filter_styles()
        self.load_queue()

    def _toggle_completed(self):
        self._hide_completed = not self._completed_btn.isChecked()
        self._apply_filter_styles()
        self.load_queue()

    def _apply_filter_styles(self):
        active = (
            "QPushButton { background:#0F2942; color:white; border:none;"
            " border-radius:6px; padding:0 16px; font-size:13px; font-weight:700; }"
        )
        inactive = (
            "QPushButton { background:#F1F5F9; color:#374151; border:1px solid #D1D5DB;"
            " border-radius:6px; padding:0 16px; font-size:13px; }"
            "QPushButton:hover { background:#E2E8F0; }"
        )
        for key, btn in self._filter_btns.items():
            btn.setStyleSheet(active if key == self._current_filter else inactive)
            btn.setChecked(key == self._current_filter)

        completed_on = (
            "QPushButton { background:#E8F8EC; color:#2E7D32; border:1px solid #A7F3D0;"
            " border-radius:6px; padding:0 14px; font-size:13px; font-weight:600; }"
        )
        completed_off = (
            "QPushButton { background:#F1F5F9; color:#374151; border:1px solid #D1D5DB;"
            " border-radius:6px; padding:0 14px; font-size:13px; }"
            "QPushButton:hover { background:#E2E8F0; }"
        )
        self._completed_btn.setStyleSheet(
            completed_on if not self._hide_completed else completed_off
        )

    def _passes_filter(self, treatment) -> bool:
        """Return True if treatment should be shown given current filters."""
        if self._hide_completed and treatment.status == "completed":
            return False
        if self._current_filter == "all":
            return True
        try:
            from datetime import date as _date, timedelta
            today = _date.today()
            t_date = treatment.start_date
            if isinstance(t_date, str):
                from datetime import datetime
                t_date = datetime.fromisoformat(t_date).date()
            if t_date is None:
                return self._current_filter == "all"
            if self._current_filter == "today":
                return t_date == today
            if self._current_filter == "week":
                week_start = today - timedelta(days=today.weekday())
                return week_start <= t_date <= today + timedelta(days=6 - today.weekday())
        except (ValueError, AttributeError) as e:
            import logging
            logging.getLogger(__name__).warning(f"Date filter error for treatment {treatment.id}: {e}")
            return True
        return True

    def load_queue(self):
        """Load treatment queue applying current filter."""
        from datetime import date as _date
        all_patients = self.patient_service.get_all_patients()
        self.queue_table.setRowCount(0)
        shown = 0

        for patient in all_patients:
            treatments = self.treatment_service.get_patient_treatments(patient.id)
            for treatment in treatments:
                if not self._passes_filter(treatment):
                    continue

                row = self.queue_table.rowCount()
                self.queue_table.insertRow(row)
                shown += 1

                _f = QFont("Ubuntu", 12)
                _f_bold = QFont("Ubuntu", 12)
                _f_bold.setWeight(QFont.Weight.Medium)

                name_item = QTableWidgetItem(patient.name)
                name_item.setFont(_f_bold)
                self.queue_table.setItem(row, 0, name_item)

                mobile_item = QTableWidgetItem(patient.mobile_number)
                mobile_item.setFont(_f)
                self.queue_table.setItem(row, 1, mobile_item)

                treatment_item = QTableWidgetItem(treatment.treatment_type_name or "N/A")
                treatment_item.setFont(_f)
                self.queue_table.setItem(row, 2, treatment_item)

                cost_item = QTableWidgetItem(f"Rs.{treatment.total_cost:.2f}")
                cost_item.setFont(_f)
                self.queue_table.setItem(row, 3, cost_item)

                # Colored status badge
                status_key = treatment.status.lower().replace(" ", "_")
                label, bg, fg = self.STATUS_STYLE.get(status_key, (treatment.status.upper(), "#F1F5F9", "#374151"))
                status_item = QTableWidgetItem(label)
                status_item.setFont(_f_bold)
                status_item.setBackground(QColor(bg))
                status_item.setForeground(QColor(fg))
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.queue_table.setItem(row, 4, status_item)

                try:
                    t_date = treatment.start_date
                    if isinstance(t_date, str):
                        from datetime import datetime
                        t_date = datetime.fromisoformat(t_date).date()
                    date_str = t_date.strftime('%d %b %Y') if t_date else "N/A"
                except (ValueError, AttributeError) as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Date parse error for treatment {treatment.id}: {e}")
                    date_str = str(treatment.start_date) if treatment.start_date else "N/A"
                self.queue_table.setItem(row, 5, QTableWidgetItem(date_str))

                actions = self.create_action_buttons(treatment.id)
                self.queue_table.setCellWidget(row, 6, actions)

        # Show empty state
        if shown == 0:
            filter_names = {"today": "today", "week": "this week", "all": ""}
            msg = f"No active treatments for {filter_names.get(self._current_filter, '')}".strip()
            self.queue_table.insertRow(0)
            empty_item = QTableWidgetItem(msg + "  —  click 'Add New Treatment' to add one.")
            empty_item.setForeground(QColor("#86868B"))
            self.queue_table.setItem(0, 0, empty_item)
            self.queue_table.setSpan(0, 0, 1, 7)

        filter_label = {"today": "Today", "week": "This Week", "all": "All Time"}
        self._count_label.setText(f"{shown} treatment{'s' if shown != 1 else ''} · {filter_label.get(self._current_filter, '')}")

    def create_action_buttons(self, treatment_id: int):
        """Create action buttons for each queue row."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        view_btn = QPushButton("👁  View Patient")
        view_btn.setFixedHeight(32)
        view_btn.setMinimumWidth(110)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setStyleSheet(
            "QPushButton { background: #EFF6FF; color: #1A4A7A; border: 1px solid #BFDBFE;"
            " border-radius: 6px; padding: 0 12px; font-size: 12px; font-weight: 600; }"
            "QPushButton:hover { background: #DBEAFE; border-color: #38BDF8; color: #0F2942; }"
        )
        view_btn.clicked.connect(lambda: self.on_view_treatment(treatment_id))
        layout.addWidget(view_btn)

        return widget

    def on_add_new_treatment(self):
        """Show add treatment form."""
        self.parent_widget.show_add_form()

    def refresh(self):
        """Refresh queue."""
        self.load_queue()
        
    def on_view_treatment(self, treatment_id: int):
        """Navigate to the patient's profile (billing/payment history) for this treatment."""
        treatment = self.treatment_service.get_treatment(treatment_id)
        if not treatment:
            return

        patient = self.patient_service.get_patient(treatment.patient_id)
        if not patient:
            return

        # Switch the main window to the Patients page
        main_window = self.window()
        if hasattr(main_window, 'sidebar'):
            main_window.sidebar.on_nav_clicked('patients')

        # Open the patient details widget on the Patients page
        if hasattr(main_window, 'pages') and 'patients' in main_window.pages:
            patient_list_widget = main_window.pages['patients']
            patient_list_widget.show_patient_details(patient)

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
        """Refresh data — always reset to queue list."""
        self.show_queue_view()
