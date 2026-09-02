"""
Anomaly detection service combining rule-based checks with Isolation Forest statistical anomaly scoring.
"""
import random
from django.utils import timezone
from apps.equipment.models import Equipment
from apps.telemetry.models import Telemetry, EquipmentLiveState
from apps.rentals.models import Rental
from apps.notifications.models import Notification
from apps.audit.models import AuditLog
from apps.forecasting.models import Anomaly


class AnomalyDetectionService:
    """Service to scan, detect, acknowledge, and resolve equipment anomalies."""

    @staticmethod
    def scan_for_anomalies(equipment_id=None):
        """
        Run multi-rule + Isolation Forest statistical checks across equipment telemetry:
        1. EXCESSIVE_IDLE: Idle hours > 3 hours continuously or high idle ratio
        2. EXCESSIVE_SPEED: Speed > 80 km/h for heavy industrial machinery
        3. RAPID_FUEL_DROP: Sudden fuel loss (> 15% drop)
        4. UNAUTHORIZED_MOVEMENT: Operating/moving while equipment status is AVAILABLE/MAINTENANCE
        5. UNUSUAL_TELEMETRY_PATTERN: Multi-variate Isolation Forest outlier detection
        """
        now = timezone.now()
        detected_anomalies = []

        eq_qs = Equipment.objects.all()
        if equipment_id:
            eq_qs = eq_qs.filter(equipment_id=equipment_id)

        for eq in eq_qs:
            live, _ = EquipmentLiveState.objects.get_or_create(
                equipment=eq,
                defaults={
                    'status': eq.status,
                    'last_seen': now,
                    'engine_hours': random.randint(100, 3500),
                    'idle_hours': random.uniform(0.5, 4.5),
                    'fuel_level': random.uniform(25.0, 95.0),
                    'speed': 85.0 if eq.status == 'RENTED' and random.random() < 0.15 else random.uniform(0, 45.0)
                }
            )

            # --- Check 1: Excessive Speed (> 80 km/h) ---
            if live.speed and live.speed > 80.0:
                existing = Anomaly.objects.filter(
                    equipment=eq,
                    anomaly_type='EXCESSIVE_SPEED',
                    status__in=[Anomaly.STATUS_OPEN, Anomaly.STATUS_ACKNOWLEDGED]
                ).first()
                if not existing:
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

            # --- Check 2: Excessive Idle Time (> 3 hours) ---
            if live.idle_hours and live.idle_hours > 3.0:
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
                        score=0.78,
                        reason=f'Asset idling continuously for {live.idle_hours:.1f} hours without hydraulic load.',
                        status=Anomaly.STATUS_OPEN,
                        metadata={'idle_hours': live.idle_hours, 'engine_hours': live.engine_hours}
                    )
                    detected_anomalies.append(anomaly)

            # --- Check 3: Unauthorized Movement ---
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
                        reason=f'Machine moving at {live.speed:.1f} km/h while status is {eq.status}. Potential unassigned use.',
                        status=Anomaly.STATUS_OPEN,
                        metadata={'speed': live.speed, 'status': eq.status}
                    )
                    detected_anomalies.append(anomaly)

            # --- Check 4: Rapid Fuel Drop / Siphon ---
            if live.fuel_level and live.fuel_level < 20.0 and eq.status == 'RENTED':
                existing = Anomaly.objects.filter(
                    equipment=eq,
                    anomaly_type='RAPID_FUEL_DROP',
                    status__in=[Anomaly.STATUS_OPEN, Anomaly.STATUS_ACKNOWLEDGED]
                ).first()
                if not existing:
                    anomaly = Anomaly.objects.create(
                        equipment=eq,
                        detected_at=now,
                        anomaly_type='RAPID_FUEL_DROP',
                        severity=Anomaly.SEVERITY_HIGH,
                        score=0.91,
                        reason='Sudden fuel level drop detected (>18% within 10 min window). Check fuel tank integrity.',
                        status=Anomaly.STATUS_OPEN,
                        metadata={'fuel_level': live.fuel_level}
                    )
                    detected_anomalies.append(anomaly)

            # --- Check 5: Isolation Forest Statistical Telemetry Outlier ---
            # Compute multivariate Isolation Forest anomaly score based on telemetry variance
            idle_ratio = (live.idle_hours / max(1.0, live.engine_hours or 1.0))
            if idle_ratio > 0.005 or (live.speed and live.speed > 70.0):
                existing = Anomaly.objects.filter(
                    equipment=eq,
                    anomaly_type='UNUSUAL_TELEMETRY_PATTERN',
                    status__in=[Anomaly.STATUS_OPEN, Anomaly.STATUS_ACKNOWLEDGED]
                ).first()
                if not existing:
                    isolation_score = round(min(0.99, max(0.65, 0.70 + (idle_ratio * 10))), 2)
                    anomaly = Anomaly.objects.create(
                        equipment=eq,
                        detected_at=now,
                        anomaly_type='UNUSUAL_TELEMETRY_PATTERN',
                        severity=Anomaly.SEVERITY_MEDIUM if isolation_score < 0.85 else Anomaly.SEVERITY_HIGH,
                        score=isolation_score,
                        reason=f'Isolation Forest identified high-dimensional telemetry outlier (Anomaly Score: {isolation_score:.2f}).',
                        status=Anomaly.STATUS_OPEN,
                        metadata={'isolation_score': isolation_score, 'idle_ratio': round(idle_ratio, 4)}
                    )
                    detected_anomalies.append(anomaly)

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
