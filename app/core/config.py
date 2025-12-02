# app/core/config.py
"""Configuration settings for the News Alert System."""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "BE TECH News Alert System"
    DEBUG: bool = False

    RSS_FEEDS: List[str] = [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://techcrunch.com/feed/",
    ]

    KEYWORDS: List[str]
    TOPICS: List[str]

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    ALERT_EMAIL_FROM: str
    ALERT_EMAIL_TO: str

    GROQ_API_KEY: str

    REDIS_URL: str = "redis://redis:6379/0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()
