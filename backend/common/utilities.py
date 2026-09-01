"""
Common utilities for Smart Rental Tracking System backend.
"""
from django.utils import timezone
from datetime import datetime


def get_utc_now():
    """Get current UTC timestamp."""
    return timezone.now()


def is_overdue(due_at, now=None):
    """Check if a rental is overdue."""
    if now is None:
        now = get_utc_now()
    return now > due_at


def get_time_difference_seconds(dt1, dt2):
    """Get the difference in seconds between two datetime objects."""
    diff = dt1 - dt2
    return diff.total_seconds()


def format_timestamp(dt):
    """Format a datetime object to ISO 8601 string."""
    return dt.isoformat() if dt else None
