# app/api/routes_news.py
"""
Routes for news operations (API v1).

- GET /api/v1/news -> list with pagination
- POST /api/v1/news/fetch -> trigger fetch+classify (returns new_count and item ids)
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
import logging
from functools import lru_cache
from fastapi.concurrency import run_in_threadpool

from app.services.news_fetcher import list_news_paginated, fetch_and_process
from app.infrastructure.groq_client import GroqClient
from app.services.classifier import ClassifierService
from app.core.config import settings
from app.api.schemas import NewsListResponse, FetchResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@lru_cache()
def get_classifier() -> ClassifierService:
    """
    Cached factory for ClassifierService — reuses Groq client across requests.
    """
    groq = None
    if settings.GROQ_API_KEY:
        groq = GroqClient(settings.GROQ_API_KEY)
    return ClassifierService(classifier=groq)


@router.get("/", response_model=List[NewsListResponse], tags=["news"])
async def api_list_news(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    """
    Return paginated news items. Use limit/offset for pagination.
    """
    items = await run_in_threadpool(list_news_paginated, limit, offset)
    return items


@router.post("/fetch", response_model=FetchResponse, tags=["news"])
async def api_fetch_now(classifier: ClassifierService = Depends(get_classifier)):
    """
    Trigger a fetch + classify across configured RSS feeds.
    Runs in a threadpool because fetch_and_process is sync and performs blocking IO.
    """
    new_items = await run_in_threadpool(fetch_and_process, classifier)
    # Return only the added ids to avoid huge payloads
    item_ids = [it.id for it in new_items]
    return {"new_count": len(new_items), "items": item_ids}
