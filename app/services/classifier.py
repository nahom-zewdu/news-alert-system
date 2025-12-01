# app/services/classifier.py
"""Service for classifying news articles into topics using zero-shot classification."""

from transformers import pipeline
from app.core.config import settings
import torch

# Load once at import time fast on CPU, instant on GPU if available
device = 0 if torch.cuda.is_available() else -1
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=device,
    batch_size=8
)

def classify_article(title: str, summary: str) -> dict:
    text = f"{title} {summary}"[:1000]  # truncate for speed
    if not text.strip():
        return {"topic": "unknown", "confidence": 0.0}

    result = classifier(text, candidate_labels=settings.TOPICS, multi_label=False)
    return {
        "topic": result["labels"][0],
        "confidence": round(result["scores"][0], 3)
    }
