# app/api/routes_alerts.py
"""
Routes for alert operations.

- GET /api/v1/alerts - history (paginated)
- POST /api/v1/alerts/{news_id} - send an alert for a news item
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
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
    """
    return SMTPEmailer(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        user=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        default_from=settings.ALERT_EMAIL_FROM,
    )


@router.get("/", tags=["alerts"])
async def api_alerts(
    limit: int = Query(100, ge=1, le=500, description="Number of alerts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Return stored alert history, paginated.
    """
    try:
        alerts = await run_in_threadpool(get_alert_history, limit=limit, offset=offset)
        return {"count": len(alerts), "alerts": alerts}
    except Exception:
        logger.exception("Failed to retrieve alert history")
        raise HTTPException(status_code=500, detail="Failed to fetch alert history")


@router.post("/{news_id}", tags=["alerts"])
async def api_send_alert(
    news_id: str = Path(..., description="ID of the news item"),
    emailer: SMTPEmailer = Depends(get_emailer),
):
    try:
        records = await run_in_threadpool(send_alert_for_news, emailer, news_id)
        if not records:
            raise HTTPException(status_code=404, detail="No subscribers for this category")
        return {"sent_count": len([r for r in records if r["sent"]]), "records": records}
    except ValueError:
        raise HTTPException(status_code=404, detail="news item not found")
    except Exception:
        logger.exception("Unhandled error")
        raise HTTPException(status_code=500)
