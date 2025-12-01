# app/models/models.py
"""Database models for the News Alert System."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Article(SQLModel, table=True):
    """Model representing a news article."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    link: str = Field(index=True, unique=True)
    summary: Optional[str] = None
    published: Optional[datetime] = None
    source: str
    matched_keywords: Optional[str] = None  # JSON string
    topic: Optional[str] = None
    notified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
