"""
Serializers for equipment app.
"""
from rest_framework import serializers
from .models import Equipment
from apps.sites.serializers import SiteSerializer
from apps.operators.serializers import OperatorSerializer


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model."""
    site_detail = SiteSerializer(source='site', read_only=True)
    operator_detail = OperatorSerializer(source='current_operator', read_only=True)
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'equipment_id', 'equipment_type', 'manufacturer', 'model',
            'serial_number', 'qr_code', 'rfid_uid', 'site', 'site_detail',
            'status', 'current_operator', 'operator_detail', 'purchase_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EquipmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating equipment."""
    
    class Meta:
        model = Equipment
        fields = [
            'equipment_id', 'equipment_type', 'manufacturer', 'model',
            'serial_number', 'qr_code', 'rfid_uid', 'site', 'status',
            'current_operator', 'purchase_date'
        ]


class EquipmentStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating equipment status."""
    status = serializers.ChoiceField(choices=Equipment.STATUS_CHOICES)


class EquipmentIdentifierResolutionSerializer(serializers.Serializer):
    """Serializer for resolving equipment by QR/RFID identifier."""
    identifier_type = serializers.ChoiceField(choices=['QR', 'RFID'])
    identifier = serializers.CharField(max_length=255)
