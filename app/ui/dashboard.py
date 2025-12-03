# app/ui/dashboard.py
"""Streamlit dashboard for monitoring the News Alert System."""

import streamlit as st
from sqlmodel import Session, select, create_engine
from sqlalchemy import desc
from app.models.models import Article
import pandas as pd

engine = create_engine("postgresql+psycopg2://postgres:postgres@postgres:5432/newsalert")

st.set_page_config(page_title="BE TECH News Alerts", layout="wide")
st.title("News Alert System Live Dashboard")
st.markdown("**Real-time monitoring | AI classification | Zero duplicates**")

# Auto-refresh every 30 seconds
st.autorefresh(interval=30_000)
with Session(engine) as session:
    articles = session.exec(select(Article).order_by(desc(Article.created_at)).limit(50)).all()

if not articles:
    st.info("No articles yet ingestion worker will populate soon.")
else:
    df = pd.DataFrame([
        {
            "Time": a.created_at.strftime("%H:%M"),
            "Source": a.source[:20],
            "Topic": a.topic.title(),
            "Keywords": a.matched_keywords or "—",
            "Title": a.title[:80] + "..." if len(a.title) > 80 else a.title,
            "Link": a.link
        }
        for a in articles
    ])

    st.dataframe(df[["Time", "Source", "Topic", "Keywords", "Title"]], 
                 use_container_width=True,
                 hide_index=True,
                 on_select="rerun",
                 column_config={"Link": st.column_config.LinkColumn()})
