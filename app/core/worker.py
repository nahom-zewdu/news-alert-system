# app/core/worker.py
"""
Periodic worker for News Alert System.
"""
import logging

from app.core.logging import configure_logging
from app.services.classifier import ClassifierService
from app.services.news_fetcher import fetch_and_process
configure_logging()
logger = logging.getLogger(__name__)


class PeriodicWorker:
    """
    Wrapper class to encapsulate periodic work
    for maintainability & testability.
    """

    def __init__(self, classifier: ClassifierService):
        self.classifier = classifier

    def run(self):
        try:
            new_items = fetch_and_process(self.classifier)

            if new_items:
                logger.info("Periodic fetch produced %d new items", len(new_items))

        except Exception:
            logger.exception("Periodic task failed")