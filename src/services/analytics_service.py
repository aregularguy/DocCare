"""Analytics business logic service."""
from typing import Dict, List
from datetime import date, datetime, timedelta
from ..repositories.patient_repository import PatientRepository
from ..repositories.treatment_repository import TreatmentRepository
from ..repositories.payment_repository import PaymentRepository
from ..repositories.prescription_repository import PrescriptionRepository


class AnalyticsService:
    """Service for analytics and reporting."""

    def __init__(self):
        """Initialize analytics service."""
        self.patient_repo = PatientRepository()
        self.treatment_repo = TreatmentRepository()
        self.payment_repo = PaymentRepository()
        self.prescription_repo = PrescriptionRepository()

    def get_date_range(self, period: str) -> tuple[date, date]:
        """Get date range for a period.

        Args:
            period: One of 'today', 'week', 'month', 'year'

        Returns:
            Tuple of (start_date, end_date)
        """
        today = date.today()

        if period == 'today':
            return today, today
        elif period == 'week':
            start = today - timedelta(days=today.weekday())  # Monday
            return start, today
        elif period == 'month':
            start = date(today.year, today.month, 1)
            return start, today
        elif period == 'year':
            start = date(today.year, 1, 1)
            return start, today
        else:
            return today, today

    def get_patient_metrics(self, start_date: date, end_date: date) -> Dict:
        """Get patient metrics for date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with patient metrics
        """
        # Total patients (all time)
        total_patients = self.patient_repo.count()

        # New patients in period
        all_patients = self.patient_repo.get_all()
        new_patients = sum(
            1 for p in all_patients
            if p.created_at and start_date <= p.created_at.date() <= end_date
        )

        return {
            'total_patients': total_patients,
            'new_patients': new_patients
        }

    def get_payment_metrics(self, start_date: date, end_date: date) -> Dict:
        """Get payment metrics for date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with payment metrics
        """
        # Total payments in period
        total_amount = self.payment_repo.get_total_by_date_range(start_date, end_date)

        # Payment count
        payments = self.payment_repo.get_by_date_range(start_date, end_date)
        payment_count = len(payments)

        # Average payment
        avg_payment = total_amount / payment_count if payment_count > 0 else 0

        # Payment method breakdown
        payment_methods = self.payment_repo.get_payment_method_stats(start_date, end_date)

        return {
            'total_amount': total_amount,
            'payment_count': payment_count,
            'average_payment': avg_payment,
            'payment_methods': payment_methods
        }

    def get_treatment_metrics(self, start_date: date, end_date: date) -> Dict:
        """Get treatment metrics for date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with treatment metrics
        """
        # Treatments in period
        treatments = self.treatment_repo.get_by_date_range(start_date, end_date)
        treatment_count = len(treatments)

        # Treatment type breakdown
        treatment_types = self.treatment_repo.get_treatment_type_stats(start_date, end_date)

        # Pending payments
        pending_treatments = self.treatment_repo.get_pending_payments()
        pending_amount = sum(t.pending_amount for t in pending_treatments)

        return {
            'treatment_count': treatment_count,
            'treatment_types': treatment_types,
            'pending_treatments': len(pending_treatments),
            'pending_amount': pending_amount
        }

    def get_prescription_metrics(self, start_date: date, end_date: date) -> Dict:
        """Get prescription metrics for date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with prescription metrics
        """
        # Prescriptions in period
        prescriptions = self.prescription_repo.get_by_date_range(start_date, end_date)
        prescription_count = len(prescriptions)

        # Medicine breakdown
        medicine_stats = self.prescription_repo.get_medicine_stats(start_date, end_date)

        # Unique medicines count
        unique_medicines = len(medicine_stats)

        return {
            'prescription_count': prescription_count,
            'unique_medicines': unique_medicines,
            'medicine_stats': medicine_stats
        }

    def get_dashboard_data(self, period: str = 'today') -> Dict:
        """Get complete dashboard data for a period.

        Args:
            period: One of 'today', 'week', 'month', 'year'

        Returns:
            Dictionary with all metrics
        """
        start_date, end_date = self.get_date_range(period)

        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'patients': self.get_patient_metrics(start_date, end_date),
            'payments': self.get_payment_metrics(start_date, end_date),
            'treatments': self.get_treatment_metrics(start_date, end_date),
            'prescriptions': self.get_prescription_metrics(start_date, end_date)
        }

    def get_daily_payments(self, start_date: date, end_date: date) -> List[Dict]:
        """Get daily payment totals for charting.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of dicts with date and amount
        """
        payments = self.payment_repo.get_by_date_range(start_date, end_date)

        # Group by date
        daily_totals = {}
        current = start_date
        while current <= end_date:
            daily_totals[current] = 0.0
            current += timedelta(days=1)

        for payment in payments:
            if payment.payment_date in daily_totals:
                daily_totals[payment.payment_date] += payment.amount

        return [
            {'date': date.isoformat(), 'amount': amount}
            for date, amount in sorted(daily_totals.items())
        ]
