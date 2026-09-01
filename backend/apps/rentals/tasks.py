"""
Celery tasks for rentals app.
"""
from celery import shared_task
from django.utils import timezone
from .models import Rental
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService
from common.utilities import get_utc_now


@shared_task
def check_overdue_rentals():
    """Check for overdue rentals and create notifications."""
    now = get_utc_now()
    
    # Find active rentals that are past due date
    overdue_rentals = Rental.objects.filter(
        status__in=[Rental.STATUS_CHECKED_OUT, Rental.STATUS_ACTIVE],
        due_at__lt=now,
        checkin_at__isnull=True
    )
    
    for rental in overdue_rentals:
        # Update rental status to OVERDUE
        rental.status = Rental.STATUS_OVERDUE
        rental.save()
        
        # Create notification
        try:
            NotificationService.create_overdue_notification(rental)
        except Exception as e:
            print(f"Error creating notification for overdue rental {rental.id}: {e}")
    
    return f"Checked {len(overdue_rentals)} rentals"
