# app/main.py
"""
FastAPI application factory using lifespan-based startup/shutdown.

Integrates the new pluggable scheduler system:
- Creates classifier + scheduler during startup
- Scheduler runs a periodic task (fetch → classify → store)
- Clean shutdown ensures scheduler terminates safely

Scheduler modes:
- "background": BackgroundThreadScheduler
- "nuvom": NuvomScheduler (placeholder)
- "none": NoOpScheduler
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.core.logging import configure_logging
from app.core.config import settings
from app.core.scheduler import create_scheduler
from app.infrastructure.groq_client import GroqClient
from app.services.classifier import ClassifierService
from app.services.news_fetcher import fetch_and_process
from app.api.router import get_root_router

configure_logging()
logger = logging.getLogger(__name__)

FETCH_INTERVAL_SECONDS = 30


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager responsible for initializing and tearing down
    shared app resources including the classifier and the scheduler.
    """
    logger.info("Starting application lifespan")

    # --- Initialize classifier (Groq if configured) ---
    groq_client = GroqClient(settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
    classifier = ClassifierService(groq=groq_client)

    # --- Create periodic task ---
    def periodic_task():
        try:
            new_items = fetch_and_process(classifier)
            if new_items:
                logger.info("Periodic fetch produced %d new items", len(new_items))
        except Exception:
            logger.exception("Periodic task failed")

    # --- Create scheduler ---
    scheduler = create_scheduler(
        task=periodic_task,
        mode=settings.SCHEDULER_MODE,
        interval_seconds=FETCH_INTERVAL_SECONDS,
    )

    # Start scheduler
    scheduler.start()

    # Yield control back to FastAPI
    yield

    # Shutdown logic
    logger.info("Application lifespan ending stopping scheduler...")
    scheduler.stop()
    logger.info("Scheduler stopped cleanly")


# Create FastAPI app with lifespan
app = FastAPI(
    title="News Alert System (Demo)",
    lifespan=lifespan,
)

# Include API routes
app.include_router(get_root_router(), prefix="/api")
