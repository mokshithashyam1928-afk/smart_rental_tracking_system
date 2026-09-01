"""
Serializers and views for notifications app.
"""
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from common.responses import APIResponse


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'severity',
            'equipment', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notifications."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Only return notifications for the current user."""
        return Notification.objects.filter(user=self.request.user).all()
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read."""
        from django.utils import timezone
        notification = self.get_object()
        notification.read_at = timezone.now()
        notification.save()
        return APIResponse.success(
            data=NotificationSerializer(notification).data,
            message='Notification marked as read'
        )
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read."""
        from django.utils import timezone
        count = Notification.objects.filter(
            user=request.user,
            read_at__isnull=True
        ).update(read_at=timezone.now())
        return APIResponse.success(
            message=f'{count} notifications marked as read'
        )
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = Notification.objects.filter(
            user=request.user,
            read_at__isnull=True
        ).count()
        return APIResponse.success(
            data={'unread_count': count},
            message='Unread count retrieved'
        )
