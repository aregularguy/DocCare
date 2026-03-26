"""Payment data model."""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class Payment:
    """Payment data model."""

    id: Optional[int] = None
    treatment_id: Optional[int] = None
    amount: float = 0.0
    payment_date: Optional[date] = None
    payment_method: str = 'cash'
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row) -> 'Payment':
        """Create Payment instance from database row."""
        return cls(
            id=row['id'],
            treatment_id=row['treatment_id'],
            amount=float(row['amount']),
            payment_date=datetime.fromisoformat(row['payment_date']).date() if row['payment_date'] else None,
            payment_method=row['payment_method'],
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'treatment_id': self.treatment_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __str__(self) -> str:
        """String representation."""
        date_str = self.payment_date.strftime('%Y-%m-%d') if self.payment_date else 'N/A'
        return f"₹{self.amount:.2f} - {self.payment_method} ({date_str})"
