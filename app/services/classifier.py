# app/services/classifier.py
"""Service for classifying news articles."""
import os
from groq import Groq
from app.core.config import Settings

settings = Settings()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_article(title: str, summary: str) -> dict:
    text = f"{title}\n{summary}"[:2000]
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # or "mixtral-8x7b-32768"
            messages=[
                {"role": "system", "content": f"You are a news classifier. Only output one word from this list: {', '.join(settings.TOPICS)}. If unsure, reply 'other'."},
                {"role": "user", "content": text}
            ],
            temperature=0.0,
            max_tokens=10
        )
        topic = response.choices[0].message.content.strip().lower()
        return {"topic": topic if topic in [t.lower() for t in settings.TOPICS] else "other", "confidence": 0.99}
    except Exception as e:
        print(f"Groq error: {e}")
        return {"topic": "unknown", "confidence": 0.0}
