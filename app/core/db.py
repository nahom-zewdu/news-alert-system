# app/core/db.py
import logging
from mongoengine import connect
from pymongo.server_api import ServerApi
from app.core.config import settings

logger = logging.getLogger(__name__)

def init_db():
    logger.info("Connecting to MongoDB Atlas")
    
    connect(
        host=settings.MONGO_URI,
        server_api=ServerApi('1'),
        uuidRepresentation="standard",
    )
    
    logger.info("MongoDB connection initialized")
    
    # ping test
    try:
        from pymongo.mongo_client import MongoClient
        client = MongoClient(settings.MONGO_URI, server_api=ServerApi('1'))
        client.admin.command('ping')
        logger.info("Ping successful: Connected to MongoDB Atlas!")
    except Exception as e:
        logger.error(f"Ping failed: {e}")