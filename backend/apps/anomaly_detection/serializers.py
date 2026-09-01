"""
Serializers for anomaly detection app.
"""
from rest_framework import serializers
from apps.forecasting.models import Anomaly


class AnomalySerializer(serializers.ModelSerializer):
    equipment_code = serializers.CharField(source='equipment.equipment_id', read_only=True)
    equipment_type = serializers.CharField(source='equipment.equipment_type', read_only=True)
    site_name = serializers.CharField(source='equipment.site.name', read_only=True, default='Unassigned')

    class Meta:
        model = Anomaly
        fields = [
            'id', 'equipment', 'equipment_code', 'equipment_type', 'site_name',
            'detected_at', 'anomaly_type', 'severity', 'score',
            'reason', 'status', 'metadata',
            'resolved_at', 'resolved_by', 'created_at'
        ]
        read_only_fields = ['id', 'detected_at', 'created_at', 'score']


class AnomalyAcknowledgeSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class AnomalyResolveSerializer(serializers.Serializer):
    resolution_type = serializers.ChoiceField(
        choices=[Anomaly.STATUS_RESOLVED, Anomaly.STATUS_FALSE_POSITIVE],
        default=Anomaly.STATUS_RESOLVED
    )
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class AnomalyScanSerializer(serializers.Serializer):
    equipment_id = serializers.CharField(required=False, allow_null=True)
