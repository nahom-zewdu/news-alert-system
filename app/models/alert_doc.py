# app/models/alert_doc.py
"""Defines the MongoEngine document model for storing sent alerts."""

from mongoengine import Document, StringField, BooleanField, DateTimeField
from datetime import datetime, timezone

class AlertDocument(Document):
    meta = {"collection": "alerts"}
    
    news_id = StringField(required=True)
    to = StringField(required=True)     
    subject = StringField(required=True)
    body = StringField()
    sent = BooleanField(default=False)  
    error = StringField()               
    sent_at = DateTimeField(default=datetime.now(timezone.utc))
