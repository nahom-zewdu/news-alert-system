# app/api/router.py
"""
API router aggregator.

Includes news and alert routers and exposes a health endpoint.
"""

from fastapi import APIRouter

from app.api import routes_news, routes_alerts

router = APIRouter()
router.include_router(routes_news.router, prefix="", tags=["news"])
router.include_router(routes_alerts.router, prefix="", tags=["alerts"])


def get_root_router() -> APIRouter:
    """
    Return the root APIRouter used by the FastAPI app.
    """
    return router
