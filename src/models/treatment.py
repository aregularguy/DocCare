"""Treatment data model."""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class TreatmentType:
    """Treatment type data model."""

    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None

    @classmethod
    def from_db_row(cls, row) -> 'TreatmentType':
        """Create TreatmentType instance from database row."""
        return cls(
            id=row['id'],
            name=row['name'],
            description=row['description']
        )

    def __str__(self) -> str:
        """String representation."""
        return self.name


@dataclass
class Treatment:
    """Treatment data model."""

    id: Optional[int] = None
    patient_id: Optional[int] = None
    treatment_type_id: Optional[int] = None
    treatment_type_name: Optional[str] = None  # For display purposes
    total_cost: float = 0.0
    amount_paid: float = 0.0
    status: str = 'planned'
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row) -> 'Treatment':
        """Create Treatment instance from database row."""
        return cls(
            id=row['id'],
            patient_id=row['patient_id'],
            treatment_type_id=row['treatment_type_id'],
            treatment_type_name=row.get('treatment_type_name'),
            total_cost=float(row['total_cost']),
            amount_paid=float(row['amount_paid']),
            status=row['status'],
            start_date=datetime.fromisoformat(row['start_date']).date() if row['start_date'] else None,
            completion_date=datetime.fromisoformat(row['completion_date']).date() if row['completion_date'] else None,
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    @property
    def pending_amount(self) -> float:
        """Calculate pending payment amount."""
        return max(0.0, self.total_cost - self.amount_paid)

    @property
    def is_paid(self) -> bool:
        """Check if treatment is fully paid."""
        return self.pending_amount <= 0.01  # Small tolerance for float comparison

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'treatment_type_id': self.treatment_type_id,
            'treatment_type_name': self.treatment_type_name,
            'total_cost': self.total_cost,
            'amount_paid': self.amount_paid,
            'pending_amount': self.pending_amount,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __str__(self) -> str:
        """String representation."""
        return f"{self.treatment_type_name} - ₹{self.total_cost:.2f}"
