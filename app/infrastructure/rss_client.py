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
    Handles Hacker News special case where <link> is comments page.
    """
    logger.info("Fetching RSS feed: %s", url)
    parsed = feedparser.parse(url)
    items: List[NewsItem] = []

    # Detect if this is Hacker News feed
    is_hn = "news.ycombinator.com" in url or (parsed.feed.get("title") or "").lower().startswith("hacker news")

    for entry in parsed.entries:
        nid = entry.get("id") or entry.get("guid") or entry.get("link") or str(uuid.uuid4())

        published_at = None
        if entry.get("published_parsed"):
            published_at = datetime(*entry.published_parsed[:6])

        categories = []
        if entry.get("tags"):
            for tag in entry.get("tags", []):
                term = tag.get("term")
                if term:
                    categories.append(term)
        category = categories[0] if categories else "uncategorized"

        # Default values
        article_link = entry.get("link")
        summary = entry.get("summary", "")

        # Resolve Hacker News article link from comments link
        if is_hn and summary:
            import re
            match = re.search(r'<a href="([^"]+)">', summary)
            if match:
                article_link = match.group(1)
                summary = re.sub(r'<a href="[^"]+">Comments</a>\s*', '', summary).strip()

        item = NewsItem(
            id=str(nid),
            title=entry.get("title", "")[:500],
            link=article_link,
            summary=summary or None,
            published_at=published_at,
            source=parsed.feed.get("title", "Unknown"),
            category=category,
        )
        items.append(item)

    return items


def fetch_all_configured(limit_per_feed: int = 5) -> List[NewsItem]:
    """Fetch all feeds defined in settings, aggregate items, with a per-feed limit."""
    feeds = settings.rss_feed_list
    logger.info("Configured RSS feeds: %s", feeds)
    all_items: List[NewsItem] = []

    for feed_url in feeds:
        try:
            items = fetch_from_feed_url(feed_url)
            all_items.extend(items[:limit_per_feed])
        except Exception:
            logger.exception("Failed to fetch feed %s", feed_url)

    return all_items
