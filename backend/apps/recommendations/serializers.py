"""
Serializers for equipment recommendations app.
"""
from rest_framework import serializers
from apps.forecasting.models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    equipment_code = serializers.CharField(source='equipment.equipment_id', read_only=True)
    equipment_type = serializers.CharField(source='equipment.equipment_type', read_only=True)
    source_site_name = serializers.CharField(source='source_site.name', read_only=True)
    source_site_code = serializers.CharField(source='source_site.site_code', read_only=True)
    target_site_name = serializers.CharField(source='target_site.name', read_only=True)
    target_site_code = serializers.CharField(source='target_site.site_code', read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            'id', 'equipment', 'equipment_code', 'equipment_type',
            'source_site', 'source_site_code', 'source_site_name',
            'target_site', 'target_site_code', 'target_site_name',
            'reason', 'current_utilization', 'predicted_target_demand',
            'score', 'status', 'created_at', 'acted_at', 'acted_by'
        ]
        read_only_fields = ['id', 'created_at', 'acted_at', 'acted_by', 'score']


class RecommendationActionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class RecommendationGenerateSerializer(serializers.Serializer):
    force = serializers.BooleanField(default=False)
