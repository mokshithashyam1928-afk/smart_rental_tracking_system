"""
Serializers for telemetry app.
"""
from rest_framework import serializers
from .models import Telemetry, EquipmentLiveState


class TelemetrySerializer(serializers.ModelSerializer):
    """Serializer for Telemetry model."""
    
    class Meta:
        model = Telemetry
        fields = [
            'id', 'event_id', 'equipment', 'timestamp',
            'latitude', 'longitude', 'engine_hours', 'idle_hours',
            'fuel_level', 'fuel_consumed', 'speed', 'operator', 'created_at'
        ]
        read_only_fields = ['id', 'event_id', 'created_at']


class TelemetryIngestSerializer(serializers.Serializer):
    """Serializer for telemetry ingestion."""
    event_id = serializers.CharField(max_length=255)
    equipment_id = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    engine_hours = serializers.FloatField()
    idle_hours = serializers.FloatField()
    fuel_level = serializers.FloatField()
    fuel_consumed = serializers.FloatField(required=False, default=0)
    speed = serializers.FloatField(default=0)
    operator_id = serializers.CharField(max_length=50, required=False)


class EquipmentLiveStateSerializer(serializers.ModelSerializer):
    """Serializer for EquipmentLiveState model."""
    
    class Meta:
        model = EquipmentLiveState
        fields = [
            'equipment', 'status', 'last_seen', 'latitude', 'longitude',
            'engine_hours', 'idle_hours', 'fuel_level', 'speed', 'operator',
            'updated_at'
        ]
        read_only_fields = ['equipment', 'updated_at']
