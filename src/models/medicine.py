"""Medicine data model."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Medicine:
    """Medicine data model."""

    id: Optional[int] = None
    name: str = ""
    common_dosage: Optional[str] = None
    category: Optional[str] = None
    medicine_type: Optional[str] = None
    brand_name: Optional[str] = None

    @classmethod
    def from_db_row(cls, row) -> 'Medicine':
        """Create Medicine instance from database row."""
        keys = row.keys() if hasattr(row, 'keys') else []
        return cls(
            id=row['id'],
            name=row['name'],
            common_dosage=row['common_dosage'],
            category=row['category'],
            medicine_type=row['medicine_type'] if 'medicine_type' in keys else None,
            brand_name=row['brand_name'] if 'brand_name' in keys else None,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'common_dosage': self.common_dosage,
            'category': self.category,
            'medicine_type': self.medicine_type,
            'brand_name': self.brand_name,
        }

    def __str__(self) -> str:
        """String representation."""
        if self.common_dosage:
            return f"{self.name} ({self.common_dosage})"
        return self.name
