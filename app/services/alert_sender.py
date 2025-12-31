# app/services/alert_sender.py
"""
Alert sender service.
Now sends to all subscribers whose topics match the news category.
Stores alert history per recipient.
"""
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timezone

from app.infrastructure.smtp_emailer import SMTPEmailer
from app.services.news_fetcher import get_news_by_id
from app.domain.entities import NewsItem
from app.models.alert_doc import AlertDocument
from app.models.subscriber_doc import SubscriberDocument

logger = logging.getLogger(__name__)

def build_message_for_news(news: NewsItem) -> Dict[str, str]:
    subject = f"[News Alert] {news.title}"
    body_lines = [
        news.title,
        "",
        news.summary or "",
        "",
        f"Source: {news.source or 'unknown'}",
        f"Category: {news.category or 'uncategorized'}",
    ]
    if news.link:
        body_lines.append("")
        body_lines.append(f"Link: {news.link}")
    body = "\n".join(line for line in body_lines if line)
    return {"subject": subject, "body": body}

def send_alert_for_news(
    emailer: SMTPEmailer,
    news_id: str,
    subject: Optional[str] = None,
    body: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Send alert to all active subscribers interested in the news category.
    Returns list of send records.
    """
    news = get_news_by_id(news_id)
    if not news:
        raise ValueError("news item not found")

    category = news.category or "uncategorized"

    # Find subscribers interested in this category (or all if no topics specified)
    subscribers = SubscriberDocument.objects(active=True).filter(
        __raw__={"$or": [{"topics": category}, {"topics": {"$size": 0}}]}
    )

    if not subscribers:
        logger.info("No subscribers for category %s", category)
        return []

    msg = build_message_for_news(news)
    subject = subject or msg["subject"]
    body = body or msg["body"]

    records = []
    for sub in subscribers:
        record = AlertDocument(
            news_id=news_id,
            to=sub.email,
            subject=subject,
            body=body,
            sent=False,
            sent_at=datetime.now(timezone.utc)
        )
        try:
            emailer.send(to=sub.email, subject=subject, body=body)
            record.sent = True
            record.sent_at = datetime.now(timezone.utc)
            logger.info("Alert sent to %s for news_id=%s", sub.email, news_id)
        except Exception as exc:
            record.error = str(exc)
            record.sent_at = datetime.now(timezone.utc)
            logger.exception("Failed to send to %s", sub.email)
        record.save()
        records.append({
            "to": record.to,
            "sent": record.sent,
            "error": record.error,
            "sent_at": record.sent_at.isoformat() if record.sent_at else None,
        })

    return records

def get_alert_history(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    qs = AlertDocument.objects.order_by("-sent_at").skip(offset).limit(limit)
    return [
        {
            "news_id": a.news_id,
            "to": a.to,
            "subject": a.subject,
            "sent": a.sent,
            "error": a.error,
            "sent_at": a.sent_at.isoformat() if a.sent_at else None,
        }
        for a in qs
    ]