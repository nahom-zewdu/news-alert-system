# app/api/schemas.py
"""
Pydantic request/response schemas for API endpoints.

Keep these small and explicit so the OpenAPI docs are useful during the demo.
"""

from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional
from datetime import datetime


class SendAlertRequest(BaseModel):
    """
    Body for sending alert manually. 'to' defaults to configured ALERT_EMAIL_TO
    when omitted.
    """
    to: Optional[EmailStr] = None


class NewsListResponse(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    link: Optional[HttpUrl]
    source: Optional[str]
    category: Optional[str]
    published_at: Optional[datetime]


class FetchResponse(BaseModel):
    new_count: int
    # To avoid returning huge payloads, this includes only the newly added ids
    items: List[str]
