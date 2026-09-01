"""
Notifications app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.equipment.models import Equipment

User = get_user_model()


class Notification(models.Model):
    """Model for notifications."""
    
    TYPE_OVERDUE = 'OVERDUE'
    TYPE_OFFLINE = 'OFFLINE'
    TYPE_ANOMALY = 'ANOMALY'
    TYPE_UNDERUTILIZED = 'UNDERUTILIZED'
    TYPE_FORECAST = 'FORECAST'
    TYPE_SYSTEM = 'SYSTEM'
    
    TYPE_CHOICES = [
        (TYPE_OVERDUE, 'Overdue'),
        (TYPE_OFFLINE, 'Offline'),
        (TYPE_ANOMALY, 'Anomaly'),
        (TYPE_UNDERUTILIZED, 'Underutilized'),
        (TYPE_FORECAST, 'Forecast'),
        (TYPE_SYSTEM, 'System'),
    ]
    
    SEVERITY_INFO = 'INFO'
    SEVERITY_WARNING = 'WARNING'
    SEVERITY_CRITICAL = 'CRITICAL'
    
    SEVERITY_CHOICES = [
        (SEVERITY_INFO, 'Info'),
        (SEVERITY_WARNING, 'Warning'),
        (SEVERITY_CRITICAL, 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_INFO)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notifications_notification'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['type', '-created_at']),
        ]
        ordering = ['-created_at']


class NotificationService:
    """Service for creating notifications."""
    
    @staticmethod
    def create_overdue_notification(rental):
        """Create an overdue notification."""
        from apps.accounts.models import User
        
        # Create for all ADMIN and MANAGER users
        admin_users = User.objects.filter(role__in=['ADMIN', 'MANAGER'])
        for user in admin_users:
            Notification.objects.create(
                user=user,
                type=Notification.TYPE_OVERDUE,
                title=f'Rental Overdue: {rental.rental_reference}',
                message=f'Equipment {rental.equipment.equipment_id} rental is overdue (due: {rental.due_at})',
                severity=Notification.SEVERITY_WARNING,
                equipment=rental.equipment
            )
