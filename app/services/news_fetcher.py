# app/services/news_fetcher.py
"""
Service functions for fetching, classifying, and storing news items.
Uses RSS feeds and a classification service.
Provides functions to fetch news, classify them, and store new items in the database.
"""

from typing import List, Dict
import logging

from app.infrastructure.rss_client import fetch_all_configured
from app.services.classifier import ClassifierService
from app.domain.entities import NewsItem
from app.core.config import settings
from app.models.news_item_doc import NewsItemDocument

logger = logging.getLogger(__name__)

def store_items(items: List[NewsItem]):
    added = []
    for it in items:
        doc = NewsItemDocument.objects(id=it.id).first()
        if not doc:
            link = str(it.link) if it.link else None

            doc = NewsItemDocument(
                id=it.id,
                title=it.title,
                summary=it.summary,
                link=link,
                source=it.source,
                category=it.category,
                published_at=it.published_at,
            )
            doc.save()
            added.append(it)
    logger.info("store_items: added=%d", len(added))
    return added


def list_news() -> List[NewsItem]:
    items = []
    for doc in NewsItemDocument.objects.order_by("-published_at"):
        items.append(NewsItem(
            id=doc.id,
            title=doc.title,
            summary=doc.summary,
            link=doc.link,
            source=doc.source,
            category=doc.category,
            published_at=doc.published_at
        ))
    return items

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
        it.category = classifier.classify(title=it.title, settings=settings, summary=it.summary or "",)
    new = store_items(fetched)
    logger.info("fetch_and_process: new=%d", len(new))
    return new
