# app/core/config.py
"""Configuration settings for the News Alert System."""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "BE TECH News Alert System"
    DEBUG: bool = False

    # Sources
    RSS_FEEDS: List[str] = [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://techcrunch.com/feed/",
    ]
    NEWSAPI_KEY: str = ""  # optional
    NEWSAPI_URL: str = "https://newsapi.org/v2/everything"

    # Filtering
    KEYWORDS: List[str] = ["AI", "artificial intelligence", "machine learning", "Ethiopia", "Addis Ababa"]
    TOPICS: List[str] = ["technology", "business", "science"]  # for zero-shot

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    ALERT_EMAIL_TO: str
    ALERT_EMAIL_FROM: str

    # Redis & RQ
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
