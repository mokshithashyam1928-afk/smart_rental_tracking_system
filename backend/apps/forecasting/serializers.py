"""
Serializers for forecasting app.
"""
from rest_framework import serializers
from .models import Forecast


class ForecastSerializer(serializers.ModelSerializer):
    site_code = serializers.CharField(source='site.site_code', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)

    class Meta:
        model = Forecast
        fields = [
            'id', 'site', 'site_code', 'site_name',
            'equipment_type', 'forecast_date',
            'predicted_demand', 'confidence',
            'model_version', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class ForecastGenerateSerializer(serializers.Serializer):
    site_id = serializers.IntegerField(required=False, allow_null=True)
    days_ahead = serializers.IntegerField(default=14, min_value=1, max_value=90)
