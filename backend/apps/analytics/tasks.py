"""
Celery tasks for analytics.
"""
from celery import shared_task


@shared_task
def aggregate_daily_usage():
    """Aggregate daily usage statistics (Phase 2)."""
    return "Daily usage aggregated"
