# app/core/db.py
""" Initialize database connection. """
from mongoengine import connect
import os
from app.core.config import settings


def init_db():
    MONGO_URI = os.getenv(settings.MONGO_URI, "mongodb://localhost:27017/news_db")
    connect(host=MONGO_URI)
