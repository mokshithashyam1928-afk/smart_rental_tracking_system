"""
Django AppConfig for the common package.

Starts the Kafka (or in-process) event consumer background thread
exactly once when Django is fully initialized.
"""
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CommonConfig(AppConfig):
    name = 'common'
    verbose_name = 'Common'

    def ready(self):
        """Called once after all apps are loaded. Start consumer threads here."""
        import sys

        # Don't start consumer threads during migrations, shell, or tests
        skip_commands = {'migrate', 'makemigrations', 'test', 'shell', 'collectstatic', 'check'}
        if any(cmd in sys.argv for cmd in skip_commands):
            return

        # Also skip in the reloader's child process (prevents double-start)
        if 'runserver' in sys.argv and not self._is_main_process():
            return

        try:
            from common.events.consumer import DomainEventConsumer
            DomainEventConsumer.start()
            logger.info("[CommonConfig] Event consumer started successfully")
        except Exception as exc:
            logger.warning(f"[CommonConfig] Could not start event consumer: {exc}")

    @staticmethod
    def _is_main_process() -> bool:
        """True when running as the main Django dev-server process (not the autoreloader)."""
        import os
        return os.environ.get('RUN_MAIN') == 'true'
