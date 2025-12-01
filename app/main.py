# app/main.py
"""Main application entry point for the News Alert System."""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.workers import ingest
from rq import Queue
from redis import Redis
import asyncio

redis_conn = Redis.from_url(settings.REDIS_URL)
queue = Queue(connection=redis_conn)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: enqueue first ingestion
    queue.enqueue(ingest.run_ingestion)
    yield

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "News Alert System running demo."}

@app.get("/health")
async def health():
    return {"status": "healthy"}
