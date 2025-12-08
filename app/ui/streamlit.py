# app/ui/streamlit.py
"""
Streamlit demo UI for News Alert System
- Live auto-refresh
- Highlight new items for 10 seconds
- Search, filter by source, category, date
- Robust API response handling
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from app.core.config import settings as _settings

API_BASE = f"http://{_settings.APP_HOST}:{_settings.APP_PORT}/api/v1"

st.set_page_config(page_title="News Alert Demo", layout="wide")
st.title("News Alert System Demo Dashboard")

# Sidebar: Config
st.sidebar.header("Config")
refresh_interval = st.sidebar.slider("Auto-refresh (seconds)", 5, 60, 15)
st.sidebar.write(f"API: {API_BASE}")
st.sidebar.write(f"Scheduler: {_settings.SCHEDULER_MODE}")
query = st.sidebar.text_input("Search", placeholder="Search title or summary...")

# Auto-refresh
st_autorefresh(interval=refresh_interval * 1000, limit=None)

# Session state for highlights
if "last_ids" not in st.session_state:
    st.session_state.last_ids = set()
if "highlight_until" not in st.session_state:
    st.session_state.highlight_until = {}

now = datetime.now()

# Layout
col_left, col_right = st.columns([2.2, 1])

# ---------------- Left Panel: News Feed ----------------
with col_left:
    st.subheader("News Feed")

    # Fetch button
    if st.button("Fetch Latest News"):
        try:
            r = requests.post(f"{API_BASE}/news/fetch/")
            r.raise_for_status()
            new_count = r.json().get("new_count", 0)
            st.success(f"Fetched {new_count} new items")
        except Exception as e:
            st.error(f"Fetch failed: {e}")

    # Fetch news from API
    try:
        resp = requests.get(f"{API_BASE}/news/")
        resp.raise_for_status()
        news = resp.json() if isinstance(resp.json(), list) else []
    except Exception as e:
        st.error(f"Could not load news: {e}")
        news = []

    df = pd.DataFrame(news)
    if df.empty:
        st.info("No news items found. Try fetching.")
    else:
        # Sidebar filters
        sources = sorted(df["source"].dropna().unique())
        categories = sorted(df["category"].dropna().unique())
        selected_sources = st.sidebar.multiselect("Source", options=sources)
        selected_categories = st.sidebar.multiselect("Category", options=categories)

        # Date range filter
        if "date_range_default" not in st.session_state:
            min_d = pd.to_datetime(df["published_at"]).min().date()
            max_d = pd.to_datetime(df["published_at"]).max().date()
            st.session_state.date_range_default = (min_d, max_d)
        date_range = st.sidebar.date_input("Published Date", value=st.session_state.date_range_default)

        # Apply filters
        filtered = df.copy()
        if query:
            q = query.lower()
            filtered = filtered[
                filtered["title"].str.lower().str.contains(q) |
                filtered["summary"].str.lower().str.contains(q)
            ]
        if selected_sources:
            filtered = filtered[filtered["source"].isin(selected_sources)]
        if selected_categories:
            filtered = filtered[filtered["category"].isin(selected_categories)]

        start_date, end_date = date_range
        filtered["published_at"] = pd.to_datetime(filtered["published_at"])
        filtered = filtered[
            (filtered["published_at"] >= pd.Timestamp(start_date)) &
            (filtered["published_at"] <= pd.Timestamp(end_date))
        ]

        # Highlight new items
        current_ids = set(filtered["id"])
        new_ids = current_ids - st.session_state.last_ids
        for nid in new_ids:
            st.session_state.highlight_until[nid] = now.timestamp() + 10
        st.session_state.last_ids = current_ids

        # Render news items
        for _, row in filtered.sort_values("published_at", ascending=False).iterrows():
            item = row.to_dict()
            highlight = now.timestamp() < st.session_state.highlight_until.get(item["id"], 0)
            bg_color = "#fff3bf" if highlight else "#f8f9fa"

            with st.container():
                st.markdown(
                    f"<div style='background-color: {bg_color}; padding: 14px; border-radius: 8px; margin-bottom: 12px;'>",
                    unsafe_allow_html=True
                )
                st.write(f"**{item['title']}**")
                st.caption(
                    f"📰 {item.get('source', 'N/A')} | 🏷️ {item.get('category', 'N/A')} | "
                    f"{item['published_at'].strftime('%Y-%m-%d %H:%M')}"
                )
                if item.get("summary"):
                    st.write(item["summary"])
                if item.get("link"):
                    st.markdown(f"[🔗 Read more]({item['link']})")

                # Send alert
                if st.button("Send Alert", key=f"alert_{item['id']}"):
                    try:
                        send = requests.post(f"{API_BASE}/alerts/{item['id']}")
                        send.raise_for_status()
                        st.success("Alert sent")
                    except Exception as e:
                        st.error(f"Failed to send alert: {e}")

                st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Right Panel: Alert History ----------------
with col_right:
    st.subheader("Alert History")
    try:
        hist_resp = requests.get(f"{API_BASE}/alerts/")
        hist_resp.raise_for_status()

        resp_json = hist_resp.json()
        hist_data = resp_json.get("alerts", [])

    except Exception as e:
        st.error(f"Failed to load alert history: {e}")
        hist_data = []


    if hist_data:
        for al in reversed(hist_data):
            st.write(
                f"📧 **{al.get('to', 'N/A')}**\n\n"
                f"Subject: {al.get('subject', 'N/A')}\n\n"
                f"Sent: {al.get('sent', False)} at {al.get('sent_at', 'N/A')}"
            )
            st.markdown("---")
    else:
        st.info("No alerts found.")
