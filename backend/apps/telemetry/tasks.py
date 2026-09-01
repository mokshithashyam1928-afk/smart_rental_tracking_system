"""
Celery tasks for telemetry app.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from apps.equipment.models import Equipment
from apps.notifications.models import Notification
from .models import EquipmentLiveState
from common.utilities import get_utc_now, get_time_difference_seconds


@shared_task
def check_offline_equipment():
    """Check for offline equipment and create notifications."""
    threshold = settings.EQUIPMENT_OFFLINE_THRESHOLD_SECONDS
    now = get_utc_now()
    
    offline_states = EquipmentLiveState.objects.filter(
        last_seen__lt=timezone.now() - timezone.timedelta(seconds=threshold)
    )
    
    for state in offline_states:
        # Update equipment status to OFFLINE if not already
        if state.equipment.status != Equipment.STATUS_OFFLINE:
            state.equipment.status = Equipment.STATUS_OFFLINE
            state.equipment.save()
            
            state.status = Equipment.STATUS_OFFLINE
            state.save()
            
            # Create notification
            try:
                Notification.objects.get_or_create(
                    type=Notification.TYPE_OFFLINE,
                    defaults={
                        'equipment': state.equipment,
                        'title': f'Equipment {state.equipment.equipment_id} is offline',
                        'message': f'Equipment has not reported status for over {threshold}s',
                        'severity': Notification.SEVERITY_WARNING
                    }
                )
            except Exception as e:
                print(f"Error creating offline notification: {e}")
    
    return f"Checked offline status for {offline_states.count()} equipment"
