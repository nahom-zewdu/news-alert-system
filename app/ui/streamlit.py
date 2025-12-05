# app/ui/streamlit.py
"""
Streamlit demo UI with:
- live auto-refresh
- new item highlighting
- search & filtering (query, source, categories, date range)
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from app.core.config import settings as _settings

API_BASE = f"http://{_settings.APP_HOST}:{_settings.APP_PORT}/api"

st.set_page_config(page_title="News Alert Demo", layout="wide")
st.title("News Alert System — Demo Dashboard")

# Sidebar controls
st.sidebar.header("Config")
refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds)", 5, 60, 15)
st.sidebar.write(f"API: {API_BASE}")
st.sidebar.write(f"Scheduler: {_settings.SCHEDULER_MODE}")

st.sidebar.header("Filters")

# Search
query = st.sidebar.text_input("Search", placeholder="Search in title or summary...")

# Placeholders until data loads
_sources = []
_categories = []

# Date range defaults will be set after data is loaded
date_range = None

# Auto refresh
refresh_counter = st_autorefresh(interval=refresh_interval * 1000, limit=None)

# State for new item highlighting
if "last_ids" not in st.session_state:
    st.session_state.last_ids = set()

if "highlight_until" not in st.session_state:
    st.session_state.highlight_until = {}

now = datetime.now()

# Layout
col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("News")

    if st.button("Fetch now"):
        r = requests.post(f"{API_BASE}/fetch")
        if r.ok:
            st.success(f"Fetched {r.json().get('new_count')} new items")
        else:
            st.error("Fetch failed; check backend")

    # Load news
    r = requests.get(f"{API_BASE}/news")
    news = r.json() if r.ok else []
    if not r.ok:
        st.error("Failed to load news from API")

    # Convert to DataFrame for easier filtering
    df = pd.DataFrame(news)

    if not df.empty:
        # Extract sources and categories for sidebar
        _sources = sorted(df["source"].dropna().unique())
        _categories = sorted(
            set(cat for cats in df["categories"].dropna() for cat in cats)
        )

        # Set date range defaults only once
        if "default_date_range_set" not in st.session_state:
            min_date = pd.to_datetime(df["published_at"]).min().date()
            max_date = pd.to_datetime(df["published_at"]).max().date()
            st.session_state.default_date_range = (min_date, max_date)
            st.session_state.default_date_range_set = True

        date_range = st.sidebar.date_input(
            "Date Range",
            value=st.session_state.default_date_range,
        )

        sources_filter = st.sidebar.multiselect(
            "Sources",
            options=_sources,
            default=[],
        )

        categories_filter = st.sidebar.multiselect(
            "Categories",
            options=_categories,
            default=[],
        )

        # Apply Filters
        filtered = df.copy()

        # Search text
        if query:
            q = query.lower()
            filtered = filtered[
                filtered["title"].str.lower().str.contains(q)
                | filtered["summary"].str.lower().str.contains(q)
            ]

        # Filter by sources
        if sources_filter:
            filtered = filtered[filtered["source"].isin(sources_filter)]

        # Filter by categories
        if categories_filter:
            filtered = filtered[
                filtered["categories"].apply(
                    lambda lst: any(cat in lst for cat in categories_filter)
                )
            ]

        # Filter by date
        start, end = date_range
        filtered["published_at"] = pd.to_datetime(filtered["published_at"])
        filtered = filtered[
            (filtered["published_at"] >= pd.Timestamp(start))
            & (filtered["published_at"] <= pd.Timestamp(end))
        ]

        # Track new IDs for highlight
        current_ids = set(filtered["id"])
        new_ids = current_ids - st.session_state.last_ids

        for nid in new_ids:
            st.session_state.highlight_until[nid] = now.timestamp() + 10

        st.session_state.last_ids = current_ids

        # Render items
        for _, item in filtered.sort_values("published_at", ascending=False).iterrows():
            item = item.to_dict()

            highlight = False
            expire = st.session_state.highlight_until.get(item["id"])
            if expire and now.timestamp() < expire:
                highlight = True

            box_style = (
                "background-color: #fff3bf; padding: 10px; border-radius: 8px;"
                if highlight
                else "background-color: #f8f9fa; padding: 10px; border-radius: 8px;"
            )

            with st.container():
                st.markdown(f"<div style='{box_style}'>", unsafe_allow_html=True)

                st.subheader(item["title"])
                st.write(
                    f"Source: {item.get('source')} — Categories: {', '.join(item.get('categories', []))}"
                )
                st.write(item.get("summary") or "")

                if item.get("link"):
                    st.markdown(f"[Open link]({item['link']})")

                cols = st.columns([1, 5])
                with cols[0]:
                    if st.button("Send Alert", key=item["id"]):
                        send = requests.post(
                            f"{API_BASE}/send",
                            params={"news_id": item["id"]},
                        )
                        if send.ok:
                            st.success("Sent")
                        else:
                            st.error(send.text)

                with cols[1]:
                    st.write("")

                st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("No news items yet. Try fetching.")

with col_right:
    st.header("Alert history")
    resp = requests.get(f"{API_BASE}/alerts")
    if resp.ok:
        for al in reversed(resp.json()):
            st.write(
                f"To: {al['to']} | Subject: {al['subject']} | Sent: {al['sent']} | At: {al.get('sent_at')}"
            )
    else:
        st.write("Failed to load alert history")
