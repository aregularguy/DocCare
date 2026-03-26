"""Patient details dialog showing complete history."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from ...models.patient import Patient
from ...services.treatment_service import TreatmentService
from ...utils.formatters import format_currency, format_date


class PatientDetailsDialog(QDialog):
    """Dialog for viewing patient details and history."""

    def __init__(self, patient: Patient, parent=None):
        super().__init__(parent)
        self.patient = patient
        self.treatment_service = TreatmentService()

        self.setWindowTitle(f"Patient Details - {patient.name}")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        self.init_ui()

    def init_ui(self):
        """Initialize the details UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(f"👤 {self.patient.name}")
        header.setObjectName("page_title")
        layout.addWidget(header)

        # Patient info card
        info_card = self.create_info_card()
        layout.addWidget(info_card)

        # Tabs for history
        tabs = QTabWidget()
        tabs.addTab(self.create_treatments_tab(), "Treatments")
        tabs.addTab(self.create_payments_tab(), "Payments")
        tabs.addTab(self.create_prescriptions_tab(), "Prescriptions")
        layout.addWidget(tabs)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondary_button")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def create_info_card(self):
        """Create patient info card."""
        card = QFrame()
        card.setObjectName("card")
        layout = QHBoxLayout(card)

        info_text = f"""
        <b>Mobile:</b> {self.patient.mobile_number}<br>
        <b>Age:</b> {self.patient.age} years<br>
        <b>City:</b> {self.patient.city}<br>
        <b>Address:</b> {self.patient.address or 'N/A'}
        """

        info_label = QLabel(info_text)
        layout.addWidget(info_label)

        return card

    def create_treatments_tab(self):
        """Create treatments history tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        treatments = self.treatment_service.get_patient_treatments(self.patient.id)

        if not treatments:
            label = QLabel("No treatments recorded")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #86868B; padding: 40px;")
            layout.addWidget(label)
        else:
            for treatment in treatments:
                treatment_card = self.create_treatment_card(treatment)
                layout.addWidget(treatment_card)

        layout.addStretch()
        return widget

    def create_treatment_card(self, treatment):
        """Create a treatment card."""
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        # Treatment name and status
        header_layout = QHBoxLayout()
        name_label = QLabel(f"🦷 {treatment.treatment_type_name}")
        name_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        header_layout.addWidget(name_label)

        status_label = QLabel(treatment.status.upper())
        status_label.setStyleSheet("font-size: 11px; color: #86868B;")
        header_layout.addWidget(status_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Cost and payment info
        info_label = QLabel(
            f"Cost: {format_currency(treatment.total_cost)} | "
            f"Paid: {format_currency(treatment.amount_paid)} | "
            f"Pending: {format_currency(treatment.pending_amount)}"
        )
        info_label.setStyleSheet("color: #86868B; font-size: 12px;")
        layout.addWidget(info_label)

        return card

    def create_payments_tab(self):
        """Create payments history tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Payment history will be displayed here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #86868B; padding: 40px;")
        layout.addWidget(label)

        return widget

    def create_prescriptions_tab(self):
        """Create prescriptions history tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Prescription history will be displayed here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #86868B; padding: 40px;")
        layout.addWidget(label)

        return widget
