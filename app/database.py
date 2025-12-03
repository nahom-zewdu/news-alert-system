# app/database.py

from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.models import Article

engine = create_engine("postgresql+psycopg2://postgres:postgres@postgres:5432/newsalert")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
