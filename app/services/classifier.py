# app/services/classifier.py
"""
Classifier service.

Tries to use a pluggable LLM (GroqClient) if present; otherwise falls back to a simple
keyword-based classifier. Returns a list of category labels as strings.
"""

from typing import List, Optional
import re
import logging

from app.infrastructure.groq_client import GroqClient
from app.domain.interfaces import ClassifierInterface

logger = logging.getLogger(__name__)

DEFAULT_KEYWORDS = {
    "tech": ["ai", "ml", "machine learning", "openai", "software", "developer", "cloud"],
    "business": ["market", "stock", "ipo", "funding", "investment", "economy"],
    "politics": ["president", "election", "parliament", "policy", "government"],
    "health": ["covid", "vaccine", "health", "hospital", "medical"],
    "sports": ["football", "soccer", "nba", "cricket", "olympic"],
}


class ClassifierService(ClassifierInterface):
    """
    Pluggable classifier which accepts an optional GroqClient instance.
    """

    def __init__(self, groq: Optional[GroqClient] = None):
        self.groq = groq

    def classify(self, title: str, summary: str = "") -> List[str]:
        """
        Return list of categories for the provided title/summary.
        """
        text = f"{title}\n{summary}".lower()
        # Try LLM first
        if self.groq:
            try:
                labels = self.groq.classify_text(text)
                if labels:
                    logger.info("Classified via Groq: %s", labels)
                    return labels
            except Exception as exc:
                logger.warning("Groq classification failed, falling back to keyword classifier: %s", exc)

        # Keyword fallback
        found = set()
        for label, keywords in DEFAULT_KEYWORDS.items():
            pattern = r"\b(" + "|".join(re.escape(k) for k in keywords) + r")\b"
            if re.search(pattern, text):
                found.add(label)
        if not found:
            return ["uncategorized"]
        return sorted(found)
