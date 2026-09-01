"""
Tests for rental lifecycle management API.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from apps.rentals.models import Rental


@pytest.mark.django_db
class TestRentalAPI:
    def test_checkout_and_checkin_lifecycle(self, authenticated_client, equipment, operator, site):
        due_at = (timezone.now() + timedelta(days=2)).isoformat()
        checkout_payload = {
            'equipment_id': equipment.id,
            'operator_id': operator.id,
            'site_id': site.id,
            'due_at': due_at
        }
        # Checkout
        checkout_resp = authenticated_client.post('/api/rentals/checkout/', checkout_payload, format='json')
        assert checkout_resp.status_code == status.HTTP_201_CREATED
        rental_id = checkout_resp.json()['data']['id']
        
        # Verify equipment status transitioned to RENTED
        equipment.refresh_from_db()
        assert equipment.status == 'RENTED'

        # Checkin
        checkin_payload = {'rental_id': rental_id}
        checkin_resp = authenticated_client.post('/api/rentals/checkin/', checkin_payload, format='json')
        assert checkin_resp.status_code == status.HTTP_200_OK

        # Verify rental checked in and equipment available
        equipment.refresh_from_db()
        assert equipment.status == 'AVAILABLE'
        rental = Rental.objects.get(id=rental_id)
        assert rental.status == Rental.STATUS_CHECKED_IN

    def test_checkout_already_rented_fails(self, authenticated_client, equipment, operator, site):
        due_at = (timezone.now() + timedelta(days=1)).isoformat()
        payload = {
            'equipment_id': equipment.id,
            'operator_id': operator.id,
            'site_id': site.id,
            'due_at': due_at
        }
        # First checkout succeeds
        res1 = authenticated_client.post('/api/rentals/checkout/', payload, format='json')
        assert res1.status_code == status.HTTP_201_CREATED

        # Second checkout should fail with 409
        res2 = authenticated_client.post('/api/rentals/checkout/', payload, format='json')
        assert res2.status_code == status.HTTP_409_CONFLICT

