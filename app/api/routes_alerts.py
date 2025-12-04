# app/api/routes_alerts.py
"""
Routes for alert operations.

- /api/alerts [GET] - history
- /api/send [POST] - send an alert for a news item
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Any
import logging

from app.services.alert_sender import send_alert_for_news, get_alert_history
from app.services.news_fetcher import list_news
from app.infrastructure.smtp_emailer import SMTPEmailer
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_emailer() -> SMTPEmailer:
    """
    Instantiate SMTPEmailer from config.
    """
    return SMTPEmailer(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        user=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        default_from=settings.ALERT_EMAIL_FROM,
    )


@router.get("/alerts", tags=["alerts"])
def api_alerts():
    """
    Return stored alert history.
    """
    return get_alert_history()


@router.post("/send", tags=["alerts"])
def api_send_alert(news_id: str, to: str = settings.ALERT_EMAIL_TO, emailer: SMTPEmailer = Depends(get_emailer)) -> Any:
    """
    Send an alert for a given news_id. Builds a simple subject/body from the news item.
    """
    all_news = list_news()
    match = next((n for n in all_news if n.id == news_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="news item not found")
    subject = f"News Alert: {match.title}"
    body = f"{match.title}\n\n{match.summary or ''}\n\nLink: {match.link or ''}"
    rec = send_alert_for_news(emailer, news_id=news_id, subject=subject, body=body, to=to)
    return rec
