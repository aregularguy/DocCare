"""Treatment business logic service."""
from typing import List, Optional, Tuple
from datetime import date
from ..models.treatment import Treatment, TreatmentType
from ..repositories.treatment_repository import TreatmentRepository, TreatmentTypeRepository
from ..utils.validators import validate_amount


class TreatmentService:
    """Service for treatment business logic."""

    def __init__(self):
        """Initialize treatment service."""
        self.repository = TreatmentRepository()
        self.type_repository = TreatmentTypeRepository()

    def create_treatment(
        self,
        patient_id: int,
        treatment_type_id: int,
        total_cost: float,
        status: str = 'planned',
        start_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """Create a new treatment.

        Args:
            patient_id: Patient ID
            treatment_type_id: Treatment type ID
            total_cost: Total treatment cost
            status: Treatment status
            start_date: Treatment start date
            notes: Additional notes

        Returns:
            Tuple of (success, message, treatment_id)
        """
        # Validate inputs
        is_valid, error = validate_amount(total_cost, "Treatment cost")
        if not is_valid:
            return False, error, None

        # Verify treatment type exists
        if not self.type_repository.exists(treatment_type_id):
            return False, "Invalid treatment type", None

        try:
            treatment_id = self.repository.create(
                patient_id=patient_id,
                treatment_type_id=treatment_type_id,
                total_cost=total_cost,
                amount_paid=0.0,
                status=status,
                start_date=start_date.isoformat() if start_date else None,
                notes=notes.strip() if notes else None
            )
            return True, "Treatment created successfully", treatment_id
        except Exception as e:
            return False, f"Error creating treatment: {str(e)}", None

    def update_treatment(
        self,
        treatment_id: int,
        total_cost: Optional[float] = None,
        status: Optional[str] = None,
        completion_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Update treatment information.

        Args:
            treatment_id: Treatment ID
            total_cost: New total cost
            status: New status
            completion_date: Completion date
            notes: New notes

        Returns:
            Tuple of (success, message)
        """
        if not self.repository.exists(treatment_id):
            return False, "Treatment not found"

        updates = {}

        if total_cost is not None:
            is_valid, error = validate_amount(total_cost, "Treatment cost")
            if not is_valid:
                return False, error
            updates['total_cost'] = total_cost

        if status is not None:
            if status not in ['planned', 'in_progress', 'completed']:
                return False, "Invalid status"
            updates['status'] = status

        if completion_date is not None:
            updates['completion_date'] = completion_date.isoformat()

        if notes is not None:
            updates['notes'] = notes.strip()

        try:
            success = self.repository.update(treatment_id, **updates)
            if success:
                return True, "Treatment updated successfully"
            else:
                return False, "Failed to update treatment"
        except Exception as e:
            return False, f"Error updating treatment: {str(e)}"

    def get_treatment(self, treatment_id: int) -> Optional[Treatment]:
        """Get treatment by ID.

        Args:
            treatment_id: Treatment ID

        Returns:
            Treatment object or None
        """
        return self.repository.get_by_id(treatment_id)

    def get_patient_treatments(self, patient_id: int) -> List[Treatment]:
        """Get all treatments for a patient.

        Args:
            patient_id: Patient ID

        Returns:
            List of treatments
        """
        return self.repository.get_by_patient(patient_id)

    def get_all_treatment_types(self) -> List[TreatmentType]:
        """Get all treatment types.

        Returns:
            List of treatment types
        """
        return self.type_repository.get_all()

    def get_pending_payments(self) -> List[Treatment]:
        """Get treatments with pending payments.

        Returns:
            List of treatments
        """
        return self.repository.get_pending_payments()

    def get_pending_with_patient_names(self) -> list[dict]:
        """Get all treatments with pending amounts, including patient name."""
        treatments = self.repository.get_pending_payments()
        from .patient_service import PatientService
        patient_svc = PatientService()
        result = []
        patient_cache = {}
        for t in treatments:
            if t.patient_id not in patient_cache:
                p = patient_svc.get_patient(t.patient_id)
                patient_cache[t.patient_id] = p
            patient = patient_cache[t.patient_id]
            result.append({
                'treatment': t,
                'patient_name': patient.name if patient else '—',
                'patient_mobile': patient.mobile_number if patient else '',
                'patient_id': t.patient_id,
            })
        return result
