# app/api/routes_alerts.py
"""
Routes for alert operations.

- GET /api/v1/alerts - history
- POST /api/v1/alerts/{news_id} - send an alert for a news item
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.concurrency import run_in_threadpool
from functools import lru_cache
from typing import Any, Optional
import logging

from app.api.schemas import SendAlertRequest
from app.services.alert_sender import send_alert_for_news, get_alert_history
from app.infrastructure.smtp_emailer import SMTPEmailer
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@lru_cache()
def get_emailer() -> SMTPEmailer:
    """
    Create and cache a singleton SMTPEmailer instance per process.
    This avoids creating a new SMTP client on every request.
    """
    return SMTPEmailer(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        user=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        default_from=settings.ALERT_EMAIL_FROM,
    )


@router.get("/", tags=["alerts"])
async def api_alerts():
    """
    Return stored alert history.
    """
    # run in threadpool if history retrieval hits DB
    result = await run_in_threadpool(get_alert_history)
    return result


@router.post("/{news_id}", tags=["alerts"])
async def api_send_alert(
    news_id: str = Path(..., description="ID of the news item"),
    payload: SendAlertRequest = None,
    emailer: SMTPEmailer = Depends(get_emailer),
) -> Any:
    """
    Send an alert for a given news_id. The 'to' address can be provided in the
    body; otherwise the configured ALERT_EMAIL_TO is used.
    """
    to_addr = payload.to if payload and payload.to else settings.ALERT_EMAIL_TO

    try:
        # send_alert_for_news is sync; delegate to threadpool
        record = await run_in_threadpool(send_alert_for_news, emailer, news_id, to_addr)
        # inspect record to determine success
        if not record.get("sent"):
            raise HTTPException(status_code=502, detail=f"Failed to send alert: {record.get('error')}")
        return record
    except ValueError:
        raise HTTPException(status_code=404, detail="news item not found")
    except Exception as exc:
        logger.exception("Unhandled error while sending alert")
        raise HTTPException(status_code=500, detail="internal error")
