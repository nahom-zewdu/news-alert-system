# app/api/routes_subscribers.py
"""
Subscriber management API.
- POST /api/v1/subscribers - subscribe (email + optional topics)
- DELETE /api/v1/subscribers/{email} - unsubscribe
- GET /api/v1/subscribers - list all (admin/demo only)
"""
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from app.models.subscriber_doc import SubscriberDocument
from mongoengine.errors import NotUniqueError

router = APIRouter()

class SubscribeRequest(BaseModel):
    email: EmailStr
    topics: Optional[List[str]] = None  # e.g., ["politics", "technology"]

@router.post("/", status_code=201)
def subscribe(payload: SubscribeRequest):
    try:
        doc = SubscriberDocument(email=payload.email, topics=payload.topics or [])
        doc.save()
        return {"message": "Subscribed successfully"}
    except NotUniqueError:
        raise HTTPException(status_code=409, detail="Email already subscribed")

@router.delete("/{email}", status_code=200)
def unsubscribe(email: str = Path(..., description="Email to unsubscribe")):
    result = SubscriberDocument.objects(email=email, active=True).update(active=False)
    if result == 0:
        raise HTTPException(status_code=404, detail="Subscriber not found or already inactive")
    return {"message": "Unsubscribed successfully"}

@router.get("/", response_model=List[dict])
def list_subscribers():
    subs = SubscriberDocument.objects(active=True)
    return [{"email": s.email, "topics": s.topics} for s in subs]