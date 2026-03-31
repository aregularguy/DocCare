"""Prescription data model."""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class Prescription:
    """Prescription data model."""

    id: Optional[int] = None
    treatment_id: Optional[int] = None
    session_id: Optional[str] = None
    medicine_name: str = ""
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    prescribed_date: Optional[date] = None
    notes: Optional[str] = None

    @classmethod
    def from_db_row(cls, row) -> 'Prescription':
        """Create Prescription instance from database row."""
        keys = row.keys()
        return cls(
            id=row['id'],
            treatment_id=row['treatment_id'],
            session_id=row['session_id'] if 'session_id' in keys else None,
            medicine_name=row['medicine_name'],
            dosage=row['dosage'],
            frequency=row['frequency'],
            duration=row['duration'],
            prescribed_date=datetime.fromisoformat(row['prescribed_date']).date() if row['prescribed_date'] else None,
            notes=row['notes']
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'treatment_id': self.treatment_id,
            'medicine_name': self.medicine_name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'prescribed_date': self.prescribed_date.isoformat() if self.prescribed_date else None,
            'notes': self.notes
        }

    def __str__(self) -> str:
        """String representation."""
        parts = [self.medicine_name]
        if self.dosage:
            parts.append(f"({self.dosage})")
        if self.frequency:
            parts.append(f"- {self.frequency}")
        return " ".join(parts)
