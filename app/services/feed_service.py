# app/services/feed_service.py
"""Service for fetching and parsing news feeds."""

import feedparser
import httpx
from datetime import datetime
from app.core.config import Settings

settings = Settings()

async def fetch_rss_feeds() -> list[dict]:
    articles = []
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in settings.RSS_FEEDS:
            try:
                r = await client.get(url, timeout=10.0)
                r.raise_for_status()
                feed = feedparser.parse(r.text)
                for entry in feed.entries[:15]:  # limit per feed
                    articles.append({
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", "") or entry.get("description", ""),
                        "published": entry.get("published_parsed") or datetime.utcnow(),
                        "source": feed.feed.get("title", url),
                    })
            except Exception as e:
                print(f"Error fetching {url}: {e}")
    return articles
