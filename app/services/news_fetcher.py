# app/services/news_fetcher.py
"""
News fetcher service.

Orchestrates fetching feeds, classifying items, and storing them in a demo in-memory store.
Replace storage with a persistent DB for production use.
"""

from typing import List, Dict
import logging

from app.infrastructure.rss_client import fetch_all_configured
from app.services.classifier import ClassifierService
from app.domain.entities import NewsItem
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory store for demo purposes (id -> NewsItem)
_news_store: Dict[str, NewsItem] = {}


def list_news() -> List[NewsItem]:
    """
    Return all news items currently in the store.
    """
    return list(_news_store.values())


def store_items(items: List[NewsItem]) -> List[NewsItem]:
    """
    Store items into the in-memory store; idempotent by id.
    Returns the list of newly added items.
    """
    added = []
    for it in items:
        if it.id not in _news_store:
            _news_store[it.id] = it
            added.append(it)
    logger.info("store_items: added=%d", len(added))
    return added


def fetch_and_process(classifier: ClassifierService) -> List[NewsItem]:
    """
    Fetch all configured RSS feeds, classify each item and store new ones.
    Returns newly added items.
    """
    logger.info("Starting fetch_and_process")
    fetched = fetch_all_configured()
    logger.info("Fetched %d items", len(fetched))
    # classify
    for it in fetched:
        it.categories = classifier.classify(it.title, it.summary or "")
    new = store_items(fetched)
    logger.info("fetch_and_process: new=%d", len(new))
    return new
