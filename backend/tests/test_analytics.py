"""
Tests for analytics, idle, fuel, and CSV reporting.
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestAnalyticsAPI:
    def test_analytics_overview(self, authenticated_client, equipment):
        response = authenticated_client.get('/api/analytics/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()['data']
        assert 'fleet_summary' in data
        assert 'idle_summary' in data
        assert 'fuel_summary' in data
        assert 'site_breakdowns' in data

    def test_utilization_endpoint(self, authenticated_client, equipment):
        response = authenticated_client.get('/api/analytics/utilization/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()['data']
        assert 'total_equipment' in data
        assert 'utilization_rate' in data

    def test_csv_export(self, authenticated_client, equipment):
        response = authenticated_client.get('/api/analytics/export/?type=fleet')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert b'Equipment ID' in response.content
