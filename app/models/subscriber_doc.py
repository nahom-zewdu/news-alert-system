# app/models/subscriber_doc.py
"""
MongoEngine document for newsletter subscribers.
"""
from mongoengine import Document, StringField, ListField, DateTimeField, BooleanField
from datetime import datetime, timezone

class SubscriberDocument(Document):
    meta = {"collection": "subscribers"}
    
    email = StringField(required=True, unique=True)
    topics = ListField(StringField(), default=list)  # e.g., ["politics", "technology"]
    subscribed_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    active = BooleanField(default=True)
