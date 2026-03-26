"""Patient repository."""
from typing import List, Optional
from .base_repository import BaseRepository
from ..models.patient import Patient


class PatientRepository(BaseRepository[Patient]):
    """Repository for patient data access."""

    def __init__(self):
        """Initialize patient repository."""
        super().__init__('patients', Patient)

    def search(self, query: str) -> List[Patient]:
        """Search patients by name, mobile, or city.

        Args:
            query: Search query string

        Returns:
            List of matching patients
        """
        search_pattern = f"%{query}%"
        sql = """
            SELECT * FROM patients
            WHERE name LIKE ? OR mobile_number LIKE ? OR city LIKE ?
            ORDER BY name
        """
        rows = self.db.fetch_all(sql, (search_pattern, search_pattern, search_pattern))
        return [Patient.from_db_row(row) for row in rows]

    def find_by_mobile(self, mobile_number: str) -> Optional[Patient]:
        """Find patient by mobile number.

        Args:
            mobile_number: Mobile number to search

        Returns:
            Patient if found, None otherwise
        """
        query = "SELECT * FROM patients WHERE mobile_number = ?"
        row = self.db.fetch_one(query, (mobile_number,))
        return Patient.from_db_row(row) if row else None

    def get_recent_patients(self, limit: int = 10) -> List[Patient]:
        """Get recently added or updated patients.

        Args:
            limit: Maximum number of patients to return

        Returns:
            List of recent patients
        """
        query = f"""
            SELECT * FROM patients
            ORDER BY updated_at DESC
            LIMIT {limit}
        """
        rows = self.db.fetch_all(query)
        return [Patient.from_db_row(row) for row in rows]

    def get_by_city(self, city: str) -> List[Patient]:
        """Get all patients from a specific city.

        Args:
            city: City name

        Returns:
            List of patients
        """
        query = "SELECT * FROM patients WHERE city = ? ORDER BY name"
        rows = self.db.fetch_all(query, (city,))
        return [Patient.from_db_row(row) for row in rows]

    def get_all_cities(self) -> List[str]:
        """Get list of all unique cities.

        Returns:
            List of city names
        """
        query = "SELECT DISTINCT city FROM patients ORDER BY city"
        rows = self.db.fetch_all(query)
        return [row['city'] for row in rows]
