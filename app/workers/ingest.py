# app/workers/ingest.py
"""Worker for ingesting news articles from RSS feeds, classifying them, and storing in the database."""

from app.services.feed_service import fetch_rss_feeds
from app.services.classifier import classify_article
from app.models import Article
from sqlmodel import Session, create_engine, select
from app.core.config import settings
from datetime import datetime, timezone
import json

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/newsalert")

def run_ingestion():
    """Ingestion job to fetch, classify, and store news articles."""
    print(f"[{datetime.now(timezone.utc)}] Starting ingestion job started")
    articles = []
    
    # Use sync inside worker (RQ runs sync functions)
    import asyncio
    articles = asyncio.run(fetch_rss_feeds())

    with Session(engine) as session:
        for raw in articles:
            # De-duplication
            stmt = select(Article).where(Article.link == raw["link"])
            if session.exec(stmt).first():
                continue

            # Classify
            classification = classify_article(raw["title"], raw["summary"])

            # Keyword matching
            title_lower = raw["title"].lower()
            summary_lower = raw["summary"].lower()
            matched = [kw for kw in settings.KEYWORDS if kw.lower() in title_lower or kw.lower() in summary_lower]

            if not matched and classification["confidence"] < 0.4:
                continue  # skip irrelevant

            article = Article(
                title=raw["title"],
                link=raw["link"],
                summary=raw["summary"],
                published=datetime(*raw["published"][:6]) if isinstance(raw["published"], tuple) else None,
                source=raw["source"],
                matched_keywords=json.dumps(matched),
                topic=classification["topic"],
            )
            session.add(article)
        session.commit()
    print(f"[{datetime.now(timezone.utc)}] ingestion finished {len(articles)} fetched, new relevant articles added")
