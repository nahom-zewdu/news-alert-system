# app/core/db.py
"""Initialize MongoDB connection via MongoEngine."""
import logging
from mongoengine import connect
from urllib.parse import quote_plus
from app.core.config import settings

logger = logging.getLogger(__name__)

def init_db():
    username = quote_plus(settings.MONGO_DB_ATLAS_USERNAME)
    password = quote_plus(settings.MONGO_DB_ATLAS_PASSWORD)
    host = settings.MONGO_DB_ATLAS_HOST
    db = settings.MONGO_DB_NAME

    # MongoDB Atlas connection URI
    uri = f"mongodb+srv://{username}:{password}@{host}/{db}?retryWrites=true&w=majority"

    logger.info("Connecting to MongoDB Atlas")

    # Connect without deprecated tlsVersion or SSL params
    connect(
        db=db,
        host=uri,
        tls=True,  # Use TLS, default to latest supported
        tlsAllowInvalidCertificates=False,
        uuidRepresentation="standard",
    )

    logger.info("MongoDB connection initialized")
