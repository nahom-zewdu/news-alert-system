# app/ui/streamlit.py
"""
Streamlit demo UI.

Talks to the FastAPI backend at http://127.0.0.1:8000/api by default.
Provides controls to fetch, view news, and send alerts.
"""

import streamlit as st
import requests
from app.core.config import settings as _settings

API_BASE = f"http://{_settings.APP_HOST}:{_settings.APP_PORT}/api"

st.set_page_config(page_title="News Alert Demo", layout="wide")
st.title("News Alert System — Demo Dashboard")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("News")
    if st.button("Fetch now"):
        r = requests.post(f"{API_BASE}/fetch")
        if r.ok:
            st.success(f"Fetched {r.json().get('new_count')} new items")
        else:
            st.error("Fetch failed; check API logs")

    r = requests.get(f"{API_BASE}/news")
    if r.ok:
        news = r.json()
    else:
        news = []
        st.error("Failed to load news from API")

    for item in news:
        st.subheader(item.get("title"))
        st.write(f"Source: {item.get('source')} — Categories: {', '.join(item.get('categories', []))}")
        st.write(item.get("summary") or "")
        if item.get("link"):
            st.markdown(f"[Open link]({item.get('link')})")
        cols = st.columns([1, 1, 4])
        with cols[0]:
            if st.button("Send Alert", key=item["id"]):
                send = requests.post(f"{API_BASE}/send", params={"news_id": item["id"]})
                if send.ok:
                    st.success("Alert sent (check history)")
                else:
                    st.error(f"Failed to send alert: {send.text}")
        with cols[1]:
            st.write("")
        with cols[2]:
            st.write("---")

with col_right:
    st.header("Alert history")
    a = requests.get(f"{API_BASE}/alerts")
    if a.ok:
        alerts = a.json()
        for al in list(reversed(alerts)):
            st.write(f"To: {al['to']} | Subject: {al['subject']} | Sent: {al['sent']} | At: {al.get('sent_at')}")
    else:
        st.write("No alert history (or failed to load)")

st.sidebar.header("Config")
st.sidebar.write("API:", API_BASE)
st.sidebar.write("Scheduler:", _settings.SCHEDULER_MODE)
