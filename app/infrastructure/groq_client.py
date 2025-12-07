# app/infrastructure/groq_client.py
"""
Groq client adapter.
Minimal wrapper around Groq API for text classification.
"""

from typing import List, Optional
import logging
from app.core.config import Settings
try:
    from groq import Groq
except ImportError:
    Groq = None  # Allows app to start even if SDK is missing

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Minimal Groq client wrapper for classification.
    """

    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key

        if api_key and Groq is None:
            logger.warning(
                "Groq SDK not installed but GROQ_API_KEY provided. "
                "Run `uv add groq` to enable Groq integration."
            )

        self.client = Groq(api_key=api_key) if api_key and Groq else None

    def classify(self, text: str, settings: Settings) -> str:
        """
        Classify free-form text using Groq LLM.
        """

        if not self.api_key:
            raise RuntimeError("GroqClient: missing API key")
        if self.client is None:
            raise RuntimeError("GroqClient: Groq SDK unavailable")

        try:
            logger.debug("Calling Groq classify_text()")

            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a classification engine. "
                            f"Classify the following text into relevant category from this list: {settings.TOPICS}. "
                            "Respond only with one category, or 'uncategorized' if none apply."
                        ),
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                temperature=0.0,
                max_tokens=50,
            )
            category = response.choices[0].message.content.strip()
            logger.info("Groq classified text as category: %s", category)
            return category or "uncategorized"

        except Exception:
            logger.exception("Groq classification request failed")
            return "uncategorized"
