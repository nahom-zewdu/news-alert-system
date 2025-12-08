# app/models/news_item_doc.py
"""Defines the MongoEngine document model for NewsItem storage."""

from mongoengine import Document, StringField, ListField, DateTimeField
from datetime import datetime, timezone

class NewsItemDocument(Document):
    meta = {"collection": "news"}
    
    id = StringField(required=True, primary_key=True)
    title = StringField(required=True)
    summary = StringField()
    link = StringField(unique=True, required=True)
    source = StringField()
    category = StringField()
    published_at = DateTimeField(default=datetime.now(timezone.utc))
