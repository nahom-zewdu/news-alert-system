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
from app.core.config import Settings

logger = logging.getLogger(__name__)

class ClassifierService(ClassifierInterface):
    """
    Pluggable classifier which accepts an optional GroqClient instance.
    """

    def __init__(self, classifier: Optional[GroqClient] = None):
        self.classifier = classifier

    def classify(self, title: str, settings: Settings, summary: str = "") -> str:
        """
        Return list of categories for the provided title/summary.
        """
        text = f"{title}\n{summary}".lower()
        # Try LLM first
        if self.classifier:
            try:
                label = self.classifier.classify(text, settings)
                if label:
                    logger.info("Classified via Groq: %s", label)
                    return label
            except Exception as exc:
                logger.warning("Groq classification failed, falling back to keyword classifier: %s", exc)
    
        # Fallback: simple keyword matching
        for keyword in settings.KEYWORDS.split(","):
            keyword = keyword.strip().lower()
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                logger.info("Classified via keyword match: %s", keyword)
                return keyword 
        logger.info("No classification match found; returning 'uncategorized'")
        return "uncategorized"
