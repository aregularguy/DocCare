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

    @classmethod
    def from_db_row(cls, row) -> 'Medicine':
        """Create Medicine instance from database row."""
        return cls(
            id=row['id'],
            name=row['name'],
            common_dosage=row['common_dosage'],
            category=row['category']
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'common_dosage': self.common_dosage,
            'category': self.category
        }

    def __str__(self) -> str:
        """String representation."""
        if self.common_dosage:
            return f"{self.name} ({self.common_dosage})"
        return self.name
