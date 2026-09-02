"""
Domain event handlers.

Each handler receives a CloudEvents-compliant event envelope and performs
the appropriate side-effect:
  - rental events   → push live fleet summary via Django Channels WebSocket
  - anomaly events  → push overdue alert notification via WebSocket
  - telemetry events → update equipment live state cache
"""
import json
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_fleet_summary() -> dict:
    """Read current fleet counts directly from the DB (real data only)."""
    try:
        from apps.equipment.models import Equipment
        from apps.rentals.models import Rental
        from django.utils import timezone

        now = timezone.now()
        total = Equipment.objects.count()
        available = Equipment.objects.filter(status=Equipment.STATUS_AVAILABLE).count()
        rented = Equipment.objects.filter(
            status__in=[Equipment.STATUS_RENTED, Equipment.STATUS_IN_USE]
        ).count()
        overdue = Rental.objects.filter(
            status__in=[Rental.STATUS_OVERDUE, Rental.STATUS_ACTIVE],
            due_at__lt=now,
            checkin_at__isnull=True,
        ).count()

        return {
            'total': total,
            'available': available,
            'rented': rented,
            'overdue': overdue,
        }
    except Exception as exc:
        logger.warning(f"[EventHandler] Fleet summary query failed: {exc}")
        return {}


def _broadcast_ws(group: str, message_type: str, payload: dict):
    """Send a message to a Django Channels channel layer group (async-safe)."""
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.debug("[EventHandler] No channel layer configured – skipping WS broadcast")
            return
        async_to_sync(channel_layer.group_send)(
            group,
            {'type': message_type, 'payload': payload},
        )
    except Exception as exc:
        logger.warning(f"[EventHandler] WebSocket broadcast failed: {exc}")


# ---------------------------------------------------------------------------
# Topic handlers
# ---------------------------------------------------------------------------

def handle_rental_event(event: dict):
    """
    Handle a rental lifecycle event (checkout, checkin, overdue-marked).
    Broadcasts the updated fleet summary to the 'dashboard' WebSocket group.
    """
    event_type = event.get('type', '')
    data = event.get('data', {})
    logger.info(f"[RentalHandler] Processing event: {event_type}")

    summary = _get_fleet_summary()
    _broadcast_ws(
        group='dashboard',
        message_type='dashboard.fleet_update',
        payload={
            'event_type': event_type,
            'summary': summary,
            'equipment_id': data.get('equipment_id'),
            'action': data.get('action'),
            'site': data.get('site'),
        },
    )


def handle_anomaly_event(event: dict):
    """
    Handle an anomaly / overdue alert event.
    Broadcasts the alert to the 'dashboard' WebSocket group.
    """
    event_type = event.get('type', '')
    data = event.get('data', {})
    logger.info(f"[AnomalyHandler] Processing anomaly event: {event_type}")

    _broadcast_ws(
        group='dashboard',
        message_type='dashboard.overdue_alert',
        payload={
            'event_type': event_type,
            'equipment_id': data.get('equipment_id'),
            'model': data.get('model'),
            'operator': data.get('operator'),
            'site': data.get('site'),
            'overdue_hours': data.get('overdue_hours', 0),
            'message': data.get('message', 'Vehicle return is overdue'),
        },
    )


def handle_telemetry_event(event: dict):
    """
    Handle a telemetry event (machine state change, GPS update, engine hours).
    Updates the equipment live state in cache/DB if available.
    """
    event_type = event.get('type', '')
    data = event.get('data', {})
    logger.info(f"[TelemetryHandler] Processing telemetry event: {event_type}")
    # Future: write to EquipmentLiveState model for GPS/sensor tracking
    _broadcast_ws(
        group='dashboard',
        message_type='dashboard.fleet_update',
        payload={'event_type': event_type, 'summary': _get_fleet_summary()},
    )


# ---------------------------------------------------------------------------
# Topic-to-handler routing map
# ---------------------------------------------------------------------------

TOPIC_HANDLERS = {
    'smart-rental.rental.events': handle_rental_event,
    'smart-rental.anomaly.events': handle_anomaly_event,
    'smart-rental.telemetry.events': handle_telemetry_event,
}
