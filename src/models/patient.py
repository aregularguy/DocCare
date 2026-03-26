"""Patient data model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Patient:
    """Patient data model."""

    id: Optional[int] = None
    name: str = ""
    mobile_number: str = ""
    age: int = 0
    city: str = ""
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row) -> 'Patient':
        """Create Patient instance from database row.

        Args:
            row: SQLite row object

        Returns:
            Patient instance
        """
        return cls(
            id=row['id'],
            name=row['name'],
            mobile_number=row['mobile_number'],
            age=row['age'],
            city=row['city'],
            address=row['address'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'mobile_number': self.mobile_number,
            'age': self.age,
            'city': self.city,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name} ({self.mobile_number})"
