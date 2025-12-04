# scripts/run_scheduler.py
"""
Simple script to run a scheduled fetch loop outside FastAPI process.

Use this if you prefer running scheduler separately (e.g., in demo or production).
Invoked via `uv run scheduler` according to `pyproject.toml` scripts.
"""

import time
import logging
from app.core.logging import configure_logging
from app.core.config import settings
from app.services.classifier import ClassifierService
from app.infrastructure.groq_client import GroqClient
from app.services.news_fetcher import fetch_and_process

configure_logging()
logger = logging.getLogger(__name__)


def main():
    """
    Run a simple forever loop that fetches and processes news every 120 seconds.
    """
    logger.info("Starting external scheduler (interval=120s)")
    groq = GroqClient(settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
    classifier = ClassifierService(groq=groq)

    while True:
        try:
            fetch_and_process(classifier)
        except Exception:
            logger.exception("Scheduled fetch failed")
        time.sleep(120)


if __name__ == "__main__":
    main()
