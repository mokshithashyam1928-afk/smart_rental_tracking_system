"""
Real-time domain event publisher.

Publishes CloudEvents-compliant domain events to Kafka when a broker is available.
Falls back to an in-process thread-safe queue when Kafka is not configured,
so the application works identically in both environments.

Topics:
  smart-rental.telemetry.events   – machine state changes (status, GPS, engine hours)
  smart-rental.rental.events      – checkout / checkin / overdue lifecycle
  smart-rental.anomaly.events     – overdue alerts, anomaly detections
  smart-rental.recommendation.events – maintenance / routing recommendations
"""
import json
import logging
import os
import queue
import threading
import uuid
from datetime import datetime

from django.utils import timezone

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-process event bus (used when Kafka is not configured)
# This is a simple thread-safe queue that consumer threads can read from.
# ---------------------------------------------------------------------------
_in_process_bus: queue.Queue = queue.Queue(maxsize=10000)
_bus_lock = threading.Lock()


def get_in_process_bus() -> queue.Queue:
    """Return the shared in-process event bus queue."""
    return _in_process_bus


# ---------------------------------------------------------------------------
# Kafka producer (lazy-initialized, optional)
# ---------------------------------------------------------------------------
_kafka_producer = None
_kafka_init_lock = threading.Lock()


def _get_kafka_producer():
    """
    Return a KafkaProducer if KAFKA_BOOTSTRAP_SERVERS env var is set.
    Returns None if Kafka is not configured or unavailable.
    """
    global _kafka_producer
    if _kafka_producer is not None:
        return _kafka_producer

    bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', '').strip()
    if not bootstrap_servers:
        return None

    with _kafka_init_lock:
        if _kafka_producer is not None:
            return _kafka_producer
        try:
            from kafka import KafkaProducer
            _kafka_producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_block_ms=5000,
            )
            logger.info(f"[Kafka] Producer connected to {bootstrap_servers}")
        except Exception as exc:
            logger.warning(f"[Kafka] Producer unavailable – falling back to in-process bus: {exc}")
            _kafka_producer = None
    return _kafka_producer


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class DomainEventPublisher:
    """
    Publisher for standardized CloudEvents-compliant domain events.

    Usage:
        DomainEventPublisher.publish(
            topic=DomainEventPublisher.TOPIC_RENTALS,
            event_type='rental.checked_out',
            payload={'equipment_id': 'CAT-336-1001', 'site': 'Mumbai Coastal Road'},
            user=request.user,
        )
    """

    TOPIC_TELEMETRY = 'smart-rental.telemetry.events'
    TOPIC_RENTALS = 'smart-rental.rental.events'
    TOPIC_ANOMALIES = 'smart-rental.anomaly.events'
    TOPIC_RECOMMENDATIONS = 'smart-rental.recommendation.events'

    @classmethod
    def publish(
        cls,
        topic: str,
        event_type: str,
        payload: dict,
        user=None,
        correlation_id: str = None,
    ) -> dict:
        """
        Build a CloudEvents envelope and dispatch to Kafka or the in-process bus.
        Also writes to the audit outbox for durability and traceability.
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

        # 1. Write to audit outbox (DB-level durability)
        if user and getattr(user, 'is_authenticated', False):
            try:
                from apps.audit.models import AuditLog
                AuditLog.objects.create(
                    actor=user,
                    action=AuditLog.ACTION_UPDATE,
                    entity_type='DomainEvent',
                    entity_id=None,
                    metadata=event_envelope,
                )
            except Exception as exc:
                logger.warning(f"[Kafka] Could not write event to audit log: {exc}")

        # 2. Try Kafka first, fall back to in-process bus
        producer = _get_kafka_producer()
        if producer:
            try:
                future = producer.send(
                    topic,
                    key=event_envelope['id'],
                    value=event_envelope,
                )
                future.get(timeout=5)
                logger.info(
                    f"[Kafka] Published [{event_type}] → topic [{topic}] "
                    f"id=[{event_envelope['id']}]"
                )
            except Exception as exc:
                logger.error(f"[Kafka] Failed to publish to broker, falling back: {exc}")
                _dispatch_in_process(topic, event_envelope)
        else:
            _dispatch_in_process(topic, event_envelope)

        return event_envelope


def _dispatch_in_process(topic: str, event: dict):
    """Put event into the in-process bus for consumer threads to pick up."""
    try:
        _in_process_bus.put_nowait({'topic': topic, 'event': event})
        logger.debug(
            f"[InProcessBus] Dispatched [{event.get('type')}] → topic [{topic}]"
        )
    except queue.Full:
        logger.warning("[InProcessBus] Queue full – event dropped")
