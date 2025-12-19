# app/core/db.py
""" Initialize database connection. """
from mongoengine import connect
import os
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def init_db():
    logger.info("Connecting to MongoDB")
    MONGO_URI = settings.MONGO_URI
    connect(host=MONGO_URI)
