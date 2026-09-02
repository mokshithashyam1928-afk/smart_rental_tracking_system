"""
Domain event consumer.

Two modes (auto-detected):

1. **Kafka mode** (when KAFKA_BOOTSTRAP_SERVERS is set):
   Runs a real KafkaConsumer in a background daemon thread, polling all
   smart-rental.* topics and routing to the correct handler.

2. **In-process bus mode** (default, no broker needed):
   Runs a background thread reading from the shared in-memory Queue that
   DomainEventPublisher._dispatch_in_process() writes to.  Same handlers,
   same routing, zero infrastructure.
"""
import logging
import os
import threading

logger = logging.getLogger(__name__)


class DomainEventConsumer:
    """
    Idempotent consumer with Redis-based deduplication.
    start() is called once at Django startup (via AppConfig.ready).
    """

    TOPICS = [
        'smart-rental.telemetry.events',
        'smart-rental.rental.events',
        'smart-rental.anomaly.events',
        'smart-rental.recommendation.events',
    ]
    DEDUPLICATION_TTL = 3600  # seconds

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    @classmethod
    def start(cls):
        """Detect mode and launch the appropriate consumer thread."""
        bootstrap = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', '').strip()
        if bootstrap:
            t = threading.Thread(
                target=cls._kafka_consumer_loop,
                args=(bootstrap,),
                daemon=True,
                name='kafka-consumer',
            )
        else:
            t = threading.Thread(
                target=cls._in_process_consumer_loop,
                daemon=True,
                name='in-process-event-consumer',
            )
        t.start()
        mode = 'Kafka' if bootstrap else 'InProcess'
        logger.info(f"[Consumer] Started {mode} consumer thread")

    # ------------------------------------------------------------------ #
    # Kafka consumer loop
    # ------------------------------------------------------------------ #

    @classmethod
    def _kafka_consumer_loop(cls, bootstrap_servers: str):
        try:
            from kafka import KafkaConsumer
            consumer = KafkaConsumer(
                *cls.TOPICS,
                bootstrap_servers=bootstrap_servers.split(','),
                group_id='smart-rental-backend',
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda m: __import__('json').loads(m.decode('utf-8')),
            )
            logger.info(f"[Kafka] Consumer listening on topics: {cls.TOPICS}")
            for msg in consumer:
                event = msg.value
                cls._dispatch(topic=msg.topic, event=event)
        except Exception as exc:
            logger.error(f"[Kafka] Consumer loop crashed – falling back to in-process: {exc}")
            cls._in_process_consumer_loop()

    # ------------------------------------------------------------------ #
    # In-process consumer loop
    # ------------------------------------------------------------------ #

    @classmethod
    def _in_process_consumer_loop(cls):
        from common.events.publisher import get_in_process_bus
        bus = get_in_process_bus()
        logger.info("[InProcess] Consumer listening on in-process event bus")
        while True:
            try:
                item = bus.get(timeout=1)
                topic = item.get('topic', '')
                event = item.get('event', {})
                cls._dispatch(topic=topic, event=event)
            except Exception:
                # queue.Empty or other transient errors – keep looping
                pass

    # ------------------------------------------------------------------ #
    # Dispatch + deduplication
    # ------------------------------------------------------------------ #

    @classmethod
    def _dispatch(cls, topic: str, event: dict):
        event_id = event.get('id')

        if event_id and cls._is_duplicate(event_id):
            logger.debug(f"[Consumer] Duplicate event {event_id} ignored")
            return

        from common.events.handlers import TOPIC_HANDLERS
        handler = TOPIC_HANDLERS.get(topic)
        if handler:
            try:
                handler(event)
            except Exception as exc:
                logger.error(f"[Consumer] Handler for topic [{topic}] raised: {exc}")
        else:
            logger.debug(f"[Consumer] No handler registered for topic [{topic}]")

    @classmethod
    def _is_duplicate(cls, event_id: str) -> bool:
        """Redis-based deduplication; falls back to no-dedup if Redis is unavailable."""
        try:
            from django.core.cache import cache
            key = f"processed_event:{event_id}"
            if cache.get(key):
                return True
            cache.set(key, '1', cls.DEDUPLICATION_TTL)
            return False
        except Exception:
            return False
