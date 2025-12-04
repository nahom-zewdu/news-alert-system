# app/infrastructure/groq_client.py
"""
Groq client adapter.
Minimal wrapper around Groq API for text classification.
"""

from typing import List, Optional
import logging

try:
    from groq import Groq
except ImportError:  # pragma: no cover
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

    def classify_text(self, text: str, model: str = "llama-3.1-8b-instant") -> List[str]:
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
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a classification engine. "
                            "Return ONLY a comma-separated list of categories."
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

            raw = response.choices[0].message.content.strip()
            logger.debug("Groq raw response: %s", raw)

            # Basic parsing: split comma-separated categories
            labels = [x.strip().lower() for x in raw.split(",") if x.strip()]
            return labels or ["uncategorized"]

        except Exception:
            logger.exception("Groq classification request failed")
            return ["uncategorized"]
