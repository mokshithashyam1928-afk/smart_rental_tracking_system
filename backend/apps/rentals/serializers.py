"""
Serializers for rentals app.
"""
from rest_framework import serializers
from .models import Rental
from apps.equipment.serializers import EquipmentSerializer
from apps.operators.serializers import OperatorSerializer
from apps.sites.serializers import SiteSerializer
from apps.accounts.serializers import UserSerializer


class RentalSerializer(serializers.ModelSerializer):
    """Serializer for Rental model."""
    equipment_detail = EquipmentSerializer(source='equipment', read_only=True)
    operator_detail = OperatorSerializer(source='operator', read_only=True)
    site_detail = SiteSerializer(source='site', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Rental
        fields = [
            'id', 'rental_reference', 'equipment', 'equipment_detail',
            'operator', 'operator_detail', 'site', 'site_detail',
            'checkout_at', 'due_at', 'checkin_at', 'status',
            'created_by', 'created_by_detail', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rental_reference', 'checkout_at', 'checkin_at', 'created_at', 'updated_at']


class RentalCheckoutSerializer(serializers.Serializer):
    """Serializer for rental checkout request."""
    equipment_id = serializers.IntegerField()
    operator_id = serializers.IntegerField()
    site_id = serializers.IntegerField()
    due_at = serializers.DateTimeField()


class RentalCheckinSerializer(serializers.Serializer):
    """Serializer for rental check-in request."""
    rental_id = serializers.IntegerField()


class RentalCancelSerializer(serializers.Serializer):
    """Serializer for rental cancellation request."""
    rental_id = serializers.IntegerField()


class RentalHistorySerializer(serializers.ModelSerializer):
    """Serializer for rental history."""
    
    class Meta:
        model = Rental
        fields = [
            'id', 'rental_reference', 'equipment', 'operator', 'site',
            'checkout_at', 'due_at', 'checkin_at', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rental_reference', 'checkout_at', 'checkin_at', 'created_at', 'updated_at']
