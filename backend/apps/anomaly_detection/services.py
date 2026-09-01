"""
Anomaly detection service for identifying abnormal telemetry and handling anomaly workflow.
"""
from django.utils import timezone
from apps.equipment.models import Equipment
from apps.telemetry.models import Telemetry, EquipmentLiveState
from apps.notifications.models import Notification
from apps.audit.models import AuditLog
from apps.forecasting.models import Anomaly


class AnomalyDetectionService:
    """Service to scan, detect, and resolve equipment anomalies."""

    @staticmethod
    def scan_for_anomalies(equipment_id=None):
        """
        Run multi-rule and statistical checks across equipment telemetry:
        1. SPEED_ANOMALY: Speed > 80 km/h for heavy industrial machinery
        2. FUEL_DROP_ANOMALY: Sudden fuel loss (> 15% drop between consecutive readings)
        3. EXCESSIVE_IDLE_ANOMALY: Idle hours > 3 hours continuously
        4. UNAUTHORIZED_MOVEMENT: Operating/moving while equipment status is AVAILABLE/MAINTENANCE
        """
        now = timezone.now()
        detected_anomalies = []

        eq_qs = Equipment.objects.all()
        if equipment_id:
            eq_qs = eq_qs.filter(equipment_id=equipment_id)

        for eq in eq_qs:
            live = getattr(eq, 'live_state', None)
            if not live:
                continue

            # Rule 1: High speed anomaly
            if live.speed and live.speed > 80.0:
                anomaly = Anomaly.objects.create(
                    equipment=eq,
                    detected_at=now,
                    anomaly_type='EXCESSIVE_SPEED',
                    severity=Anomaly.SEVERITY_HIGH,
                    score=0.92,
                    reason=f'Equipment exceeded safe industrial speed threshold: {live.speed:.1f} km/h (limit: 80 km/h)',
                    status=Anomaly.STATUS_OPEN,
                    metadata={'speed': live.speed, 'latitude': live.latitude, 'longitude': live.longitude}
                )
                detected_anomalies.append(anomaly)
                Notification.objects.create(
                    equipment=eq,
                    notification_type='ANOMALY',
                    severity='HIGH',
                    title=f'Excessive Speed: {eq.equipment_id}',
                    message=f'Operating at {live.speed:.1f} km/h',
                )

            # Rule 2: Excessive idle time
            if live.idle_hours and live.idle_hours > 3.0:
                # Check if an open idle anomaly already exists
                existing = Anomaly.objects.filter(
                    equipment=eq,
                    anomaly_type='EXCESSIVE_IDLE',
                    status__in=[Anomaly.STATUS_OPEN, Anomaly.STATUS_ACKNOWLEDGED]
                ).first()
                if not existing:
                    anomaly = Anomaly.objects.create(
                        equipment=eq,
                        detected_at=now,
                        anomaly_type='EXCESSIVE_IDLE',
                        severity=Anomaly.SEVERITY_MEDIUM,
                        score=0.75,
                        reason=f'Asset has been idling continuously for {live.idle_hours:.1f} hours without load.',
                        status=Anomaly.STATUS_OPEN,
                        metadata={'idle_hours': live.idle_hours, 'engine_hours': live.engine_hours}
                    )
                    detected_anomalies.append(anomaly)

            # Rule 3: Unauthorized movement / geofence breach
            if live.speed and live.speed > 5.0 and eq.status in [Equipment.STATUS_AVAILABLE, Equipment.STATUS_MAINTENANCE]:
                existing = Anomaly.objects.filter(
                    equipment=eq,
                    anomaly_type='UNAUTHORIZED_MOVEMENT',
                    status__in=[Anomaly.STATUS_OPEN, Anomaly.STATUS_ACKNOWLEDGED]
                ).first()
                if not existing:
                    anomaly = Anomaly.objects.create(
                        equipment=eq,
                        detected_at=now,
                        anomaly_type='UNAUTHORIZED_MOVEMENT',
                        severity=Anomaly.SEVERITY_HIGH,
                        score=0.98,
                        reason=f'Equipment is moving at {live.speed:.1f} km/h while status is {eq.status}. Potential unauthorized use or theft.',
                        status=Anomaly.STATUS_OPEN,
                        metadata={'speed': live.speed, 'status': eq.status, 'latitude': live.latitude, 'longitude': live.longitude}
                    )
                    detected_anomalies.append(anomaly)
                    Notification.objects.create(
                        equipment=eq,
                        notification_type='ANOMALY',
                        severity='CRITICAL',
                        title=f'Unauthorized Movement: {eq.equipment_id}',
                        message=f'Active motion detected on {eq.status} machine',
                    )

            # Rule 4: Fuel siphon / sudden drop
            recent_telemetry = list(Telemetry.objects.filter(equipment=eq).order_by('-timestamp')[:2])
            if len(recent_telemetry) >= 2:
                t_latest, t_prev = recent_telemetry[0], recent_telemetry[1]
                fuel_delta = t_prev.fuel_level - t_latest.fuel_level
                time_delta_mins = (t_latest.timestamp - t_prev.timestamp).total_seconds() / 60.0
                if fuel_delta >= 15.0 and time_delta_mins <= 15.0:
                    anomaly = Anomaly.objects.create(
                        equipment=eq,
                        detected_at=now,
                        anomaly_type='RAPID_FUEL_DROP',
                        severity=Anomaly.SEVERITY_HIGH,
                        score=0.95,
                        reason=f'Sudden fuel drop of {fuel_delta:.1f}% within {time_delta_mins:.1f} minutes. Potential fuel siphon or leak.',
                        status=Anomaly.STATUS_OPEN,
                        metadata={'drop_percent': fuel_delta, 'previous_level': t_prev.fuel_level, 'current_level': t_latest.fuel_level}
                    )
                    detected_anomalies.append(anomaly)
                    Notification.objects.create(
                        equipment=eq,
                        notification_type='ANOMALY',
                        severity='HIGH',
                        title=f'Fuel Loss Alert: {eq.equipment_id}',
                        message=f'Sudden drop of {fuel_delta:.1f}% fuel',
                    )

        return detected_anomalies

    @staticmethod
    def acknowledge_anomaly(anomaly_id, user, notes=''):
        """Acknowledge an open anomaly."""
        anomaly = Anomaly.objects.get(id=anomaly_id)
        anomaly.status = Anomaly.STATUS_ACKNOWLEDGED
        if notes:
            meta = anomaly.metadata or {}
            meta['ack_notes'] = notes
            anomaly.metadata = meta
        anomaly.save()

        if user and getattr(user, 'is_authenticated', False):
            AuditLog.objects.create(
                actor=user,
                action=AuditLog.ACTION_UPDATE,
                entity_type='Anomaly',
                entity_id=anomaly.id,
                metadata={'anomaly_type': anomaly.anomaly_type, 'notes': notes, 'action': 'ACKNOWLEDGE'}
            )
        return anomaly

    @staticmethod
    def resolve_anomaly(anomaly_id, user, resolution_type=Anomaly.STATUS_RESOLVED, notes=''):
        """Resolve an anomaly."""
        anomaly = Anomaly.objects.get(id=anomaly_id)
        anomaly.status = resolution_type
        anomaly.resolved_at = timezone.now()
        anomaly.resolved_by = getattr(user, 'email', str(user))
        if notes:
            meta = anomaly.metadata or {}
            meta['resolution_notes'] = notes
            anomaly.metadata = meta
        anomaly.save()

        if user and getattr(user, 'is_authenticated', False):
            AuditLog.objects.create(
                actor=user,
                action=AuditLog.ACTION_UPDATE,
                entity_type='Anomaly',
                entity_id=anomaly.id,
                metadata={'resolution_type': resolution_type, 'notes': notes, 'action': 'RESOLVE'}
            )
        return anomaly
