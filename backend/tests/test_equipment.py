"""
Tests for equipment management API.
"""
import pytest
from rest_framework import status
from apps.equipment.models import Equipment


@pytest.mark.django_db
class TestEquipmentAPI:
    def test_list_equipment(self, authenticated_client, equipment):
        response = authenticated_client.get('/api/equipment/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['data']) >= 1

    def test_create_equipment(self, authenticated_client, site):
        payload = {
            'equipment_id': 'EQX9999',
            'equipment_type': 'BULLDOZER',
            'manufacturer': 'Caterpillar',
            'model': 'CAT D8T',
            'serial_number': 'SN99999',
            'site': site.id,
            'status': 'AVAILABLE'
        }
        response = authenticated_client.post('/api/equipment/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Equipment.objects.filter(equipment_id='EQX9999').exists()

    def test_filter_equipment_by_status(self, authenticated_client, equipment):
        response = authenticated_client.get('/api/equipment/?status=AVAILABLE')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(eq['status'] == 'AVAILABLE' for eq in data['data'])

