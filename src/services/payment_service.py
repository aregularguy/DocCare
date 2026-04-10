"""Payment business logic service."""
from typing import List, Tuple, Optional
from datetime import date
from ..models.payment import Payment
from ..repositories.payment_repository import PaymentRepository
from ..repositories.treatment_repository import TreatmentRepository
from ..utils.validators import validate_payment_amount


class PaymentService:
    """Service for payment business logic."""

    def __init__(self):
        """Initialize payment service."""
        self.repository = PaymentRepository()
        self.treatment_repository = TreatmentRepository()

    def add_payment(
        self,
        treatment_id: int,
        amount: float,
        payment_date: date,
        payment_method: str = 'cash',
        notes: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """Add a payment for a treatment.

        Args:
            treatment_id: Treatment ID
            amount: Payment amount
            payment_date: Date of payment
            payment_method: Payment method
            notes: Additional notes

        Returns:
            Tuple of (success, message, payment_id)
        """
        # Get treatment to check pending amount
        treatment = self.treatment_repository.get_by_id(treatment_id)
        if not treatment:
            return False, "Treatment not found", None

        # Validate payment amount
        pending_amount = treatment.pending_amount
        is_valid, error = validate_payment_amount(amount, pending_amount)
        if not is_valid:
            return False, error, None

        try:
            # Create payment record
            payment_id = self.repository.create(
                treatment_id=treatment_id,
                amount=amount,
                payment_date=payment_date.isoformat(),
                payment_method=payment_method,
                notes=notes.strip() if notes else None
            )

            # Atomically increment treatment's amount_paid in a single SQL statement
            self.treatment_repository.increment_amount_paid(treatment_id, amount)

            return True, "Payment added successfully", payment_id
        except Exception as e:
            return False, f"Error adding payment: {str(e)}", None

    def get_treatment_payments(self, treatment_id: int) -> List[Payment]:
        """Get all payments for a treatment.

        Args:
            treatment_id: Treatment ID

        Returns:
            List of payments
        """
        return self.repository.get_by_treatment(treatment_id)

    def get_total_amount(self, treatment_id: int) -> float:
        """Get total amount paid for a treatment.

        Args:
            treatment_id: Treatment ID

        Returns:
            Total amount paid
        """
        return self.repository.get_total_amount(treatment_id)

    def get_payments_by_date_range(self, start_date: date, end_date: date) -> List[Payment]:
        """Get payments within date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of payments
        """
        return self.repository.get_by_date_range(start_date, end_date)

    def get_total_by_date_range(self, start_date: date, end_date: date) -> float:
        """Get total payments in date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Total amount
        """
        return self.repository.get_total_by_date_range(start_date, end_date)

    def delete_payment(self, payment_id: int) -> Tuple[bool, str]:
        """Delete a payment and update treatment amount.

        Args:
            payment_id: Payment ID

        Returns:
            Tuple of (success, message)
        """
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            return False, "Payment not found"

        try:
            # Get treatment
            treatment = self.treatment_repository.get_by_id(payment.treatment_id)
            if not treatment:
                return False, "Associated treatment not found"

            # Delete payment
            success = self.repository.delete(payment_id)
            if not success:
                return False, "Failed to delete payment"

            # Atomically decrement treatment's amount_paid, clamped to 0
            self.treatment_repository.increment_amount_paid(payment.treatment_id, -payment.amount)
            # Clamp to 0 in case of data inconsistency
            from ..database.db_manager import DatabaseManager
            DatabaseManager().execute(
                "UPDATE treatments SET amount_paid = MAX(0, amount_paid) WHERE id = ?",
                (payment.treatment_id,)
            )

            return True, "Payment deleted successfully"
        except Exception as e:
            return False, f"Error deleting payment: {str(e)}"
