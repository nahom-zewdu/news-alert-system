# app/domain/entities.py
"""
Domain entities for the News Alert system.

Pydantic models are used for validation and convenient serialization.
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Category(str, Enum):
    TECH = "tech"
    BUSINESS = "business"
    POLITICS = "politics"
    HEALTH = "health"
    SPORTS = "sports"
    UNCATEGORIZED = "uncategorized"


class NewsItem(BaseModel):
    """
    Represents a normalized news item.
    """
    id: str
    title: str
    link: Optional[HttpUrl] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    source: Optional[str] = None
    categories: List[str] = []


class Alert(BaseModel):
    """
    Represents a sent alert (minimal schema for demo).
    """
    id: str
    news_id: str
    subject: str
    body: str
    to: str
    sent: bool = False
    sent_at: Optional[datetime] = None
