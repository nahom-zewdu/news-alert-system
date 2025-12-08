# app/api/routes_admin.py
from fastapi import APIRouter, HTTPException, status
from app.models.news_item_doc import NewsItemDocument
from app.models.alert_doc import AlertDocument
from pymongo.errors import PyMongoError

router = APIRouter()

@router.post("/reset-db")
async def reset_db():
    """
    Delete all news and alerts documents. DEVELOPMENT ONLY.
    """
    try:
        news_result = NewsItemDocument.objects.delete()
        alerts_result = AlertDocument.objects.delete()
        return {
            "message": "Database reset complete",
            "news_deleted": news_result,
            "alerts_deleted": alerts_result,
        }
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB reset failed: {e}"
        )
