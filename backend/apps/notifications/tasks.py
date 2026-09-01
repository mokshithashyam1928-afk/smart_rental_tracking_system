"""
Celery tasks for notifications.
"""
from celery import shared_task


@shared_task
def generate_notifications():
    """Generate daily notifications."""
    # Placeholder for Phase 2 implementation
    return "Notifications generated"
