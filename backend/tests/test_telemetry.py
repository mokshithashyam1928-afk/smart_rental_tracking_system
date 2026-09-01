"""
Tests for telemetry ingestion and live state updates.
"""
import pytest
from django.utils import timezone
from rest_framework import status
from apps.telemetry.models import Telemetry, EquipmentLiveState


@pytest.mark.django_db
class TestTelemetryAPI:
    def test_ingest_telemetry_event(self, authenticated_client, equipment, operator):
        payload = {
            'event_id': 'TEL-EVT-001',
            'equipment_id': equipment.equipment_id,
            'timestamp': timezone.now().isoformat(),
            'latitude': 12.9716,
            'longitude': 77.5946,
            'engine_hours': 15.5,
            'idle_hours': 2.5,
            'fuel_level': 75.0,
            'fuel_consumed': 5.0,
            'speed': 12.4,
            'operator_id': operator.employee_id
        }
        response = authenticated_client.post('/api/telemetry/ingest/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Telemetry.objects.filter(event_id='TEL-EVT-001').exists()

        # Check live state updated
        live_state = EquipmentLiveState.objects.get(equipment=equipment)
        assert live_state.engine_hours == 15.5
        assert live_state.fuel_level == 75.0

    def test_duplicate_telemetry_event_idempotency(self, authenticated_client, equipment, operator):
        payload = {
            'event_id': 'TEL-EVT-DUPE',
            'equipment_id': equipment.equipment_id,
            'timestamp': timezone.now().isoformat(),
            'latitude': 12.9716,
            'longitude': 77.5946,
            'engine_hours': 20.0,
            'idle_hours': 3.0,
            'fuel_level': 80.0,
            'speed': 0.0,
        }
        res1 = authenticated_client.post('/api/telemetry/ingest/', payload, format='json')
        assert res1.status_code == status.HTTP_201_CREATED

        # Second submission with same event_id should succeed gracefully without duplicating
        res2 = authenticated_client.post('/api/telemetry/ingest/', payload, format='json')
        assert res2.status_code == status.HTTP_200_OK
        assert Telemetry.objects.filter(event_id='TEL-EVT-DUPE').count() == 1
