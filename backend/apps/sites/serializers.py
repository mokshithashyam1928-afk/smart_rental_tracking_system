"""
Serializers for sites app.
"""
from rest_framework import serializers
from .models import Site


class SiteSerializer(serializers.ModelSerializer):
    """Serializer for Site model."""
    
    class Meta:
        model = Site
        fields = ['id', 'site_code', 'name', 'description', 'address', 'latitude', 'longitude', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SiteCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating sites."""
    
    class Meta:
        model = Site
        fields = ['site_code', 'name', 'description', 'address', 'latitude', 'longitude', 'status']
