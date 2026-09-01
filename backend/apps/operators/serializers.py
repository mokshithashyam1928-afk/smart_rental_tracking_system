"""
Serializers for operators app.
"""
from rest_framework import serializers
from .models import Operator


class OperatorSerializer(serializers.ModelSerializer):
    """Serializer for Operator model."""
    
    class Meta:
        model = Operator
        fields = ['id', 'employee_id', 'name', 'phone', 'email', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class OperatorCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating operators."""
    
    class Meta:
        model = Operator
        fields = ['employee_id', 'name', 'phone', 'email', 'status']
