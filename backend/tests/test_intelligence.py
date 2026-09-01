"""
Tests for demand forecasting, anomaly detection, recommendations, and domain events.
"""
import pytest
from rest_framework import status
from apps.sites.models import Site
from apps.equipment.models import Equipment
from apps.forecasting.models import Anomaly, Recommendation, Forecast
from common.events import DomainEventPublisher, DomainEventConsumer


@pytest.mark.django_db
class TestForecastingAPI:
    def test_generate_and_list_forecasts(self, authenticated_client, site, equipment):
        gen_resp = authenticated_client.post('/api/forecasting/generate/', {'days_ahead': 7}, format='json')
        assert gen_resp.status_code == status.HTTP_200_OK
        
        list_resp = authenticated_client.get('/api/forecasting/')
        assert list_resp.status_code == status.HTTP_200_OK
        data = list_resp.json()['data']
        assert len(data) >= 1

    def test_forecast_summary(self, authenticated_client):
        response = authenticated_client.get('/api/forecasting/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_predicted_demand_next_7_days' in response.json()['data']


@pytest.mark.django_db
class TestAnomalyAPI:
    def test_anomaly_scan_and_workflow(self, authenticated_client, equipment):
        # Create an anomaly directly or via scan
        anomaly = Anomaly.objects.create(
            equipment=equipment,
            detected_at='2026-09-01T12:00:00Z',
            anomaly_type='EXCESSIVE_SPEED',
            severity='HIGH',
            score=0.95,
            reason='Speed exceeded 90 km/h',
            status='OPEN'
        )

        # Acknowledge
        ack_resp = authenticated_client.post(
            f'/api/anomalies/{anomaly.id}/acknowledge/',
            {'notes': 'Checking with site manager'},
            format='json'
        )
        assert ack_resp.status_code == status.HTTP_200_OK
        anomaly.refresh_from_db()
        assert anomaly.status == Anomaly.STATUS_ACKNOWLEDGED

        # Resolve
        res_resp = authenticated_client.post(
            f'/api/anomalies/{anomaly.id}/resolve/',
            {'resolution_type': 'RESOLVED', 'notes': 'Sensor re-calibrated'},
            format='json'
        )
        assert res_resp.status_code == status.HTTP_200_OK
        anomaly.refresh_from_db()
        assert anomaly.status == Anomaly.STATUS_RESOLVED


@pytest.mark.django_db
class TestRecommendationAPI:
    def test_recommendation_lifecycle(self, authenticated_client, equipment, site):
        site2 = Site.objects.create(
            site_code='S002', name='Site Beta', address='456 North St', latitude=12.0, longitude=77.0
        )
        rec = Recommendation.objects.create(
            equipment=equipment,
            source_site=site,
            target_site=site2,
            reason='High demand surge at Site Beta',
            current_utilization=0.0,
            predicted_target_demand=4.0,
            score=0.88,
            status=Recommendation.STATUS_PENDING
        )

        # Accept recommendation
        accept_resp = authenticated_client.post(
            f'/api/recommendations/{rec.id}/accept/',
            {'notes': 'Transferring unit via transport truck'},
            format='json'
        )
        assert accept_resp.status_code == status.HTTP_200_OK
        rec.refresh_from_db()
        assert rec.status == Recommendation.STATUS_ACCEPTED
        
        # Verify equipment was reallocated to site2
        equipment.refresh_from_db()
        assert equipment.site == site2


@pytest.mark.django_db
class TestDomainEvents:
    def test_event_publish_and_idempotency(self, admin_user):
        event = DomainEventPublisher.publish(
            topic='smart-rental.telemetry.events',
            event_type='telemetry.ingested',
            payload={'equipment_id': 'EQX0001', 'speed': 25.0},
            user=admin_user
        )
        assert event['id'] is not None

        # First consumption
        res1 = DomainEventConsumer.handle_event(event)
        assert res1['status'] == 'processed'

        # Duplicate consumption
        res2 = DomainEventConsumer.handle_event(event)
        assert res2['status'] == 'ignored'
