"""Treatment repository."""
from typing import List, Optional
from datetime import date
from .base_repository import BaseRepository
from ..models.treatment import Treatment, TreatmentType


class TreatmentTypeRepository(BaseRepository[TreatmentType]):
    """Repository for treatment types."""

    def __init__(self):
        """Initialize treatment type repository."""
        super().__init__('treatment_types', TreatmentType)

    def get_by_name(self, name: str) -> Optional[TreatmentType]:
        """Get treatment type by name.

        Args:
            name: Treatment type name

        Returns:
            TreatmentType if found
        """
        query = "SELECT * FROM treatment_types WHERE name = ?"
        row = self.db.fetch_one(query, (name,))
        return TreatmentType.from_db_row(row) if row else None


class TreatmentRepository(BaseRepository[Treatment]):
    """Repository for treatments."""

    def __init__(self):
        """Initialize treatment repository."""
        super().__init__('treatments', Treatment)

    def get_by_patient(self, patient_id: int) -> List[Treatment]:
        """Get all treatments for a patient.

        Args:
            patient_id: Patient ID

        Returns:
            List of treatments
        """
        query = """
            SELECT t.*, tt.name as treatment_type_name
            FROM treatments t
            JOIN treatment_types tt ON t.treatment_type_id = tt.id
            WHERE t.patient_id = ?
            ORDER BY t.created_at DESC
        """
        rows = self.db.fetch_all(query, (patient_id,))
        return [Treatment.from_db_row(row) for row in rows]

    def get_by_status(self, status: str) -> List[Treatment]:
        """Get treatments by status.

        Args:
            status: Treatment status

        Returns:
            List of treatments
        """
        query = """
            SELECT t.*, tt.name as treatment_type_name
            FROM treatments t
            JOIN treatment_types tt ON t.treatment_type_id = tt.id
            WHERE t.status = ?
            ORDER BY t.created_at DESC
        """
        rows = self.db.fetch_all(query, (status,))
        return [Treatment.from_db_row(row) for row in rows]

    def get_pending_payments(self) -> List[Treatment]:
        """Get treatments with pending payments.

        Returns:
            List of treatments with pending amount
        """
        query = """
            SELECT t.*, tt.name as treatment_type_name
            FROM treatments t
            JOIN treatment_types tt ON t.treatment_type_id = tt.id
            WHERE t.total_cost > t.amount_paid
            ORDER BY t.created_at DESC
        """
        rows = self.db.fetch_all(query)
        return [Treatment.from_db_row(row) for row in rows]

    def get_by_date_range(self, start_date: date, end_date: date) -> List[Treatment]:
        """Get treatments within date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of treatments
        """
        query = """
            SELECT t.*, tt.name as treatment_type_name
            FROM treatments t
            JOIN treatment_types tt ON t.treatment_type_id = tt.id
            WHERE t.start_date BETWEEN ? AND ?
            ORDER BY t.start_date DESC
        """
        rows = self.db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        return [Treatment.from_db_row(row) for row in rows]

    def update_amount_paid(self, treatment_id: int, amount: float) -> bool:
        """Update amount paid for a treatment.

        Args:
            treatment_id: Treatment ID
            amount: New total amount paid

        Returns:
            True if updated successfully
        """
        return self.update(treatment_id, amount_paid=amount)

    def increment_amount_paid(self, treatment_id: int, delta: float) -> bool:
        """Atomically increment amount_paid by delta using a single SQL UPDATE.

        Args:
            treatment_id: Treatment ID
            delta: Amount to add (positive) or subtract (negative)

        Returns:
            True if updated successfully
        """
        from ..database.db_manager import DatabaseManager
        db = DatabaseManager()
        cursor = db.execute(
            "UPDATE treatments SET amount_paid = amount_paid + ? WHERE id = ?",
            (delta, treatment_id)
        )
        return cursor.rowcount > 0

    def get_treatment_type_stats(self, start_date: date, end_date: date) -> List[dict]:
        """Get treatment statistics by type.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of dicts with treatment type and count
        """
        query = """
            SELECT tt.name, COUNT(*) as count
            FROM treatments t
            JOIN treatment_types tt ON t.treatment_type_id = tt.id
            WHERE t.start_date BETWEEN ? AND ?
            GROUP BY tt.name
            ORDER BY count DESC
        """
        rows = self.db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        return [{'name': row['name'], 'count': row['count']} for row in rows]
