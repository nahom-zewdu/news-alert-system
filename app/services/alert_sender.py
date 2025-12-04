# app/services/alert_sender.py
"""
Alert sender service.

Creates alert records in an in-memory history and uses an EmailerInterface for sending.
For production, persist alerts in DB and use durable queues for sending.
"""

from typing import List, Dict
import uuid
from datetime import datetime
import logging

from app.domain.entities import Alert
from app.domain.interfaces import EmailerInterface

logger = logging.getLogger(__name__)

_alert_history: List[Dict] = []


def send_alert_for_news(emailer: EmailerInterface, news_id: str, subject: str, body: str, to: str) -> Dict:
    """
    Send an alert using `emailer`. Record the attempt in in-memory history and return the record.
    """
    record = {
        "id": str(uuid.uuid4()),
        "news_id": news_id,
        "subject": subject,
        "body": body,
        "to": to,
        "sent": False,
        "sent_at": None
    }
    try:
        emailer.send(to=to, subject=subject, body=body)
        record["sent"] = True
        record["sent_at"] = datetime.utcnow().isoformat()
    except Exception as exc:
        logger.exception("Failed to send alert: %s", exc)
    _alert_history.append(record)
    return record


def get_alert_history() -> List[Dict]:
    """
    Return alert history (most recent last).
    """
    return list(_alert_history)
