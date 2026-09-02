"""
Django Channels routing configuration.
"""
from django.urls import re_path
from apps.tracking import consumers as tracking_consumers
from apps.notifications import consumers as notification_consumers

websocket_urlpatterns = [
    re_path(r'ws/equipment/$', tracking_consumers.EquipmentLiveStateConsumer.as_asgi()),
    re_path(r'ws/equipment/(?P<equipment_id>\w+)/$', tracking_consumers.EquipmentLiveStateConsumer.as_asgi()),
    # Live dashboard fleet updates & overdue alerts
    re_path(r'ws/dashboard/$', notification_consumers.DashboardConsumer.as_asgi()),
]
