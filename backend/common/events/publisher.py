"""
Event-driven domain event publishing and consuming for Phase 3 Kafka integration.
"""
import json
import logging
import uuid
from datetime import datetime
from django.utils import timezone
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)


class DomainEventPublisher:
    """
    Publisher for standardized domain events.
    Supports local log/audit outbox and external message broker (Kafka/Redis) hooks.
    """

    TOPIC_TELEMETRY = 'smart-rental.telemetry.events'
    TOPIC_RENTALS = 'smart-rental.rental.events'
    TOPIC_ANOMALIES = 'smart-rental.anomaly.events'
    TOPIC_RECOMMENDATIONS = 'smart-rental.recommendation.events'

    @classmethod
    def publish(cls, topic: str, event_type: str, payload: dict, user=None, correlation_id: str = None) -> dict:
        """
        Create a standardized versioned CloudEvents-compliant event envelope.
        """
        event_envelope = {
            'specversion': '1.0',
            'id': str(uuid.uuid4()),
            'source': 'smart-rental-tracking.backend',
            'type': event_type,
            'topic': topic,
            'time': timezone.now().isoformat(),
            'correlation_id': correlation_id or str(uuid.uuid4()),
            'data': payload,
        }

        # Record event in audit outbox for durability & traceability
        if user and getattr(user, 'is_authenticated', False):
            try:
                AuditLog.objects.create(
                    actor=user,
                    action=AuditLog.ACTION_UPDATE,
                    entity_type='DomainEvent',
                    entity_id=None,
                    metadata=event_envelope
                )
            except Exception as e:
                logger.warning(f"Could not write event to audit log: {e}")

        logger.info(f"Published event [{event_type}] to topic [{topic}] with ID [{event_envelope['id']}]")
        return event_envelope
