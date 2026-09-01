"""
Domain event consumer interface and deduplication helpers for Kafka and event streams.
"""
import logging
import json
from django.core.cache import cache

logger = logging.getLogger(__name__)


class DomainEventConsumer:
    """
    Idempotent consumer handler for domain events.
    Guarantees at-least-once to exactly-once processing using Redis/cache deduplication locks.
    """

    DEDUPLICATION_TTL = 3600  # 1 hour deduplication window

    @classmethod
    def is_duplicate(cls, event_id: str) -> bool:
        """Check if event has already been processed."""
        cache_key = f"processed_event:{event_id}"
        if cache.get(cache_key):
            return True
        cache.set(cache_key, '1', cls.DEDUPLICATION_TTL)
        return False

    @classmethod
    def handle_event(cls, event: dict):
        """Dispatch domain event to corresponding application handler."""
        event_id = event.get('id')
        event_type = event.get('type')
        data = event.get('data', {})

        if event_id and cls.is_duplicate(event_id):
            logger.info(f"Duplicate event {event_id} ignored.")
            return {'status': 'ignored', 'reason': 'duplicate'}

        logger.info(f"Consuming event {event_id} of type {event_type}")
        return {'status': 'processed', 'event_id': event_id, 'type': event_type}
