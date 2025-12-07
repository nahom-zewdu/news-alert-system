# app/services/news_fetcher.py
"""
News fetcher service.

Responsibilities:
- fetch_and_process(classifier) -> List[NewsItem] (unchanged)
- store_items(items) -> List[NewsItem] (unchanged)
- list_news() -> List[NewsItem] (unchanged)
- get_news_by_id(news_id) -> Optional[NewsItem] (NEW)
- list_news_paginated(limit, offset) -> List[NewsItem] (NEW)
"""

from typing import List, Optional
import logging
import math

from app.infrastructure.rss_client import fetch_all_configured
from app.services.classifier import ClassifierService
from app.domain.entities import NewsItem
from app.core.config import settings
from app.models.news_item_doc import NewsItemDocument

logger = logging.getLogger(__name__)


def store_items(items: List[NewsItem]) -> List[NewsItem]:
    """
    Persist new items into Mongo (idempotent). Returns added items.
    """
    added = []
    for it in items:
        # ensure link is a plain string (mongodb validation)
        link = str(it.link) if it.link else None

        doc = NewsItemDocument.objects(id=it.id).first()
        if not doc:
            doc = NewsItemDocument(
                id=it.id,
                title=it.title,
                summary=it.summary,
                link=link,
                source=it.source,
                category=getattr(it, "category", None),
                published_at=it.published_at,
            )
            doc.save()
            added.append(it)
    logger.info("store_items: added=%d", len(added))
    return added


def list_news() -> List[NewsItem]:
    """
    Return all news items (descending by published_at).
    NOTE: not paginated (kept for backward compatibility). Prefer list_news_paginated.
    """
    items: List[NewsItem] = []
    for doc in NewsItemDocument.objects.order_by("-published_at"):
        items.append(
            NewsItem(
                id=doc.id,
                title=doc.title,
                summary=doc.summary,
                link=doc.link,
                source=doc.source,
                category=doc.category,
                published_at=doc.published_at,
            )
        )
    return items


def get_news_by_id(news_id: str) -> Optional[NewsItem]:
    """
    Efficient lookup by primary key. Returns None if missing.
    """
    doc = NewsItemDocument.objects(id=news_id).first()
    if not doc:
        return None
    return NewsItem(
        id=doc.id,
        title=doc.title,
        summary=doc.summary,
        link=doc.link,
        source=doc.source,
        category=doc.category,
        published_at=doc.published_at,
    )


def list_news_paginated(limit: int = 50, offset: int = 0) -> List[NewsItem]:
    """
    Paginated read (limit, offset). Use for UI to avoid loading whole collection.
    """
    qs = NewsItemDocument.objects.order_by("-published_at").skip(offset).limit(limit)
    items = []
    for doc in qs:
        items.append(
            NewsItem(
                id=doc.id,
                title=doc.title,
                summary=doc.summary,
                link=doc.link,
                source=doc.source,
                category=doc.category,
                published_at=doc.published_at,
            )
        )
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
        # classifier.classify may be blocking; this function stays sync
        it.category = classifier.classify(it.title, it.summary or "")
    new = store_items(fetched)
    logger.info("fetch_and_process: new=%d", len(new))
    return new
