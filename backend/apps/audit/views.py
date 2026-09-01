"""
Serializers and views for audit app.
"""
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import AuditLog
from common.permissions import IsAdmin


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog."""
    actor_email = serializers.CharField(source='actor.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'actor', 'actor_email', 'action', 'entity_type',
            'entity_id', 'metadata', 'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs (admin only)."""
    queryset = AuditLog.objects.select_related('actor').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['actor', 'action', 'entity_type']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']
