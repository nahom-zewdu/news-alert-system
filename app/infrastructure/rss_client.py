# app/infrastructure/rss_client.py
"""
RSS client implementation.

Uses `feedparser` to read RSS/Atom feeds and convert entries into NewsItem entities.
Synchronous and intentionally simple for demo purposes.
"""

from typing import List
import feedparser
from datetime import datetime
import uuid
import logging

from app.domain.entities import NewsItem
from app.core.config import settings

logger = logging.getLogger(__name__)


def fetch_from_feed_url(url: str) -> List[NewsItem]:
    """
    Fetch and normalize one RSS/Atom feed.
    """
    logger.info("Fetching RSS feed: %s", url)
    parsed = feedparser.parse(url)
    items: List[NewsItem] = []
    for entry in parsed.entries:
        nid = entry.get("id") or entry.get("guid") or entry.get("link") or str(uuid.uuid4())
        published_at = None
        if entry.get("published_parsed"):
            published_at = datetime(*entry.published_parsed[:6])
        categories = []
        if entry.get("tags"):
            for tag in entry.get("tags"):
                term = tag.get("term")
                if term:
                    categories.append(term)
        category = categories[0] if categories else "uncategorized"
        item = NewsItem(
            id=str(nid),
            title=entry.get("title", "")[:500],
            link=entry.get("link"),
            summary=entry.get("summary"),
            published_at=published_at,
            source=parsed.feed.get("title"),
            category=category,
        )
        items.append(item)
    return items


def fetch_all_configured() -> List[NewsItem]:
    """
    Fetch all feeds defined in settings and return aggregated NewsItem list.
    """
    feeds = settings.rss_feed_list
    logger.info("Configured RSS feeds: %s", feeds)
    result = []
    for f in feeds:
        try:
            result.extend(fetch_from_feed_url(f))
        except Exception as exc:
            logger.exception("Failed to fetch feed %s: %s", f, exc)
    return result
