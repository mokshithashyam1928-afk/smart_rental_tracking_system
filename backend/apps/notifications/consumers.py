"""
WebSocket consumer for the live dashboard.

Clients connect to ws://localhost:8000/ws/dashboard/ and receive:
  - dashboard.fleet_update  → updated fleet counts (total, available, rented, overdue)
  - dashboard.overdue_alert → an overdue return alert for a specific vehicle

No authentication required for read-only dashboard consumers in dev.
For production, add AuthMiddlewareStack in routing.
"""
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

DASHBOARD_GROUP = 'dashboard'


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time fleet dashboard updates.
    Joins the 'dashboard' channel layer group and relays events
    published by the Kafka/in-process consumer to the browser.
    """

    async def connect(self):
        await self.channel_layer.group_add(DASHBOARD_GROUP, self.channel_name)
        await self.accept()
        logger.debug(f"[DashboardConsumer] Client connected: {self.channel_name}")

        # Send the current fleet summary immediately on connect
        summary = await self._get_fleet_summary()
        await self.send(text_data=json.dumps({
            'type': 'dashboard.fleet_update',
            'payload': {
                'event_type': 'initial_load',
                'summary': summary,
            },
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(DASHBOARD_GROUP, self.channel_name)
        logger.debug(f"[DashboardConsumer] Client disconnected: {self.channel_name}")

    # ------------------------------------------------------------------ #
    # Message handlers (called by channel layer group_send)
    # ------------------------------------------------------------------ #

    async def dashboard_fleet_update(self, event):
        """Relay a fleet_update event to the WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'dashboard.fleet_update',
            'payload': event.get('payload', {}),
        }))

    async def dashboard_overdue_alert(self, event):
        """Relay an overdue_alert event to the WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'dashboard.overdue_alert',
            'payload': event.get('payload', {}),
        }))

    # ------------------------------------------------------------------ #
    # DB helpers
    # ------------------------------------------------------------------ #

    @database_sync_to_async
    def _get_fleet_summary(self) -> dict:
        try:
            from apps.equipment.models import Equipment
            from apps.rentals.models import Rental
            from django.utils import timezone

            now = timezone.now()
            return {
                'total': Equipment.objects.count(),
                'available': Equipment.objects.filter(status=Equipment.STATUS_AVAILABLE).count(),
                'rented': Equipment.objects.filter(
                    status__in=[Equipment.STATUS_RENTED, Equipment.STATUS_IN_USE]
                ).count(),
                'overdue': Rental.objects.filter(
                    status__in=[Rental.STATUS_OVERDUE, Rental.STATUS_ACTIVE],
                    due_at__lt=now,
                    checkin_at__isnull=True,
                ).count(),
            }
        except Exception as exc:
            logger.warning(f"[DashboardConsumer] Fleet summary failed: {exc}")
            return {'total': 0, 'available': 0, 'rented': 0, 'overdue': 0}
