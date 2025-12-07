"""
Streamlit demo UI with:
- live auto-refresh
- new item highlighting
- search & filtering (query, source, category, date range)
- updated for single `category` string field
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

# Sidebar: Config
st.sidebar.header("Config")
refresh_interval = st.sidebar.slider("Auto-refresh (seconds)", 5, 60, 15)
st.sidebar.write(f"API: {API_BASE}")
st.sidebar.write(f"Scheduler: {_settings.SCHEDULER_MODE}")

st.sidebar.header("Filters")

# Search box
query = st.sidebar.text_input("Search", placeholder="Search title or summary...")

# Auto refresh
st_autorefresh(interval=refresh_interval * 1000, limit=None)

# Session state for highlighting new items
if "last_ids" not in st.session_state:
    st.session_state.last_ids = set()

if "highlight_until" not in st.session_state:
    st.session_state.highlight_until = {}

now = datetime.now()

# Main layout
col_left, col_right = st.columns([2.2, 1])

with col_left:
    st.subheader("News Feed")

    if st.button("Fetch Latest News"):
        r = requests.post(f"{API_BASE}/fetch")
        if r.ok:
            st.success(f"Fetched {r.json().get('new_count')} new items")
        else:
            st.error("Fetch failed")

    # Fetch from backend
    resp = requests.get(f"{API_BASE}/news")
    news = resp.json() if resp.ok else []
    if not resp.ok:
        st.error("Could not load news from backend")

    df = pd.DataFrame(news)

    if df.empty:
        st.info("No news items found. Try fetching.")
    else:
        # Extract sidebar options
        sources = sorted(df["source"].dropna().unique())
        categories = sorted(df["category"].dropna().unique())

        # Sidebar filters (after data available)
        selected_sources = st.sidebar.multiselect(
            "Source",
            options=sources,
            default=[],
        )

        selected_categories = st.sidebar.multiselect(
            "Category",
            options=categories,
            default=[],
        )

        # Date range (set defaults once)
        if "date_range_default" not in st.session_state:
            min_d = pd.to_datetime(df["published_at"]).min().date()
            max_d = pd.to_datetime(df["published_at"]).max().date()
            st.session_state.date_range_default = (min_d, max_d)

        date_range = st.sidebar.date_input(
            "Published Date",
            value=st.session_state.date_range_default,
        )

        # Apply filters
        filtered = df.copy()

        # Text search
        if query:
            q = query.lower()
            filtered = filtered[
                filtered["title"].str.lower().str.contains(q)
                | filtered["summary"].str.lower().str.contains(q)
            ]

        # Source filter
        if selected_sources:
            filtered = filtered[filtered["source"].isin(selected_sources)]

        # Category filter
        if selected_categories:
            filtered = filtered[filtered["category"].isin(selected_categories)]

        # Date filter
        start_date, end_date = date_range
        filtered["published_at"] = pd.to_datetime(filtered["published_at"])
        filtered = filtered[
            (filtered["published_at"] >= pd.Timestamp(start_date))
            & (filtered["published_at"] <= pd.Timestamp(end_date))
        ]

        # Highlight tracking
        current_ids = set(filtered["id"])
        new_ids = current_ids - st.session_state.last_ids

        for nid in new_ids:
            st.session_state.highlight_until[nid] = now.timestamp() + 10

        st.session_state.last_ids = current_ids

        # Render items
        for _, row in filtered.sort_values("published_at", ascending=False).iterrows():
            item = row.to_dict()

            highlight = False
            expiry = st.session_state.highlight_until.get(item["id"])
            if expiry and now.timestamp() < expiry:
                highlight = True

            box_style = (
                "background-color: #fff3bf; padding: 14px; border-radius: 8px; margin-bottom: 12px;"
                if highlight
                else "background-color: #f8f9fa; padding: 14px; border-radius: 8px; margin-bottom: 12px;"
            )

            with st.container():
                st.markdown(f"<div style='{box_style}'>", unsafe_allow_html=True)

                st.write(f"**{item['title']}**")
                st.caption(
                    f"📰 {item.get('source', 'N/A')}   |   🏷️ {item.get('category', 'N/A')}   |   "
                    f"{pd.to_datetime(item['published_at']).strftime('%Y-%m-%d %H:%M')}"
                )

                if item.get("summary"):
                    st.write(item["summary"])

                if item.get("link"):
                    st.markdown(f"[🔗 Read more]({item['link']})")

                if st.button("Send Alert", key=item["id"]):
                    send = requests.post(f"{API_BASE}/send", params={"news_id": item["id"]})
                    if send.ok:
                        st.success("Alert sent")
                    else:
                        st.error(send.text)

                st.markdown("</div>", unsafe_allow_html=True)

# Right panel: alert history
with col_right:
    st.subheader("Alert History")

    hist = requests.get(f"{API_BASE}/alerts")
    if hist.ok:
        for al in reversed(hist.json()):
            st.write(
                f"📧 **{al['to']}**\n\n"
                f"Subject: {al['subject']}\n\n"
                f"Sent: {al['sent']} at {al.get('sent_at')}"
            )
            st.markdown("---")
    else:
        st.write("Failed to load alert history")
