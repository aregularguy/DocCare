"""Prescription repository."""
from typing import List
from datetime import date
from .base_repository import BaseRepository
from ..models.prescription import Prescription
from ..models.medicine import Medicine


class PrescriptionRepository(BaseRepository[Prescription]):
    """Repository for prescriptions."""

    def __init__(self):
        """Initialize prescription repository."""
        super().__init__('prescriptions', Prescription)

    def get_by_treatment(self, treatment_id: int) -> List[Prescription]:
        """Get all prescriptions for a treatment.

        Args:
            treatment_id: Treatment ID

        Returns:
            List of prescriptions
        """
        query = """
            SELECT * FROM prescriptions
            WHERE treatment_id = ?
            ORDER BY prescribed_date DESC
        """
        rows = self.db.fetch_all(query, (treatment_id,))
        return [Prescription.from_db_row(row) for row in rows]

    def get_by_date_range(self, start_date: date, end_date: date) -> List[Prescription]:
        """Get prescriptions within date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of prescriptions
        """
        query = """
            SELECT * FROM prescriptions
            WHERE prescribed_date BETWEEN ? AND ?
            ORDER BY prescribed_date DESC
        """
        rows = self.db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        return [Prescription.from_db_row(row) for row in rows]

    def get_medicine_stats(self, start_date: date, end_date: date) -> List[dict]:
        """Get prescription statistics by medicine.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of dicts with medicine name and count
        """
        query = """
            SELECT medicine_name, COUNT(*) as count
            FROM prescriptions
            WHERE prescribed_date BETWEEN ? AND ?
            GROUP BY medicine_name
            ORDER BY count DESC
        """
        rows = self.db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        return [{'medicine': row['medicine_name'], 'count': row['count']} for row in rows]


class MedicineRepository(BaseRepository[Medicine]):
    """Repository for medicines."""

    def __init__(self):
        """Initialize medicine repository."""
        super().__init__('medicines', Medicine)

    def search(self, query: str) -> List[Medicine]:
        """Search medicines by name.

        Args:
            query: Search query

        Returns:
            List of matching medicines
        """
        search_pattern = f"%{query}%"
        sql = """
            SELECT * FROM medicines
            WHERE name LIKE ?
            ORDER BY name
            LIMIT 20
        """
        rows = self.db.fetch_all(sql, (search_pattern,))
        return [Medicine.from_db_row(row) for row in rows]

    def get_by_category(self, category: str) -> List[Medicine]:
        """Get medicines by category.

        Args:
            category: Medicine category

        Returns:
            List of medicines
        """
        query = """
            SELECT * FROM medicines
            WHERE category = ?
            ORDER BY name
        """
        rows = self.db.fetch_all(query, (category,))
        return [Medicine.from_db_row(row) for row in rows]

    def get_all_categories(self) -> List[str]:
        """Get list of all medicine categories.

        Returns:
            List of category names
        """
        query = "SELECT DISTINCT category FROM medicines ORDER BY category"
        rows = self.db.fetch_all(query)
        return [row['category'] for row in rows if row['category']]
