"""Prescription business logic service."""
from typing import List, Tuple, Optional
from datetime import date
from ..models.prescription import Prescription
from ..models.medicine import Medicine
from ..repositories.prescription_repository import PrescriptionRepository, MedicineRepository
from ..utils.validators import validate_required_field


class PrescriptionService:
    """Service for prescription business logic."""

    def __init__(self):
        """Initialize prescription service."""
        self.repository = PrescriptionRepository()
        self.medicine_repository = MedicineRepository()

    def add_prescription(
        self,
        treatment_id: int,
        medicine_name: str,
        session_id: Optional[str] = None,
        dosage: Optional[str] = None,
        frequency: Optional[str] = None,
        duration: Optional[str] = None,
        prescribed_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """Add a prescription.

        Args:
            treatment_id: Treatment ID
            medicine_name: Medicine name
            dosage: Dosage information
            frequency: Frequency (e.g., "3 times daily")
            duration: Duration (e.g., "7 days")
            prescribed_date: Date of prescription
            notes: Additional notes

        Returns:
            Tuple of (success, message, prescription_id)
        """
        # Validate inputs
        is_valid, error = validate_required_field(medicine_name, "Medicine name")
        if not is_valid:
            return False, error, None

        if prescribed_date is None:
            prescribed_date = date.today()

        try:
            prescription_id = self.repository.create(
                treatment_id=treatment_id,
                session_id=session_id,
                medicine_name=medicine_name.strip(),
                dosage=dosage.strip() if dosage else None,
                frequency=frequency.strip() if frequency else None,
                duration=duration.strip() if duration else None,
                prescribed_date=prescribed_date.isoformat(),
                notes=notes.strip() if notes else None
            )
            return True, "Prescription added successfully", prescription_id
        except Exception as e:
            return False, f"Error adding prescription: {str(e)}", None

    def get_treatment_prescriptions(self, treatment_id: int) -> List[Prescription]:
        """Get all prescriptions for a treatment.

        Args:
            treatment_id: Treatment ID

        Returns:
            List of prescriptions
        """
        return self.repository.get_by_treatment(treatment_id)

    def search_medicines(self, query: str) -> List[Medicine]:
        """Search for medicines.

        Args:
            query: Search query

        Returns:
            List of matching medicines
        """
        if not query or not query.strip():
            return []
        return self.medicine_repository.search(query.strip())

    def get_all_medicines(self) -> List[Medicine]:
        """Get all medicines.

        Returns:
            List of medicines
        """
        return self.medicine_repository.get_all()

    def delete_prescription(self, prescription_id: int) -> Tuple[bool, str]:
        """Delete a prescription.

        Args:
            prescription_id: Prescription ID

        Returns:
            Tuple of (success, message)
        """
        if not self.repository.exists(prescription_id):
            return False, "Prescription not found"

        try:
            success = self.repository.delete(prescription_id)
            if success:
                return True, "Prescription deleted successfully"
            else:
                return False, "Failed to delete prescription"
        except Exception as e:
            return False, f"Error deleting prescription: {str(e)}"
