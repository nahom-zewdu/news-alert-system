# app/infrastructure/groq_client.py
"""
Groq client adapter.
Minimal wrapper around Groq API for text classification.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Minimal Groq client wrapper.

    If api_key is empty, calls to classify_text will raise RuntimeError.
    """

    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key

    def classify_text(self, text: str) -> List[str]:
        """
        Classify `text` and return list of labels.

        Replace this stub with real Groq/OpenAI/etc call.
        """
        if not self.api_key:
            raise RuntimeError("GroqClient: missing API key")
        # TODO: implement actual HTTP call to Groq SDK/API and parse response.
        logger.info("GroqClient.classify_text called — implement actual network call.")
        # Example placeholder response:
        return ["uncategorized"]
