# app/api/routes_news.py
"""
Routes for news operations.

- /api/news [GET] - list all news
- /api/fetch [POST] - trigger fetch+classify (returns newly added)
"""

from fastapi import APIRouter, Depends
from typing import List
import logging

from app.services.news_fetcher import list_news, fetch_and_process
from app.services.classifier import ClassifierService
from app.infrastructure.groq_client import GroqClient
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_classifier() -> ClassifierService:
    """
    Factory for ClassifierService using Groq if configured.
    """
    groq = None
    if settings.GROQ_API_KEY:
        groq = GroqClient(settings.GROQ_API_KEY)
    return ClassifierService(groq=groq)


@router.get("/news", tags=["news"])
def api_list_news():
    """
    Return all news items known to the system.
    """
    return list_news()


@router.post("/fetch", tags=["news"])
def api_fetch_now(classifier: ClassifierService = Depends(get_classifier)):
    """
    Trigger a fetch + classify across configured RSS feeds.
    """
    new_items = fetch_and_process(classifier)
    return {"new_count": len(new_items), "items": new_items}
