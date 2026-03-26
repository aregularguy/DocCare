"""Patient business logic service."""
from typing import List, Optional, Tuple
from ..models.patient import Patient
from ..repositories.patient_repository import PatientRepository
from ..utils.validators import validate_mobile_number, validate_age, validate_required_field


class PatientService:
    """Service for patient business logic."""

    def __init__(self):
        """Initialize patient service."""
        self.repository = PatientRepository()

    def create_patient(
        self,
        name: str,
        mobile_number: str,
        age: int,
        city: str,
        address: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """Create a new patient.

        Args:
            name: Patient name
            mobile_number: Mobile number
            age: Patient age
            city: City/Address
            address: Detailed address

        Returns:
            Tuple of (success, message, patient_id)
        """
        # Validate inputs
        is_valid, error = validate_required_field(name, "Name")
        if not is_valid:
            return False, error, None

        is_valid, error = validate_mobile_number(mobile_number)
        if not is_valid:
            return False, error, None

        is_valid, error = validate_age(age)
        if not is_valid:
            return False, error, None

        is_valid, error = validate_required_field(city, "City")
        if not is_valid:
            return False, error, None

        # Check if mobile number already exists
        existing = self.repository.find_by_mobile(mobile_number)
        if existing:
            return False, f"Patient with mobile number {mobile_number} already exists", None

        # Create patient
        try:
            patient_id = self.repository.create(
                name=name.strip(),
                mobile_number=mobile_number.strip(),
                age=age,
                city=city.strip(),
                address=address.strip() if address else None
            )
            return True, "Patient created successfully", patient_id
        except Exception as e:
            return False, f"Error creating patient: {str(e)}", None

    def update_patient(
        self,
        patient_id: int,
        name: str,
        mobile_number: str,
        age: int,
        city: str,
        address: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Update patient information.

        Args:
            patient_id: Patient ID
            name: Patient name
            mobile_number: Mobile number
            age: Patient age
            city: City
            address: Detailed address

        Returns:
            Tuple of (success, message)
        """
        # Validate inputs
        is_valid, error = validate_required_field(name, "Name")
        if not is_valid:
            return False, error

        is_valid, error = validate_mobile_number(mobile_number)
        if not is_valid:
            return False, error

        is_valid, error = validate_age(age)
        if not is_valid:
            return False, error

        is_valid, error = validate_required_field(city, "City")
        if not is_valid:
            return False, error

        # Check if patient exists
        if not self.repository.exists(patient_id):
            return False, "Patient not found"

        # Check if new mobile number conflicts with another patient
        existing = self.repository.find_by_mobile(mobile_number)
        if existing and existing.id != patient_id:
            return False, f"Mobile number {mobile_number} is already used by another patient"

        # Update patient
        try:
            success = self.repository.update(
                patient_id,
                name=name.strip(),
                mobile_number=mobile_number.strip(),
                age=age,
                city=city.strip(),
                address=address.strip() if address else None
            )

            if success:
                return True, "Patient updated successfully"
            else:
                return False, "Failed to update patient"
        except Exception as e:
            return False, f"Error updating patient: {str(e)}"

    def delete_patient(self, patient_id: int) -> Tuple[bool, str]:
        """Delete a patient.

        Args:
            patient_id: Patient ID

        Returns:
            Tuple of (success, message)
        """
        if not self.repository.exists(patient_id):
            return False, "Patient not found"

        try:
            success = self.repository.delete(patient_id)
            if success:
                return True, "Patient deleted successfully"
            else:
                return False, "Failed to delete patient"
        except Exception as e:
            return False, f"Error deleting patient: {str(e)}"

    def get_patient(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID.

        Args:
            patient_id: Patient ID

        Returns:
            Patient object or None
        """
        return self.repository.get_by_id(patient_id)

    def search_patients(self, query: str) -> List[Patient]:
        """Search patients.

        Args:
            query: Search query

        Returns:
            List of matching patients
        """
        if not query or not query.strip():
            return self.repository.get_all()

        return self.repository.search(query.strip())

    def get_all_patients(self) -> List[Patient]:
        """Get all patients.

        Returns:
            List of all patients
        """
        return self.repository.get_all()

    def get_recent_patients(self, limit: int = 10) -> List[Patient]:
        """Get recently added/updated patients.

        Args:
            limit: Maximum number of patients

        Returns:
            List of recent patients
        """
        return self.repository.get_recent_patients(limit)

    def get_patient_count(self) -> int:
        """Get total patient count.

        Returns:
            Number of patients
        """
        return self.repository.count()
