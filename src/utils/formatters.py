"""Data formatting utilities."""
from datetime import date, datetime
from typing import Optional


def format_currency(amount: float) -> str:
    """Format amount as currency.

    Args:
        amount: Amount to format

    Returns:
        Formatted currency string
    """
    return f"Rs.{amount:,.2f}"


def format_date(date_obj: Optional[date]) -> str:
    """Format date for display.

    Args:
        date_obj: Date object

    Returns:
        Formatted date string
    """
    if not date_obj:
        return "N/A"

    return date_obj.strftime("%d-%m-%Y")


def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime object

    Returns:
        Formatted datetime string
    """
    if not dt:
        return "N/A"

    return dt.strftime("%d-%m-%Y %I:%M %p")


def format_mobile(mobile: str) -> str:
    """Format mobile number for display.

    Args:
        mobile: Mobile number

    Returns:
        Formatted mobile number
    """
    if len(mobile) == 10:
        return f"{mobile[:5]} {mobile[5:]}"
    return mobile


def format_percentage(value: float, total: float) -> str:
    """Format as percentage.

    Args:
        value: Numerator value
        total: Denominator value

    Returns:
        Formatted percentage string
    """
    if total == 0:
        return "0%"

    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."
