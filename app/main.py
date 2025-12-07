# app/main.py
"""
FastAPI application factory using lifespan-based startup/shutdown.

Uses a pluggable scheduler system:
- Creates classifier + scheduler during startup
- Scheduler runs a periodic task (fetch → classify → store)
- Clean shutdown ensures scheduler terminates safely
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.core.logging import configure_logging
from app.core.config import settings
from app.core.scheduler import create_scheduler
from app.infrastructure.groq_client import GroqClient
from app.services.classifier import ClassifierService
from app.api.router import get_root_router
from app.core.db import init_db
from app.core.worker import PeriodicWorker

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager that initializes and tears down shared resources."""

    logger.info("Starting application lifespan")

    # Initialize classifier
    groq_client = GroqClient(settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
    classifier = ClassifierService(classifier=groq_client)

    # Initialize database
    init_db()

    # Set up periodic worker
    worker = PeriodicWorker(classifier=classifier)

    # Create scheduler
    scheduler = create_scheduler(
        task=worker.run,
        mode=settings.SCHEDULER_MODE,
        interval_seconds=settings.FETCH_INTERVAL_SECONDS,
    )

    scheduler.start()

    # Hand back to FastAPI
    yield

    # Shutdown
    logger.info("Application lifespan ending; stopping scheduler...")
    scheduler.stop()
    logger.info("Scheduler stopped cleanly")


app = FastAPI(
    title="News Alert System (Demo)",
    lifespan=lifespan,
)

app.include_router(get_root_router(), prefix="/api")
