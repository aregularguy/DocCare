"""Input validation utilities."""
import re
from typing import Tuple


def validate_mobile_number(mobile: str) -> Tuple[bool, str]:
    """Validate mobile number format.

    Args:
        mobile: Mobile number string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not mobile:
        return False, "Mobile number is required"

    # Remove spaces and hyphens
    mobile_clean = re.sub(r'[\s\-]', '', mobile)

    # Check if it contains only digits
    if not mobile_clean.isdigit():
        return False, "Mobile number must contain only digits"

    # Check length (10 digits for India)
    if len(mobile_clean) != 10:
        return False, "Mobile number must be 10 digits"

    return True, ""


def validate_age(age: int) -> Tuple[bool, str]:
    """Validate patient age.

    Args:
        age: Age in years

    Returns:
        Tuple of (is_valid, error_message)
    """
    if age <= 0:
        return False, "Age must be greater than 0"

    if age > 120:
        return False, "Age must be less than 120"

    return True, ""


def validate_amount(amount: float, field_name: str = "Amount") -> Tuple[bool, str]:
    """Validate monetary amount.

    Args:
        amount: Amount to validate
        field_name: Name of the field for error message

    Returns:
        Tuple of (is_valid, error_message)
    """
    if amount < 0:
        return False, f"{field_name} cannot be negative"

    if amount == 0:
        return False, f"{field_name} must be greater than 0"

    return True, ""


def validate_required_field(value: str, field_name: str) -> Tuple[bool, str]:
    """Validate required text field.

    Args:
        value: Field value
        field_name: Name of the field for error message

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name} is required"

    return True, ""


def validate_payment_amount(amount: float, pending_amount: float) -> Tuple[bool, str]:
    """Validate payment amount against pending amount.

    Args:
        amount: Payment amount
        pending_amount: Remaining amount to be paid

    Returns:
        Tuple of (is_valid, error_message)
    """
    is_valid, error = validate_amount(amount, "Payment amount")
    if not is_valid:
        return is_valid, error

    if amount > pending_amount:
        return False, f"Payment amount (₹{amount:.2f}) cannot exceed pending amount (₹{pending_amount:.2f})"

    return True, ""
