"""
Django Channels routing configuration.
"""
from django.urls import re_path
from apps.tracking import consumers

websocket_urlpatterns = [
    re_path(r'ws/equipment/$', consumers.EquipmentLiveStateConsumer.as_asgi()),
    re_path(r'ws/equipment/(?P<equipment_id>\w+)/$', consumers.EquipmentLiveStateConsumer.as_asgi()),
]
