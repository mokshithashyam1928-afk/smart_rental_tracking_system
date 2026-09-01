"""
Celery configuration for Smart Rental Tracking System backend.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('smart_rental_tracking')

# Load configuration from Django settings, all config keys should have a `CELERY_` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'check-overdue-rentals-every-5-minutes': {
        'task': 'apps.rentals.tasks.check_overdue_rentals',
        'schedule': crontab(minute='*/5'),
    },
    'check-offline-equipment-every-5-minutes': {
        'task': 'apps.telemetry.tasks.check_offline_equipment',
        'schedule': crontab(minute='*/5'),
    },
    'aggregate-daily-usage-at-midnight': {
        'task': 'apps.analytics.tasks.aggregate_daily_usage',
        'schedule': crontab(hour=0, minute=0),
    },
    'generate-daily-notifications-at-6am': {
        'task': 'apps.notifications.tasks.generate_notifications',
        'schedule': crontab(hour=6, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
