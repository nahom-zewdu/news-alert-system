# app/core/db.py
""" Initialize database connection. """
from mongoengine import connect
import os
from app.core.config import settings


def init_db():
    MONGO_URI = settings.MONGO_URI
    connect(host=MONGO_URI)
