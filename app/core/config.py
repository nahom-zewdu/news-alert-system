### app/core/config.py
"""
Application configuration.

Loads environment variables using Pydantic's BaseSettings for typed access.
Provides convenience helpers (rss_feed_list).
"""

try:
    # pydantic v2 provides settings in a separate package
    from pydantic_settings import BaseSettings
    from pydantic import Field
except Exception:
    # fallback for pydantic v1 where BaseSettings is in pydantic
    from pydantic import BaseSettings, Field

from typing import List, Optional


class Settings(BaseSettings):
    APP_HOST: str = Field("127.0.0.1", env="APP_HOST")
    APP_PORT: int = Field(8000, env="APP_PORT")

    # SMTP settings
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASS: str = Field(..., env="SMTP_PASS")
    ALERT_EMAIL_FROM: str
    ALERT_EMAIL_TO: str

    # LLM / Groq
    GROQ_API_KEY: Optional[str] = ""
    GROQ_MODEL: str = Field("llama-3.1-8b-instant", env="GROQ_MODEL")

    # News filtering
    KEYWORDS: Optional[str] = "[]"
    TOPICS: Optional[str] = "[]"

    # Redis (future)
    REDIS_URL: Optional[str] = None

    # MongoDB
    MONGO_URI: str = Field("mongodb://localhost:27017/news_db", env="MONGO_URI")
    
    # Scheduler mode
    SCHEDULER_MODE: str = Field("background")

    # RSS feeds
    RSS_FEEDS: Optional[str] = ""

    # Logging
    LOG_LEVEL: str = Field("INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


    @property
    def rss_feed_list(self) -> List[str]:
        """
        Return a list of RSS feed URLs configured in RSS_FEEDS.
        """
        raw = (self.RSS_FEEDS or "").strip()
        if not raw:
            return []
        return [s.strip() for s in raw.split(",") if s.strip()]


settings = Settings()
