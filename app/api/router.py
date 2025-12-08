# app/api/router.py
"""
API router aggregator.

This module exposes a single APIRouter for API v1.  All route modules should
be mounted under /api/v1 to permit non-breaking future changes.
"""

from fastapi import APIRouter

from app.api import routes_news, routes_alerts, routes_admin

api_v1 = APIRouter(prefix="/v1")
api_v1.include_router(routes_news.router, prefix="/news", tags=["news"])
api_v1.include_router(routes_alerts.router, prefix="/alerts", tags=["alerts"])
api_v1.include_router(routes_admin.router, prefix="/admin", tags=["admin"])

def get_root_router() -> APIRouter:
    """
    Return the root APIRouter used by the FastAPI app.
    """
    return api_v1
