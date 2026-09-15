"""Payment repository."""
from typing import List
from datetime import date
from .base_repository import BaseRepository
from ..models.payment import Payment


class PaymentRepository(BaseRepository[Payment]):
    """Repository for payments."""

    def __init__(self):
        """Initialize payment repository."""
        super().__init__('payments', Payment)

    def get_by_treatment(self, treatment_id: int) -> List[Payment]:
        """Get all payments for a treatment.

        Args:
            treatment_id: Treatment ID

        Returns:
            List of payments
        """
        query = """
            SELECT * FROM payments
            WHERE treatment_id = ?
            ORDER BY payment_date DESC
        """
        rows = self.db.fetch_all(query, (treatment_id,))
        return [Payment.from_db_row(row) for row in rows]

    def get_by_date_range(self, start_date: date, end_date: date) -> List[Payment]:
        """Get payments within date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of payments
        """
        query = """
            SELECT * FROM payments
            WHERE payment_date BETWEEN ? AND ?
            ORDER BY payment_date DESC
        """
        rows = self.db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        return [Payment.from_db_row(row) for row in rows]

    def get_total_amount(self, treatment_id: int) -> float:
        """Get total amount paid for a treatment.

        Args:
            treatment_id: Treatment ID

        Returns:
            Total amount paid
        """
        query = """
            SELECT SUM(amount) as total FROM payments
            WHERE treatment_id = ?
        """
        row = self.db.fetch_one(query, (treatment_id,))
        return float(row['total']) if row and row['total'] else 0.0

    def get_total_by_date_range(self, start_date: date, end_date: date) -> float:
        """Get total payments in date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Total amount
        """
        query = """
            SELECT SUM(amount) as total FROM payments
            WHERE payment_date BETWEEN ? AND ?
        """
        row = self.db.fetch_one(query, (start_date.isoformat(), end_date.isoformat()))
        return float(row['total']) if row and row['total'] else 0.0

    def get_payment_method_stats(self, start_date: date, end_date: date) -> List[dict]:
        """Get payment statistics by method.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of dicts with payment method, count, and total
        """
        query = """
            SELECT payment_method, COUNT(*) as count, SUM(amount) as total
            FROM payments
            WHERE payment_date BETWEEN ? AND ?
            GROUP BY payment_method
            ORDER BY total DESC
        """
        rows = self.db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        return [
            {
                'method': row['payment_method'],
                'count': row['count'],
                'total': float(row['total'])
            }
            for row in rows
        ]

    def get_recent_payments(self, limit: int = 10) -> List[Payment]:
        """Get recent payments.

        Args:
            limit: Maximum number of payments

        Returns:
            List of recent payments
        """
        query = """
            SELECT * FROM payments
            ORDER BY payment_date DESC, created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (limit,))
        return [Payment.from_db_row(row) for row in rows]
