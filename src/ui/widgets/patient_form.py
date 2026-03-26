"""Patient form dialog for add/edit operations."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSpinBox, QTextEdit,
    QFormLayout, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from ...models.patient import Patient
from ...services.patient_service import PatientService


class PatientFormDialog(QDialog):
    """Dialog for adding or editing patient information."""

    def __init__(self, parent=None, patient: Patient = None):
        super().__init__(parent)
        self.patient = patient
        self.patient_service = PatientService()
        self.is_edit_mode = patient is not None

        self.setWindowTitle("Edit Patient" if self.is_edit_mode else "Add New Patient")
        self.setMinimumWidth(500)
        self.setModal(True)

        self.init_ui()
        if self.is_edit_mode:
            self.load_patient_data()

    def init_ui(self):
        """Initialize the form UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("Edit Patient Details" if self.is_edit_mode else "New Patient")
        title.setObjectName("page_title")
        layout.addWidget(title)

        # Form
        form_frame = QFrame()
        form_frame.setObjectName("card")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Name field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter patient name")
        name_label = QLabel("Name:")
        name_label.setObjectName("form_label")
        form_layout.addRow(name_label, self.name_input)

        # Mobile number field
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("10-digit mobile number")
        self.mobile_input.setMaxLength(10)
        mobile_label = QLabel("Mobile Number:")
        mobile_label.setObjectName("form_label")
        form_layout.addRow(mobile_label, self.mobile_input)

        # Age field
        self.age_input = QSpinBox()
        self.age_input.setMinimum(1)
        self.age_input.setMaximum(120)
        self.age_input.setValue(30)
        age_label = QLabel("Age:")
        age_label.setObjectName("form_label")
        form_layout.addRow(age_label, self.age_input)

        # City field
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        city_label = QLabel("City:")
        city_label.setObjectName("form_label")
        form_layout.addRow(city_label, self.city_input)

        # Address field
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter full address (optional)")
        self.address_input.setMaximumHeight(80)
        address_label = QLabel("Address:")
        address_label.setObjectName("form_label")
        form_layout.addRow(address_label, self.address_input)

        layout.addWidget(form_frame)

        # Error label
        self.error_label = QLabel()
        self.error_label.setObjectName("error_label")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Patient" if not self.is_edit_mode else "Update Patient")
        save_btn.setObjectName("primary_button")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.on_save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def load_patient_data(self):
        """Load patient data into form fields."""
        if not self.patient:
            return

        self.name_input.setText(self.patient.name)
        self.mobile_input.setText(self.patient.mobile_number)
        self.age_input.setValue(self.patient.age)
        self.city_input.setText(self.patient.city)
        if self.patient.address:
            self.address_input.setPlainText(self.patient.address)

    def on_save(self):
        """Handle save button click."""
        # Get form data
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()
        age = self.age_input.value()
        city = self.city_input.text().strip()
        address = self.address_input.toPlainText().strip()

        # Save patient
        if self.is_edit_mode:
            success, message = self.patient_service.update_patient(
                self.patient.id,
                name=name,
                mobile_number=mobile,
                age=age,
                city=city,
                address=address if address else None
            )
        else:
            success, message, patient_id = self.patient_service.create_patient(
                name=name,
                mobile_number=mobile,
                age=age,
                city=city,
                address=address if address else None
            )

        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            self.error_label.setText(f"❌ {message}")
            self.error_label.setVisible(True)
