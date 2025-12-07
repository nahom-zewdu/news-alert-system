# app/services/alert_sender.py
"""
Alert sender service.

Encapsulates building email messages for a news item and sending them using
the SMTPEmailer adapter (infra layer). Stores alert history in MongoDB.
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timezone

from app.infrastructure.smtp_emailer import SMTPEmailer
from app.services.news_fetcher import get_news_by_id
from app.domain.entities import NewsItem
from app.models.alert_doc import AlertDocument

logger = logging.getLogger(__name__)


def build_message_for_news(news: NewsItem) -> Dict[str, str]:
    """
    Build a short subject and plain-text body for the supplied news item.
    """
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
    body = "\n".join(line for line in body_lines if line is not None)
    return {"subject": subject, "body": body}


def send_alert_for_news(
    emailer: SMTPEmailer,
    news_id: str,
    to: str,
    subject: Optional[str] = None,
    body: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send an alert for a news item and store it in MongoDB.
    Returns a record describing the result.
    """
    news = get_news_by_id(news_id)
    if not news:
        raise ValueError("news item not found")

    # Build message if caller didn't supply
    if not subject or not body:
        msg = build_message_for_news(news)
        subject = subject or msg["subject"]
        body = body or msg["body"]

    record = AlertDocument(
        news_id=news_id,
        to=to,
        subject=subject,
        body=body,
        sent=False,
        sent_at=datetime.now(timezone.utc)
    )

    try:
        emailer.send(to=to, subject=subject, body=body)
        record.sent = True
        record.sent_at = datetime.now(timezone.utc)
        record.save()
        logger.info("Email sent for news_id=%s to=%s", news_id, to)
    except Exception as exc:
        record.error = str(exc)
        record.sent_at = datetime.now(timezone.utc)
        record.save()
        logger.exception("Failed to send email for news_id=%s to=%s", news_id, to)

    return {
        "news_id": record.news_id,
        "to": record.to,
        "subject": record.subject,
        "body": record.body,
        "sent": record.sent,
        "error": record.error,
        "sent_at": record.sent_at.isoformat(),
    }


def get_alert_history(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Retrieve alert history from MongoDB, paginated.
    """
    qs = AlertDocument.objects.order_by("-sent_at").skip(offset).limit(limit)
    return [
        {
            "news_id": a.news_id,
            "to": a.to,
            "subject": a.subject,
            "body": a.body,
            "sent": a.sent,
            "error": a.error,
            "sent_at": a.sent_at.isoformat(),
        }
        for a in qs
    ]
