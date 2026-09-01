"""
Audit app for logging system activities.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditLog(models.Model):
    """Model for audit logging."""
    
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_CHECKOUT = 'CHECKOUT'
    ACTION_CHECKIN = 'CHECKIN'
    ACTION_CANCEL = 'CANCEL'
    
    ACTION_CHOICES = [
        (ACTION_LOGIN, 'Login'),
        (ACTION_LOGOUT, 'Logout'),
        (ACTION_CREATE, 'Create'),
        (ACTION_UPDATE, 'Update'),
        (ACTION_DELETE, 'Delete'),
        (ACTION_CHECKOUT, 'Checkout'),
        (ACTION_CHECKIN, 'Checkin'),
        (ACTION_CANCEL, 'Cancel'),
    ]
    
    actor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_audit_log'
        indexes = [
            models.Index(fields=['actor', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.actor.email} - {self.action} - {self.entity_type}({self.entity_id}) at {self.timestamp}"
